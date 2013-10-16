import sqlite3
import pandas as pd
from collections import OrderedDict
import urllib2
import numpy as np


def calc_latlon_offset():


	icaos = get_airportcodes(connection)
	nairports = len(icaos)

	df = pd.DataFrame(columns=('code1', 'code2', 'dist', 'dlat', 'dlon'))

	for i in range(nairports):
		for j in range(i, nairports):
			icao1 = icaos[i]
			icao2 = icaos[j]
			lat1, lon1 = get_latlon(connection, icao1)
			lat2, lon2 = get_latlon(connection, icao2)
			if i==j:
				dist=0
			else:
				dist = np.abs(distance_on_unit_sphere(lat1, lon1, lat2, lon2)*6373)
			dlat = lat2-lat1
			dlon = lon2-lon1
			df = df.append(dict(code1=icao1, code2=icao2, dist=dist, dlat=dlat, dlon=dlon), ignore_index=True)
			if i!=j:
				df = df.append(dict(code1=icao2, code2=icao1, dist=dist, dlat=-dlat, dlon=-dlon), ignore_index=True)

	df['dlat_bin'] = pd.cut(df.dlat, bins=np.arange(-30, 35, 5))
	df['dlon_bin'] = pd.cut(df.dlon, bins=np.arange(-100, 110, 10))

	return df


def plot_by_distance(df):
	'''
	Plots the correlations in the changes of temperature and cloud coverage
	as a function of distance. The first point (distance=0) shows how a city's
	weather predicts its own future weather.
	'''

	distbins = np.hstack((-1, np.arange(1, 10000, 500)))
	ndists = len(distbins)-1
	y_temp = np.zeros((ndists, 3))
	y_cloud = np.zeros_like(y_temp)

	lags = [1, 3, 7]
	for i in range(ndists):
		ix = np.vstack((distbins[i]<df.dist, df.dist<distbins[i+1])).all(0)
		if ix.sum()>0:
			for k, lag in enumerate(lags):
				y_temp[i, k] = np.mean(df.ix[ix]['temp_corr%i' % lag])
				y_cloud[i, k] = np.mean(df.ix[ix]['cloud_corr%i' % lag])

	fig, axs = plt.subplots(2, 1)
	axs[0].plot(distbins[:-1], y_temp, marker='.')
	axs[0].set_title('Max temperature')
	axs[1].plot(distbins[:-1], y_cloud, marker='.')
	axs[1].set_title('Cloud cover')
	[a.legend(['%i days' % lag for lag in lags]) for a in axs]
	axs[1].set_xlabel('Distance (km)')
	axs[1].set_ylabel('Correlation coefficient')


def plot_correlation_matrix(df):

	latbins = np.arange(-30, 35, 5)
	lonbins = np.arange(-100, 110, 10)
	nlats = len(latbins)-1
	nlons = len(lonbins)-1
	
	lags = [1, 3, 7]
	nlags = len(lags)
	cmat_temp = np.zeros((nlats, nlons, 3))
	cmat_cloud = np.zeros_like(cmat_temp)
	for i in range(nlats):
		for j in range(nlons):
			ix = np.vstack((latbins[i]<df.dlat, df.dlat<latbins[i+1],
				lonbins[j]<df.dlon, df.dlon<lonbins[j+1])).all(0)
			if ix.sum()>0:
				for k, lag in enumerate(lags):
					cmat_temp[i, j, k] = np.mean(df.ix[ix]['temp_corr%i' % lag])
					cmat_cloud[i, j, k] = np.mean(df.ix[ix]['cloud_corr%i' % lag])

	fig, axs = plt.subplots(nlags, 2)
	fig.suptitle('Max temperature')
	for i, lag in enumerate(lags):
		axs[i, 0].imshow(cmat_temp[..., i],
			interpolation='nearest',
			extent=(lonbins[0], lonbins[-1], latbins[0], latbins[-1]),
			vmin=-0.2, vmax=0.2,
			aspect='auto')
		axs[i, 0].set_title('Max temp %i day lag' % lag)
		img = axs[i, 1].imshow(cmat_cloud[..., i],
			interpolation='nearest',
			extent=(lonbins[0], lonbins[-1], latbins[0], latbins[-1]),
			vmin=-0.2, vmax=0.2,
			aspect='auto')
		axs[i, 1].set_title('Cloud cover %i day lag' % lag)
	fig.tight_layout()
	plt.colorbar(img, ax=axs[0,0])

