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

	data = pd.read_csv(f + '/stato_clinico.csv', parse_dates=['iss_date'], encoding="ISO-8859-1") 

	if all_data is None:
		all_data = data
	else:
		all_data = all_data.append(data)


all_data.drop_duplicates(keep='first', inplace=True) 
all_data.sort_values(by=['iss_date'])

all_data.drop_duplicates(keep='first', inplace=True) 

all_data.loc[all_data['CASI'] == '<5', 'CASI'] = 3
print(all_data[4910:])

all_data['CASI'] = all_data['CASI'].astype(int)


all_data['iss_date'] = pd.to_datetime(all_data['iss_date']).dt.date

ages = ['10-19', '20-29', '30-39', '40-49', '50-59', '60-69', '70-79', '80-89', '>90', 'Non noto']
ages = ['all']

all_dates = pd.DataFrame(all_data['iss_date'].unique(), columns=['_data'])
stati = pd.DataFrame(all_data['STATO_CLINICO'].unique(), columns=['_stato'])

print(all_dates)
print(stati)
all_dates['dummy'] = 'a'
stati['dummy'] = 'a'

idx =all_dates.merge(stati, how='inner', on='dummy')
del idx['dummy']

print(idx)

for age in ages:

	df = all_data.groupby(['iss_date','AGE_GROUP', 'STATO_CLINICO'])['CASI'].sum().reset_index()	# sum sex

	df = df.loc[df['AGE_GROUP'] == age]
	df = df[['iss_date', 'STATO_CLINICO', 'CASI']]

	df.set_index("iss_date")


	df = df.groupby(['iss_date', 'STATO_CLINICO']).sum().unstack()
	#df.sort_values(by=['iss_date'])
	print(df.shape)

	df[('CASI_PERC', 'ASINTOMATICO')] = 100 * df[('CASI',      'ASINTOMATICO')] / df['CASI'].sum(axis=1)
	df[('CASI_PERC', 'PAUCI-SINTOMATICO')] = 100 * df[('CASI',      'PAUCI-SINTOMATICO')] / df['CASI'].sum(axis=1)
	df[('CASI_PERC', 'LIEVE')] = 100 * df[('CASI',      'LIEVE')] / df['CASI'].sum(axis=1)
	df[('CASI_PERC', 'SEVERO')] = 100 * df[('CASI',      'SEVERO')] / df['CASI'].sum(axis=1)
	df[('CASI_PERC', 'CRITICO')] = 100 * df[('CASI',      'CRITICO')] / df['CASI'].sum(axis=1)

	print(df)

	ax = df.plot(y='CASI_PERC', kind='bar', stacked=True, color=['#069af3', '#15b01a', 'r', 'b', 'k'], figsize=(10,6), rot=30);

	ax.legend(loc='lower left', fontsize = 6) 

	ax.set_ylabel('percentage', fontsize = 8)
	ax.set_xlabel(None)

	#plt.axvline(x=161, color="green", linewidth=0.5, alpha=0.5, linestyle='--', label="1 luglio (EU GP)")
	#plt.axvline(x=267, color="purple", linewidth=0.5, alpha=0.5, linestyle='--', label="15 ottobre (GP)")	# 15 ottobre
	#plt.axvline(x=319, color="red", linewidth=0.5, alpha=0.5, linestyle='--', label="6 dicembre (SGP)")	# 6 dicembre
	#plt.axvline(x=330, color="gray", linewidth=0.5, alpha=0.5, linestyle='--', label="25 dicembre")

	plt.xticks(fontsize = 5)
	plt.yticks(fontsize = 5)

	locator=MaxNLocator(prune='both', nbins=30)
	ax.xaxis.set_major_locator(locator)

	plt.yticks(fontsize = 5)

	plt.suptitle(f"Sintomi per età {age}", fontsize = 5)

	plt.tight_layout()

	plt.savefig(f"charts/sintomi_{age}.png", dpi=250) 

	#plt.show()

plt.close()

