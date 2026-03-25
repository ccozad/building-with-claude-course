from dotenv import load_dotenv
load_dotenv()

from anthropic import Anthropic

client = Anthropic()
model = "claude-sonnet-4-0"
concise_code_system_prompt ="""
When the user wants to generate code, generate the most concise code possible that accomplishes the task.
"""

def add_user_message(messages, text):
    user_message = {
        "role": "user",
        "content": text
    }
    messages.append(user_message)

def add_assistant_message(messages, text):
    assistant_message = {
        "role": "assistant",
        "content": text
    }
    messages.append(assistant_message)

def chat(messages, system_prompt=None):
    params = {
        "model": model,
        "max_tokens": 1000,
        "messages": messages
    }

    if system_prompt:
        params["system"] = system_prompt

    response = client.messages.create(**params)
    return response.content[0].text

messages = []
done = False
while not done:
    user_input = input("> ")
    if user_input.lower() in ["exit", "quit"]:
        done = True
        print("Exiting chat.")
    else:
        add_user_message(messages, user_input)
        print("Assistant is thinking...")
        response = chat(messages, system_prompt=concise_code_system_prompt)
        add_assistant_message(messages, response)
        print(f"Assistant: {response}")