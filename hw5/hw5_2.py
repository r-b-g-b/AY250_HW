from pitchDetect import pitchDetect
from matplotlib import pyplot as plt
import os
from glob import glob

fpaths = glob(os.path.join('sound_files', '*.aif'))
for fpath in fpaths:
	p = pitchDetect(fpath)
	plt.close('all')

fpath = fpaths[0]
p = pitchDetect(fpath)
p.check()