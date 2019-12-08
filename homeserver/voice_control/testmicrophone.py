

import pyaudio
import wave

from homeserver.voice_control.sound_utilities import record_audio, play_back_audio

if __name__ == "__main__":
	record_audio(3, "test.wav")

	play_back_audio("test.wav")
