import whisper
import sounddevice as sd
import numpy as np
import torch
import wave
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class VoiceToText:
    def __init__(self):
        try:
            # Get configuration from environment
            self.WHISPER_MODEL = os.getenv('WHISPER_MODEL', 'base')
            self.SAMPLE_RATE = int(os.getenv('SAMPLE_RATE', 16000))
            self.DURATION = int(os.getenv('RECORDING_DURATION', 5))
            
            print(f"Loading Whisper model: {self.WHISPER_MODEL}")
            self.model = whisper.load_model(self.WHISPER_MODEL)
            print("Model loaded successfully")
            
            self.FILENAME = "temp/voice_command.wav"
            os.makedirs("temp", exist_ok=True)
            
        except Exception as e:
            print(f"Error initializing VoiceToText: {str(e)}")
            raise

    def record_audio(self):
        """Record audio from microphone"""
        try:
            print("Listening for command...")
            recording = sd.rec(
                int(self.DURATION * self.SAMPLE_RATE),
                samplerate=self.SAMPLE_RATE,
                channels=1,
                dtype=np.int16
            )
            sd.wait()  # Wait until recording is finished

            # Save as WAV file
            with wave.open(self.FILENAME, 'wb') as wf:
                wf.setnchannels(1)
                wf.setsampwidth(2)
                wf.setframerate(self.SAMPLE_RATE)
                wf.writeframes(recording.tobytes())

            print("Recording saved.")
            
        except Exception as e:
            print(f"Error recording audio: {str(e)}")
            raise

    def transcribe_audio(self):
        """Transcribe audio using Whisper"""
        try:
            print("Transcribing...")
            result = self.model.transcribe(self.FILENAME)
            
            # Clean up the temporary file
            try:
                os.remove(self.FILENAME)
            except:
                pass
                
            return result["text"]
            
        except Exception as e:
            print(f"Error transcribing audio: {str(e)}")
            raise

    def get_voice_command(self):
        """Main function to get voice command"""
        try:
            self.record_audio()
            command = self.transcribe_audio()
            print(f"Recognized Command: {command}")
            return command.lower()
            
        except Exception as e:
            print(f"Error getting voice command: {str(e)}")
            return "Sorry, I couldn't understand that."

# Initialize service with error handling
try:
    vtt_service = VoiceToText()
except Exception as e:
    print(f"Failed to initialize VoiceToText service: {str(e)}")
    # You might want to provide a mock service or handle this error appropriately
