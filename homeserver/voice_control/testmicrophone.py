

import pyaudio
import wave


def record_audio(record_len, filename):
	"""
		records an audio clip from the default input device
		@params: length: the length of recorded audio [seconds]
				 filename: the ouput filename 
	"""
	print("recording to filename: ", filename)

	try:

		CHUNK = 1024
		FORMAT = pyaudio.paInt16
		CHANNELS = 1
		RATE = 16000
		RECORD_SECONDS = record_len
		#WAVE_OUTPUT_FILENAME = "output.wav"
		WAVE_OUTPUT_FILENAME = filename

		p = pyaudio.PyAudio()

		# from pprint import pprint
		# info = p.get_host_api_info_by_index(0)
		# numdevices = info.get('deviceCount')
		# print("number of devices: ", numdevices)
		# for i in range(0, numdevices):
		#         if (p.get_device_info_by_host_api_device_index(0, i).get('maxInputChannels')) > 0:
		# 	        infostruct = p.get_device_info_by_host_api_device_index(0, i)
		# 	        pprint(infostruct)
		# 	        print("Input Device id ", i, " - ", infostruct.get('name'))

		stream = p.open(format=FORMAT,
		                channels=CHANNELS,
		                rate=RATE,
		                input=True,
		                frames_per_buffer=CHUNK)

		print("* recording")

		frames = []

		for i in range(0, int(RATE / CHUNK * RECORD_SECONDS)):
		    data = stream.read(CHUNK)
		    frames.append(data)

		print("* done recording")

		stream.stop_stream()
		stream.close()
		p.terminate()

		wf = wave.open(WAVE_OUTPUT_FILENAME, 'wb')
		wf.setnchannels(CHANNELS)
		wf.setsampwidth(p.get_sample_size(FORMAT))
		wf.setframerate(RATE)
		wf.writeframes(b''.join(frames))
		wf.close()

		return WAVE_OUTPUT_FILENAME

	except:
		pass
			

	return None



if __name__ == "__main__":
	record_audio(3, "test.wav")
