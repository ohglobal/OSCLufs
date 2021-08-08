#OSCLufs
#Originally Created by Programming for People
#Maintained and updated by Andy Carluccio
#Liminal Entertainment Technologies, LLC

#Last updated 8/8/2021

#OSC variables & libraries
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

#Other audio parameters
form_1 = pyaudio.paInt16 # 16-bit resolution
chans = 2 # 2 channel
samp_rate = 44100 # 44.1kHz sampling rate
chunk = 1024 # 2^12 samples for buffer
durr = 0.7 #durration of sample
file_name = "buffer.wav" #file name

# create pyaudio stream
stream = audio_stream.open(format = form_1,rate = samp_rate,channels = chans, \
                    input_device_index = micIndex,input = True, \
                    frames_per_buffer=chunk)

def getLufs(unused_addr):
	#print("Running function!")
	data = stream.read(chunk)

	frames = []
	for i in range(0, int(samp_rate / chunk * durr)):
		data = stream.read(chunk)
		frames.append(data)

	#conform the buffer to wav
	waveFile = wave.open(file_name, 'wb')
	waveFile.setnchannels(chans)
	waveFile.setsampwidth(audio_stream.get_sample_size(form_1))
	waveFile.setframerate(samp_rate)
	waveFile.writeframes(b''.join(frames))
	waveFile.close()

	#pull in the wav for analysis
	dat, rt = soundfile.read("buffer.wav")
	meter = pyln.Meter(rt) # create BS.1770 meter
	loudness = meter.integrated_loudness(dat) # measure loudness
	
	#send the loundess as OSC
	client.send_message("/OSCLufs/lufs", loudness)


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