def combine_latlon_weatherdata():

	df = calc_latlon_offset()

	tmp = np.load('C.npz')
	C_temp = tmp['C_temp']
	C_cloud = tmp['C_cloud']
	icaos = tmp['ICAOs']

	temp_corr1 = []
	temp_corr3 = []
	temp_corr7 = []
	cloud_corr1 = []
	cloud_corr3 = []
	cloud_corr7 = []
	for ix, row in df.iterrows():
		i = (icaos==row['code1']).nonzero()[0][0]
		j = (icaos==row['code2']).nonzero()[0][0]
		temp_corr1.append(C_temp[i, j, 0])
		temp_corr3.append(C_temp[i, j, 1])
		temp_corr7.append(C_temp[i, j, 2])
		cloud_corr1.append(C_cloud[i, j, 0])
		cloud_corr3.append(C_cloud[i, j, 1])
		cloud_corr7.append(C_cloud[i, j, 2])

	df['temp_corr1'] = temp_corr1
	df['temp_corr3'] = temp_corr3
	df['temp_corr7'] = temp_corr7
	df['cloud_corr1'] = cloud_corr1
	df['cloud_corr3'] = cloud_corr3
	df['cloud_corr7'] = cloud_corr7

	return df

def get_airportcodes(connection):
	
	cursor = connection.cursor()

	cmd = """
		SELECT ICAO
		FROM mytable
	"""
	cursor.execute(cmd)
	icaos, = zip(*cursor.fetchall())
	return icaos

def calculate_correlations():
	'''
	Calculates correlation coefficients in changes of 
	max temperature and cloud cover for each pair of
	top airports.
	'''

	connection = sqlite3.connect('airports.db')
	cursor = connection.cursor()

	icaos = get_airportcodes(connection)

	nairports = len(icaos)
	lags = [1, 3, 5]
	nlags = len(lags)
	C_temp = np.empty((nairports, nairports, nlags))
	C_cloud = np.empty((nairports, nairports, nlags))

	# run for all pairs of locations
	for i in range(len(icaos)):
		for j in range(len(icaos)):

			icao1 = icaos[i]
			icao2 = icaos[j]

			# get weather data, lat/lon for the two locations
			datestr1,temp1,cloud1 = get_weatherdata(connection, icao1)
			datestr2,temp2,cloud2 = get_weatherdata(connection, icao2)

			# remove missing entries
			dtemp1 = np.diff(clean_entry(temp1))
			dtemp2 = np.diff(clean_entry(temp2))
			dcloud1 = np.diff(clean_entry(cloud1))
			dcloud2 = np.diff(clean_entry(cloud2))

			for k, lag in enumerate(lags): # repeat for each lag

				# how does city 2 predict city 1
				C_temp[i, j, k] = run_correlation(dtemp1, dtemp2, lag)
				C_cloud[i, j, k] = run_correlation(dcloud1, dcloud2, lag)

	np.savez('C2.npz', C_temp=C_temp, C_cloud=C_cloud, ICAOs=icaos)


def clean_entry(x):
	x2 = np.empty(len(x), dtype=np.float32)
	for i, v in enumerate(x):
		try:
			x2[i] = np.float32(v)
		except ValueError:
			x2[i] = np.nan
	return x2


def run_correlation(x1, x2, lag):

	# how does city 2 predict city 1

	# get rid of missing entries
	X = zip(x1[lag:], x2[:-lag])
	y1, y2 = zip(*[(i, j) for i, j in X if not np.isnan(i) and not np.isnan(j)])
	c = np.corrcoef(y1, y2)

	return c[0, 1]

def get_latlon(connection, icao):
	cursor = connection.cursor()
	cmd = """
	SELECT latitude_deg,
		longitude_deg
	FROM mytable
	WHERE ident='%s'
	""" % icao
	cursor.execute(cmd)
	return cursor.fetchall()[0]

def get_weatherdata(connection, icao):
	'''
	return the max temp, cloud cover, lat and long for one station
	'''
	cursor = connection.cursor()
	cmd = """SELECT EST, Max_TemperatureF, CloudCover FROM weatherdata WHERE ICAO='%s';
	""" % icao

	cursor.execute(cmd)
	return zip(*cursor.fetchall())


