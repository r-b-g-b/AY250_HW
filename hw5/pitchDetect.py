import aifc
import numpy as np
from matplotlib import pyplot as plt
from statsmodels.tsa.stattools import acf
from scipy.signal import periodogram, hilbert
import scikits.audiolab as al
from scipy.interpolate import InterpolatedUnivariateSpline

class pitchDetect(object):
	'''
	A class implementing simple pitch detection.
	'''
	def __init__(self, fpath):

		print fpath

		self.fpath = fpath
		self.basedir, tmp = os.path.split(self.fpath)
		self.title, _ = os.path.splitext(tmp)

		self.load_aiff()

		self._get_middle(frac=0.01)
		self.axs = []

		self.calc_periodogram()
		self.detect(method='m1')

	def detect(self, method='m1'):
		'''
		Run the pitch detection. The one and only method available
		just calculates a periodogram and gets the peak.
		'''
		if method=='m1':

			ix_center = self.Sxx.argmax()
			ix_min = max([0, ix_center-10])
			ix_max = min([ix_center+10, len(self.Sxx)])
			Sxx2 = self.Sxx[ix_min:ix_max]
			Sxx_freq2 = self.Sxx_freq[ix_min:ix_max]

			spl = InterpolatedUnivariateSpline(Sxx_freq2, Sxx2)
			xs = np.linspace(Sxx_freq2.min(), Sxx_freq2.max(), 500)

			y = spl(xs)

			pitch = xs[y.argmax()]

			self.plot_periodogram()
			ax = self.axs[-1]

			ax.axvline(pitch, color='r', ls='--')
			
			ax.get_figure().savefig(os.path.join(self.basedir, '%s_fig.png' % self.title))

			self.pitch = pitch

			print 'Detected pitch: %f\n' % pitch

	def load_aiff(self):
		'''
		Loads a .aiff file from self.fpath
		(Removes DC offset)
		'''
		f = aifc.open(self.fpath, 'rb')
		fs = f.getframerate()
		a = f.readframes(f.getnframes())
		s = np.fromstring(a, np.short).byteswap()

		# normalize to 1
		s = np.float64(s) / s.max()
		# remove bias
		s = s - s.mean()

		self.s = s
		self.fs = fs

		self._minfreq = 40.
		self._maxfreq = 18000.

	def _get_middle(self, frac=0.5):
		'''
		Returns the middle fraction of an array
		'''
		start = int((0.5-frac)*self.s.size)
		stop = int((0.5+frac)*self.s.size)
		self.s2 = self.s[start:stop]

	def calc_autocorr(self):
		'''
		Calculate the autocorrelation of an array.
		'''
		nlags = int(self.fs / self._minfreq)
		self.acorr = acf(self._windowed(self.s2), nlags=nlags)
		self.acorr_freq = self.fs / np.arange(self.acorr.size)

	def calc_periodogram(self):
		'''
		Calculate a periodogram of the sound.
		'''
		Sxx_freq, Sxx = periodogram(self.s2, fs=self.fs,
			window='hamming', return_onesided=True)
		ix = np.vstack((Sxx_freq>self._minfreq,
				Sxx_freq<self._maxfreq)).all(0)
		Sxx = Sxx[ix]	
		Sxx_freq = Sxx_freq[ix]

		self.Sxx = Sxx
		self.Sxx_freq = Sxx_freq

	def calc_rms(self):
		self.rms = np.sqrt(self.s2**2.)

	def calc_fft(self):
		'''
		Calculates the FFT on self.s2
		Applies hamming window first
		'''

		wind = np.hamming(self.s2.size)
		S = np.fft.fft(self.s2*wind)

		S_freq = np.fft.fftfreq(self.s2.size, 1./self.fs)
		S_freq = S_freq[:S.size]

		self.S = S
		self.S_freq = S_freq

	def plot_periodogram(self):

		fig, ax = plt.subplots()
		ax.plot(self.Sxx_freq, self.Sxx)
		ax.set_title(self.fpath)
		self.axs.append(ax)

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

	def playSound(self):

		al.play(self._ramped(self.s2, self.fs), self.fs)

	def playTone(self, freq):

		t = np.arange(0, 0.5, 1./self.fs)
		s = np.sin(2*np.pi*freq*t)

		s_ramp = self._ramped(s, self.fs)

		al.play(s_ramp, self.fs)

	def check(self, freq=None):
		if freq is None: freq = self.pitch
		self.playSound()
		self.playTone(freq)

	@staticmethod
	def _windowed(x):
		return x * np.hamming(x.size)

	@staticmethod
	def _ramped(x, fs, ramplen=0.1):

		w = np.hamming(ramplen*fs)
		att = w[:(w.size/2)]
		sus = np.ones(x.size-2*att.size)
		rel = att[::-1]
		wind = np.concatenate((att, sus, rel))
		return x*wind