''' 
Reads OptNIR_ALL.txt file and creates plot of avg spectral types v. J-K colors for field-gravity spectra used in templates. It includes extreme points (as error bars). It also includes Faherty-13 values.
'''

import numpy as np
import astropy.io.ascii as asc
import matplotlib.pyplot as plt
import pdb  

with open("def_constants.py") as f:
    code = compile(f.read(), "def_constants.py", "exec")
    exec(code)

# Faherty-12 J-K averages, extremes, and counts, L0 to L8 in sequential order
JKAVGS    = np.array([1.3,1.35,1.48,1.64,1.69,1.72,1.84,1.75,1.85])
EXTREMES = np.array([[0.809,1.98],[0.95,1.926],[0.974,1.946],[1.136,2.103],[1.168,2.178], \
                     [1.205,2.033],[1.386,2.382],[1.412,2.079],[1.594,2.115]])
COUNTS   = np.array([102,95,60,51,33,28,13,9,10])
SPTYPESN = np.array(SPTYPESN)

# Read data
dataraw = asc.read(FOLDER_DATA + 'OptNIR_ALL.txt', delimiter='\t')
sptypes = dataraw.columns['SpType']
jks = dataraw.columns['J-K']
jksuncs = dataraw.columns['J-K_unc']
categories_raw = dataraw.columns['NStars Publication.Table']

# Format some columns
categories = np.zeros(categories_raw.shape)
for irow, row in enumerate(categories_raw):
    categories[irow] = float(categories_raw[irow][:1])

# Create data filter for field objects in templates
ifg = np.where(categories == 3)[0]

jksavgs = []
extremes = []
counts = []
for ist, sptp in enumerate(SPTYPESN):
    isptp = np.where(sptypes[ifg] == sptp)[0]
    jksavgs.append(np.average(jks[ifg[isptp]]))
    extremes.append([jks[ifg[isptp]].min(), jks[ifg[isptp]].max()])
    counts.append(len(isptp))
extremes = np.array(extremes)

# Plot data -------------------------------------------------------------------
plt.close()
fig = plt.figure(1, figsize=(3.30709, 3.30709)) # 84 x 84 mm
plt.clf()
plt.rc('font', size=8)
ax = fig.add_axes([0.12,0.09,0.86,0.88]) # left, bottom, width, height

# Plot Faherty data
extremes_JF = EXTREMES.T.copy()
extremes_JF[0,:] = JKAVGS - extremes_JF[0,:]
extremes_JF[1,:] = extremes_JF[1,:] - JKAVGS
ax.errorbar(SPTYPESN-0.1, JKAVGS, yerr=extremes_JF, ecolor=L_BLUE, linestyle='', marker='o', \
            markersize=6, markerfacecolor=L_BLUE, markeredgecolor='none', markeredgewidth=1.1)

# Plot Kelle data
extremes_KC = extremes.T.copy()
extremes_KC[0,:] = jksavgs - extremes_KC[0,:]
extremes_KC[1,:] = extremes_KC[1,:] - jksavgs
ax.errorbar(SPTYPESN+0.1, jksavgs, yerr=extremes_KC, ecolor=BLACK, linestyle='', marker='s', \
            markersize=6, markerfacecolor=BLACK, markeredgecolor='none', markeredgewidth=1.1)

# Annotate top of Faherty bars
for idxc, count in enumerate(COUNTS):
    if idxc == 5:
        xoff = 9.8
    else:
        xoff = 9.9
    loc = (idxc + xoff, EXTREMES[idxc,1]+0.01)
    ax.text(loc[0],loc[1],str(int(count)), color=GRAY, fontstyle='italic', fontsize=7, \
            ha='center')

# Annotate top of Kelle bars
for idxc, count in enumerate(counts):
    if idxc == 5:
        xoff = 10.2
    else:
        xoff = 10.1
    loc = (idxc + xoff, extremes[idxc,1]+0.01)
    ax.text(loc[0],loc[1],str(int(count)), color=GRAY, fontstyle='italic', fontsize=7, \
            ha='center')

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

ax.set_xlabel('Optical spectral type', labelpad=0)
ax.set_ylabel(r'J-K$_s$ (2MASS)', labelpad=0)
ax.set_xticks(SPTYPESN)
ax.set_xticklabels(SPTYPES)
ax.set_yticks(np.arange(0.8,2.8,0.2))
ax.set_ylim(0.79,2.45)
ax.set_xlim(9.6, 18.5)

# Add horizontal grid
ax.yaxis.grid(True, linestyle='-', which='major', color='lightgrey', alpha=0.8)
ax.set_axisbelow(True)

# Annotate Faherty data
loc = (15-0.1, 1.2)
loctext = (14.7, 0.88)
linetype = dict(arrowstyle='-', shrinkB=4, shrinkA=2, color=L_BLUE, relpos=(1,0))
plt.annotate('Faherty et al. \'13', xy=loc, xytext=loctext, fontsize=8, color=L_BLUE, \
             ha='right', arrowprops=linetype)
loctext = (14.7, 0.815)
plt.annotate('photometric sample', xy=loc, xytext=loctext, fontsize=8, color=L_BLUE, \
             ha='right')

# Annotate Kelle data
loc = (15+0.1, 1.56)
loctext = (15.45, 1.27)
linetype = dict(arrowstyle='-', shrinkB=4, shrinkA=2, color=BLACK, relpos=(0,0))
plt.annotate('field gravity', xy=loc, xytext=loctext, fontsize=8, color=BLACK, \
             ha='left', arrowprops=linetype)
loctext = (15.45, 1.205)
plt.annotate('template objects', xy=loc, xytext=loctext, fontsize=8, color=BLACK, \
             ha='left')

# Annotate bin numbers
loc = (13-0.1, 2.15)
loctext = (10.5, 2.3)
linetype = dict(arrowstyle='-', shrinkB=4, shrinkA=0, color=GRAY, relpos=(1,0))
plt.annotate('objects in bin', xy=loc, xytext=loctext, fontsize=8, color=GRAY, \
             ha='left', arrowprops=linetype)

fig.savefig(FOLDER_OUT_PLT + 'JK_JF.pdf', dpi=300)