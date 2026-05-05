import pygame
import random
import asyncio
import edge_tts
import os
import re
from dotenv import dotenv_values

env_vars = dotenv_values(".env")
AssistantVoice = env_vars.get("AssistantVoice", "en-US-AriaNeural")

os.makedirs("Data", exist_ok=True)

async def TextTOAudioFile(text) -> None:
    file_path = r"Data\speech.mp3"
    if os.path.exists(file_path):
        try:
            os.remove(file_path)
        except PermissionError:
            pygame.mixer.quit()
            os.remove(file_path)

    communicate = edge_tts.Communicate(text, AssistantVoice, pitch='+5Hz', rate='+13%')
    await communicate.save(file_path)

def TTS(Text, func=lambda r=None: True):
    try:
        asyncio.run(TextTOAudioFile(Text))

        pygame.mixer.init()
        pygame.mixer.music.load(r"Data\speech.mp3")
        pygame.mixer.music.play()

        while pygame.mixer.music.get_busy():
            if func() == False:
                break
            pygame.time.Clock().tick(10)

        return True
    except Exception as e:
        print(f"Error in TTS: {e}")
    finally:
        try:
            func(False)
            pygame.mixer.music.stop()
            pygame.mixer.quit()
        except Exception as e:
            print(f"Error in finally block: {e}")

def TextToSpeech(Text, func=lambda r=None: True):
    # Prevent crashing on empty inputs
    if not str(Text).strip():
        return

    code_patterns = [
        r"```[\s\S]*```",
        r"\bdef\s+\w+\(",
        r"\bclass\s+\w+",
        r"\bfunction\s+\w+\(",
        r"\b(public|private|protected)\s+class\b",
        r"#include\s*<",
        r"<html[\s>]",
    ]
    if any(re.search(pattern, str(Text), re.IGNORECASE) for pattern in code_patterns):
        return

    Data = str(Text).split(",")

    responses = [
        "The rest of the result has been printed to the chat screen, kindly check it out.",
        "The rest of the text is now on the chat screen, please check it.",
        "You can see the rest of the text on the chat screen.",
        "The remaining part of the text is now on the chat screen.",
        "Sir, you'll find more text on the chat screen for you to see.",
        "The rest of the answer is now on the chat screen.",
        "Sir, please look at the chat screen, the rest of the answer is there.",
        "You'll find the complete answer on the chat screen.",
        "The next part of the text is on the chat screen.",
        "Sir, please check the chat screen for more information.",
        "There's more text on the chat screen for you.",
        "Sir, take a look at the chat screen for additional text.",
        "You'll find more to read on the chat screen.",
        "Sir, check the chat screen for the rest of the text.",
        "The chat screen has the rest of the text.",
        "There's more to see on the chat screen, please have a look.",
        "Sir, the chat screen holds the continuation of the text.",
        "You'll find the complete answer on the chat screen, kindly check it out.",
        "Please review the chat screen for the rest of the text",
        "Sir, look at the chat screen for the complete answer."
    ]

    if len(Data) > 4 and len(Text) >= 250:
        shortened_text = " ".join(Text.split(".")[:2]) + ". " + random.choice(responses)
        TTS(shortened_text, func)
    else:
        TTS(Text, func)

if __name__ == "__main__":
    print("Text-to-Speech Engine Initialized. Type something and press Enter.")
    while True:
        try:
            user_input = input("Enter the text: ")
            TextToSpeech(user_input)
        except KeyboardInterrupt:
            print("\nExiting TTS engine.")
            break
