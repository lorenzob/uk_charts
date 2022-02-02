import pandas as pd
import numpy as np
import sys

files = sys.argv[1:]

# differenze tra regioni
# valori alti di % nei we e in ferie


# https://www.tuttitalia.it/statistiche/popolazione-eta-sesso-stato-civile-2020/

pop_by_age = {
	'05-11': 3761980,	# approx
	'12-19': 4288586,	# approx
	'20-29': 6084382,
	'30-39': 6854632,
	'40-49': 8937229,
	'50-59': 9414195,
	'60-69': 7364364,
	'70-79': 5968373,
	'80-89': 3628160,
	'90+': 791543,
}

all_data = None
for f in files:

	print(f)

	data = pd.read_csv(f, encoding="ISO-8859-1") 

	if all_data is None:
		all_data = data
	else:
		all_data = all_data.append(data)

all_data.drop_duplicates(keep='first', inplace=True) 
#all_data.sort_values(by=['data_somministrazione'])

ages = list(sorted(all_data['fascia_anagrafica'].unique()))
print(ages)
#ages = ["80-89", "90+"]

dates = list(sorted(all_data['data_somministrazione'].unique()))

dosi = ['prima_dose', 'seconda_dose', 'dose_addizionale_booster']
for dose in dosi:
	for filtra_regione in ["ITA"] + list(all_data['area'].unique()):

		print("filtra_regione", filtra_regione)

		if filtra_regione != 'ITA':
			is_regione = all_data['area'] == filtra_regione	

			print(all_data[is_regione])
			casi = all_data[is_regione]
		else:
			casi = all_data  #[['data','tamponi', 'nuovi_positivi']]

		if casi.empty:
			print("No casi for", filtra_regione)
			continue

		if filtra_regione != 'ITA':
			regione = casi['area'].values[0]
		else:
			regione = 'Italia'

		casi = casi[['data_somministrazione','fascia_anagrafica', 'prima_dose', 'seconda_dose', 'pregressa_infezione', 'dose_addizionale_booster']]


		print(casi)


		num_casi = casi.groupby(['data_somministrazione','fascia_anagrafica']).sum().reset_index()

		with pd.option_context('display.max_columns', None,):
			print(num_casi)

		casi_by_date = num_casi[['data_somministrazione','fascia_anagrafica', dose]]

		import matplotlib.pyplot as plt
		from matplotlib.ticker import MaxNLocator

		fig,ax = plt.subplots()

		#ax = casi_by_date.plot(kind='bar', stacked=True, color=['#069af3', '#15b01a'], figsize=(10,6), rot=30);

		# https://mokole.com/palette.html  http://phrogz.net/css/distinct-colors.html 
		colors = ['#006400', '#00008b', '#b03060', '#ff0000', '#ffd700', '#00ff00', '#00ffff', '#ff00ff', '#6495ed', '#ffdead']
		for age, color in zip(ages, colors):
			print(age, color)
			df = casi_by_date[casi_by_date['fascia_anagrafica']==age]

			df = df.set_index('data_somministrazione')
			new_index = pd.Index(dates, name="data_somministrazione")
			df = df.reindex(new_index)


			df[dose + "_MA"] = df[dose].rolling(window=7).mean() 

			ax.plot(df[dose + "_MA"], color=color, linewidth=0.7, label=age);


		ax.set_ylabel('somministrazioni', fontsize = 8)
		#ax.set_xlabel(None)

		#plt.axvline(x=161, color="green", linewidth=0.5, alpha=0.5, linestyle='--', label="1 luglio (EU GP)")
		#plt.axvline(x=267, color="purple", linewidth=0.5, alpha=0.5, linestyle='--', label="15 ottobre (GP)")	# 15 ottobre
		#plt.axvline(x=319, color="red", linewidth=0.5, alpha=0.5, linestyle='--', label="6 dicembre (SGP)")	# 6 dicembre

		plt.xticks(fontsize = 5, rotation=30)
		plt.yticks(fontsize = 5)

		locator=MaxNLocator(prune='both', nbins=25)
		ax.xaxis.set_major_locator(locator)

		#from textwrap import wrap
		plt.suptitle(f"Somministrazioni {dose} {regione}", fontsize = 5)
		#subtitle = subtitles.get(regione, "Missing...")
		#plt.title('\n'.join(wrap(subtitle, 220)), fontsize=6)

		ax.legend(loc='upper left', fontsize = 6) 

		plt.tight_layout()

		plt.savefig(f"vacc_charts/{dose}/vacc_{dose}_{regione}.png", dpi=300) 



		############### cumulativo

		fig,ax = plt.subplots()

		#ax = casi_by_date.plot(kind='bar', stacked=True, color=['#069af3', '#15b01a'], figsize=(10,6), rot=30);


		# generare un y con tutte le date

		for age, color in zip(ages, colors):


			print(age, color)
			df = casi_by_date[casi_by_date['fascia_anagrafica']==age][['data_somministrazione', dose]]

			df = df.set_index('data_somministrazione')
			new_index = pd.Index(dates, name="data_somministrazione")
			df = df.reindex(new_index)

			with pd.option_context('display.max_rows', None,):
				print(df)


			df = df.cumsum()

			ax.plot(100 * df[dose] / pop_by_age[age], color=color, linewidth=0.7, label=age);


		ax.set_ylabel('percentuale', fontsize = 8)
		#ax.set_xlabel(None)

		#plt.axvline(x=161, color="green", linewidth=0.5, alpha=0.5, linestyle='--', label="1 luglio (EU GP)")
		#plt.axvline(x=267, color="purple", linewidth=0.5, alpha=0.5, linestyle='--', label="15 ottobre (GP)")	# 15 ottobre
		#plt.axvline(x=319, color="red", linewidth=0.5, alpha=0.5, linestyle='--', label="6 dicembre (SGP)")	# 6 dicembre

		plt.xticks(fontsize = 5, rotation=30)
		plt.yticks(fontsize = 5)

		locator=MaxNLocator(prune='both', nbins=25)
		ax.xaxis.set_major_locator(locator)

		#from textwrap import wrap
		plt.suptitle(f"Percentuale {dose} {regione} rispetto alla popolazione totale italiana per fascia d'eta'", fontsize = 5)
		#subtitle = subtitles.get(regione, "Missing...")
		#plt.title('\n'.join(wrap(subtitle, 220)), fontsize=6)

		ax.yaxis.grid(linewidth=0.5)

		ax.legend(loc='upper left', fontsize = 6) 

		plt.tight_layout()

		plt.savefig(f"vacc_charts/{dose}/vacc_{dose}_{regione}_cum.png", dpi=300) 

		plt.close()


	#plt.show()
	#break


