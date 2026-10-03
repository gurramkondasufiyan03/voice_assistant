import os
import re
import time
import logging
import datetime
import subprocess
import webbrowser
from urllib.parse import quote

import pyttsx3
import speech_recognition as sr

logging.getLogger("google_genai").setLevel(logging.ERROR)
logging.getLogger("google.genai").setLevel(logging.ERROR)

try:
    from google import genai
    client = genai.Client()  # reads GEMINI_API_KEY
except Exception:
    client = None

recognizer = sr.Recognizer()
MODELS = ["gemini-3.5-flash", "gemini-2.5-flash"]


def speak(text):
    text = re.sub(r"[*#_`]", "", str(text))
    print("Assistant:", text)
    try:
        engine = pyttsx3.init()
        engine.say(text)
        engine.runAndWait()
        engine.stop()
    except Exception as e:
        print("(voice error:", e, ")")


def listen():
    try:
        with sr.Microphone() as source:
            recognizer.adjust_for_ambient_noise(source, duration=0.5)
            print("Listening...")
            audio = recognizer.listen(source, timeout=8, phrase_time_limit=12)
        text = recognizer.recognize_google(audio, language="en-IN")
        print("You:", text)
        return text.lower()
    except (sr.WaitTimeoutError, sr.UnknownValueError):
        return ""
    except sr.RequestError:
        speak("I cannot reach the internet")
        return ""
    except Exception as e:
        print("Mic error:", e)
        time.sleep(1)
        return ""


def ask_ai(question):
    if client is None:
        return "My AI key is not set. Please set the Gemini API key."
    for model in MODELS:
        for _ in range(2):
            try:
                response = client.models.generate_content(
                    model=model,
                    contents="Answer in 2 short sentences, simple English: " + question,
                )
                if response.text:
                    return response.text
            except Exception as e:
                print("AI error:", e)
                time.sleep(2)
    return "Sorry, the AI is busy right now. Please try again in a minute."


def has(words, text):
    return any(re.search(r"\b" + w + r"\b", text) for w in words)


def open_app(name):
    try:
        subprocess.Popen(name, shell=True)
    except Exception as e:
        print("App error:", e)


SITES = {
    "youtube": "https://www.youtube.com",
    "instagram": "https://www.instagram.com",
    "google": "https://www.google.com",
}


def handle(command):
    """Returns False when the assistant should quit."""
    if not command:
        return True
    words = command.split()

    if has(["stop", "exit", "quit", "goodbye", "bye"], command) and len(words) <= 4:
        speak("Goodbye Sufiyan")
        return False

    if has(["time"], command) and len(words) <= 5:
        speak("The time is " + datetime.datetime.now().strftime("%I:%M %p"))
    elif has(["date", "today"], command) and len(words) <= 5:
        speak("Today is " + datetime.datetime.now().strftime("%A, %d %B %Y"))
    elif has(["search"], command):
        query = re.sub(r"\b(search|for|on google|google)\b", "", command).strip()
        if query:
            speak("Searching " + query)
            webbrowser.open("https://www.google.com/search?q=" + quote(query))
        else:
            speak("What should I search for?")
    elif has(["open"], command) and any(s in command for s in SITES):
        for name, url in SITES.items():
            if name in command:
                speak("Opening " + name)
                webbrowser.open(url)
                break
    elif has(["open"], command) and "notepad" in command:
        speak("Opening Notepad")
        open_app("notepad")
    elif has(["open"], command) and "calculator" in command:
        speak("Opening Calculator")
        open_app("calc")
    else:
        speak(ask_ai(command))
    return True


def main():
    speak("Hello Sufiyan, how can I help you?")
    try:
        while True:
            if not handle(listen()):
                break
    except KeyboardInterrupt:
        print("\nStopped.")


if __name__ == "__main__":
    main()