from google import genai
from google.genai import types
from json import load, dump
import datetime
from dotenv import dotenv_values

# Load environment variables from .env
env_vars = dotenv_values(".env")

# Get values from .env
Username = env_vars.get("Username")
Assistantname = env_vars.get("Assistantname")
GeminiAPIKey = env_vars.get("GeminiAPIKey")

# Initialize Gemini client
client = genai.Client(api_key=GeminiAPIKey)

# Chat messages list
messages = []

# System prompt
System = f"""Hello, I am {Username}, You are a very accurate and advanced AI chatbot named {Assistantname} which also has real-time up-to-date information from the internet. I created you.

*** Do not tell time until I ask, do not talk too much, just answer the question. ***
*** Reply in only English, if the question is in other language , reply in that language and in other case if the asker ask in specific language. ***
*** Do not provide notes in the output, just answer the question and never mention your training data. ***
"""

# Load existing chat log
try:
    with open(r"Data\\ChatLog.json", "r") as f:
        messages = load(f)

except FileNotFoundError:
    with open(r"Data\\ChatLog.json", "w") as f:
        dump([], f)

# Real-time information
def RealtimeInformation():
    current_date_time = datetime.datetime.now()

    day = current_date_time.strftime("%A")
    date = current_date_time.strftime("%d")
    month = current_date_time.strftime("%B")
    year = current_date_time.strftime("%Y")
    hour = current_date_time.strftime("%H")
    minute = current_date_time.strftime("%M")
    second = current_date_time.strftime("%S")

    data = f"Please use this real-time information if needed,\n"
    data += f"Day: {day}\n"
    data += f"Date: {date}\n"
    data += f"Month: {month}\n"
    data += f"Year: {year}\n"
    data += f"Time: {hour}:{minute}:{second}\n"

    return data

# Clean response
def AnswerModifier(answer):
    lines = answer.split("\n")
    non_empty_lines = [line for line in lines if line.strip()]
    return "\n".join(non_empty_lines)

# Main chatbot function
def ChatBot(Query):

    try:
        # Load chat history
        with open(r"Data\\ChatLog.json", "r") as f:
            messages = load(f)

        # Add user query
        messages.append({"role": "user", "content": Query})

        # Build conversation history
        conversation = ""

        for msg in messages:
            role = msg["role"]
            content = msg["content"]

            if role == "user":
                conversation += f"User: {content}\n"

            elif role == "assistant":
                conversation += f"Assistant: {content}\n"

        # Final prompt
        FullPrompt = f"""
{System}

{RealtimeInformation()}

Conversation History:
{conversation}

User: {Query}
Assistant:
"""

        # Generate response
        response = client.models.generate_content(
            model="gemini-3.5-flash-lite",
            contents=FullPrompt,
            config=types.GenerateContentConfig(
                temperature=0.7,
                max_output_tokens=800,
            )
        )

        Answer = response.text

        # Save assistant response
        messages.append({"role": "assistant", "content": Answer})

        # Save chat log
        with open(r"Data\\ChatLog.json", "w") as f:
            dump(messages, f, indent=4)

        return AnswerModifier(Answer)

    except Exception as e:
        print(f"Error: {e}")

        with open(r"Data\\ChatLog.json", "w") as f:
            dump([], f, indent=4)

        return ChatBot(Query)

# Main
if __name__ == "__main__":

    while True:
        user_input = input("Enter Your Question: ")
        print(ChatBot(user_input))