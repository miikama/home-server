

from homeserver.voice_control.snowboydecoder import HotwordDetector, play_audio_file
import sys
import signal

from multiprocessing import Process, Event



class MyProcess(Process):

    def __init__(self, **kvargs ):
        Process.__init__(self, **kvargs)
        self.exit = Event()

    def run(self):
        while not self.exit.is_set():
            pass
        print("You exited!")

    def terminate(self):
        print("Shutdown initiated")
        self.exit.set()





class KeyWordDetector():



	def __init__(self, modelpath, detected_callback=None, 
									audio_recorder_callback=None,
					              	silent_count_threshold=4,
					              	recording_timeout=10,
					              	audio_path=''):

		#store the callbacks
		self.audio_recorder_callback= audio_recorder_callback
		self.silent_count_threshold= silent_count_threshold
		self.recording_timeout= recording_timeout

		#flag to to stop 
		self.interrupted = False

		#the path to your own model downloaded from the web
		self.model = modelpath

		# # capture SIGINT signal, e.g., Ctrl+C
		# signal.signal(signal.SIGINT, self.signal_handler)
	

		self.detector = HotwordDetector(self.model, sensitivity=0.5)
		print('Listening for voice keyword...')

		#if a callback function is given, use it
		self.callback_func = detected_callback or play_audio_file

		#set the path of the audio file saved
		self.detector.set_recording_filepath(audio_path)

		#start the listening in a separate thread
		#self.p = MyProcess(target=self.start_detection)
		#self.p.start()	    
		self.start_detection()


	def start_detection(self):

		# main loop
		self.detector.start(detected_callback=self.callback_func,
		               interrupt_check=self.interrupt_callback,
		               sleep_time=0.03,
		               audio_recorder_callback=self.audio_recorder_callback,
		              	silent_count_threshold=self.silent_count_threshold,
		              	recording_timeout=self.recording_timeout)

		#after the loop finishes, clean up the audio reservation
		self.detector.terminate()

	def stop_detection(self):
		print("stopping detection")
		self.interrupted = True
		self.p.terminate()

		





	def signal_handler(self, signal, frame):	
		print("HALTED !!!!!!!!!")   		
		self.interrupted = True


