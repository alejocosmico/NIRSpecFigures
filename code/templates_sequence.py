'''

'''

from astropy.io import ascii
import numpy as np
import matplotlib.pyplot as plt
import pdb

# Initialize variables --------------------------------------------------------
execfile('def_constants.py')

DELL_CHAR = '\t' # Delimiter character
COMM_CHAR = '#'  # Comment character

grav = raw_input('Enter gravity (f or lg): ').lower()

# Break down template sequence for plotting
if grav == 'f':
    DIVISIONS = [0,5,9]
    TITLE = 'Field gravity'
elif grav == 'lg':
    DIVISIONS = [0,3,6]
    TITLE = 'Low gravity'

# Arrays to hold template data
labels = []
data = {}.fromkeys(BANDS)
for band in BANDS:
    data[band] = []

# Read template files ---------------------------------------------------------
for isp, spType in enumerate(SPTYPES):
    for band in BANDS:
        filename = spType + band + '_' + grav + '.txt'
        try:
            tmpdata = ascii.read(FOLDER_OUT_TMPL + filename, format='no_header', \
                                 delimiter=DELL_CHAR, comment=COMM_CHAR)
        except:
            tmpdata = []
        if len(tmpdata) != 0:
            data[band].append(tmpdata)
            if band == 'J':
                labels.append(spType)

# Plot templates --------------------------------------------------------------
for idiv in range(len(DIVISIONS) - 1):
    plt.close()
    plt.rc('font', size=10)
    fig = plt.figure(idiv, figsize=(7,4.25))
    plt.clf()
    
    # Choose colors (colorSet defined in def_constants.py)
    numtempls = DIVISIONS[idiv+1] - DIVISIONS[idiv]
    plotColors = colorSet[numtempls][::-1]
    
    for iband, band in enumerate(BANDS):
        ax = fig.add_axes([0.05 + (iband * 0.32), 0.1, 0.28, 0.83]) # [left, bottom, width, height]
        
        # Plot templates within range specified in DIVISIONS
        icolor = 0
        for itempl,templ in enumerate(data[band]):
            # Manually skip low-g L1 (template not that solid)
            if grav == 'lg' and labels[itempl] == 'L1':
                continue
            
            if labels[itempl] >= ('L' + str(DIVISIONS[idiv])) \
                        and labels[itempl] < ('L' + str(DIVISIONS[idiv+1])):
                xs = templ['col1']
                ys = templ['col2']
                ax.plot(xs, ys, color=plotColors[icolor], label=labels[itempl])
                icolor = icolor + 1
        
        # Add labels and legend
        if iband == 1:
            ax.set_xlabel('Wavelength ($\mu$m)')
        if iband == 0:
            yloc = ax.get_ylim()[1] * 0.94
            ax.text(0.81, yloc, TITLE, fontsize=12)
            ax.text(0.81, yloc - 0.1, 'templates', fontsize=12)
            ax.set_ylabel('Normalized Flux (F$_{\lambda}$)')
            lgd = ax.legend(handlelength=0, handletextpad=0.1, loc='upper left', \
                            bbox_to_anchor=(0,0.88), labelspacing=0.3, numpoints=1)
            lgd.draw_frame(False)
            for ilgdtxt,lgdtxt in enumerate(lgd.get_texts()):
                plt.setp(lgdtxt, color=plotColors[ilgdtxt])
        
        # Clean up axes
        ax.spines['left'].set_color('none')
        ax.spines['right'].set_color('none')
        ax.yaxis.set_ticks([])
    
    fig.savefig(FOLDER_OUT_PLT + 'sequence' + str(idiv) + '_' + grav + '.pdf', dpi=300)