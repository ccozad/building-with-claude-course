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

def specific_prompt(prompt_inputs):
    prompt = f"""
Generate a one-day meal plan for an athlete that meets their dietary restrictions.

- Height: {prompt_inputs["height"]}
- Weight: {prompt_inputs["weight"]}
- Goal: {prompt_inputs["goal"]}
- Dietary restrictions: {prompt_inputs["restrictions"]}

Guidelines:
1. Include accurate daily calorie amount
2. Show protein, fat, and carb amounts  
3. Specify when to eat each meal
4. Use only foods that fit restrictions
5. List all portion sizes in grams
6. Keep budget-friendly if mentioned
"""
    messages = []
    chat_model.add_user_message(messages, prompt)
    return chat_model.chat(messages)

def xml_prompt(prompt_inputs):
    prompt = f"""
Generate a one-day meal plan for an athlete that meets their dietary restrictions.

<athlete_information>
- Height: {prompt_inputs["height"]}
- Weight: {prompt_inputs["weight"]}
- Goal: {prompt_inputs["goal"]}
- Dietary restrictions: {prompt_inputs["restrictions"]}
</athlete_information>

<guidelines>
1. Include accurate daily calorie amount
2. Show protein, fat, and carb amounts  
3. Specify when to eat each meal
4. Use only foods that fit restrictions
5. List all portion sizes in grams
6. Keep budget-friendly if mentioned
</guidelines>
"""
    messages = []
    chat_model.add_user_message(messages, prompt)
    return chat_model.chat(messages)

def one_shot_prompt(prompt_inputs):
    prompt = f"""
Generate a one-day meal plan for an athlete that meets their dietary restrictions.

<athlete_information>
- Height: {prompt_inputs["height"]}
- Weight: {prompt_inputs["weight"]}
- Goal: {prompt_inputs["goal"]}
- Dietary restrictions: {prompt_inputs["restrictions"]}
</athlete_information>

<guidelines>
1. Include accurate daily calorie amount
2. Show protein, fat, and carb amounts  
3. Specify when to eat each meal
4. Use only foods that fit restrictions
5. List all portion sizes in grams
6. Keep budget-friendly if mentioned
</guidelines>

<ideal_output>
# One-Day Marathon Training Meal Plan
**Target: 3,200 calories | Carbs: 520g | Protein: 120g | Fat: 80g**

---

## BREAKFAST (7:00 AM) - 850 calories
**Carb-Loading Oatmeal Bowl**
- Rolled oats: 100g
- Banana: 150g
- Honey: 40g
- Whole milk: 250ml
- Almonds: 25g
- Berries (blueberries): 80g

**Macros:** Carbs 120g | Protein 22g | Fat 18g

---

## MID-MORNING SNACK (10:00 AM) - 450 calories
**Pre-Run Fuel**
- White bread: 80g
- Peanut butter: 30g
- Apple: 180g
- Energy drink (sports): 400ml

**Macros:** Carbs 95g | Protein 12g | Fat 10g

---

## LUNCH (1:00 PM) - 950 calories
**Carbohydrate-Rich Pasta**
- Spaghetti (cooked): 250g
- Lean ground turkey: 150g
- Tomato-based pasta sauce: 200ml
- Olive oil: 15ml
- Parmesan cheese: 20g
- Side salad with mixed greens: 100g
- Breadroll: 60g

**Macros:** Carbs 145g | Protein 45g | Fat 24g

---

## POST-RUN SNACK (4:00 PM) - 400 calories
**Recovery Shake**
- Greek yogurt: 200g
- White rice cakes: 50g
- Honey: 25g
- Whole milk: 200ml
- Protein powder (whey): 25g

**Macros:** Carbs 75g | Protein 28g | Fat 6g

---

## DINNER (7:00 PM) - 550 calories
**Salmon with Rice**
- Salmon fillet: 150g
- White rice (cooked): 200g
- Broccoli: 150g
- Butter: 10ml
- Sea salt & lemon: to taste

**Macros:** Carbs 85g | Protein 45g | Fat 12g

---

## EVENING SNACK (9:30 PM) - 100 calories
- Banana: 120g

**Macros:** Carbs 27g | Protein 1g | Fat 0.3g

---

## **DAILY TOTALS**
| Nutrient | Amount |
|----------|--------|
| **Calories** | **3,300** |
| **Carbohydrates** | **547g (66%)** |
| **Protein** | **153g (18%)** |
| **Fat** | **70g (19%)** |

---

## HYDRATION NOTES
- 3-4 liters of water throughout the day
- 400ml sports drink during run
- Electrolyte drink post-run (included in snack)

**Budget estimate:** $12-14 USD | Suitable for 3-hour+ marathon training sessions",

</ideal_output>

The ideal output comprehensively meets all mandatory requirements: it provides a daily caloric total (3,300), complete macronutrient breakdown (carbs/protein/fat with percentages), and includes all meals with exact foods, portions, and specific timing (7:00 AM through 9:30 PM). It exceeds the 3,000+ calorie target and achieves the 55-65% carbohydrate range at 66%. Hydration is addressed with specific recommendations (3-4 liters water, sports drink timing). The plan includes breakfast, lunch, dinner, and three snacks. The only minor considerations are that protein is slightly elevated for a carb-loading day and the presentation, while excellent for clarity, is not minimalist. However, these do not violate any stated criteria. The solution directly addresses the athlete's marathon training goal with appropriate carbohydrate loading strategy."

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
        },
        "specific_prompt": {
            "function": specific_prompt,
            "json_output_file": "specific_prompt_output.json",
            "html_output_file": "specific_prompt_output.html"
        },
        "xml_prompt": {
            "function": xml_prompt,
            "json_output_file": "xml_prompt_output.json",
            "html_output_file": "xml_prompt_output.html"
        },
        "one_shot_prompt": {
            "function": one_shot_prompt,
            "json_output_file": "one_shot_prompt_output.json",
            "html_output_file": "one_shot_prompt_output.html"
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
