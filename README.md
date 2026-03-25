# Introduction

Course work for https://anthropic.skilljar.com/claude-with-the-anthropic-api

# Setup

## Python Virtual Environment

 - Move to the building-with-claude-course folder
   - `cd <building-with-claude-course>`
 - Create a virtual environment
   - On Mac: `python3 -m venv .venv`
   - On Windows: `python -m venv .venv`
 - Activate the virtual environment
   - On Mac: `source .venv/bin/activate`
   - On Windows: `.venv\Scripts\activate`
 - Install dependencies
   - On Mac: `pip3 install -r requirements.txt`
   - On Windows: `pip install -r requirements.txt`
 - Call a specific script
   - On Mac: `python3 <script_name>.py`
   - On Windows: `python <script_name>.py`
 - Deactivate virtual environment
   - `deactivate`

# Exercises

1. [Intro](/intro.py) Minimal example to confirm depedendcies and API key
2. [Multi-turn](/multi-turn.py) Manage context over multiple model calls
3. [Chat Bot](/chat-bot.py) A practical example of context management and user input
4. [System Prompt](/system-prompt.py) Control how the model responds
5. [Concise Code](/concise-code.py) A practical example of using a system prompt to influence the type of code that the model generates

# Course Notes

- We create an Anthropic client using a funded API key and the model we want to use.

```python
from dotenv import load_dotenv
load_dotenv()

from anthropic import Anthropic

client = Anthropic()
model = "claude-sonnet-4-0"

message = client.messages.create(
    model=model,
    max_tokens=1000,
    messages=[
        {
            "role": "user",
            "content": "What is quantum computing? Answer in one sentence"
        }
    ]
)

print(message.content[0].text)
```

- Questions and responses are not stored between API calls.
- The caller is responsible for tracking state and passing in the full context with each call to the model.
- Multi-turn flows identify user input and assistant responses

```python
def add_user_message(messages, text):
    user_message = {
        "role": "user",
        "content": text
    }
    messages.append(user_message)
```

```python
def add_assistant_message(messages, text):
    assistant_message = {
        "role": "assistant",
        "content": text
    }
    messages.append(assistant_message)
```

```python
def chat(messages):
    response = client.messages.create(
        model=model,
        max_tokens=1000,
        messages=messages
    )
    return response.content[0].text
```

```python
messages = []
done = False
while not done:
    user_input = input("You: ")
    if user_input.lower() in ["exit", "quit"]:
        done = True
        print("Exiting chat.")
    else:
        add_user_message(messages, user_input)
        response = chat(messages)
        add_assistant_message(messages, response)
        print(f"Assistant: {response}")
```

- System prompts provide the model guidance on how to respond
- System prompts are passed into the create message call

```python
system_prompt ="""
You are a patient math tutor. 
Do not directly  answer a student's questions. 
Guide them to a solution step by step.
"""

#...

response = client.messages.create(
        model=model,
        max_tokens=1000,
        messages=messages,
        system=system_prompt
    )
"""