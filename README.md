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
11. [Prompting](/prompting/prompt_runner.py) Use evals to show how different prompting techniques can produce better responses
12. [Tool Use](/tool_use/app.py) Offer a set of functions that the language model can request to invoke
13. [Chunking Approaches](/rag/chunk_demo.py) Different approaches for splitting up text for processing in a RAG pipeline.
14. [Embeddings](/rag/embedding_demo.py) Use VoyageAI to create an embedding from a chunk of text
15. [RAG](/rag/rag_demo.py) Combine chunking and embeddings with the ChromaDB vector database to find relevant content.
16. [Lexical Search](/rag/enhanced_rag_demo.py) Combine RAG with BM25 key word search for both semantic match and exact match benefits.

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

# Prompt Engineering Process

1. Set a goal
2. Create an initial prompt
3. Eval the prompt
4. Apply prompt engineering technique
5. Re-eval to verify better performance, repeat step 4

# Prompt Engineering Techniques

- Be clear
   - Use simple language
   - State what you want explicitly
   - Lead your prompt with a simple statement of the model's task.
- Be direct
   - Use instructions not questions
   - Use direct action verbs
- Be specific
   - List qualities that the output should have
   - Provide steps the model should follow
- Structure with XML tags
   - Use XML tags to separate distinct portions of the prompt
- Provide examples

# Tool Use

By default, Claude only knows information from its training data and can't access current events, real-time data, or external systems. Tool use solves this limitation by creating a structured way for Claude to request and receive fresh information.

Flow
1. Initial Request: You send Claude a question along with instructions on how to get extra data from external sources
2. Tool Request: Claude analyzes the question and decides it needs additional information, then asks for specific details about what data it needs
3. Data Retrieval: Your server runs code to fetch the requested information from external APIs or databases
4. Final Response: You send the retrieved data back to Claude, which then generates a complete response using both the original question and the fresh data

Stop reasons

- `tool_use` Claude has determined it needs to call a tool
- `end_turn` Claude has finished generating its assistant message
- `max_tokens` Claude has hit the token limit and can't generate any more output
- `stop_sequence` Claude has encountered one of your provided stop sequences

The text edit tool

- Built directly into Claude
- Allows Claude to create, read and edit files and directories
- Only the schema is built in, you have to provide the implementation

# Retrieval Augmented Generation

Why not just put everything from a large document into the prompt?

- There's a hard limit on prompt length - your document might be too long
- Claude becomes less effective with very long prompts
- Larger prompts cost more to process
- Larger prompts take longer to process

Solution: Break the document into many chunks. Put chunks relevant to the user's question in the prompt.

Benefits:
-Claude can focus on only the most relevant content
- Scales up to very large documents
- Works with multiple documents
- Smaller prompts cost less and run faster

Challenges
- Requires a preprocessing step to chunk documents
- Need a search mechanism to find "relevant" chunks
- Included chunks might not contain all the context Claude needs
- Many ways to chunk text - which approach is best?

# Chunking Strategies

- Size based
   - Divide the text into strings of equal length
   - Include overlap on each side of the chunk to include context
   - Easy to implement but might break up related content
- Structure Based
   - Dive the text based upon the structure (headers, paragraphs, sections)
   - Avoids breaking up related content into multiple chunks
   - Requires us to understand the streucture of the document before hand
- Semantic Based
   - Divide text into groups of related sentences or sections
   - Requires us to understand the meaning of individual sentences
   - Computationally expensive but more relevant chunks


# Text Embeddings

A numerical representation of the meaning contained in some text.

Anthropic does not currently provide embeddings and they recommend using VoyageAI for this task.

`pip3 install voyageai`

```python
from dotenv import load_dotenv
import voyageai
import chunking

def generate_embedding(text, model="voyage-3-large", input_type="query"):
    result = client.embed([text], model=model, input_type=input_type)

    return result.embeddings[0]

if __name__ == "__main__":

    load_dotenv()

    client = voyageai.Client()

    with open("./report.md", "r") as f:
        text = f.read()

    chunks = chunking.chunk_by_section(text)

    embedding = generate_embedding(chunks[0])
    print("Embedding for first chunk:")
    print(embedding)
```

# Lexical Search

`pip3 install bm25s[all]`

```python
import bm25s

# 1. Define your document collection
documents = [
    "The quick brown fox jumps over the lazy dog",
    "Python is an amazing programming language for data science",
    "BM25 is a ranking function used by search engines to estimate relevance",
    "Artificial intelligence and machine learning are transforming industries"
]

# 2. Tokenize your text (breaks strings into words and applies stemming)
corpus_tokens = bm25s.tokenize(documents, stopwords="english")

# 3. Initialize and fit the BM25 index
retriever = bm25s.BM25(corpus=documents)
retriever.index(corpus_tokens)

# 4. Search the index using a query
query = "python programming search engine"
query_tokens = bm25s.tokenize(query)

# Retrieve the top 2 most relevant documents
results, scores = retriever.retrieve(query_tokens, k=2)

# 5. Display results
for doc, score in zip(results[0], scores[0]):
    print(f"(Score: {score:.4f}) -> {doc}")
```

# Extended Thinking

Extended thinking is Claude's advanced reasoning feature that gives the model time to work through complex problems before generating a final response.

With thinking enabled, you get both the reasoning process and the final answer.

The key benefits include:

- Better reasoning capabilities for complex tasks
- Increased accuracy on difficult problems
- Transparency into Claude's thought process

However, there are important trade-offs:

- Higher costs (you pay for thinking tokens)
- Increased latency (thinking takes time)
- More complex response handling in your code

# Citations

Citations reference specific parts of source documents and show users exactly where each piece of information comes from.

Citations are particularly valuable when:

- Users need to verify information for accuracy
- You're working with authoritative documents that users should be able to reference
- Transparency about information sources is critical for your application
- Users might want to explore the broader context around specific facts