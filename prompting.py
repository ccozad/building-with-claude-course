import os
from dotenv import load_dotenv
from anthropic import Anthropic
from prompt_evaluator import PromptEvaluator
from chat_model import ChatModel

def base_prompt(prompt_inputs):
    prompt = f"""
What should this person eat?

- Height: {prompt_inputs["height"]}
- Weight: {prompt_inputs["weight"]}
- Goal: {prompt_inputs["goal"]}
- Dietary restrictions: {prompt_inputs["restrictions"]}
"""
    messages = []
    chat_model.add_user_message(messages, prompt)
    return chat_model.chat(messages)

def clear_and_direct_prompt(prompt_inputs):
    prompt = f"""
Generate a one-day meal plan for an athlete that meets their dietary restrictions.

- Height: {prompt_inputs["height"]}
- Weight: {prompt_inputs["weight"]}
- Goal: {prompt_inputs["goal"]}
- Dietary restrictions: {prompt_inputs["restrictions"]}
"""
    messages = []
    chat_model.add_user_message(messages, prompt)
    return chat_model.chat(messages)



if __name__ == "__main__":
    load_dotenv()

    #  Read the prompt to use from the first command line argument, defaulting to base_prompt if not provided
    import argparse
    parser = argparse.ArgumentParser(description="Evaluate prompts for meal planning.")
    parser.add_argument("--prompt", type=str, default="base_prompt", help="The prompt to evaluate: base_prompt or clear_and_direct_prompt")
    args = parser.parse_args()

    prompts = {
        "base_prompt": {
            "function": base_prompt,
            "json_output_file": "base_prompt_output.json",
            "html_output_file": "base_prompt_output.html"
        },
        "clear_and_direct_prompt": {
            "function": clear_and_direct_prompt,
            "json_output_file": "clear_and_direct_prompt_output.json",
            "html_output_file": "clear_and_direct_prompt_output.html"
        }
    }

    if args.prompt not in prompts:
        print(f"Invalid prompt choice: {args.prompt}. Valid options are: {list(prompts.keys())}")
        exit(1)


    client = Anthropic()
    model = "claude-haiku-4-5"
    chat_model = ChatModel(client, model)

    evaluator = PromptEvaluator(max_concurrency=1, chat_model=chat_model)

    # If dataset.json doesn't exist, create it.
    if not os.path.exists("dataset.json"):
        dataset = evaluator.generate_dataset(
                task_description="Write a compact, concise 1 day meal plan for a single athlete",
                prompt_inputs_spec={
                    "height": "Athlete's height in cm",
                    "weight": "Athlete's weight in kg", 
                    "goal": "Goal of the athlete",
                    "restrictions": "Dietary restrictions of the athlete"
                },
                output_file="dataset.json",
                num_cases=3
        )

    results = evaluator.run_evaluation(
        run_prompt_function=prompts[args.prompt]["function"], 
        dataset_file="dataset.json",
        json_output_file=prompts[args.prompt]["json_output_file"],
        html_output_file=prompts[args.prompt]["html_output_file"],
        extra_criteria="""
The output should include:
- Daily caloric total
- Macronutrient breakdown  
- Meals with exact foods, portions, and timing
"""
    )
