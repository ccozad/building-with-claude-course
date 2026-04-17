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


if __name__ == "__main__":
    load_dotenv()

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
        run_prompt_function=base_prompt, 
        dataset_file="dataset.json",
        extra_criteria="""
The output should include:
- Daily caloric total
- Macronutrient breakdown  
- Meals with exact foods, portions, and timing
"""
    )
