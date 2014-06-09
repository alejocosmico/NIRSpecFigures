'''
Reads OptNIR_ALL.txt file and creates histogram of spectral types and color-codes by four categories: field gravity, low gravity, rejected field-gravity, and rejected low-gravity. It also color-codes by either new or old OPT and/or NIR data within each category.
'''

import numpy as np
import asciidata as ad
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle

execfile('def_constants.py')

# Read data
dataraw = ad.open(FOLDER_DATA + 'OptNIR_ALL.txt', delimiter='\t')
data = np.array(dataraw).T
sptypes = data[1:,4].astype('float')
categories_raw = data[1:,6]
nirages = data[1:,7]
optages = data[1:,8]

# Format some columns
categories = np.zeros(categories_raw.shape)
for irow, row in enumerate(categories_raw):
    categories[irow] = float(categories_raw[irow][:1])

# Create data filters
ifg = np.where(categories == 3)[0] # field gravity in template
ifgx = np.where(categories == 4)[0] # field gravity, excluded from template
ilg = np.where(categories == 5)[0] # low gravity in template
ilgx = np.where(categories == 6)[0] # low gravity, excluded from template

ifgo = np.where((optages[ifg] == '') & (nirages[ifg] == ''))[0]
ifgn = np.where((optages[ifg] != '') & (nirages[ifg] != ''))[0]
ifgno = np.where((optages[ifg] != '') & (nirages[ifg] == ''))[0]
ifgnn = np.where((optages[ifg] == '') & (nirages[ifg] != ''))[0]

ifgxo = np.where((optages[ifgx] == '') & (nirages[ifgx] == ''))[0]
ifgxn = np.where((optages[ifgx] != '') & (nirages[ifgx] != ''))[0]
ifgxno = np.where((optages[ifgx] != '') & (nirages[ifgx] == ''))[0]
ifgxnn = np.where((optages[ifgx] == '') & (nirages[ifgx] != ''))[0]

ilgo = np.where((optages[ilg] == '') & (nirages[ilg] == ''))[0]
ilgn = np.where((optages[ilg] != '') & (nirages[ilg] != ''))[0]
ilgno = np.where((optages[ilg] != '') & (nirages[ilg] == ''))[0]
ilgnn = np.where((optages[ilg] == '') & (nirages[ilg] != ''))[0]
ilgxo = np.where((optages[ilgx] == '') & (nirages[ilgx] == ''))[0]
ilgxn = np.where((optages[ilgx] != '') & (nirages[ilgx] != ''))[0]
ilgxno = np.where((optages[ilgx] != '') & (nirages[ilgx] == ''))[0]
ilgxnn = np.where((optages[ilgx] == '') & (nirages[ilgx] != ''))[0]


# Plot data
plt.close()
fig = plt.figure(1, figsize=(8,8))
plt.clf()
plt.rc('font', size=15)
plt.rc('hatch', linewidth=0.9)
ax = fig.add_axes([0.09,0.08,0.88,0.89]) # left, bottom, width, height

bns = np.arange(10,20,1)
stacked_sptypes = [sptypes[ilgx[ilgxo]],sptypes[ilgx[ilgxn]],
                   sptypes[ilgx[ilgxno]],sptypes[ilgx[ilgxnn]],
                   sptypes[ilg[ilgo]],sptypes[ilg[ilgn]],
                   sptypes[ilg[ilgno]],sptypes[ilg[ilgnn]],
                   sptypes[ifgx[ifgxo]],sptypes[ifgx[ifgxn]],
                   sptypes[ifgx[ifgxno]],sptypes[ifgx[ifgxnn]],
                   sptypes[ifg[ifgo]],sptypes[ifg[ifgn]],
                   sptypes[ifg[ifgno]],sptypes[ifg[ifgnn]]]
barscolors = [ORANGE,ORANGE,ORANGE,ORANGE,RED,RED,RED,RED,
              GRAY,GRAY,GRAY,GRAY,BLACK,BLACK,BLACK,BLACK]
ns,bins,patches = ax.hist(stacked_sptypes, bins=bns, rwidth=0.8, stacked=True, \
                          edgecolor=WHITE, color=barscolors)

ax.set_ylabel('Number of objects', labelpad=8)
ax.set_xlabel('Optical spectral type', labelpad=8)
ax.set_xticks((10.5,11.5,12.5,13.5,14.5,15.5,16.5,17.5,18.5))
ax.set_xticklabels(SPTYPES)
ax.set_xlim(xmin=9.5, xmax=19.5)
newcollections = (1,5,9,13) # patches with new data
newoptcollections = (2,6,10,14) # patches with new opt data
newnircollections = (3,7,11,15) # patches with new nir data
for newcoll in newcollections:
    for ip,patch in enumerate(patches[newcoll]):
        patches[newcoll][ip].set_hatch('x')
for newcoll in newoptcollections:
    for ip,patch in enumerate(patches[newcoll]):
        patches[newcoll][ip].set_hatch('\\')
for newcoll in newnircollections:
    for ip,patch in enumerate(patches[newcoll]):
        patches[newcoll][ip].set_hatch('/')

# Format plot (make lots of things disappear)
# Hide axes lines
ax.spines['top'].set_color(WHITE)
ax.spines['bottom'].set_color(WHITE)
ax.spines['left'].set_color(WHITE)
ax.spines['right'].set_color(WHITE)

# Hide ticker lines
tcks = ax.xaxis.get_ticklines()
for tl in tcks:
    tl.set_color(WHITE)
tcks = ax.yaxis.get_ticklines()
for tl in tcks:
    tl.set_color(WHITE)

# Add horizontal grid
ax.yaxis.grid(True, linestyle='-', which='major', color='lightgrey', alpha=0.8)
ax.set_axisbelow(True)

# Add annotations
ax.text(15,34.7,'low gravity, excluded', color=ORANGE, size=16, weight='bold')
ax.text(15,33.2, 'low gravity, in template', color=RED, size=16, weight='bold')
ax.text(15,31.7,'field gravity, excluded', color=GRAY, size=16, weight='bold')
ax.text(15,30.2, 'field gravity, in template', color=BLACK, size=16, weight='bold')
# align everything @ 15
ax.add_patch(Rectangle((15,27.6), 0.37, 1.2, hatch='\\\\', facecolor='none', edgecolor=GRAY))
ax.text(15.4,27.9, 'new optical spectra', fontstyle='italic', size=16, color=GRAY)
ax.add_patch(Rectangle((15,26), 0.37, 1.2, hatch='//', facecolor='none', edgecolor=GRAY))
ax.text(15.4,26.3, 'new NIR spectra', fontstyle='italic', size=16, color=GRAY)

fig.savefig(FOLDER_OUT_PLT + 'histogram.pdf', dpi=300)