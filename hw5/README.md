Part 1: XML-RPC server

	From a python terminal, run hw_1_server.py
	From a separate python terminal, run hw_1_client.py

	First select the method you wish to apply by selecting a number.
	Next, select the image to which you'd like to apply the manipulation, or select Help to view the documentation regarding that method.

	The "server" and "client" images will be stored in folders called "server" and "client" respectively. If the folders are not already present they will be created.


Part 2: Pitch detection

	Implements an admittedly simple, and not very effective pitch detection. Just finds the peak in the periodogram. To be honest, I kind of ran out of time on this one, but it's not the WORST, it gets probably 2/3rds right. A figure containing the periodogram and a line indicating the peak is saved to the directory in which the aif file lives.

	The pitchDetect class is pretty nice. Upon initialization, it runs the simple pitch detection. You can also run a "check()" method that will play the original sound followed by a pure sine wave at the detected pitch.
