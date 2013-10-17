If you want to build the tables in the database from scratch, type
	>>> import hw6
	>>> hw6.build_database()
in an ipython terminal. you probably shouldn't since it will take a while.

You probably want to just do
	>>> import hw6
	>>> hw6.run(connection)
which will run the methods
	plot_top10_by_dist: plots the airport pairs with the highest correlation coefficients for each measure (max temperature, cloud cover) and day delay (1, 3, 7 days) combination
	plot_top10_by_latlon: same but plots the data as a function of latitude and longitude

I wanted to also look at more than just the top 10 for each measure, so I also made a function to display the same relationship (measure x distance) for all of the cities binned by distance. You can look at that plot by doing
	>>> connection = sqlite3.connect('airports.db')
	>>> import hw6
	>>> hw6.plot_all_by_distance(connection)

From here you can see a few interesting patterns. First if you look at the 0 distance point (that is, cities predicting their own future weather data) you notice that mostly a city's change in weather data one day is negatively correlated with its change the following day. Presumbaly that's because it's unstable for weather to change too much in one direction multiple days in a row. Cities at a distance of about 500 km show the greatest positive correlation after 1 day and cities around 2500 km show the greatest correlation after 5. So I guess you could conclude that "weather" moves at about 500 km day. After 7 days, there are no significant correlations with either of the measures reported here.
