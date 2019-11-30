

import pyaudio
import wave

from homeserver.voice_control.voice_service import record_audio

if __name__ == "__main__":
	record_audio(3, "test.wav")
