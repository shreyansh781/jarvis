from googlesearch import search
from groq import Groq
from json import load, dump
import datetime
from dotenv import dotenv_values
import ddgs
import re

# Load environment variables
env_vars = dotenv_values(".env")
Username = env_vars.get("Username")
Assistantname = env_vars.get("Assistantname")
GroqAPIKey = env_vars.get("GroqAPIKey")

client = Groq(api_key=GroqAPIKey)

System = f"""Hello, I am {Username}, You are a very accurate and advanced AI chatbot named {Assistantname} which has real-time up-to-date information from the internet.
*** Provide answers professionally using correct grammar, punctuation, and facts. ***"""

try:
    with open(r"Data\ChatLog.json", "r") as f:
        messages = load(f)
except:
    with open(r"Data\ChatLog.json", "w") as f:
        dump([], f)

# Temporary memory for last site
last_site = {"name": None, "url": None}

def GoogleSearch(query: str) -> str:
    """
    Perform a DuckDuckGo search and return formatted results.
    """
    global last_site
    try:
        # If user asks for "that site"
        if re.search(r"(that site|previous site|site link)", query, re.I):
            if last_site["url"]:
                return f"The link to {last_site['name']} is: {last_site['url']}"
            else:
                return "No previous site reference found."

        # If user specifies a particular site
        site_match = re.search(r"(on|from)\s+([a-zA-Z0-9\-\.]+)", query)
        if site_match:
            site = site_match.group(2).replace(".com", "").strip()
            query = query.replace(site, "").strip()
        else:
            site = None

        with ddgs() as ddgs:
            results = list(ddgs.text(query, max_results=5))

        if not results:
            return f"No search results found for '{query}'."

        answer = [f"Here’s what I found for '{query}':", "[start]"]

        # store site if found in results
        first_link = None

        for r in results:
            title = r.get("title", "No title available")
            body = r.get("body", "No description available")
            href = r.get("href", "")

            # detect site domain
            domain_match = re.search(r"https?://(?:www\.)?([^/]+)", href)
            domain = domain_match.group(1).replace("www.", "") if domain_match else "unknown site"

            if not first_link and href:
                first_link = href
                last_site["url"] = href
                last_site["name"] = domain.split(".")[0].capitalize()

            # if user specified a site, filter for it
            if site and site not in domain:
                continue

            answer.append(f"From {domain.split('.')[0].capitalize()}: {body}")

        answer.append("[end]")

        if first_link:
            last_site["url"] = first_link
            if site:
                last_site["name"] = site.capitalize()

        return "\n".join(answer)

    except Exception as e:
        return f"Error during search: {e}"

def AnswerModifier(Answer):
    lines = Answer.split('\n')
    non_empty_lines = [line for line in lines if line.strip()]
    return '\n'.join(non_empty_lines)

SystemChatBot = [
    {"role": "system", "content": System},
    {"role": "user", "content": "Hi"},
    {"role": "assistant", "content": "Hello, how can I help you?"}
]

def Information():
    now = datetime.datetime.now()
    return (
        f"Day: {now.strftime('%A')}\n"
        f"Date: {now.strftime('%d %B %Y')}\n"
        f"Time: {now.strftime('%H:%M:%S')}\n"
    )

def RealtimeSearchEngine(prompt):
    global SystemChatBot, messages

    with open(r"Data\ChatLog.json", "r") as f:
        messages = load(f)

    messages.append({"role": "user", "content": prompt})
    SystemChatBot.append({"role": "system", "content": GoogleSearch(prompt)})

    completion = client.chat.completions.create(
        model="qwen/qwen3.8-27b",
        messages=SystemChatBot + [{"role": "system", "content": Information()}] + messages,
        temperature=0.7,
        max_tokens=848,
        top_p=1,
        stream=True,
    )

    Answer = ""
    for chunk in completion:
        if chunk.choices[0].delta.content:
            Answer += chunk.choices[0].delta.content

    Answer = Answer.strip().replace("</s>", "")
    messages.append({"role": "assistant", "content": Answer})

    with open(r"Data\ChatLog.json", "w") as f:
        dump(messages, f, indent=4)

    SystemChatBot.pop()
    return AnswerModifier(Answer)

if __name__ == "__main__":
    while True:
        q = input("Enter your query: ").strip()
        if not q or q.lower() in ["exit", "quit"]:
            break
        try:
            print("\n" + RealtimeSearchEngine(q) + "\n")
        except Exception as e:
            print("Error:", e)
