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
        with client.messages.stream(
            model=model,
            max_tokens=1000,
            messages=messages
        ) as stream:
            for text in stream.text_stream:
                print(text, end="")
            
            final_message = stream.get_final_message()
            # Write the final message to a file
            with open("final_message.txt", "w") as f:
                f.write(final_message.content[0].text)