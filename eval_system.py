import json
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

def run_prompt(prompt, test_case):
    prompt = f"{prompt}\n\n{test_case['task']}"
    messages = []
    add_user_message(messages, prompt)
    add_assistant_message(messages, "```json")
    response = chat(messages, stop_sequences=["```"])
    return response

def run_test_case(prompt, test_case):
    """Calls run_prompt, then grades the results"""
    output = run_prompt(prompt, test_case)
    
    score = 10

    return {
        "output": output,
        "test_case": test_case,
        "score": score
    }

def chat(
    messages, 
    system_prompt=None, 
    temperature=0.7, 
    stop_sequences=[]):
    params = {
        "model": model,
        "max_tokens": 1000,
        "messages": messages,
        "temperature": temperature
    }

    if system_prompt:
        params["system"] = system_prompt
    if stop_sequences:
        params["stop_sequences"] = stop_sequences

    response = client.messages.create(**params)
    return response.content[0].text

def run_evaluations(prompt,test_cases_file):
    results = []
    with open(test_cases_file, "r") as f:
        test_cases = json.load(f)
        for test_case in test_cases:
            result = run_test_case(prompt, test_case)
            results.append(result)
    return results

if __name__ == "__main__":
    prompt = "Please solve the following task:"
    print(f"Running evaluations with prompt: {prompt}")
    results = run_evaluations(prompt, "eval_dataset.json")
    print(f"Results:")
    for result in results:
        print(f"Test Case: {result['test_case']['task']}")
        print(f"Output: {result['output']}")
        print(f"Score: {result['score']}")
        print("-" * 20)