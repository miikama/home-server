
import time
import wave
import os
import pyaudio
from homeserver import logger

from ctypes import c_char_p, c_int, CFUNCTYPE
from contextlib import contextmanager





@contextmanager
def no_alsa_error():
    """
        When sound is loaded with pyaudio, it spits out error messages

        see https://stackoverflow.com/questions/7088672/pyaudio-working-but-spits-out-error-messages-each-time
    """

    ERROR_HANDLER_FUNC = CFUNCTYPE(None, c_char_p, c_int, c_char_p, c_int, c_char_p)

    def py_error_handler(filename, line, function, err, fmt):
        pass

    c_error_handler = ERROR_HANDLER_FUNC(py_error_handler)

    try:
        asound = cdll.LoadLibrary('libasound.so')
        asound.snd_lib_error_set_handler(c_error_handler)
        yield
        asound.snd_lib_error_set_handler(None)
    except:
        yield
        pass




def record_audio(record_len, filename):
    """
        records an audio clip from the default input device
        @params: length: the length of recorded audio [seconds]
                filename: the ouput filename 
    """

    try:

        CHUNK = 1024
        FORMAT = pyaudio.paInt16
        CHANNELS = 1
        RATE = 16000
        RECORD_SECONDS = record_len
        WAVE_OUTPUT_FILENAME = filename

        p = None
        with no_alsa_error():
            p = pyaudio.PyAudio()

        stream = p.open(format=FORMAT,
                        channels=CHANNELS,
                        rate=RATE,
                        input=True,
                        frames_per_buffer=CHUNK)

        logger.info("Recording {}.".format(WAVE_OUTPUT_FILENAME))

        frames = []

        for i in range(0, int(RATE / CHUNK * RECORD_SECONDS)):
            data = stream.read(CHUNK)
            frames.append(data)

        logger.info("Done recording.")

        stream.stop_stream()
        stream.close()
        p.terminate()

        with wave.open(WAVE_OUTPUT_FILENAME, 'wb') as wf:
            wf.setnchannels(CHANNELS)
            wf.setsampwidth(p.get_sample_size(FORMAT))
            wf.setframerate(RATE)
            wf.writeframes(b''.join(frames))
		

        return WAVE_OUTPUT_FILENAME

    except:
        pass			

    return None

def play_back_audio(audio_file):

    if not os.path.exists(audio_file):
        logger.error("Audio file {} does not exist, cannot play it".format(audio_file))
        return 

    name, file_extension = os.path.splitext(audio_file)
    if not file_extension == '.wav':
        raise RuntimeError("Playing other that wav files is not supported")
    
    # open file
    with wave.open(audio_file, 'rb') as wf:
        
        # init pyaudio
        audio = None
        with no_alsa_error():
            audio = pyaudio.PyAudio()
        
        # create audio stream    
        stream = audio.open(format=audio.get_format_from_width(wf.getsampwidth()),
                            channels=wf.getnchannels(),
                            rate=wf.getframerate(),
                            input=False,
                            output=True)

        CHUNK = 1024

        #data = wf.readframes(wf.getnframes())
        data = wf.readframes(CHUNK)

        # when the stream is done the final read data will be b'' (empty byte char)
        while data != b'':
            stream.write(data)    
            data = wf.readframes(CHUNK)

        # close file
        stream.close()
        audio.terminate()