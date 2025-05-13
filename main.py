import tkinter as tk
from tkinter import ttk, scrolledtext
import threading
import queue
import os
import json
import webbrowser
import requests
import pygame
import speech\_recognition as sr
import sounddevice as sd
import vosk
import google.generativeai as genai
from gtts import gTTS
from PIL import Image, ImageTk

# Configuration Constants

CONFIG = {
"GEMINI\_API\_KEY": "",  # Add your API key here
"NEWS\_API\_KEY": "",
"VOSK\_MODEL\_PATH": r"C:\Users\bhish\PycharmProjects\PythonProject\model\vosk-model-small-en-us-0.15",
"BG\_IMAGE\_PATH": r"D:\abstract-ai-circuit-board-background-600nw-2471339475.jpg",
"SAMPLE\_RATE": 16000,
"MODEL\_NAME": "gemini-1.5-flash",
"TEMPERATURE": 0.7,  # Lower for more precise answers
"MAX\_TOKENS": 1024   # Reduced for faster responses
}

# Initialize components

pygame.mixer.init()
vosk\_model = vosk.Model(CONFIG\["VOSK\_MODEL\_PATH"])
audio\_queue = queue.Queue()
gui\_update\_queue = queue.Queue()
recognizer = sr.Recognizer()

class VoiceAssistant:
def **init**(self):
self.setup\_gui()
self.setup\_ai\_model()
self.start\_voice\_thread()
self.gui\_loop()

```
def setup_ai_model(self):
    """Initialize the Gemini AI model with optimized configuration"""
    if not CONFIG["GEMINI_API_KEY"]:
        raise ValueError("Gemini API key not configured")

    genai.configure(api_key=CONFIG["GEMINI_API_KEY"])
    self.generation_config = {
        "temperature": CONFIG["TEMPERATURE"],
        "max_output_tokens": CONFIG["MAX_TOKENS"],
    }
    self.model = genai.GenerativeModel(CONFIG["MODEL_NAME"])

def setup_gui(self):
    """Set up the graphical user interface"""
    self.root = tk.Tk()
    self.root.title("leo - Optimized Voice Assistant")
    self.root.geometry("700x500")

    # Load and set background image
    try:
        bg_image = Image.open(CONFIG["BG_IMAGE_PATH"])
        bg_image = bg_image.resize((700, 500), Image.Resampling.LANCZOS)
        self.bg_image = ImageTk.PhotoImage(bg_image)
        tk.Label(self.root, image=self.bg_image).place(relwidth=1, relheight=1)
    except Exception as e:
        print(f"Background image error: {e}")
        self.root.configure(bg="#2e3b4e")

    # Widgets
    self.status_label = ttk.Label(self.root, text="Status: Initializing...")
    self.status_label.grid(row=0, column=0, padx=10, pady=10, sticky="w")

    self.heard_text = ttk.Label(self.root, text="Heard: ")
    self.heard_text.grid(row=1, column=0, padx=10, pady=5, sticky="w")

    self.response_log = scrolledtext.ScrolledText(
        self.root, height=12, width=60, wrap=tk.WORD,
        font=("Helvetica", 10), bg="#2e3b4e", fg="white"
    )
    self.response_log.grid(row=2, column=0, padx=10, pady=10)

def update_gui(self, update_type, message):
    """Thread-safe GUI updates"""
    if update_type == "status":
        self.status_label.config(text=f"Status: {message}")
    elif update_type == "heard":
        self.heard_text.config(text=f"Heard: {message}")
    elif update_type == "log":
        self.response_log.insert(tk.END, message + "\n")
        self.response_log.see(tk.END)
        self.response_log.update()

def speak(self, text):
    """Optimized text-to-speech with caching"""
    try:
        # Create a hash of the text for caching
        cache_file = f"cache_{hash(text)}.mp3"

        if not os.path.exists(cache_file):
            tts = gTTS(text)
            tts.save(cache_file)

        pygame.mixer.music.load(cache_file)
        pygame.mixer.music.play()
        while pygame.mixer.music.get_busy():
            continue
    except Exception as e:
        print(f"Speech error: {e}")

def process_command(self, command):
    """Optimized command processing with direct execution for common commands"""
    cmd = command.lower()

    # Predefined commands (faster than AI processing)
    if "open google" in cmd:
        webbrowser.open("https://google.com")
        return "Opening Google"
    elif "open youtube" in cmd:
        webbrowser.open("https://youtube.com")
        return "Opening YouTube"
    elif "news" in cmd:
        return self.get_news()
    elif cmd.startswith("play "):
        return self.play_music(cmd[5:])

    # AI processing for complex queries
    return self.ai_process(command)

def ai_process(self, query):
    """Optimized AI processing with error handling"""
    try:
        response = self.model.generate_content(
            query,
            generation_config=self.generation_config
        )
        return response.text or "I didn't get a response."
    except Exception as e:
        return f"Error processing request: {str(e)}"

def get_news(self):
    """Optimized news fetching"""
    try:
        response = requests.get(
            f"https://newsapi.org/v2/top-headlines?country=us&apiKey={CONFIG['NEWS_API_KEY']}",
            timeout=3  # Faster timeout
        )
        articles = response.json().get("articles", [])[:3]  # Fewer articles
        return "\n".join(article['title'] for article in articles)
    except Exception as e:
        return f"Couldn't fetch news: {str(e)}"

def play_music(self, song):
    """Music playback placeholder"""
    # Implement your music library logic here
    return f"Attempting to play {song}"

def voice_loop(self):
    """Optimized voice recognition loop"""
    with sd.RawInputStream(
            samplerate=CONFIG["SAMPLE_RATE"],
            blocksize=8000,
            dtype='int16',
            channels=1,
            callback=lambda indata, *_: audio_queue.put(bytes(indata))
    ):
        rec = vosk.KaldiRecognizer(vosk_model, CONFIG["SAMPLE_RATE"])

        while True:
            data = audio_queue.get()
            if rec.AcceptWaveform(data):
                result = json.loads(rec.Result())
                text = result.get("text", "")

                gui_update_queue.put(("heard", text))

                if "leo" in text.lower():
                    gui_update_queue.put(("status", "Wake word detected!"))
                    self.speak("Yes Boss")

                    try:
                        with sr.Microphone() as source:
                            gui_update_queue.put(("status", "Listening..."))
                            recognizer.adjust_for_ambient_noise(source, duration=0.5)
                            audio = recognizer.listen(source, timeout=3, phrase_time_limit=5)
                            command = recognizer.recognize_google(audio)

                            gui_update_queue.put(("heard", f"Command: {command}"))
                            gui_update_queue.put(("log", f"You: {command}"))

                            response = self.process_command(command)
                            gui_update_queue.put(("log", f"leo: {response}"))
                            self.speak(response)

                    except Exception as e:
                        self.speak("Sorry, I didn't catch that.")
                        gui_update_queue.put(("log", f"Error: {str(e)}"))

                    finally:
                        gui_update_queue.put(("status", "Waiting for wake word..."))

def start_voice_thread(self):
    """Start the voice processing thread"""
    threading.Thread(target=self.voice_loop, daemon=True).start()
    self.speak("leo is online. Say 'leo' to activate.")

def gui_loop(self):
    """Process GUI updates"""
    while not gui_update_queue.empty():
        update_type, message = gui_update_queue.get_nowait()
        self.update_gui(update_type, message)
    self.root.after(50, self.gui_loop)  # Faster update interval

def run(self):
    """Run the application"""
    self.root.mainloop()
```

# Start the application

if **name** == "**main**":
assistant = VoiceAssistant()
assistant.run()