def initialize_airports():
	# open connection
	connection = sqlite3.connect('airports.db')

	return connection

def add_topairports(connection):

	cursor = connection.cursor()
	
	df1 = pd.read_csv('data/top_airports.csv')
	columns = ['id']
	columns.extend(df1.columns)
	dtypes = ['INTEGER PRIMARY KEY AUTOINCREMENT', 'TEXT', 'TEXT', 'TEXT', 'TEXT', 'TEXT', 'TEXT', 'INTEGER']
	dtype_dict = OrderedDict(zip(columns, dtypes))
	dtypes = ', '.join(['%s %s' % (k, v) for k, v in dtype_dict.iteritems()])

	# open connection
	connection = sqlite3.connect('airports.db')
	cursor = connection.cursor()

	# ['id', 'City', 'FAA', 'IATA', 'ICAO', 'Airport', 'Role', 'Enplanements']

	# create table
	cmd = """CREATE TABLE topairports (%s)
	""" % dtypes
	cursor.execute(cmd)
	connection.commit()

	# populate table
	for k, v in df1.iterrows():
		cmd = """INSERT INTO topairports (%s) VALUES %s""" % (', '.join(dtype_dict.keys()[1:]), str(tuple(v.values)))
		cursor.execute(cmd)
	connection.commit()

	return connection

def add_ICAO_airports(connection):

	cursor = connection.cursor()

	df2 = pd.read_csv('data/ICAO_airports.csv')
	del df2['id']
	columns = list(['id'])
	columns.extend(df2.columns)
	dtypes = ['INTEGER PRIMARY KEY AUTOINCREMENT', 'TEXT', 'TEXT', 'TEXT', 'FLOAT', 'FLOAT',
	'INTEGER', 'TEXT', 'TEXT', 'TEXT', 'TEXT', 'TEXT', 'TEXT', 'TEXT', 'TEXT', 'TEXT', 'TEXT', 'TEXT']
	dtype_dict = OrderedDict(zip(columns, dtypes))
	dtypes = ', '.join(['%s %s' % (k, v) for k, v in dtype_dict.iteritems()])

	# Index([u'id', u'ident', u'type', u'name', u'latitude_deg', u'longitude_deg', u'elevation_ft', u'continent',
	# u'iso_country', u'iso_region', u'municipality', u'scheduled_service', u'gps_code', u'iata_code', u'local_code', u'home_link', u'wikipedia_link', u'keywords'], dtype=object)

	tables = print_tables(connection)
	if not 'icao' in tables:
		# create table
		cmd = """CREATE TABLE icao (%s)
		""" % dtypes
		cursor.execute(cmd)
		connection.commit()

	# populate table
	for k, v in df2.iterrows():
		v[v.isnull()] = 'nan'
		values = v.values
		cmd = """INSERT INTO icao (%s) VALUES %s""" % (', '.join(dtype_dict.keys()[1:]), str(tuple(values)))
		cursor.execute(cmd)
	connection.commit()

	return connection


def print_tables(connection):

	cursor = connection.cursor()
	cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
	tables, = zip(*cursor.fetchall())
	return tables


def join_top_and_icao(connection):

	cursor = connection.cursor()
	cmd = """
	CREATE TABLE mytable
	AS SELECT *
	FROM topairports
	LEFT JOIN icao
	ON topairports.ICAO = icao.ident
	"""
	cursor.execute(cmd)
	connection.commit()

	return connection

 # 'Max_TemperatureF',
 # 'Mean_TemperatureF',
 # 'Min_TemperatureF',
 # 'Max_Dew_PointF',
 # 'MeanDew_PointF',
 # 'Min_DewpointF',
 # 'Max_Humidity',
 # 'Mean_Humidity',
 # 'Min_Humidity',
 # 'Max_Sea_Level_PressureIn',
 # 'Mean_Sea_Level_PressureIn',
 # 'Min_Sea_Level_PressureIn',
 # 'Max_VisibilityMiles',
 # 'Mean_VisibilityMiles',
 # 'Min_VisibilityMiles',
 # 'Max_Wind_SpeedMPH',
 # 'Mean_Wind_SpeedMPH',
 # 'Max_Gust_SpeedMPH',
 # 'PrecipitationIn',
 # 'CloudCover',
 # 'Events',
 # 'WindDirDegrees'

