import pandas as pd
from matplotlib import pyplot as plt
from datetime import datetime
import numpy as np
from collections import Counter

issues = pd.read_json('closed.json')
issues = issues[~issues.id.duplicated()]

#Transform the user values to be simply the 'login' string, so that the user
#column contains only string usernames.
df2 = pd.DataFrame(dict(title=issues['title'], created_at=issues['created_at'],
		labels=issues['labels'], closed_at=issues['closed_at'],
		user=[i['login'] for i in issues['user']], id=issues['id']))

#2) Remove duplicate rows by id from the DataFrame you just created using the id
#column's duplicated method.
df2 = df2[~df2.id.duplicated()]

# 5) Now construct appropriate time series and pandas functions to make the
# following plots:

# - Number of issues created by month
df2.set_index('created_at', inplace=True)
count = df2.id.resample('M', how=len)
fig, ax = plt.subplots()
count.plot()

# - Number of distinct users creating issues each month (hint: you can pass a
#   function to resample's how argument, and there's nothing wrong with having
#   string values in a TimeSeries)
nunique = df2.user.resample('M', how=lambda x: len(np.unique(x)))
fig, ax = plt.subplots()
nunique.plot()

# 6) Make a table and an accompanying plot illustrating:

# - The mean number of days it took for issues to be closed by the month they
#   were opened. In other words, for closed issues created in August 2012, how
#   long were they open on average? (hint: use the ``total_seconds`` function on the
#   timedelta objects computed when subtracting datetime objects). Also show the
#   number of issues in each month in the table.
duration = df2.closed_at-df2.index.values
duration = pd.TimeSeries(duration.values.astype('timedelta64[D]').astype(int), index=duration.index)

duration_by_month = duration.resample('M', how=(np.mean, len))
fig, ax = plt.subplots()
duration_by_month.plot()

# 7) Make a DataFrame containing all the comments for all of the issues. You will
# want to add an ``id`` attribute to each comment while doing so so that each row
# contains a single comment and has the id of the issue it belongs to.
issues = issues[~issues.id.duplicated()]

comms, ids, created, authors = [], [], [], []
for i, issue in issues.iterrows():
	for comment in issue['comments']:
		comms.append(comment['text'])
		created.append(comment['created'])
		authors.append(comment['author'])
		ids.append(issue['id'])

comments = pd.DataFrame(dict(comment=comms, author=authors, id=ids, created=created))
# Convert the ``created`` column to datetime format; note you will need to multiply
# the values (appropriately converted to integers) by 1000000 to get them in
# nanoseconds and pass to to_datetime.
comments['created'] = pd.to_datetime(comments.created.astype(int)*1000000)
comments['month'] = ['%4.4i_%2.2i' % (i.year, i.month) for i in comments.created]

# 8) For each month, compute a table summarizing the following for each month:
# - Total number of issue comments
# - The "chattiest" user (most number of comments)
# - The percentage of total comments made by the chattiest users
# - The number of distinct participants in the issue comments
gp = comments.groupby('month')
comments_table = gp.apply(temp)
ncomments, chattiest, chattiest_pct, nusers = zip(*comments_table.values)
comments_table = pd.DataFrame(dict(ncomments=ncomments, chattiest=chattiest, chattiest_pct=chattiest_pct, nusers=nusers),
		index=comments_table.index)

def temp(df):
	ncomments = len(df)
	(chattiestuser, chattiestnum), = Counter(df.author).most_common(1)
	nusers = len(np.unique(df.author))
	return ncomments, chattiestuser, 100*float(chattiestnum)/ncomments, nusers


# 9) Create a helper ``labels`` table from the issues data with two columns: id and
# label. If an issue has 3 elements in its 'labels' value, add 3 rows to the
# table. If an issue does not have any labels, place a single row with None as
# the label (hint: construct a list of tuples, then make the DataFrame).
labels, ids = [], []
for i, issue in issues.iterrows():
	# if len(issue['labels'])>0:
	if len(issue['labels'])==0:
		labels.append(None)
		ids.append(issue['id'])
	for label in issue['labels']:
		labels.append(label['name'])
		ids.append(issue['id'])

labels = pd.DataFrame(dict(labels=labels, id=ids))

# 10) Now, join the issues data with the labels helper table (pandas.merge). Add
# a column to this table containing the number of days (as a floating point
# number) it took to close each issue.
issues_labels = issues.merge(labels, on='id', how='left')
duration = [(i-j).total_seconds()/86400. for i,j in zip(issues_labels.closed_at, issues_labels.created_at)]
issues_labels['duration'] = duration
issues_labels['month'] = ['%4.4i_%2.2i' % (i.year, i.month) for i in issues_labels.created_at]

# 11) Compute a table containing the average time to close for each label
# type. Now make a plot comparing mean time to close by month for Enhancement
# versus Bug issue types.
gp_labels = issues_labels.groupby('labels_y')
gp_labels.duration.apply(np.mean)

gp_labels_mo = issues_labels.groupby(('labels_y', 'month'))
results = gp_labels_mo.duration.apply(np.mean)
fig, ax = plt.subplots();
results.unstack('labels_y')[['Enhancement', 'Bug']].plot();
