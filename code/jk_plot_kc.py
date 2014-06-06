'''
Reads OptNIR_ALL.txt file and creates plot of spectral types v. J-K colors. It also calculates and plots the average.
'''

import numpy as np
import asciidata as ad
import matplotlib.pyplot as plt
import pdb

execfile('def_constants.py')
COLORS = [BLACK, GRAY, RED, ORANGE]

# Read data
dataraw = ad.open(FOLDER_DATA + 'OptNIR_ALL.txt', delimiter='\t')
data = np.array(dataraw).T
sptypes = data[:,4].astype('float')
jks = data[:,2].astype('float')
jksuncs = data[:,3].astype('float')
categories_raw = data[:,6]

# Format some columns
categories = np.zeros(categories_raw.shape)
for irow, row in enumerate(categories_raw):
    categories[irow] = float(categories_raw[irow][:1])

# Create data filters - categories
ifg = np.where(categories == 3)[0] # field gravity in template
ifgx = np.where(categories == 4)[0] # field gravity, excluded from template
ilg = np.where(categories == 5)[0] # low gravity in template
ilgx = np.where(categories == 6)[0] # low gravity, excluded from template

# Plot data -------------------------------------------------------------------
plt.close()
fig = plt.figure(1, figsize=(6,6))
plt.clf()
plt.rc('font', size=15)

ax = fig.add_axes([0.12,0.09,0.86,0.88]) # left, bottom, width, height
ax.scatter(sptypes[ifg], jks[ifg], marker='s', edgecolor='none', facecolor=BLACK, s=30, \
           label='field gravity, in template', zorder=7)
ax.scatter(sptypes[ifgx], jks[ifgx], marker='s', edgecolor=GRAY, facecolor='none', s=10, \
           label='field gravity, excluded', zorder=10)
ax.scatter(sptypes[ilg], jks[ilg], marker='D', edgecolor='none', facecolor=RED, s=30, \
           label='low gravity, in template', zorder=8)
ax.scatter(sptypes[ilgx], jks[ilgx], marker='D', edgecolor=ORANGE, facecolor='none', s=10, \
           label='low gravity, excluded', zorder=9)

# Plot averages
for sptp in SPTYPESN:
    isptp = np.where(sptypes == sptp)[0]
    avgjk = np.average(jks[isptp])
    ax.scatter(sptp, avgjk, marker='*', edgecolor=BLUE, facecolor='none', s=130, zorder=11)

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

ax.set_xlabel('Optical spectral type')
ax.set_ylabel(r'J-K$_s$ (2MASS)')
ax.set_xticks(SPTYPESN)
ax.set_xticklabels(SPTYPES)
ax.set_yticks(np.arange(0.8,2.8,0.2))
ax.set_ylim(0.79,2.605)
ax.set_xlim(9.6, 18.5)

# Add horizontal grid
ax.yaxis.grid(True, linestyle='-', which='major', color='lightgrey', alpha=0.8)
ax.set_axisbelow(True)

# Add legend
lgd = ax.legend(loc='lower right', scatterpoints=1, markerscale=1.5, handletextpad=-0.5, \
                bbox_to_anchor=(1.04,-0.04), labelspacing=0.04)
lgd.draw_frame(False)
for it,lgdtxt in enumerate(lgd.get_texts()):
    plt.setp(lgdtxt, color=COLORS[it])
    plt.setp(lgdtxt, fontsize=14)

# Annotate average label
loc = (16, 1.84)
loctext = (16.83, 1.32)
linetype = dict(arrowstyle='-', shrinkB=4, shrinkA=2, color=BLUE, relpos=(0,0))
plt.annotate('averages', xy=loc, xytext=loctext, fontsize=14, color=BLUE, \
             ha='left', arrowprops=linetype)

# Annotate individual object label
loc = (15, 1.4)
loctext = (15.45, 1.23)
linetype = dict(arrowstyle='-', shrinkB=4, shrinkA=2, color=BLACK, relpos=(0,0))
plt.annotate('individual objects', xy=loc, xytext=loctext, \
             fontsize=14, color=BLACK, ha='left', arrowprops=linetype)

fig.savefig(FOLDER_OUT_PLT + 'JK.pdf', dpi=300)