def parse_wunderground(http):

	lines = http.split('\n')
	x = []
	cols = lines[1]
	cols = [l_.strip().replace(' ', '_') for l_ in lines[1].split(',')]
	assert cols[-1][-6:]=='<br_/>'
	cols[-1] = cols[-1][:-6]
	for l in lines[2:-1]:
		x_ = [l_.strip() for l_ in l.split(',')]
		for i in range(len(x_)):
			try:
				x_[i]=float(x_[i])
			except ValueError:
				pass
		x_[-1] = x_[-1][:-6]
		x.append(x_)

	return cols, x

def add_weatherdata(connection):
	
	cursor = connection.cursor()

	# get icao codes
	cursor.execute('SELECT icao FROM mytable')

	icaocodes, = zip(*cursor.fetchall())
	
	years = np.arange(2008, 2014)
	months = np.arange(1, 13)

	# create dtype for weatherdata table
	dtypes = ['INTEGER PRIMARY KEY AUTOINCREMENT',
	'TEXT',	'DATE',	'INTEGER',	'INTEGER',	'INTEGER',
	'INTEGER',	'INTEGER',	'INTEGER',	'INTEGER',	'INTEGER',
	'INTEGER',	'FLOAT',	'FLOAT',	'FLOAT',	'INTEGER',
	'INTEGER',	'INTEGER',	'INTEGER',	'INTEGER',	'INTEGER',
	'TEXT',	'INTEGER',	'TEXT',	'INTEGER']

	first=True
	for icaocode in icaocodes: # airport loop
		print icaocode
		for yr in years: # year loop
			for mo in months: # month loop

				# load http
				url = 'http://www.wunderground.com/history/airport/%s/%i/%i/1/MonthlyHistory.html?format=1' % (icaocode, yr, mo)
				http = urllib2.urlopen(url).read()
				# parse into header and data
				cols, x = parse_wunderground(http)

				if first:
						columns = list(['id', 'ICAO'])
						columns.extend(cols)
						dtype_dict = OrderedDict(zip(columns, dtypes))
						dtypes = ', '.join(['%s %s' % (k, v) for k, v in dtype_dict.iteritems()])

						cmd = """CREATE TABLE weatherdata (%s)""" % dtypes
						cursor.execute(cmd)
						connection.commit()
						first=False

				for x_ in x: # for each day's data
					values = list([str(icaocode)]) # start with the icao code
					values.extend(x_) # append weather data
					cmd = """INSERT INTO weatherdata (%s) 
					VALUES %s""" % (', '.join(dtype_dict.keys()[1:]), str(tuple(values)))
					cursor.execute(cmd)

	connection.commit()

	return connection


import math

def distance_on_unit_sphere(lat1, long1, lat2, long2):
	'''
	http://www.johndcook.com/python_longitude_latitude.html
	'''
	# Convert latitude and longitude to 
	# spherical coordinates in radians.
	degrees_to_radians = math.pi/180.0

	# phi = 90 - latitude
	phi1 = (90.0 - lat1)*degrees_to_radians
	phi2 = (90.0 - lat2)*degrees_to_radians

	# theta = longitude
	theta1 = long1*degrees_to_radians
	theta2 = long2*degrees_to_radians

	# Compute spherical distance from spherical coordinates.

	# For two locations in spherical coordinates 
	# (1, theta, phi) and (1, theta, phi)
	# cosine( arc length ) = 
	#    sin phi sin phi' cos(theta-theta') + cos phi cos phi'
	# distance = rho * arc length

	cos = (math.sin(phi1)*math.sin(phi2)*math.cos(theta1 - theta2) + 
	       math.cos(phi1)*math.cos(phi2))
	arc = math.acos( cos )

	# Remember to multiply arc by the radius of the earth 
	# in your favorite set of units to get length.
	return arc



def build_database():
	
	connection = initialize_airports()
	connection = add_topairports(connection)
	connection = add_ICAO_airports(connection)
	connection = join_top_and_icao(connection)
	connection = add_weatherdata(connection)

	connection.commit()
	connection.close()


