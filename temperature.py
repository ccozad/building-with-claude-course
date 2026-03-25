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

def chat(messages, system_prompt=None, temperature=0.7):
    params = {
        "model": model,
        "max_tokens": 1000,
        "messages": messages,
        "temperature": temperature
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
        low_temp_response = chat(messages, temperature=0.0)
        medium_temp_response = chat(messages, temperature=0.5)
        high_temp_response = chat(messages, temperature=0.9)
        print(f"Low Temperature Assistant: {low_temp_response}")
        print(f"Medium Temperature Assistant: {medium_temp_response}")
        print(f"High Temperature Assistant: {high_temp_response}")