# OSCLufs
OSCLufs is an audio analytics tool that posts LUFS data to the network via the Open Sound Control (OSC) protocol. 

## Source Dependencies
You'll need to install these external libraries if you plan to build from source:

PythonOSC for using Open Sound Control: https://pypi.org/project/python-osc/

PyAudio for getting data from the audio bus: https://pypi.org/project/PyAudio/

Python Sound File for decoding the audio buffer: https://pypi.org/project/SoundFile/

Pyloudnorm for calculating the lufs: https://github.com/csteinmetz1/pyloudnorm

## OSC Commands

OSC API for Controlling OSCTranscribe:

/OSCLufs/getLufs : request for the lufs data reply, do not call more frequently than twice per second. 

By default, you send these commands to port 7070. Then, you should listen for the following OSC message:
/OSCLufs/lufs {float data}: The current lufs reading from the buffer
