import json
import time
import ast
import re
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

def grade_by_model(test_case, output):
    eval_prompt = f"""
    You are an expert code reviewer. Evaluate this AI-generated solution.
    
    Original Task:
    <task>
    {test_case['task']}
    </task>

    Solution Criteria:
    <criteria>
    {test_case['solution_criteria']}
    </criteria>

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

def run_prompt(prompt, system_prompt, test_case):
    prompt = f"{prompt}\n\n{test_case['task']}"
    messages = []
    add_user_message(messages, prompt)
    add_assistant_message(messages, "```code")
    response = chat(messages, system_prompt=system_prompt, stop_sequences=["```"])
    return response

def run_test_case(prompt, system_prompt, test_case):
    """Calls run_prompt, then grades the results"""
    output = run_prompt(prompt, system_prompt, test_case)
    
    model_grade = grade_by_model(test_case, output)
    model_score = model_grade.get("score", 0)
    reasoning = model_grade.get("reasoning", "")

    code_grade = grade_syntax(output, test_case)
    score = (model_score + code_grade) / 2

    return {
        "output": output,
        "test_case": test_case,
        "score": score,
        "reasoning": reasoning
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

def run_evaluations(prompt, system_prompt=None, test_cases_file=None):
    results = []
    with open(test_cases_file, "r") as f:
        test_cases = json.load(f)
        for test_case in test_cases:
            print(f"Running test case: {test_case['task']}...")
            start_time = time.time()
            result = run_test_case(prompt, system_prompt, test_case)
            end_time = time.time()
            print(f" Done. (Elapsed Time: {end_time - start_time:.2f} seconds)")
            results.append(result)
    return results

if __name__ == "__main__":
    system_prompt = """
- Only return the code solution to the user's task. 
- Do not include any explanations or reasoning, just return the code.
- Responses should only be JSON, plain Regex or Python
"""
    print(f"System Prompt: {system_prompt}")
    prompt = "Please solve the following task:"
    print(f"Prompt: {prompt}")
    results = run_evaluations(prompt, system_prompt, "eval_dataset.json")
    average_score = sum(result['score'] for result in results) / len(results)
    print(f"Average Score: {average_score:.2f}/10")
    print(f"Details:")
    for result in results:
        print(f"Test Case: {result['test_case']['task']}")
        print(f"Format: {result['test_case']['format']}")
        print(f"Output: {result['output']}")
        print(f"Score: {result['score']}")
        print(f"Reasoning: {result['reasoning']}")
        print("-" * 20)