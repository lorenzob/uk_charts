import pandas as pd
import numpy as np
import sys

files = sys.argv[1:]

# differenze tra regioni
# valori alti di % nei we e in ferie

subtitles = {
'Abruzzo': 'Nessun positivo da test antigenico (AG) con risveglio improvviso',
'Basilicata': 'Nessun positivo da test antigenico, pochi antigenici',
'Calabria': 'Solo qualche gruppo sparso di positivi da antigenico e recentissimo risveglio improvviso',
'Campania': 'Dopo un perido inziale nessun positivo da antigenico',
'Emilia-Romagna': 'Pochissmi positivi da test antigenico, numero di antigenici elevato in confronto ai molecolari. Aumento recentissimo dei positivi rapidi.',
'Friuli Venezia Giulia': 'Numero di positivi AG molto elevato nei primi mesi, poi si sposta verso la media di altre regioni. Aumento invernale appena visibile per gli AG',
'Lazio': '''Percentuale AG quasi costante, non risente della stagionalita'. Dati sospesi ad agosto probabilmente per l'"attacco hacker", non segnalato nelle note. Apparentemente i dati di agosto non sono mai stati recuperati.''',
'Liguria': 'Nessun positivo da test antigenico',
'Lombardia': "Dati di riferimento: aumento progressivo degli AG. Gli AG seguono l'andamento dei molecolari ma con una percentuale inferiore di positivi.",
'Marche': 'Nessun positivo da test antigenico.',
'Molise': 'Quasi nessun test antigenico, salvo un picco ad aprile',
'P.A. Bolzano': 'Pochi positivi AG sparsi, numero molto elevato di AG',
'P.A. Trento': 'Numeri in linea con quelli di riferimento',
'Piemonte': 'Numeri in linea con quelli di riferimento, bassa percentuale di positivi AG nei primi mesi',
'Puglia': 'Basso numero di positivi AG, con registrazioni frequenti. AG spesso negativi nella fase inziale',
'Sardegna': 'Positivi AG sostanzialmente assenti tranne per due picchi 	a fine luglio e fine agosto',
'Sicilia': 'Nessun positivo da test antigenico',
'Toscana': 'Pochi positivi AG registrati frequentemente con risveglio improvviso',
'Umbria': 'Nessun positivo da test antigenico con risveglio improvviso',
"Valle d'Aosta": 'Numeri molto "rumorosi" apparentemente in linea col riferimento',
"Veneto": "Bassa percentuale di AG senza stagionalita'",
"Italia": "",
}

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

	'''
	num_casi['nuovi_tamponi_m'] = num_casi['tamponi_test_molecolare'].diff()
	num_casi['nuovi_tamponi_ag'] = num_casi['tamponi_test_antigenico_rapido'].diff()

	num_casi['nuovi_positivi_m'] = num_casi['totale_positivi_test_molecolare'].diff()
	num_casi['nuovi_positivi_ag'] = num_casi['totale_positivi_test_antigenico_rapido'].diff()

	num_casi['perc_positivi_m'] = 100 * num_casi['nuovi_positivi_m'] / num_casi['nuovi_tamponi_m']
	num_casi['perc_positivi_ag'] = 100 * num_casi['nuovi_positivi_ag'] / num_casi['nuovi_tamponi_ag']

	num_casi = num_casi[['data', 'nuovi_tamponi_m', 'nuovi_tamponi_ag', 'perc_positivi_m', 'perc_positivi_ag']]

	num_casi = num_casi[1:]	# discard first row with NaN diff


	num_casi['perc_positivi_ag'].fillna(0, inplace=True)
	num_casi['perc_positivi_m'].replace(np.inf, 100, inplace=True)

	with pd.option_context('display.max_rows', None,):
		print(num_casi)

	num_casi['data'] = num_casi['data'].str.slice(0, 10)	# remove timestamp

	num_casi[num_casi['nuovi_tamponi_m'] > 5e06] = 0   # clip max values (per Toscana)
	num_casi[num_casi['nuovi_tamponi_m'] < -2000] = -2000   # clip min values
	num_casi[num_casi['nuovi_tamponi_ag'] < -2000] = -2000   # clip min values

	casi_by_date = num_casi.groupby('data').agg(molecolari =('nuovi_tamponi_m','sum'), antigenici  =('nuovi_tamponi_ag','sum'))
	'''
	casi_by_date = num_casi[['data_somministrazione','fascia_anagrafica', 'prima_dose']]


	import matplotlib.pyplot as plt
	from matplotlib.ticker import MaxNLocator

	fig,ax = plt.subplots()

	#ax = casi_by_date.plot(kind='bar', stacked=True, color=['#069af3', '#15b01a'], figsize=(10,6), rot=30);

	colors = ['#006400', '#00008b', '#b03060', '#ff0000', '#ffd700', '#00ff00', '#00ffff', '#ff00ff', '#6495ed', '#ffdead']
	for age, color in zip(ages, colors):
		print(age, color)
		df = casi_by_date[casi_by_date['fascia_anagrafica']==age]

		df = df.set_index('data_somministrazione')
		new_index = pd.Index(dates, name="data_somministrazione")
		df = df.reindex(new_index)

		ax.plot(df['prima_dose'], color=color, linewidth=0.7, label=age);


	ax.set_ylabel('number of doses', fontsize = 8)
	#ax.set_xlabel(None)

	#plt.axvline(x=161, color="green", linewidth=0.5, alpha=0.5, linestyle='--', label="1 luglio (EU GP)")
	#plt.axvline(x=267, color="purple", linewidth=0.5, alpha=0.5, linestyle='--', label="15 ottobre (GP)")	# 15 ottobre
	#plt.axvline(x=319, color="red", linewidth=0.5, alpha=0.5, linestyle='--', label="6 dicembre (SGP)")	# 6 dicembre

	plt.xticks(fontsize = 5, rotation=30)
	plt.yticks(fontsize = 5)

	locator=MaxNLocator(prune='both', nbins=25)
	ax.xaxis.set_major_locator(locator)

	#from textwrap import wrap
	#plt.suptitle(regione)
	#subtitle = subtitles.get(regione, "Missing...")
	#plt.title('\n'.join(wrap(subtitle, 220)), fontsize=6)

	ax.legend(loc='upper left', fontsize = 6) 

	plt.tight_layout()

	plt.savefig(f"vacc_charts/vacc_{regione}.png", dpi=200) 

	# cumulativo

	fig,ax = plt.subplots()

	#ax = casi_by_date.plot(kind='bar', stacked=True, color=['#069af3', '#15b01a'], figsize=(10,6), rot=30);


	# generare un y con tutte le date

	for age, color in zip(ages, colors):


		print(age, color)
		df = casi_by_date[casi_by_date['fascia_anagrafica']==age][['data_somministrazione', 'prima_dose']]

		df = df.set_index('data_somministrazione')
		new_index = pd.Index(dates, name="data_somministrazione")
		df = df.reindex(new_index)

		with pd.option_context('display.max_rows', None,):
			print(df)


		df = df.cumsum()

		ax.plot(100 * df['prima_dose'] / pop_by_age[age], color=color, linewidth=0.7, label=age);


	ax.set_ylabel('number of doses', fontsize = 8)
	#ax.set_xlabel(None)

	#plt.axvline(x=161, color="green", linewidth=0.5, alpha=0.5, linestyle='--', label="1 luglio (EU GP)")
	#plt.axvline(x=267, color="purple", linewidth=0.5, alpha=0.5, linestyle='--', label="15 ottobre (GP)")	# 15 ottobre
	#plt.axvline(x=319, color="red", linewidth=0.5, alpha=0.5, linestyle='--', label="6 dicembre (SGP)")	# 6 dicembre

	plt.xticks(fontsize = 5, rotation=30)
	plt.yticks(fontsize = 5)

	locator=MaxNLocator(prune='both', nbins=25)
	ax.xaxis.set_major_locator(locator)

	#from textwrap import wrap
	#plt.suptitle(regione)
	#subtitle = subtitles.get(regione, "Missing...")
	#plt.title('\n'.join(wrap(subtitle, 220)), fontsize=6)

	ax.yaxis.grid(linewidth=0.5)

	ax.legend(loc='upper left', fontsize = 6) 

	plt.tight_layout()

	plt.savefig(f"vacc_charts/vacc_{regione}_cum.png", dpi=200) 

	plt.close()


	#plt.show()
	#break


