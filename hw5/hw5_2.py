import os, aifc
from glob import glob
import numpy as np
from matplotlib import pyplot as plt
from statsmodels.tsa.stattools import acf
from scipy.signal import periodogram, hilbert


class pitchDetect(object):

	def __init__(self, fpath):

		print 'V0.1'
		self.fpath = fpath
		self.load_aiff()

		self.get_middle(frac=0.01)

		self.axs = []

		# self.acorr = acf(self.s2)
		# self.rms = self.rms()

	def load_aiff(self):
		'''
		Loads a .aiff file from self.fpath
		(Removes DC offset)
		'''
		f = aifc.open(self.fpath, 'rb')
		fs = f.getframerate()
		a = f.readframes(f.getnframes())
		s = np.fromstring(a, np.short).byteswap()

		# remove bias
		s = s - s.mean()

		self.s = s
		self.fs = fs

		self._minfreq = 50.
		self._maxfreq = 18000.

	def get_middle(self, frac=0.5):

		start = int((0.5-frac)*self.s.size)
		stop = int((0.5+frac)*self.s.size)
		self.s2 = self.s[start:stop]

	def calc_autocorr(self):

		nlags = int(self.fs / self._minfreq)
		self.acorr = acf(self._windowed(self.s2), nlags=nlags)
		self.acorr_freq = self.fs / np.arange(self.acorr.size)

	def calc_periodogram(self):

		self.Sxx_freq, self.Sxx = periodogram(self.s2, fs=self.fs)

	def calc_rms(self):
		self.rms = np.sqrt(self.s2**2.)

	def calc_fft(self):
		'''
		Calculates the FFT on self.s2
		Applies hamming window first
		'''

		wind = np.hamming(self.s2.size)
		S = np.fft.fft(self.s2*wind)
		# S = S[:-1]
		S_freq = np.fft.fftfreq(self.s2.size, 1./self.fs)
		S_freq = S_freq[:S.size]

		self.S = S
		self.S_freq = S_freq

	def calc_cepstrum(self):

		if not hasattr(self, 'S'):
			self.calc_fft()

		Slm = np.log(np.abs(self.S)) # log magnitude spectrum
		Slm = Slm - Slm.mean()
		C = np.fft.ifft(Slm)
		C = C[:-1]
		C_freq = np.fft.fftfreq(Slm.size, 1./self.fs)
		C_freq = C_freq[:C.size]

		self.C = C
		self.C_freq = C_freq
		self.Slm = Slm

	def plot_fft(self, ax=None):

		if not hasattr(self, 'S'):
			self.calc_fft()

		fig, axs = plt.subplots(3, 1, sharex=True)

		axs[0].plot(np.fft.fftshift(self.S_freq), np.fft.fftshift(np.abs(self.S)))

		axs[1].plot(np.fft.fftshift(self.S_freq), np.fft.fftshift(self.Slm))

		axs[2].plot(np.fft.fftshift(self.C_freq), np.fft.fftshift(np.abs(self.C)))

		self.axs.extend(axs)

	def plot(self):

		fig, axs = plt.subplots(2, 1)
		axs[0].plot(self.s2, c='b')
		axs[0].plot(self.rms, c='r')

		if hasattr(self, 'acorr'):
			axs[1].plot(self.acorr)
			axs[1].set_xlabel('Frequency (Hz)')
			axs[1].set_xticks(np.arange(0, self.acorr.size, 100))
			axs[1].set_xticklabels(self.acorr_freq[np.arange(0, self.acorr.size, 100)])

	@staticmethod
	def _windowed(x):
		return x * np.hamming(x.size)


