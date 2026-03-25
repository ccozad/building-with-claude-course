from dotenv import load_dotenv
load_dotenv()

from anthropic import Anthropic

client = Anthropic()
model = "claude-sonnet-4-0"

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

def chat(messages):
    response = client.messages.create(
        model=model,
        max_tokens=1000,
        messages=messages
    )
    return response.content[0].text

messages = []
add_user_message(messages, "What is quantum computing? Answer in one sentence")
response = chat(messages)
add_assistant_message(messages, response)
add_user_message(messages, "Can you explain that in more detail?")
response = chat(messages)
add_assistant_message(messages, response)

for message in messages:
    print(f"{message['role']}: {message['content']}")