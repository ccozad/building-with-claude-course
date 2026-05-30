import time_tools
import task_tools
#import batch_tools

# Helper functions
def add_user_message(messages, text):
    user_message = {"role": "user", "content": text}
    messages.append(user_message)


def add_assistant_message(messages, text):
    assistant_message = {"role": "assistant", "content": text}
    messages.append(assistant_message)


def chat(messages, system=None, temperature=1.0, stop_sequences=[]):
    params = {
        "model": model,
        "max_tokens": 1000,
        "messages": messages,
        "temperature": temperature,
        "stop_sequences": stop_sequences,
    }

    if system:
        params["system"] = system

    message = client.messages.create(**params)
    return message.content[0].text

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
        "content": "What is the exact time, formatted as HH:MM:SS?"
    })

    response = client.messages.create(
        model=model,
        messages=messages,
        tools=[time_tools.get_current_datetime_schema],
        max_tokens=1000,
    )

    messages.append({
        "role": "assistant",
        "content": response.content
    })

    current_time = time_tools.get_current_datetime(**response.content[0].input)

    messages.append({
        "role": "user",
        "content" :[
            {
                "type": "tool_result",
                "tool_use_id": response.content[0].id,
                "content": current_time,
                "is_error": False
            }
        ]
    })

    response = client.messages.create(
        model=model,
        messages=messages,
        tools=[time_tools.get_current_datetime_schema],
        max_tokens=1000,
    )

    messages.append({
        "role": "assistant",
        "content": response.content
    })
    
    print(messages)