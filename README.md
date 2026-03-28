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
6. [Temperature](/temperature.py) Use the temperature setting to control the randmoness of responses
7. [Streaming](/streaming.py) Stream intermediate results to improve UX
8. [Structured Data](/structured-data.py) Capture structured data like JSON with a pre-fill response and stop sequences
9. [Generate Eval Data](/generate-eval-dataset.py) Generate test data for evaluations using multishot prompts and structured data responses
10. [Evaluation System](/eval_system.py) A pipeline for combining prompts with test cases, running them against the model and grading the result.

# Course Notes

## Intro

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

## Multi-turn

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

# System Prompts

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
```

## Temperature

- Temperature controls how predictable or creative the model outputs will be.
- Temperature ranges:
   - Low (0.0-0.3)
      - Factual responses
      - Coding assistance
      - Data extraction
      - Content moderation
   - Medium (0.4-0.7)
      - Summarization
      - Educational content
      - Problem-solving
      - Creative writing with constraints
   - High (0.8-1.0)
      - Brainstorming
      - Creative writing
      - Marketing content
      - Joke generation

```python
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
```

## Streaming

- Streaming mode allows the model to return data in chuncks as it is generated
- Common streaming events include:
   - **MessageStart** A new message is being sent
   - **ContentBlockStart** Start of a new block containing text, tool use, or other content
   - **ContentBlockDelta** Chunks of the actual generated text
   - **ContentBlockStop** The current content block has been completed
   - **MessageDelta** The current message is complete
   - **MessageStop** End of information about the current message
- We can stream the data for better UX and still capture the full message from the completed stream

```python
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
```

## Structured Data

- Message pre-filling and stop sequences can be combined to output only structured data

```python
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
```

```python
add_user_message(messages, user_input)
add_assistant_message(messages, "```json")
print("Assistant is thinking...")
response = json_chat(messages, system_prompt=json_system_prompt)
print(f"Assistant: {response}")
```

# Prompt Evaluation

- Prompt engineering is a set of best practices and guidance to improve your prompts
   - Being clear
   - Being specific
   - Output formatting
   - Multishot prompting
   - Structuring with XML tags
- Prompt evaluation is automated testing to measure how well your prompts work
   - Test agent expected answers
   - Compile different versions of the same prompt
   - Review outputs for errors

# Typical Eval Workflow

- Draft prompt
- Create an eval dataset
- Feed through Claude
- Feed through a grader
- Change prompt and repeat

# Generate Evaluations

- Claude can be used to generate evaluation datasets using multishot prompts and structured output.

````python
def generate_dataset():
    prompt = """
Generate an evaluation dataset for a prompt evaluation. The dataset will be used to evaluate prompts that generate Python, JSON, or Regex specifically for AWS-related tasks. Generate an array of JSON objects, each representing task that requires Python, JSON, or a Regex to complete.

Example output:
```json
[
  {
    "task": "Description of task",
  },
  ...additional
]
```

* Focus on tasks that can be solved by writing a single Python function, a single JSON object, or a single regex
* Focus on tasks that do not require writing much code

Please generate 3 objects.
"""

    messages = []
    add_user_message(messages, prompt)
    add_assistant_message(messages, "```json")
    response = chat(messages, stop_sequences=["```"])
    return json.loads(response)
````

# Evaluation Systems

- Evaluation systems provide a pipeline for combining a prompt with a test case, generating a response from the model and a grading system for the output.
- The is no one right way to implement an evaluation pipeline

# Grading

- Code
    - Programatically evaluate the result
    - Useful for:
        - Checking output length
        - Verifying outpt does/doesn't have certain words
        - Syntax validation
        - Readability scores
- Model
    - Ask a model to assign a score to the output, or compare two versions
    - Useful for:
        - Response quality
        - Quality of instruction following
        - Completeness
        - Helpfulness
        - Safety
- Human
    - Ask a human to assign a score to the output, or compare two versions
    - Useful for:
        - General response quality
        - Comprehensiveness
        - Depth
        - Conciseness
        - Relevance

# Grade by Model

- Don't just ask the model for a score, ask for positive and negative reasoning

```python
def grade_by_model(test_case, output):
    eval_prompt = f"""
    You are an expert code reviewer. Evaluate this AI-generated solution.
    
    Original Task:
    <task>
    {test_case['task']}
    </task>

    Solution to Evaluate:
    <solution>
    {output}
    </solution>
    
    Provide your evaluation as a structured JSON object with:
    - "strengths": An array of 1-3 key strengths
    - "weaknesses": An array of 1-3 key areas for improvement  
    - "reasoning": A concise explanation of your assessment
    - "score": A number between 1-10
    """
    
    messages = []
    add_user_message(messages, eval_prompt)
    add_assistant_message(messages, "```json")
    
    eval_text = chat(messages, stop_sequences=["```"])
    return json.loads(eval_text)
```

# Grade by Code

- Use code based mechanisms such as compilers and syntax checkers to evaluate results

```python
def validate_json(text):
    try:
        json.loads(text.strip())
        return 10
    except json.JSONDecodeError:
        return 0

def validate_python(text):
    try:
        ast.parse(text.strip())
        return 10
    except SyntaxError:
        return 0

def validate_regex(text):
    try:
        re.compile(text.strip())
        return 10
    except re.error:
        return 0

def grade_syntax(response, test_case):
    if test_case.get("format") == "json":
        return validate_json(response)
    elif test_case.get("format") == "python":
        return validate_python(response)
    elif test_case.get("format") == "regex":
        return validate_regex(response)
    else:
        return 0
```