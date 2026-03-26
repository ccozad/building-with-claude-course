from dotenv import load_dotenv
load_dotenv()

from anthropic import Anthropic

client = Anthropic()
model = "claude-sonnet-4-0"
json_system_prompt ="""
Your job is to create mock data in JSON format based on the user's request. The user will specify the type of data they need and any relevant details. You should generate a JSON object that matches the user's specifications. Make sure the JSON is properly formatted and valid.
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

def json_chat(messages, system_prompt=None):
    params = {
        "model": model,
        "max_tokens": 1000,
        "messages": messages,
        "stop_sequences": ["```"]
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
        add_assistant_message(messages, "```json")
        print("Assistant is thinking...")
        response = json_chat(messages, system_prompt=json_system_prompt)
        print(f"Assistant: {response}")