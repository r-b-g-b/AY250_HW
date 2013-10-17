import sqlite3
import pandas as pd
import math
from collections import OrderedDict
import urllib2
import numpy as np
from matplotlib import pyplot as plt

def build_database():
	
	'''builds the airports.db database containing the tables
		correlations
			code1: ICAO code for city "lag" days ahead 
			code2: ICAO code for city "lag" days behind
			dtemp: correlation for change in max temperature
			dcloud: correlation for change in cloud cover
			lag: city 1 is this many days ahead of city 2

		icao (from ICAO_airports.csv)
			ident
			type
			name
			latitude_deg
			longitude_deg
			elevation_ft
			continent
			iso_country
			iso_regionmunicipality TEXT, scheduled_service TEXT, gps_code TEXT, iata_code TEXT, local_code TEXT, home_link TEXT, wikipedia_link TEXT, keywords TEXT);
		
		mytable
			combination of topairports and icao data to get names of top 50 stations and
			latitude/longitude

		weatherdata
			a table of data aggregated from wunderground for the 50 airports in topairports
			I use the columns Max_TemperatureF and CloudCover

		topairports
			the top 50 airports'''

	connection = sqlite3.connect('airports.db')
	connection = add_topairports(connection)
	connection = add_ICAO_airports(connection)
	connection = join_top_and_icao(connection)
	connection = add_weatherdata(connection)
	connection = calculate_correlations(connection)

	connection.commit()
	connection.close()


def plot_all_by_distance(connection):
	'''
	Plot the correlations for all of the city pairs by distance
	'''

	measures = ['dtemp', 'dcloud']
	lags = [1, 3, 7]

	fig, axs = plt.subplots(3, 2, sharex=True, sharey=True)
	for i, measure in enumerate(measures):
		for j, lag in enumerate(lags):
			x, y = get_all_by_distance(connection, measure, lag)
	
			axs[j, i].plot(x, y, marker='.', label='Day %i' % lag)
			axs[j, i].legend()

		axs[0, i].set_title(measure)
	axs[-1, 0].set_xlabel('Distance (km)')

def get_all_by_distance(connection, measure, lag):

	cursor = connection.cursor()

	cmd = """
	SELECT code1, code2, %s
	FROM correlations
	WHERE lag=%i
	ORDER BY %s DESC
	"""% (measure, lag, measure)

	cursor.execute(cmd)
	results = cursor.fetchall()
	x = np.zeros(len(results))
	y = np.zeros(len(results))
	for i, (code1, code2, y_) in enumerate(results):
		lat1, lon1 = get_latlon(connection, code1)
		lat2, lon2 = get_latlon(connection, code2)
		if code1==code2:
			x[i] = 0
		else:
			x[i] = distance_on_unit_sphere(lat1, lon1, lat2, lon2)*6373.
		y[i] = y_

	distbins = np.hstack((-1, np.arange(1, 10000, 500)))
	ymeans = np.zeros(len(distbins)-1)
	for i in range(len(distbins)-1):
		ix = np.vstack((distbins[i]<x, x<distbins[i+1])).all(0)
		ymeans[i] = np.mean(y[ix])

	return distbins[:-1], ymeans

def plot_top10_by_latlon(connection):
	'''
	Plots the top 10 sorted by longitude
	'''
	measures = ['dtemp', 'dcloud']
	lags = [1, 3, 7]
	for i, measure in enumerate(measures):
		print measure
		fig, axs = plt.subplots(3, 2)
		for j, lag in enumerate(lags):
			print lag
			xlat, ylat, xlon, ylon = get_top10_by_latlon(connection, measure, lag)
			axs[j, 0].plot(xlat, ylat, marker='.')
			axs[j, 1].plot(xlon, ylon, marker='.')

		axs[0, 0].set_title('Correlation for $\Delta$ %s by latitude' % measure)
		axs[-1, 0].set_xlabel('Difference in latitude')
		axs[0, 1].set_title('Correlation for $\Delta$ %s by longitude' % measure)
		axs[-1, 1].set_xlabel('Difference in longitude')

	plt.draw()
	plt.show()

def get_top10_by_latlon(connection, measure, lag):
	'''
	Returns the top 10 for a particular measure and delay
	sorted by latitude and longitude
	'''
	cursor = connection.cursor()

	cmd = """
	SELECT code1, code2, %s
	FROM correlations
	WHERE lag=%i
	ORDER BY %s DESC
	"""% (measure, lag, measure)

	cursor.execute(cmd)
	results = cursor.fetchall()
	xlat = np.zeros(10); xlon = np.zeros(10)
	y = np.zeros(10)
	for i, (code1, code2, y_) in enumerate(results[:10]):
		lat1, lon1 = get_latlon(connection, code1)
		lat2, lon2 = get_latlon(connection, code2)
		dlat = lat2-lat1
		dlon = lon2-lon1
		xlat[i] = dlat
		xlon[i] = dlon
		y[i] = y_

	ixlat = xlat.argsort()[::-1]
	ixlon = xlon.argsort()[::-1]

	return xlat[ixlat], y[ixlat], xlon[ixlon], y[ixlon]

