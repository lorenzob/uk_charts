import json
import re
import requests
import xmltodict
import os
from urllib.parse import urlparse



url = "https://www.england.nhs.uk/statistics/statistical-work-areas/covid-19-vaccinations/covid-19-vaccinations-archive/"

res = requests.get(url)

decoded_response = res.content.decode("utf-8")

lines = decoded_response.split("\n")

for l in lines:

	#if "https://www.england.nhs.uk/statistics/wp-content/uploads/sites/" in l and "weekly" in l and 'xlsx' in l:
	if 'weekly announced vaccinations' in l and 'xlsx' in l:

		l = l.replace("<p><a href=\"", "")

		l = re.sub('">COVID.19 weekly announced vaccinations.*</a></p>', "", l)

		file = requests.get(l)

		up = urlparse(l)

		out_file = 'data/' + os.path.basename(up.path)
		with open(out_file, 'wb') as out:
			out.write(file.content)


