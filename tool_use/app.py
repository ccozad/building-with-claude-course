import json
import time_tools
import task_tools
#import batch_tools

from anthropic.types import Message

# Helper functions
def add_user_message(messages, message):
    user_message = {
        "role": "user", 
        "content": message.content if isinstance(message, Message) else message
    }
    messages.append(user_message)


def add_assistant_message(messages, message):
    assistant_message = {
        "role": "assistant",
        "content": message.content if isinstance(message, Message) else message
    }
    messages.append(assistant_message)


def chat(messages, system=None, temperature=1.0, stop_sequences=[], tools=None):
    params = {
        "model": model,
        "max_tokens": 1000,
        "messages": messages,
        "temperature": temperature,
        "stop_sequences": stop_sequences,
    }

    if system:
        params["system"] = system

    if tools:
        params["tools"] = tools

    message = client.messages.create(**params)
    return message


def text_from_message(message):
    return "\n".join(
        [block.text for block in message.content if block.type == "text"]
    )


def run_tool(tool_name, tool_input):
    if tool_name == "get_current_datetime":
        return time_tools.get_current_datetime(**tool_input)
    elif tool_name == "add_duration_to_datetime":
        return time_tools.add_duration_to_datetime(**tool_input)
    elif tool_name == "set_reminder":
        return task_tools.set_reminder(**tool_input)
    else:
        raise ValueError(f"No implementation for tool {tool_name}")


def run_tools(message):
    tool_requests = [
        block for block in message.content if block.type == "tool_use"
    ]

    tool_result_blocks = []

    for tool_request in tool_requests:
        tool_name = tool_request.name
        tool_input = tool_request.input

        try:
            result = run_tool(tool_name, tool_input)
            tool_result_blocks.append({
                "type": "tool_result",
                "tool_use_id": tool_request.id,
                "content": json.dumps(result),
                "is_error": False
            })
        except Exception as e:
            tool_result_blocks.append({
                "type": "tool_result",
                "tool_use_id": tool_request.id,
                "content": json.dumps({
                    "error": str(e)
                }),
                "is_error": True
            })
    
    return tool_result_blocks


def run_conversation(messages):
    while True:
        response = chat(messages, tools=[time_tools.get_current_datetime_schema])
        add_assistant_message(messages, response)
        print(text_from_message(response))
        
        if response.stop_reason != "tool_use":
            break

        tool_results = run_tools(response)
        add_user_message(messages, tool_results)

    return messages


if __name__ == "__main__":
    # Load env variables and create client
    from dotenv import load_dotenv
    from anthropic import Anthropic

    load_dotenv()

    client = Anthropic()
    model = "claude-haiku-4-5"

    messages = []

    messages.append({
        "role": "user",
        "content": "What is the current time, formatted as HH:MM:SS? Also, what is the current time in SS format?"
    })

    run_conversation(messages)

    print(messages)