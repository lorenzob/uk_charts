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

all_data = None
for f in files:

	print(f)

	data = pd.read_csv(f, encoding="ISO-8859-1") 

	if all_data is None:
		all_data = data
	else:
		all_data = all_data.append(data)


all_data.drop_duplicates(keep='first', inplace=True) 
all_data.sort_values(by=['data'])


for reg_id in range(1, 23):	

	filtra_regione = reg_id
	if filtra_regione:
		is_regione = all_data['codice_regione'] == filtra_regione	

		print(all_data[is_regione])
		casi = all_data[is_regione]
		#casi = regione[['data','tamponi_test_molecolare', 'tamponi_test_antigenico_rapido']]
	else:
		casi = all_data  #[['data','tamponi', 'nuovi_positivi']]

	if casi.empty:
		print("No casi for", reg_id)
		continue

	regione = casi['denominazione_regione'].values[0]

	casi = casi[['data','tamponi_test_molecolare', 'tamponi_test_antigenico_rapido', 'totale_positivi_test_molecolare', 'totale_positivi_test_antigenico_rapido']]


	if filtra_regione: 
		casi = casi[-340:]
	else:
		regione = "Italia"
		casi = casi[-7200:]

	num_casi = casi.groupby(['data']).sum().reset_index()
	print(num_casi)


	num_casi['nuovi_tamponi_m'] = num_casi['tamponi_test_molecolare'].diff()
	num_casi['nuovi_tamponi_ag'] = num_casi['tamponi_test_antigenico_rapido'].diff()

	num_casi['nuovi_positivi_m'] = num_casi['totale_positivi_test_molecolare'].diff()
	num_casi['nuovi_positivi_ag'] = num_casi['totale_positivi_test_antigenico_rapido'].diff()

	num_casi['perc_positivi_m'] = 100 * num_casi['nuovi_positivi_m'] / num_casi['nuovi_tamponi_m']
	num_casi['perc_positivi_ag'] = 100 * num_casi['nuovi_positivi_ag'] / num_casi['nuovi_tamponi_ag']

	num_casi = num_casi[['data', 'nuovi_tamponi_m', 'nuovi_tamponi_ag', 'perc_positivi_m', 'perc_positivi_ag', 'nuovi_positivi_m', 'nuovi_positivi_ag']]

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

	import matplotlib.pyplot as plt
	from matplotlib.ticker import MaxNLocator

	ax = casi_by_date.plot(kind='bar', stacked=True, color=['#069af3', '#15b01a'], figsize=(10,6), rot=30);
	ax.set_ylabel('tests', fontsize = 6)
	ax.set_xlabel(None)

	plt.axvline(x=num_casi.index[num_casi['data']=='2021-07-01'].tolist()[0], color="green", linewidth=0.5, alpha=0.5, linestyle='--', label="1 luglio (EU GP)")
	plt.axvline(x=num_casi.index[num_casi['data']=='2021-10-15'].tolist()[0], color="purple", linewidth=0.5, alpha=0.5, linestyle='--', label="15 ottobre (GP)")	# 15 ottobre
	plt.axvline(x=num_casi.index[num_casi['data']=='2021-12-06'].tolist()[0], color="red", linewidth=0.5, alpha=0.5, linestyle='--', label="6 dicembre (SGP)")	# 6 dicembre
	plt.axvline(x=num_casi.index[num_casi['data']=='2021-12-25'].tolist()[0], color="gray", linewidth=0.5, alpha=0.5, linestyle='--', label="25 dicembre")

	plt.xticks(fontsize = 5)
	plt.yticks(fontsize = 5)

	locator=MaxNLocator(prune='both', nbins=25)
	ax.xaxis.set_major_locator(locator)

	ax2=ax.twinx()
	#plt.axhline(y=0, linewidth=0.5, alpha=0.5, color='black', label="0% positivi")
	num_casi["rapporto m/ag"] = num_casi["perc_positivi_ag"] / num_casi["perc_positivi_m"]

	#num_casi["rapporto m/ag"] = 100 * num_casi["nuovi_positivi_ag"] / (num_casi["nuovi_positivi_m"] + num_casi["nuovi_positivi_ag"])

	#num_casi["rapporto m/ag MA"] = num_casi["rapporto m/ag"].rolling(window=7).mean() 

	print(num_casi["rapporto m/ag"])

	#num_casi.plot(kind='line', x='data', y='perc_positivi_m', color='#0343df', linewidth=1, ax=ax2, label="% molecolari positivi")
	#num_casi.plot(kind='line', x='data', y='perc_positivi_ag', color='firebrick', linewidth=1, ax=ax2, label="% antigenici positivi")
	num_casi.plot(kind='line', x='data', y='rapporto m/ag', color='firebrick', linewidth=1, ax=ax2, label="rapporto tra la quota di positivi rilevati da rapido / quota di positivi rilevati da molecolare")

	ax2.grid(axis='y', linewidth=0.5, alpha=0.6)
	ax2.set_ylim([0, 1])
	#ax2.set_ylabel('positives %', fontsize = 8)
	plt.yticks(fontsize = 5)

	from textwrap import wrap
	plt.suptitle(regione)
	subtitle = subtitles.get(regione, "Missing...")
	plt.title('\n'.join(wrap(subtitle, 220)), fontsize=6)

	ax.legend(loc='upper left', fontsize = 6) 
	ax2.legend(loc='upper right', fontsize = 6) 

	plt.tight_layout()

	plt.savefig(f"charts/rapporto_perc_{regione}.png", dpi=200) 

	plt.close()

	#plt.show()


