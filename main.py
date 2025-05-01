import speech_recognition as sr
import webbrowser
import pyttsx3
import musiclibrary
import requests
from gtts import gTTS
import pygame
import os


recognizer = sr.Recognizer()
engine = pyttsx3.init()
newsapi = "bca0114adef442d08090dbd36d379e17"

def old_speak(text):

    engine.say(text)
    engine.runAndWait()

def speak(text):
    tts = gTTS(text)
    tts.save('temp.mp3')

  # Initialize pygame mixer
    pygame.mixer.init()

    # Load your MP3 file
    pygame.mixer.music.load("temp.mp3")

    # Play the MP3 file
    pygame.mixer.music.play()

    # Keep the program running while the music plays
    while pygame.mixer.music.get_busy():
        continue  # This keeps checking if the music is still playing

    pygame.mixer.music.unload()

    os.remove("temp.mp3")


def aiProcess(command):

    API_KEY = "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"
    URL = "https://api.groq.com/openai/v1/chat/completions"

    headers = {
        "Authorization": f"Bearer {API_KEY}",
        "Content-Type": "application/json"
    }

    data = {
        "model": "mixtral-8x7b-32768",
        "messages": [{"role": "user", "content": command}]
    }

    response = requests.post(URL, headers=headers, json=data)

    if response.status_code == 200:
        result = response.json()
        assistant_response = result["choices"][0]["message"]["content"]  # Extract only the text response
        return (assistant_response)
    else:
        print(f"Error {response.status_code}: {response.json()}")

def processCommand(c):
    if "open google" in c.lower():
        webbrowser.open("google.com")

    elif "open youtube" in c.lower():
        webbrowser.open("youtube.com")

    elif "open facebook" in c.lower():
        webbrowser.open("facebook.com")

    elif c.lower().startswith("play"):
        song = c.lower().split(" ")[1]
        link = musiclibrary.music[song]
        webbrowser.open(link)

    elif "news" in c.lower():
        r = requests.get(f" https://newsapi.org/v2/top-headlines?country=us&apiKey={newsapi}")
        if r.status_code == 200:
            data = r.json()
            articles = data.get('articles', [])
            for article in articles:
                speak(article['title'])

    else:
        output = aiProcess(c)
        speak(output)



if __name__ == "__main__":
    speak("Initialize Lexo.....")

    while True:

        r = sr.Recognizer()


        # recognize speech using Goolge
        try:
            with sr.Microphone() as source:
                print("Listening...")
                audio = r.listen(source, timeout=10, phrase_time_limit=5)
                print("Recognizing...")

            word = r.recognize_google(audio)
            if (word.lower() == "lexo"):
                speak("Yes Boss")

                with sr.Microphone() as source:
                    print("Lexo Activated")
                    audio = r.listen(source)
                    command = r.recognize_google(audio)

                    processCommand(command)


        except Exception as e:
            print("Error; {0}".format(e))



# Initialize recognizer and text-to-speech engine


