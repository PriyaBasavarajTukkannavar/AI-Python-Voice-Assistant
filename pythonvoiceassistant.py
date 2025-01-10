import google.generativeai as genai
import speech_recognition as sr
import pyttsx3
import os
import webbrowser
import threading
import urllib.parse

# Replace with your actual Gemini API Key
GOOGLE_API_KEY = "Your API KEY"

# Configure Gemini API
genai.configure(api_key=GOOGLE_API_KEY)
model = genai.GenerativeModel('gemini-pro')

# Configure Speech Recognition
r = sr.Recognizer()

# Configure Text-to-Speech
engine = pyttsx3.init()

# Flags
speaking_flag = False
stop_flag = threading.Event()

def listen():
    """Captures user's voice and returns the text."""
    try:
        # Check for microphone availability
        with sr.Microphone() as source:
            print("Listening...")
            r.adjust_for_ambient_noise(source, duration=1)  # Reduce background noise
            audio = r.listen(source)
        
        try:
            print("Recognizing...")
            text = r.recognize_google(audio)
            print(f"You said: {text}")
            return text
        except sr.UnknownValueError:
            print("Could not understand audio")
            speak("I could not understand you. Please try again.")
            return None
        except sr.RequestError as e:
            print(f"Could not request results from speech recognition service; {e}")
            speak("I'm having trouble connecting to the speech recognition service.")
            return None

    except OSError as e:
        print(f"Microphone error: {e}")
        speak("I couldn't access the microphone. Please check your microphone settings.")
        return None
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
        speak("An unexpected error occurred. Please try again.")
        return None

def respond_gemini(prompt):
    """Sends prompt to Gemini AI and gets the response."""
    try:
        response = model.generate_content(prompt)
        text_response = response.text
        print(f"Gemini said: {text_response}")
        return text_response
    except Exception as e:
        print(f"Error generating response: {e}")
        speak("I'm having trouble generating a response.")
        return None

def speak(text):
    """Converts text to speech."""
    global speaking_flag
    speaking_flag = True
    stop_flag.clear()
    engine.say(text)
    try:
        engine.runAndWait()
    except RuntimeError:
        print("Speech interrupted.")
    speaking_flag = False

def interrupt_speech():
    """Stops ongoing speech."""
    stop_flag.set()
    engine.stop()

def open_youtube():
    """Opens YouTube in the default web browser."""
    webbrowser.open("https://www.youtube.com")
    speak("Opening YouTube")

def search_youtube(song_name):
    """Searches for a song on YouTube."""
    query = urllib.parse.quote(song_name)
    url = f"https://www.youtube.com/results?search_query={query}"
    webbrowser.open(url)
    speak(f"Searching for {song_name} on YouTube")

def open_website(url):
    """Opens a given website."""
    webbrowser.open(url)
    speak(f"Opening {url}")

def ask_exit_confirmation():
    """Asks the user for confirmation before exiting."""
    speak("Do you really want to exit? Say 'yes' to confirm or 'no' to continue.")
    while True:
        spoken_text = listen()
        if spoken_text:
            if "yes" in spoken_text.lower():
                print("Exiting...")
                speak("Goodbye")
                return True  # Exit confirmed
            elif "no" in spoken_text.lower():
                print("Continuing...")
                speak("Continuing. Please give the next command.")
                return False  # Exit canceled
            else:
                speak("Please say 'yes' to exit or 'no' to continue.")

def main():
    while True:
        # Reset the stop flag
        stop_flag.clear()

        # Listen for user input
        spoken_text = listen()
        if spoken_text:
            # Handle "bye" or "exit" command to stop the program
            if "bye" in spoken_text.lower() or "exit" in spoken_text.lower():
                if ask_exit_confirmation():
                    break  # Exit the program after confirmation

            # Handle 'stop' command to stop the speech
            elif "stop" in spoken_text.lower():
                print("Stop command received. Speech stopped.")
                interrupt_speech()
                continue  # Skip the current action and prompt for the next command

            # Play song or search YouTube
            elif "play the song" in spoken_text.lower():
                search_youtube("Shape of You")  # Default song
            elif "youtube" in spoken_text.lower() and "play" in spoken_text.lower():
                song_name = spoken_text.lower().replace("youtube play", "").strip()
                if song_name:
                    search_youtube(song_name)  # Play song on YouTube
                else:
                    speak("Please specify the song name you want to play.")
            
            # Open other websites or services
            elif "youtube" in spoken_text.lower():
                open_youtube()  # Open YouTube
            elif "leetcode" in spoken_text.lower():
                open_website("https://www.leetcode.com")  # Open LeetCode
            elif "stackoverflow" in spoken_text.lower():
                open_website("https://www.stackoverflow.com")  # Open StackOverflow
            elif "open" in spoken_text.lower() and "website" in spoken_text.lower():
                url = spoken_text.lower().split("website")[-1].strip()
                if url:
                    open_website(url)  # Open a specific website
                else:
                    speak("Please specify the website name.")
            
            # Respond with Gemini AI
            else:
                gemini_response = respond_gemini(spoken_text)
                if gemini_response:
                    speak(gemini_response)

        # Adding a retry mechanism for Gemini API errors
        if '500' in str(gemini_response):
            speak("The system is facing an issue. Please try again later.")
            break  # Exit the loop or retry depending on your needs

if _name_ == "_main_":
    main()