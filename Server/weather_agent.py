import json
import requests
from dotenv import load_dotenv
from openai import OpenAI
import os
import re

load_dotenv()

# ⚙️ Setup Gemini (OpenAI-compatible client)
client = OpenAI(
    api_key=os.getenv("GOOGLE_GENAI_API_KEY"),
    base_url="https://generativelanguage.googleapis.com/v1beta/",
)

# 🛠️ Tools


def get_weather(city: str):
    print("🔨 Tool Called: get_weather", city)
    url = f"https://wttr.in/{city}?format=%C+%t"
    response = requests.get(url)
    if response.status_code == 200:
        return f"The weather in {city} is {response.text.strip()}."
    return "Something went wrong"


def run_command(command):
    result = os.system(command)
    return str(result)


available_tools = {
    "get_weather": {
        "fn": get_weather,
        "description": "Takes a city name as input and returns the current weather for the city.",
    },
    "run_command": {
        "fn": run_command,
        "description": "Executes a command on the system and returns its output.",
    },
}

# 🧠 Prompt for Gemini
system_prompt = """
You are a helpful AI assistant using multi-step reasoning.

You always follow this format step-by-step:
1. "step": "start"
2. "step": "plan"
3. "step": "action" (with "function" and "input")
4. "step": "observe"
5. "step": "output"

Each response must be a JSON object like:
{
    "step": "string",
    "content": "string",
    "function": "string (if step is 'action')",
    "input": "string (if step is 'action')"
}

Available tools:
- get_weather: Takes a city name as input and returns the current weather.
- run_command: Executes system commands and returns output.

Note:
Don't give response to any other query except weather related queries.
Input: Who is Narendra Modi?
Output: Sorry but I'm only trained for giving weather information. For these type of queries visit to news web portal. Thank You :)

Also don't call available_tools. Just response the output.
"""


# 🧠 Main handler for LLM reasoning + tool usage
def handle_user_query(user_query: str):
    messages = [{"role": "system", "content": system_prompt}]
    messages.append({"role": "user", "content": user_query})

    steps = []

    while True:
        response = client.chat.completions.create(
            model="gemini-2.0-flash",
            response_format={"type": "json_object"},
            messages=messages,
        )

        parsed_output = json.loads(response.choices[0].message.content)
        steps.append(parsed_output)
        messages.append({"role": "assistant", "content": json.dumps(parsed_output)})

        if parsed_output.get("step") == "plan":
            continue

        if parsed_output.get("step") == "action":
            tool_name = parsed_output.get("function")
            tool_input = parsed_output.get("input")

            if available_tools.get(tool_name):
                output = available_tools[tool_name]["fn"](tool_input)
                observe_step = {
                    "step": "observe",
                    "content": f"Observed result from tool: {output}",
                }
                steps.append(observe_step)
                messages.append(
                    {"role": "assistant", "content": json.dumps(observe_step)}
                )
                continue

        if parsed_output.get("step") == "output":
            break

    return {"steps": steps, "result": parsed_output.get("content")}
