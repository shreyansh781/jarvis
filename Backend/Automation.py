# Backend/Automation.py

from AppOpener import close, open as appopen
from webbrowser import open as webopen
from pywhatkit import search, playonyt
from dotenv import dotenv_values
from groq import Groq
import webbrowser
import requests
import keyboard
import asyncio
import os

# Load environment variables
env_vars = dotenv_values(".env")
GroqApiKey = env_vars.get("GroqAPIKey")

# Initialize Groq client
client = Groq(api_key=GroqApiKey)

# System chatbot definition
SystemChatbot = [
    {"role": "system", "content": f"Hello, I am {os.environ.get('Username', 'User')}, "
                                  "You're a content writer. You have to write content like "
                                  "letters, codes, applications, essays, notes, songs, poems etc."}
]

messages = []


# -------------------- FUNCTIONS --------------------

def GoogleSearch(Topic):
    search(Topic)
    return True


def Content(Topic):
    """Generate content using AI and open it in Notepad"""
    def OpenNotepad(File):
        os.system(f'start notepad.exe "{File}"')

    def ContentWriterAI(Prompt):
        messages.append({"role": "user", "content": Prompt})
        completion = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=SystemChatbot + messages,
            max_tokens=2048,
            temperature=0.7,
            top_p=1,
            stream=True,
            stop=None
        )
        Answer = ""
        for chunk in completion:
            if chunk.choices[0].delta.content:
                Answer += chunk.choices[0].delta.content
        Answer = Answer.replace("</s>", "")
        messages.append({"role": "assistant", "content": Answer})
        return Answer

    Topic = str(Topic.replace("content", "")).strip()
    ContentByAI = ContentWriterAI(Topic)

    filepath = f"Data\\{Topic.lower().replace(' ', '')}.txt"
    os.makedirs("Data", exist_ok=True)
    with open(filepath, "w", encoding="utf-8") as file:
        file.write(ContentByAI)

    OpenNotepad(filepath)
    return True


def YouTubeSearch(Topic):
    webbrowser.open(f"https://www.youtube.com/results?search_query={Topic}")
    return True


def PlayYoutube(query):
    playonyt(query)
    return True


def OpenApp(app):
    """Open an app locally or open its website if not found"""
    try:
        appopen(app, match_closest=True, output=True, throw_error=True)
        print(f"Opening {app}")
        return True
    except:
        webbrowser.open(f"https://{app.lower()}.com")
        print(f"Opening {app}")
        return True

def CloseApp(app):
    if "chrome" in app:
        pass
    else:
        try:
            close(app, match_closest=True, output=True, throw_error=True)
            return True
        except:
            return False

CloseApp("whatsapp")
def System(Command):
    """System-level volume controls"""
    if Command == "mute":
        keyboard.press_and_release("volume mute")
    elif Command == "unmute":
        keyboard.press_and_release("volume mute")
    elif Command == "volume up":
        keyboard.press_and_release("volume up")
    elif Command == "volume down":
        keyboard.press_and_release("volume down")
    return True


# -------------------- RUN ASYNC --------------------

async def TranslateAndExecute(commands: list[str]):
    funcs = []
    for command in commands:
        command = command.lower().strip()
        if command.startswith("open "):
            funcs.append(asyncio.to_thread(OpenApp, command.removeprefix("open ")))
        elif command.startswith("close "):
            funcs.append(asyncio.to_thread(CloseApp, command.removeprefix("close ")))
        elif command.startswith("play "):
            funcs.append(asyncio.to_thread(PlayYoutube, command.removeprefix("play ")))
        elif command.startswith("content "):
            funcs.append(asyncio.to_thread(Content, command.removeprefix("content ")))
        elif command.startswith("google search "):
            funcs.append(asyncio.to_thread(GoogleSearch, command.removeprefix("google search ")))
        elif command in ["mute", "unmute", "volume up", "volume down"]:
            funcs.append(asyncio.to_thread(System, command))
        else:
            print(f"No matching function for: {command}")

    results = await asyncio.gather(*funcs)
    for result in results:
        yield result


async def Automation(commands: list[str]):
    async for _ in TranslateAndExecute(commands):
        pass
    return True


# -------------------- RUN STANDALONE --------------------

