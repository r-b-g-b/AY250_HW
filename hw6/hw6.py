import sqlite3
import pandas as pd
from collections import OrderedDict
import urllib2
import numpy as np


def run():
	'''
	Calculates correlation coefficients for each pair of top airports
	'''
	connection = sqlite3.connect('airports.db')
	cursor = connection.cursor()

	cmd = """
		SELECT ICAO
		FROM mytable
	"""
	cursor.execute(cmd)
	icaos, = zip(*cursor.fetchall())

	nairports = len(icaos)
	lags = [3]
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
			lat1, lon1 = get_latlon(connection, icao1)
			datestr2,temp2,cloud2 = get_weatherdata(connection, icao2)
			lat2, lon2 = get_latlon(connection, icao2)

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

def build_database():
	
	connection = initialize_airports()
	connection = add_topairports(connection)
	connection = add_ICAO_airports(connection)
	connection = join_top_and_icao(connection)
	connection = add_weatherdata(connection)

	connection.commit()
	connection.close()


