# https://markummitchell.github.io/engauge-digitizer/

import json
import re
import requests
import xmltodict
import os
from urllib.parse import urlparse
import sys

import pandas as pd
import numpy as np

f = sys.argv[1]
dose = int(sys.argv[2])

max_pop_1st = [1401091,
873043,
#3615799	divido 2/6, 4/6
1205266,
2410532,
2948714,
3256853,
3269061,
3216532]

max_pop_2nd = [89261,
551901,
#3238529,
1079509,
2159019,
2697936,
3024985,
3091243,
3085300
]


max_pop_3rd = [441,
39050,
#1290410,
430136,
860273,
1207416,
1548278,
1776429,
2023512
]

pd.set_option('display.max_rows', None)

df = pd.read_csv(f)

df = df.drop_duplicates()

ages = ['40-45', '35-40', '30-35', '25-30', '20-25', '18-20', '16-18', '12-16', ]
cols = ['x'] + ages

df = df[cols]

df['x'] -= 0.5   # dots in the chart are not aligned but are in the middle on the "step"

df = df.set_index('x')

# drop duplicate index...
df = df.loc[~df.index.duplicated(), :]

weeks = np.arange(0, 57, dtype=float)

print(weeks.dtype)
print(df.index.values.dtype)

print(np.intersect1d(weeks, df.index.values))

all_idx = np.unique(np.concatenate([weeks, df.index.values]))


weeks_idx = pd.Index(all_idx, name="week")

#with np.printoptions(edgeitems=2250):
#	print(all_idx)

df = df.reindex(weeks_idx)

print(df)

df = df.interpolate()

print(df)

for c in ages:
	df[c].loc[df[c] < 0.25] = 0

print(df)


max_val = df.iloc[-1]
print(max_val)
print(max_pop_1st[::-1])

if dose == 1:
	max_pop = max_pop_1st
elif dose == 2:
	max_pop = max_pop_2nd
elif dose == 3:
	max_pop = max_pop_3rd

ratio = max_val / max_pop[::-1]
print(ratio)

print(df)

df = df / ratio

df = df.loc[weeks]

first = df.loc[0]
#print(first)

df = df.diff()

df.loc[0] = first

df = df.fillna(0)

df = df.round(0).astype(int)

print(df)

df.to_csv("out_" + f)




