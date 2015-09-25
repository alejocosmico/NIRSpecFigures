'''
Reads OptNIR_ALL.txt file and creates histogram of spectral types and color-codes by four categories: field gravity, low gravity, rejected field-gravity, and rejected low-gravity. It also color-codes by either new or old OPT and/or NIR data within each category.
'''

import numpy as np
import astropy.io.ascii as asc
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle

with open("def_constants.py") as f:
    code = compile(f.read(), "def_constants.py", "exec")
    exec(code)

# Read data
dataraw = asc.read(FOLDER_DATA + 'OptNIR_ALL.txt', delimiter='\t')
sptypes = dataraw.columns['SpType']
categories_raw = dataraw.columns['NStars Publication.Table']
nirages_raw = dataraw.columns['NIR Paper: New Prism Data.Table'].tolist()
optages_raw = dataraw.columns['NIR Paper: New Optical Data.Table'].tolist()
nirages = np.zeros(len(nirages_raw))
for irow,row in enumerate(nirages_raw):
    if row is not None:
        nirages[irow] = 1
optages = np.zeros(len(optages_raw))
for irow,row in enumerate(optages_raw):
    if row is not None:
        optages[irow] = 1

# Format some columns
categories = np.zeros(categories_raw.shape)
for irow, row in enumerate(categories_raw):
    categories[irow] = float(row[:1])

# Create data filters
ifg = np.where(categories == 3)[0] # field gravity in template
ifgx = np.where(categories == 4)[0] # field gravity, excluded from template
ilg = np.where(categories == 5)[0] # low gravity in template
ilgx = np.where(categories == 6)[0] # low gravity, excluded from template

ifgo = np.where(optages[ifg] + nirages[ifg] == 0)[0]
ifgn = np.where(optages[ifg] + nirages[ifg] == 2)[0]
ifgno = np.where(optages[ifg] > nirages[ifg])[0]
ifgon = np.where(optages[ifg] < nirages[ifg])[0]

ifgxo = np.where(optages[ifgx] + nirages[ifgx] == 0)[0]
ifgxn = np.where(optages[ifgx] + nirages[ifgx] == 2)[0]
ifgxno = np.where(optages[ifgx] > nirages[ifgx])[0]
ifgxon = np.where(optages[ifgx] < nirages[ifgx])[0]

ilgo = np.where(optages[ilg] + nirages[ilg] == 0)[0]
ilgn = np.where(optages[ilg] + nirages[ilg] == 2)[0]
ilgno = np.where(optages[ilg] > nirages[ilg])[0]
ilgon = np.where(optages[ilg] < nirages[ilg])[0]
ilgxo = np.where(optages[ilgx] + nirages[ilgx] == 0)[0]
ilgxn = np.where(optages[ilgx] + nirages[ilgx] == 2)[0]
ilgxno = np.where(optages[ilgx] > nirages[ilgx])[0]
ilgxon = np.where(optages[ilgx] < nirages[ilgx])[0]

# Plot data
plt.close()
fig = plt.figure(1, figsize=(3.30709, 3.30709)) # 84 x 84 mm
plt.clf()
plt.rc('font', size=8)
#plt.rc('hatch', linewidth=0.9)
ax = fig.add_axes([0.1,0.09,0.88,0.87]) # left, bottom, width, height

bns = np.arange(10,20,1)
stacked_sptypes = [sptypes[ilgx[ilgxo]],sptypes[ilgx[ilgxn]],
                   sptypes[ilgx[ilgxno]],sptypes[ilgx[ilgxon]],
                   sptypes[ilg[ilgo]],sptypes[ilg[ilgn]],
                   sptypes[ilg[ilgno]],sptypes[ilg[ilgon]],
                   sptypes[ifgx[ifgxo]],sptypes[ifgx[ifgxn]],
                   sptypes[ifgx[ifgxno]],sptypes[ifgx[ifgxon]],
                   sptypes[ifg[ifgo]],sptypes[ifg[ifgn]],
                   sptypes[ifg[ifgno]],sptypes[ifg[ifgon]]]
barscolors = [ORANGE,ORANGE,ORANGE,ORANGE,RED,RED,RED,RED,
              GRAY,GRAY,GRAY,GRAY,WHITE,WHITE,WHITE,WHITE]
edgescolors = [ORANGE,ORANGE,ORANGE,ORANGE,RED,RED,RED,RED,
              GRAY,GRAY,GRAY,GRAY,BLACK,BLACK,BLACK,BLACK]
ns,bins,patches = ax.hist(stacked_sptypes[::-1], bins=bns, rwidth=0.8, stacked=True, \
                          edgecolor=BLACK, color=barscolors[::-1], linewidth=0.8)

ax.set_ylabel('Number of objects', labelpad=0)
ax.set_xlabel('Optical spectral type', labelpad=0)
ax.set_xticks((10.5,11.5,12.5,13.5,14.5,15.5,16.5,17.5,18.5))
ax.set_xticklabels(SPTYPES)
ax.set_xlim(xmin=9.5, xmax=19.5)
newcollections = (2,6,10,14)
newoptcollections = (1,5,9,13)
newnircollections = (0,4,8,12)
#newcollections = (1,5,9,13) # patches with new data
#newoptcollections = (2,6,10,14) # patches with new opt data
#newnircollections = (3,7,11,15) # patches with new nir data
for newcoll in newcollections:
    for ip,patch in enumerate(patches[newcoll]):
        patches[newcoll][ip].set_hatch('xxx')
for newcoll in newoptcollections:
    for ip,patch in enumerate(patches[newcoll]):
        patches[newcoll][ip].set_hatch('\\\\')
for newcoll in newnircollections:
    for ip,patch in enumerate(patches[newcoll]):
        patches[newcoll][ip].set_hatch('///')

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
ax.text(14.8,33.6,'low gravity, excluded', color=ORANGE, size=7, weight='bold')
ax.text(14.8,32.0, 'low gravity, in template', color=RED, size=7, weight='bold')
ax.text(14.8,30.4,'field gravity, excluded', color=GRAY, size=7, weight='bold')
ax.text(14.8,28.8, 'field gravity, in template', color=BLACK, size=7, weight='bold')
ax.add_patch(Rectangle((14.2,33.6), 0.5, 1.1, facecolor=ORANGE, edgecolor=BLACK, linewidth=0.7))
ax.add_patch(Rectangle((14.2,32), 0.5, 1.1, facecolor=RED, edgecolor=BLACK, linewidth=0.7))
ax.add_patch(Rectangle((14.2,30.4), 0.5, 1.1, facecolor=GRAY, edgecolor=BLACK, linewidth=0.7))
ax.add_patch(Rectangle((14.2,28.8), 0.5, 1.1, facecolor=WHITE, edgecolor=BLACK, linewidth=0.7))

# align everything @ 15
ax.add_patch(Rectangle((14.8,23), 0.8, 1.4, hatch='\\\\\\', facecolor='none', edgecolor=BLACK, linewidth=0.7))
ax.text(15.7,23.2, 'new optical spectra', fontstyle='italic', size=7, color=GRAY)
ax.add_patch(Rectangle((14.8,21), 0.8, 1.4, hatch='///', facecolor='none', edgecolor=BLACK, linewidth=0.7))
ax.text(15.7,21.3, 'new NIR spectra', fontstyle='italic', size=7, color=GRAY)

fig.savefig(FOLDER_OUT_PLT + 'histogram.pdf', dpi=300)