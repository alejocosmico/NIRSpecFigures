'''
Reads OptNIR_ALL.txt file and creates plot of spectral types v. J-K colors. It also calculates and plots the average.
'''

import numpy as np
import astropy.io.ascii as asc
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import pdb

with open("def_constants.py") as f:
    code = compile(f.read(), "def_constants.py", "exec")
    exec(code)

COLORS = [BLACK, GRAY, RED, ORANGE]
CATEGNUMS = [3,4,5,6] # [field in template, field excluded, low-g in template, low-g excluded]
CATEGLABELS = ['field gravity, in template', 'field gravity, excluded',
               'low gravity, in template', 'low gravity, excluded']
LOCSBOXFIELDS = np.arange(1,18,2)
LOCSBOXLOWG = np.arange(1.4,18,2)

# Initialize txt file to store stats
f = open(FOLDER_DATA + 'quartiles_stats.txt', 'w')
f.write('#SpType gravity min 25-quartile median 75-quartile max mean numOjbs \n')

# Read data
dataraw = asc.read(FOLDER_DATA + 'OptNIR_ALL.txt', delimiter='\t')
sptypes = dataraw.columns['SpType']
jks = dataraw.columns['J-K']
jksuncs = dataraw.columns['J-K_unc']
categories_raw = dataraw.columns['NStars Publication.Table']

# Format some columns
categories = np.zeros(categories_raw.shape)
for irow, row in enumerate(categories_raw):
    categories[irow] = float(row[:1])

# Create data filters - categories
ifg = np.where(categories == 3)[0] # field gravity in template
ifgx = np.where(categories == 4)[0] # field gravity, excluded from template
ilg = np.where(categories == 5)[0] # low gravity in template
ilgx = np.where(categories == 6)[0] # low gravity, excluded from template

# Plot data -------------------------------------------------------------------
plt.close()
fig = plt.figure(1, figsize=(3.30709, 3.30709)) # 84 x 84 mm
plt.clf()
plt.rc('font', size=8)

ax = fig.add_axes([0.12,0.09,0.86,0.88]) # left, bottom, width, height

# Plot data:
plotteduncs = np.array([])
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
            # Record J-K uncertainties of objects drawn
            plotteduncs = np.append(plotteduncs, jksuncs[icat[itoplot]].data.data)
            
            if categ == 3:
                grav = 'field'
                xloc = LOCSBOXFIELDS[isptype]
            else:
                grav = 'low-g'
                xloc = LOCSBOXLOWG[isptype]
            # If sample has < 6 objects, then just draw mean and min/max
            if len(itoplot) < 6:
                tmpmean = np.mean(jks[icat[itoplot]])
                tmpmin = tmpmean - np.min(jks[icat[itoplot]])
                tmpmax = np.max(jks[icat[itoplot]]) - tmpmean
                ax.errorbar(xloc, tmpmean, yerr=np.array([[tmpmin],[tmpmax]]), \
                            fmt='.', color=COLORS[icateg], linewidth=0.7, capsize=1.5)
            else:
                bp = ax.boxplot([jks[icat[itoplot]]], positions=[xloc], whis=np.inf, \
                                widths=0.3)
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
            ax.scatter(xloc, avgjk, marker='o', edgecolor='none', \
                       facecolor=COLORS[icateg], s=7, zorder=10)
            
            # Annotate number of objects in box
            numjk = len(jks[icat[itoplot]])
            if categ == 3 and (sptype==10 or sptype==12 or sptype==13 or sptype==15):
                yloc = jkmax + 0.06
            else:
                yloc = jkmax + 0.02
            ax.text(xloc-0.05 , yloc, str(numjk), color=COLORS[icateg], \
                    fontsize=7, ha='right', zorder=1000)
            
            # Consolidate data to print in txt file
            tmptextline = SPTYPES[isptype] + ' ' + grav + ' ' \
                               + str(np.round(bp['caps'][0].get_ydata()[0],3)) + ' ' \
                               + str(np.round(bp['boxes'][0].get_ydata()[0],3)) + ' ' \
                               + str(np.round(bp['medians'][0].get_ydata()[0],3))+' ' \
                               + str(np.round(bp['boxes'][0].get_ydata()[2],3)) + ' ' \
                               + str(np.round(bp['caps'][1].get_ydata()[0],3)) + ' ' \
                               + str(np.round(avgjk,3)) + ' ' \
                               + str(numjk) + '\n'
            f.write(tmptextline)
        
        # Plot excluded as scatter points
        elif categ in [4,6]:
            if categ == 4:
                xloc = LOCSBOXFIELDS[isptype]
            else:
                xloc = LOCSBOXLOWG[isptype]
            ax.scatter([xloc] * len(jks[icat[itoplot]]), jks[icat[itoplot]], \
                       marker='x', edgecolor=COLORS[icateg], facecolor='none', \
                       s=10, zorder=5, linewidth=0.7)

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
ax.set_ylabel(r'$J-K_s$ (2MASS)', labelpad=0)
ax.set_xticks(LOCSBOXFIELDS+0.3)
ax.set_xticklabels(SPTYPES)
ax.set_yticks(np.arange(0.8,2.8,0.2))
ax.set_ylim(0.79,2.605)
ax.set_xlim(0, 18)

# Add horizontal grid
ax.yaxis.grid(True, linestyle='-', which='major', color='lightgrey', alpha=0.9)
ax.set_axisbelow(True)

# Add legend
ax.plot([100,100], color=BLACK, label='field gravity statistics')
ax.plot([100,100], color=RED, label='low gravity statistics')
ax.scatter(100,100, marker='o', edgecolor='none', facecolor=RED, label='mean')
ax.scatter(100,100, marker='x', color=ORANGE, label='excluded (')
lgd = ax.legend(loc='upper left', handlelength=0.5, numpoints=1, scatterpoints=1, \
                labelspacing=0.2, handletextpad=0.2, bbox_to_anchor=(0,1))
lgd.draw_frame(False)
for ilgdtxt,lgdtxt in enumerate(lgd.get_texts()):
    plt.setp(lgdtxt, fontsize=7)

# Draw mean color uncertainty
meanunc = np.median(plotteduncs)
eb = ax.errorbar(LOCSBOXLOWG[-1]*1.01, 2.5, yerr=meanunc, fmt='d', ms=4, color=GRAY, \
                mec=GRAY, linewidth=1, capsize=2)

# Add additional text and icons to legend
circle = mpatches.Ellipse((0.52,2.318), 0.4, 0.04, facecolor=BLACK, edgecolor='none')
ax.add_artist(circle)
ax.text(0.28, 2.21, 'x', fontweight='bold', fontsize=8.5, color=GRAY)
ax.text(4.53, 2.21, 'field g.', color=GRAY, fontsize=7)
ax.text(6.62, 2.21, ',', color=BLACK, fontsize=7)
ax.text(6.92, 2.21, 'low g.', color=ORANGE, fontsize=7)
ax.text(8.65, 2.21, ')', fontsize=7)

fig.savefig(FOLDER_OUT_PLT + 'JK.pdf', dpi=300)
f.close()
