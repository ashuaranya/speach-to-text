import sounddevice as sd
import soundfile as sf
import tempfile
import requests

fast_url = "http://localhost:8000"

def check_fastwhisperapi():
    """Check if the FastWhisper API is running."""
    global checked_fastwhisperapi, fast_url
    if not checked_fastwhisperapi:
        infopoint = f"{fast_url}/info"
        try:
            response = requests.get(infopoint)
            if response.status_code != 200:
                raise Exception("FastWhisperAPI is not running")
        except Exception:
            raise Exception("FastWhisperAPI is not running")
        checked_fastwhisperapi = True
        
def _transcribe_with_fastwhisperapi(audio_file_path):
   # check_fastwhisperapi()
    endpoint = f"{fast_url}/v1/transcriptions"

    files = {'file': (audio_file_path, open(audio_file_path, 'rb'))}
    data = {
        'model': "base",
        'language': "en",
        'initial_prompt': None,
        'vad_filter': True,
    }
    headers = {'Authorization': 'Bearer dummy_api_key'}

    response = requests.post(endpoint, files=files, data=data, headers=headers)
    response_json = response.json()
    return response_json.get('text', 'No text found in the response.')

def record_and_transcribe(duration=5, samplerate=16000):
    """
    Records audio from the microphone, saves it to a temporary file, and transcribes it.

    Args:
        duration (int): Duration of the recording in seconds.
        samplerate (int): Sampling rate for the recording.

    Returns:
        str: Transcribed text from the audio.
    """
    print("Recording...")
    audio_data = sd.rec(int(duration * samplerate), samplerate=samplerate, channels=1, dtype='int16')
    sd.wait()  # Wait until the recording is finished
    print("Recording finished.")

    # Save the recording to a temporary file
    with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as temp_audio_file:
        sf.write(temp_audio_file.name, audio_data, samplerate)
        temp_audio_path = temp_audio_file.name

    print(f"Audio saved to temporary file: {temp_audio_path}")

    # Transcribe the audio file
    transcription = _transcribe_with_fastwhisperapi(temp_audio_path)
    print("Transcription:", transcription)

    return transcription

if __name__ == "__main__":
    print("Voice-to-Text Transcription")
    print("Say something to record and transcribe. Type 'exit' to quit.")

    while True:
        user_input = input("Press Enter to start recording or type 'exit' to quit: ").strip().lower()
        if user_input == "exit":
            print("Exiting the program. Goodbye!")
            break

        # Record and transcribe audio
        try:
            transcription = record_and_transcribe(duration=5)
            print(f"Transcription: {transcription}")
        except Exception as e:
            print(f"An error occurred: {e}")