def plot_top10_by_dist(connection):
	'''
	Plots the top 10 sorted by distance
	'''
	measures = ['dtemp', 'dcloud']
	lags = [1, 3, 7]

	fig, axs = plt.subplots(3, 2)
	for i, measure in enumerate(measures):
		for j, lag in enumerate(lags):
			x, y = get_top10_by_dist(connection, measure, lag)
			axs[j, i].plot(x, y, marker='.')

	axs[0, 0].set_title('Correlation for $\Delta$ in max temp')
	axs[-1, 0].set_xlabel('Distance (km)')
	axs[0, 1].set_title('Correlation for $\Delta$ in cloud cover')
	axs[-1, 1].set_xlabel('Distance (km)')
	plt.draw()
	plt.show()


def get_top10_by_dist(connection, measure, lag):
	'''
	Returns the top 10 for a particular measure and delay sorted by distance
	'''
	cursor = connection.cursor()

	cmd = """
	SELECT code1, code2, %s
	FROM correlations
	WHERE lag=%i
	ORDER BY %s DESC
	"""% (measure, lag, measure)

	cursor.execute(cmd)
	results = cursor.fetchall()
	x = np.zeros(10)
	y = np.zeros(10)
	for i, (code1, code2, y_) in enumerate(results[:10]):
		lat1, lon1 = get_latlon(connection, code1)
		lat2, lon2 = get_latlon(connection, code2)
		x[i] = distance_on_unit_sphere(lat1, lon1, lat2, lon2)*6373.
		y[i] = y_

	ix = x.argsort()[::-1]

	return x[ix], y[ix]

def calculate_correlations(connection):
	'''
	Calculates correlation coefficients in changes of 
	max temperature and cloud cover for each pair of
	top airports.
	'''

	cursor = connection.cursor()
	icaos = get_airportcodes(connection)
	lags = [1, 3, 7]

	cmd = """
	CREATE TABLE correlations
	(id INTEGER PRIMARY KEY AUTOINCREMENT,
	code1 TEXT,
	code2 TEXT,
	dtemp FLOAT,
	dcloud FLOAT,
	lag INTEGER)
	"""
	cursor.execute(cmd)
	connection.commit()

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

			for lag in lags: # repeat for each lag


				# how does city 2 predict city 1
				ctemp = run_correlation(dtemp1, dtemp2, lag)
				ccloud = run_correlation(dcloud1, dcloud2, lag)
				cmd = """
				INSERT INTO correlations
				(code1, code2, dtemp, dcloud, lag)
				VALUES
				('%s', '%s', '%f', '%f', %i)
				""" % (icao1, icao2, ctemp, ccloud, lag)

				cursor.execute(cmd)

	return connection
	# np.savez('C2.npz', C_temp=C_temp, C_cloud=C_cloud, ICAOs=icaos)

def get_airportcodes(connection):
	'''
	Return the airport codes for the top 50 airports
	'''
	cursor = connection.cursor()

	cmd = """
		SELECT ICAO
		FROM mytable
	"""
	cursor.execute(cmd)
	icaos, = zip(*cursor.fetchall())
	return icaos

def clean_entry(x):
	'''
	takes a list, x, with missing values and returns a numpy array with nans in place of the missing values
	'''
	x2 = np.empty(len(x), dtype=np.float32)
	for i, v in enumerate(x):
		try:
			x2[i] = np.float32(v)
		except ValueError:
			x2[i] = np.nan
	return x2

def run_correlation(x1, x2, lag):
	'''
	calculate the correlation coefficient for one pair of cities at one lag
	'''

	# how does city 2 predict city 1

	# get rid of missing entries
	X = zip(x1[lag:], x2[:-lag])
	y1, y2 = zip(*[(i, j) for i, j in X if not np.isnan(i) and not np.isnan(j)])
	c = np.corrcoef(y1, y2)

	return c[0, 1]

def get_latlon(connection, icao):
	'''
	Returns the latitude and longitude of a city given its ICAO code
	'''

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
	Return the max temp, cloud cover given a station's ICAO code
	'''
	cursor = connection.cursor()
	cmd = """SELECT EST, Max_TemperatureF, CloudCover FROM weatherdata WHERE ICAO='%s';
	""" % icao

	cursor.execute(cmd)
	return zip(*cursor.fetchall())


def add_topairports(connection):
	'''
	Creates a table "topairports" from top_airports.csv into the database linked to connection
	'''

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
	'''
	Creates a table "icao" from ICAO_airports.csv into the database linked to connection.
	'''
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

def distance_on_unit_sphere(lat1, long1, lat2, long2):
	'''
	Code thanks to
	http://www.johndcook.com/python_longitude_latitude.html
		'This code is in the public domain. Do whatever you want with it, no strings attached.'
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

def run():
	connection = sqlite3.connect('airports.db')
	plot_top10_by_dist(connection)
	plot_top10_by_latlon(connection)
