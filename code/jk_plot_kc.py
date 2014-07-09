'''
Reads OptNIR_ALL.txt file and creates plot of spectral types v. J-K colors. It also calculates and plots the average.
'''

import numpy as np
import asciidata as ad
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import pdb

execfile('def_constants.py')
COLORS = [BLACK, GRAY, RED, ORANGE]
CATEGNUMS = [3,4,5,6] # [field in template, field excluded, low-g in template, low-g excluded]
CATEGLABELS = ['field gravity, in template', 'field gravity, excluded',
               'low gravity, in template', 'low gravity, excluded']
LOCSBOXFIELDS = np.arange(1,18,2)
LOCSBOXLOWG = np.arange(1.4,18,2)

# Initialize txt file to store stats
f = open(FOLDER_DATA + 'quartiles_stats.txt', 'w')
f.write('#SpType gravity min 25-quartile mean 75-quartile max numOjbs \n')

# Read data
dataraw = ad.open(FOLDER_DATA + 'OptNIR_ALL.txt', delimiter='\t')
data = np.array(dataraw).T
data = np.delete(data, 0, axis=0)
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
plt.rc('font', size=14)

ax = fig.add_axes([0.12,0.09,0.86,0.88]) # left, bottom, width, height

# Plot data:
for isptype,sptype in enumerate(SPTYPESN):
    for icateg,categ in enumerate(CATEGNUMS):
        # Identify relevant objects to plot
        icat = np.where(categories == categ)[0]
        if len(icat) == 0:
            continue
        itoplot = np.where(sptypes[icat] == sptype)[0]
        if len(itoplot) == 0:
            continue
        # Keep track of max J-K value in each category (field v. low-g)
        jkmax = np.max(jks[icat[itoplot]])
        
        # Plot objects in template as box & whiskers
        if categ in [3,5]:
            if categ == 3:
                grav = 'field'
                xloc = LOCSBOXFIELDS[isptype]
            else:
                grav = 'low-g'
                xloc = LOCSBOXLOWG[isptype]
            
            bp = ax.boxplot([jks[icat[itoplot]]], positions=[xloc], whis=np.inf, widths=0.3)
            for box in bp['boxes']:
                box.set(color=COLORS[icateg])
                box.set(linewidth=0.7)
            for whisker in bp['whiskers']:
                whisker.set(color=COLORS[icateg])
                whisker.set(linestyle='-')
                whisker.set(linewidth=0.7)
            for median in bp['medians']:
                median.set(color=COLORS[icateg])
            for cap in bp['caps']:
                cap.set(color=COLORS[icateg])
                cap.set(linewidth=0.7)
            
            # Plot averages as scatter points
            avgjk = np.average(jks[icat[itoplot]])
            ax.scatter(xloc, avgjk, marker='o', edgecolor='none', facecolor=COLORS[icateg], \
                       s=15, zorder=10)
            
            # Annotate number of objects in box
            numjk = len(jks[icat[itoplot]])
            if categ == 3 and (sptype == 10 or sptype == 12 or sptype == 13 or sptype == 15):
                yloc = jkmax + 0.06
            else:
                yloc = jkmax + 0.02
            ax.text(xloc-0.05 , yloc, str(numjk), color=COLORS[icateg], fontsize=9, ha='center')
            
            # Consolidate data to print in txt file
            tmptextline = SPTYPES[isptype] + ' ' + grav + ' ' \
                               + str(np.round(bp['caps'][1].get_ydata()[0],3)) + ' ' \
                               + str(np.round(bp['boxes'][0].get_ydata()[0],3)) + ' ' \
                               + str(np.round(avgjk,3)) + ' ' \
                               + str(np.round(bp['boxes'][0].get_ydata()[2],3)) + ' ' \
                               + str(np.round(bp['caps'][0].get_ydata()[0],3)) + ' ' \
                               + str(numjk) + '\n'
            f.write(tmptextline)
        
        # Plot excluded as scatter points
        elif categ in [4,6]:
            if categ == 4:
                xloc = LOCSBOXFIELDS[isptype]
            else:
                xloc = LOCSBOXLOWG[isptype]
            ax.scatter([xloc] * len(jks[icat[itoplot]]), jks[icat[itoplot]], marker='x', \
                       edgecolor=COLORS[icateg], facecolor='none', s=20, zorder=5)

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
ax.set_xticks(LOCSBOXFIELDS+0.3)
ax.set_xticklabels(SPTYPES)
ax.set_yticks(np.arange(0.8,2.8,0.2))
ax.set_ylim(0.79,2.605)
ax.set_xlim(0, 18)

# Add horizontal grid
ax.yaxis.grid(True, linestyle='-', which='major', color='lightgrey', alpha=0.9)
ax.set_axisbelow(True)

# Add legend
ax.plot([100,100], color=BLACK, label='field gravity quartiles')
ax.plot([100,100], color=RED, label='low gravity quartiles')
ax.scatter(100,100, marker='o', edgecolor='none', facecolor=RED, label='average')
ax.scatter(100,100, marker='x', color=ORANGE, label='excluded (')
lgd = ax.legend(loc='upper left', handlelength=0.5, numpoints=1, scatterpoints=1, \
                labelspacing=0.2, handletextpad=0.2, bbox_to_anchor=(0.0,1))
lgd.draw_frame(False)
for ilgdtxt,lgdtxt in enumerate(lgd.get_texts()):
    plt.setp(lgdtxt, fontsize=11)

# Add additional text and icons to legend
circle = mpatches.Ellipse((0.55,2.331), 0.25, 0.023, facecolor=BLACK, edgecolor='none')
ax.add_artist(circle)
ax.text(0.45, 2.236, 'x', fontweight='bold', fontsize=9, color=GRAY)
ax.text(4.1, 2.2255, 'field g.', color=GRAY, fontsize=11)
ax.text(5.9, 2.2255, ',', color=BLACK, fontsize=11)
ax.text(6.1, 2.2255, 'low g.', color=ORANGE, fontsize=11)
ax.text(7.6, 2.2255, ')', fontsize=11)

fig.savefig(FOLDER_OUT_PLT + 'JK.pdf', dpi=300)
f.close()