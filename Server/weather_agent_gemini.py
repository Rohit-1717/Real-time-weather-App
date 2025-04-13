

import os
import json
import re
import requests
from dotenv import load_dotenv
import google.generativeai as genai

# Load env variables
load_dotenv()
apikey = os.getenv("GOOGLE_GENAI_API_KEY")

# Configure Gemini client
genai.configure(api_key=apikey)

# Init Gemini model
model = genai.GenerativeModel(model_name="gemini-2.0-flash")


# --- Tool Functions ---
def get_weather(city: str):
    print("🔨 Tool Called: get_weather", city)
    url = f"https://wttr.in/{city}?format=%C+%t"
    response = requests.get(url)
    if response.status_code == 200:
        return f"The weather in {city} is {response.text.strip()}."
    return "Something went wrong"


def run_command(command: str):
    print("🔨 Tool Called: run_command", command)
    result = os.system(command)
    return str(result)


available_tools = {
    "get_weather": {
        "fn": get_weather,
        "description": "Takes a city name as input and returns current weather",
    },
    "run_command": {
        "fn": run_command,
        "description": "Takes a shell command as input and runs it on the system",
    },
}

# --- System Prompt ---
system_prompt = f"""
You are a helpful AI assistant who resolves user queries.
You operate in 4 steps: plan, action, observe, and output.

Rules:
- Follow the JSON output format strictly.
- Carefully analyze the user query and use the appropriate tool.
- You must perform all 4 steps in one go.

Output JSON Format:
{{
    "step": "string",
    "content": "string",
    "function": "The name of the function if the step is action",
    "input": "The input parameter for the function"
}}

Available Tools:
- get_weather: Takes a city name as input and returns current weather.
- run_command: Takes a shell command as input and executes it.

Example:
User Query: What is the weather of New York?
Output: {{ "step": "plan", "content": "The user is interested in the weather data of New York." }}
Output: {{ "step": "plan", "content": "From the available tools I should call get_weather." }}
Output: {{ "step": "action", "function": "get_weather", "input": "New York" }}
Output: {{ "step": "observe", "output": "Cloudy +12°C" }}
Output: {{ "step": "output", "content": "The weather in New York is Cloudy and 12°C." }}
"""


# --- Extract multiple JSON objects ---
def extract_json_objects(text: str):
    cleaned = text.replace("```json", "").replace("```", "").strip()
    matches = re.findall(r"\{.*?\}", cleaned, re.DOTALL)
    return [json.loads(match) for match in matches]


# --- Message Context ---
messages = [f"System:\n{system_prompt}"]

while True:
    user_query = input("\n> ")
    if user_query.lower() in ["exit", "quit"]:
        break

    messages.append(f"User: What is the weather in {user_query}?")

    while True:
        # Gemini response
        response = model.generate_content(
            messages, generation_config={"temperature": 0}
        )
        raw_reply = response.text.strip()

        try:
            steps = extract_json_objects(raw_reply)
        except Exception as e:
            print("❌ Failed to parse Gemini JSON response:\n", raw_reply)
            break

        for parsed in steps:
            step = parsed.get("step")
            messages.append(f"Assistant: {json.dumps(parsed)}")

            if step == "plan":
                print("🧠", parsed["content"])

            elif step == "action":
                tool_name = parsed.get("function")
                tool_input = parsed.get("input")

                if tool_name in available_tools:
                    tool_func = available_tools[tool_name]["fn"]
                    tool_output = tool_func(tool_input)
                    obs_msg = {"step": "observe", "output": tool_output}
                    print("👀 Observation:", tool_output)
                    messages.append(f"Assistant: {json.dumps(obs_msg)}")
                else:
                    print("❌ Tool not found:", tool_name)

            elif step == "output":
                print("🤖", parsed["content"])
                break
        break
