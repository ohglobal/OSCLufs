#OSCLufs
#Originally Created by Programming for People
#Maintained and updated by Andy Carluccio
#Liminal Entertainment Technologies, LLC

#Last updated 8/8/2021
#Standard libraries
import time

#Numpy
import numpy as np

#OSC variables & libraries
from app_setup import CHANNELS, FRAMES_PER_BUFFER, SAMPLE_RATE
from pythonosc import dispatcher
from pythonosc import osc_server
from pythonosc import osc_message_builder
from pythonosc import udp_client 

#Argument management and system
import argparse
import sys

#Loudness Processing Library
import pyloudnorm as pyln

#Files
import wave
import soundfile

#Print the names of all available audio devices
import pyaudio

#App setup
from app_setup import (
    SAMPLE_RATE,
	FRAMES_PER_BUFFER,
	CHANNELS,
	DURATION)

# https://www.youtube.com/watch?v=at2NppqIZok
# from https://github.com/aniawsz/rtmonoaudio2midi
class StreamProcessor(object):
	def __init__(self, input_device, \
				format = pyaudio.paInt16, \
				input = True, \
				sample_rate = SAMPLE_RATE, \
				frames_per_buffer = FRAMES_PER_BUFFER, \
				channels = CHANNELS, \
				duration = DURATION, \
				file_name = "buffer.wav"):
		self._input_device = input_device
		self._format = format
		self._input = input
		self._sample_rate = sample_rate
		self._frames_per_buffer = frames_per_buffer
		self._channels = channels
		self._file_name = file_name
		self._meter = pyln.Meter(sample_rate)
		self._duration = duration

	def run(self):
		pya = pyaudio.PyAudio()
		self._stream = pya.open(
			format=self._format,
			channels=self._channels,
			rate=self._sample_rate,
			input=self._input,
			frames_per_buffer=self._frames_per_buffer,
			stream_callback=self._process_frame
		)
		self._stream.start_stream()

		while self._stream.is_active(): #and not self._stream.raw_input():
			time.sleep(0.1)

		self._stream.stop_stream()
		self._stream.close()
		pya.terminate()

	def _store_frame(self, data):
		frames = []
		for i in range(0, int(self._sample_rate / self._frames_per_buffer * self._duration)):
			frames.append(data)

		#conform the buffer to wav
		waveFile = wave.open(self._file_name, 'wb')
		waveFile.setnchannels(self._channels)
		waveFile.setsampwidth(audio_stream.get_sample_size(self._format))
		waveFile.setframerate(self._sample_rate)
		waveFile.writeframes(b''.join(frames))
		waveFile.close()

	def _calculate_lufs(self):
		#pull in the wav for analysis
		dat, rt = soundfile.read(self._file_name)
		self._loudness = self._meter.integrated_loudness(dat) # measure loudness

	def _process_frame(self, data, frame_count, time_info, status_flag):
		self._store_frame(data)
		self._calculate_lufs()
		return (data, pyaudio.paComplete)

	def getLoudness(self):
		return self._loudness

audio_stream = pyaudio.PyAudio()

print("ALL SYSTEM AUDIO DEVICES:")
print()

for i in range(audio_stream.get_device_count()):
	sys.stdout.write(str(i))
	sys.stdout.write(" ")
	sys.stdout.write(audio_stream.get_device_info_by_index(i).get("name"))
	sys.stdout.write('\n')

print()
print("Please select the audio device to listen to:")

micIndex = int(input())

def getLufs(unused_addr):
	#print("Running function!")
	sp = StreamProcessor(micIndex)
	sp.run()

	#send the loundess as OSC
	client.send_message("/OSCLufs/lufs", sp.getLoudness())


if __name__ == "__main__":

	#Get the networking info from the user
	print("Would you like to [1] Input network parameters or [2] use default: 127.0.0.1:1234 (send) and 127.0.0.1:7070 (receive)?")
	print("Enter 1 or 2")
	
	send_ip = "127.0.0.1"
	send_port = 1234
	in_port = 7070

	selection = int(input())
	if(selection == 1):
		print("Input network parameters")
		send_ip = str(input("Send ip?: "))
		send_port = int(input("Send port?: "))
		in_port = int(input("Receive port?: "))
	else:
		print("Using default network settings")
	
	#sending osc messages on
	client = udp_client.SimpleUDPClient(send_ip,send_port)
	sys.stdout.write("Opened Client on: ")
	sys.stdout.write(send_ip)
	sys.stdout.write(":")
	sys.stdout.write(str(send_port))
	sys.stdout.write('\n')

	#catches OSC messages
	dispatcher = dispatcher.Dispatcher()
	dispatcher.map("/OSCLufs/getLufs", getLufs)
	
	#set up server to listen for osc messages
	server = osc_server.ThreadingOSCUDPServer((send_ip,in_port),dispatcher)
	print("Starting Server on {}".format(server.server_address))
	
	#Print API
	print("OSC Networking Established")
	print()
	print("OSC API for Controlling OSCTranscribe:")
	print("/OSCLufs/getLufs: Request a lufs reply")
	print()
	print("OSC API for Receiving Text from OSCLufs:")
	print("/OSCLufs/lufs {float num}: The lufs")
	print()

	#begin the infinite loop
	server.serve_forever()
