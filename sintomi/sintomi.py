import pandas as pd
import numpy as np
import sys
import datetime
import matplotlib.pyplot as plt
from matplotlib.ticker import MaxNLocator

files = sys.argv[1:]

all_data = None
for f in files:

	print(f)

	dpf = lambda s: datetime.datetime.strptime(s,'%d/%m/%Y')
	data = pd.read_csv(f + '/stato_clinico.csv', parse_dates=['iss_date'], date_parser=dpf, encoding="ISO-8859-1") 

	if all_data is None:
		all_data = data
	else:
		all_data = all_data.append(data)


all_data.drop_duplicates(keep='first', inplace=True) 
all_data.sort_values(by=['iss_date'])

all_data.drop_duplicates(keep='first', inplace=True) 

all_data.loc[all_data['CASI'] == '<5', 'CASI'] = 2
print(all_data[4910:])

all_data['CASI'] = all_data['CASI'].astype(int)
all_data['iss_date'] = pd.to_datetime(all_data['iss_date']).dt.date


# handle missing dates
all_dates = pd.date_range(start=all_data['iss_date'].min(), end=all_data['iss_date'].max())
print(all_data['iss_date'].min(), all_data['iss_date'].max())

print(all_dates)


all_dates = pd.DataFrame(all_dates, columns=['_data'])

stati = pd.DataFrame(all_data['STATO_CLINICO'].unique(), columns=['_stato'])

oct_15_idx = all_dates.index[all_dates['_data']=='2021-10-15'].tolist()[0]
print("oct_15_idx", oct_15_idx)

aug_27_idx = all_dates.index[all_dates['_data']=='2021-08-27'].tolist()[0]
aug_2_idx = all_dates.index[all_dates['_data']=='2021-08-02'].tolist()[0]
giu_11_idx = all_dates.index[all_dates['_data']=='2021-06-11'].tolist()[0]

all_dates['_data'] = pd.to_datetime(all_dates['_data']).dt.date

# cartesian product
all_dates['dummy'] = 'a'
stati['dummy'] = 'a'
idx =all_dates.merge(stati, how='inner', on='dummy')
del idx['dummy']
new_index = pd.Index(idx, name="A")
print(new_index)

ages = ['all'] + list(all_data['AGE_GROUP'].unique())
#ages = ['all']
print(ages)


interp = True
MA = False
perc = not True
sex = None #'F'
for age in ages:

	df = all_data.copy()
	if sex:
		df = df.loc[df['SESSO'] == sex]

	if age == 'all':
		df = df.groupby(['iss_date', 'STATO_CLINICO'])['CASI'].sum().reset_index()	# sum age, sex
	else:
		df = df.groupby(['iss_date','AGE_GROUP', 'STATO_CLINICO'])['CASI'].sum().reset_index()	# sum sex
		df = df.loc[df['AGE_GROUP'] == age]

	df = df[['iss_date', 'STATO_CLINICO', 'CASI']]

	#df.set_index("iss_date")

	df = df.set_index(["iss_date", "STATO_CLINICO"])
	df = df.reindex(new_index)

	with pd.option_context('display.max_rows', None):
		print(df)


	df = df.unstack()   #df.groupby(['iss_date', 'STATO_CLINICO']).sum().unstack()
	print(df)

	# sort columns
	df = df[[('CASI', 'ASINTOMATICO'), ('CASI', 'PAUCI-SINTOMATICO'), ('CASI', 'LIEVE'), ('CASI', 'SEVERO'), ('CASI', 'CRITICO')]]
	#df = df[[('CASI', 'SEVERO')]]

	if interp:
		df =df.interpolate()

	#df.sort_values(by=['iss_date'])

	# rolling
	if MA:
		df = df.rolling(axis=0, window=30).mean()

	df[('CASI_PERC', 'ASINTOMATICO')] = 100 * df[('CASI',      'ASINTOMATICO')] / df['CASI'].sum(axis=1)
	df[('CASI_PERC', 'PAUCI-SINTOMATICO')] = 100 * df[('CASI',      'PAUCI-SINTOMATICO')] / df['CASI'].sum(axis=1)
	df[('CASI_PERC', 'LIEVE')] = 100 * df[('CASI',      'LIEVE')] / df['CASI'].sum(axis=1)
	df[('CASI_PERC', 'SEVERO')] = 100 * df[('CASI',      'SEVERO')] / df['CASI'].sum(axis=1)
	df[('CASI_PERC', 'CRITICO')] = 100 * df[('CASI',      'CRITICO')] / df['CASI'].sum(axis=1)

	#with pd.option_context('display.max_rows', None):
	#	print(df)

	idx_name = 'CASI_PERC' if perc else 'CASI'

	ax = df.plot(y=idx_name, kind='bar', stacked=True, width=1, color=['#1a926e', '#0058b3', '#e8c547', '#fa8334', '#b92d0a'], figsize=(10,6), rot=45);

	plt.xticks(fontsize = 5)
	plt.yticks(fontsize = 5)

	ax.grid(axis='y', alpha=0.5, linewidth=0.5)

	if perc:
		ax.set_ylabel('percentage', fontsize = 6)
	else:
		ax.set_ylabel('values', fontsize = 6)
	ax.set_xlabel(None)

	plt.axvline(x=oct_15_idx, color="gray", linewidth=0.5, alpha=0.5, linestyle='--', label="15 ottobre (GP)")	# 15 ottobre
	plt.axvline(x=aug_27_idx, color="cyan", linewidth=0.5, alpha=0.5, linestyle='--', label="27 agosto (?)")
	plt.axvline(x=aug_2_idx, color="purple", linewidth=0.5, alpha=0.5, linestyle='--', label="2 agosto (?)")
	plt.axvline(x=giu_11_idx, color="y", linewidth=0.5, alpha=0.5, linestyle='--', label="11 giugno (?)")



	#plt.axvline(x=161, color="green", linewidth=0.5, alpha=0.5, linestyle='--', label="1 luglio (EU GP)")
	#plt.axvline(x=319, color="red", linewidth=0.5, alpha=0.5, linestyle='--', label="6 dicembre (SGP)")	# 6 dicembre
	#plt.axvline(x=330, color="gray", linewidth=0.5, alpha=0.5, linestyle='--', label="25 dicembre")

	ax.legend(loc='lower left', fontsize = 6) 

	locator=MaxNLocator(prune='both', nbins=30)
	ax.xaxis.set_major_locator(locator)

	plt.yticks(fontsize = 5)
	if perc:
		plt.yticks(range(0, 101, 10))

	title_suffix = ""
	if sex:
		title_suffix += f"({sex})"
	plt.suptitle(f"Sintomi per età {age} " + title_suffix, fontsize = 5)

	plt.tight_layout()

	prefix = "" if perc else "val_"

	if sex:
		prefix += sex + "_"

	plt.savefig(f"charts/{prefix}sintomi_{age}.png", dpi=250) 

	#plt.show()

plt.close()

