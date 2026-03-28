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

def run_prompt(prompt, system_prompt, test_case):
    prompt = f"{prompt}\n\n{test_case['task']}"
    messages = []
    add_user_message(messages, prompt)
    add_assistant_message(messages, "```json")
    response = chat(messages, system_prompt=system_prompt, stop_sequences=["```"])
    return response

def run_test_case(prompt, system_prompt, test_case):
    """Calls run_prompt, then grades the results"""
    output = run_prompt(prompt, system_prompt, test_case)
    
    model_grade = grade_by_model(test_case, output)
    score = model_grade.get("score", 0)
    reasoning = model_grade.get("reasoning", "")

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
            result = run_test_case(prompt, system_prompt, test_case)
            results.append(result)
    return results

if __name__ == "__main__":
    system_prompt = """
Only return the code solution to the user's task. Do not include any explanations or reasoning, just return the code.
"""
    print(f"System Prompt: {system_prompt}")
    prompt = "Please solve the following task:"
    print(f"Prompt: {prompt}")
    results = run_evaluations(prompt, system_prompt, "eval_dataset.json")
    print(f"Results:")
    for result in results:
        print(f"Test Case: {result['test_case']['task']}")
        print(f"Output: {result['output']}")
        print(f"Score: {result['score']}")
        print(f"Reasoning: {result['reasoning']}")
        print("-" * 20)