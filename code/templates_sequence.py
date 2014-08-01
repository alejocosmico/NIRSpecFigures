'''
Reads templates files in templates/folder and plots them as sequences. The variable DIVISIONS defines the breakdown. e.g. DIVISIONS=[0,5,9] means that templates are divided into 2 sequences: L0-L4 and L5-L8.
'''

from astropy.io import ascii
import numpy as np
import matplotlib.pyplot as plt
import pdb

# Initialize variables --------------------------------------------------------
execfile('def_constants.py')

SKIPL1 = True
DELL_CHAR = '\t' # Delimiter character
COMM_CHAR = '#'  # Comment character

grav = raw_input('Enter gravity (f, lg, g, b): ').lower()

# Break down template sequence for plotting
if grav == 'f':
    DIVISIONS = [0,5,9] # EDIT THIS ARRAY TO BREAK DOWN FIELD SEQUENCE
    TITLE = 'Field gravity'
    plotColors = colorSet[9]
elif grav == 'lg':
    DIVISIONS = [0,5] # EDIT THIS ARRAY TO BREAK DOWN LOW-G SEQUENCE [0,3,6]
    TITLE = r'ow gravity'
    if SKIPL1:
        plotColors = colorSet[5]
    else:
        plotColors = colorSet[6]
elif grav == 'g':
    DIVISIONS = [0,2] # EDIT THIS ARRAY TO BREAK DOWN LOW-G SEQUENCE
    TITLE = r'$\gamma$ gravity'
    if SKIPL1:
        plotColors = colorSet[5]
    else:
        plotColors = colorSet[6]
elif grav == 'b':
    DIVISIONS = [0,2] # EDIT THIS ARRAY TO BREAK DOWN LOW-G SEQUENCE
    TITLE = r'$\beta$ gravity'
    if SKIPL1:
        plotColors = colorSet[5]
    else:
        plotColors = colorSet[6]

# Arrays to hold template data
labels = []
data = {}.fromkeys(BANDS)
for band in BANDS:
    data[band] = []

# Read template files ---------------------------------------------------------
for isp, spType in enumerate(SPTYPES):
    if grav == 'lg' and (SKIPL1 and spType == 'L1'):
        continue
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
plotColorsPop = list(plotColors)
for idiv in range(len(DIVISIONS) - 1):
    plt.close()
    plt.rc('font', size=10)
    fig = plt.figure(idiv, figsize=(7,4.25))
    plt.clf()
    
    # Choose colors (colorSet defined in def_constants.py)
    numtempls = DIVISIONS[idiv+1] - DIVISIONS[idiv]
    if grav== 'lg' and (SKIPL1 and idiv == 0):
        numtempls = numtempls - 1
    tmpplotColors = []
    for ipop in range(0,numtempls):
        tmpplotColors.append(plotColorsPop.pop())
    
    for iband, band in enumerate(BANDS):
        ax = fig.add_axes([0.05 + (iband * 0.32), 0.1, 0.28, 0.83]) # [left, bottom, width, height]
        
        # Plot templates within range specified in DIVISIONS
        icolor = 0
        for itempl,templ in enumerate(data[band]):
            # Manually skip low-g L1 (template not that solid)
            #if grav == 'lg' and labels[itempl] == 'L1':
            #    continue
            
            if labels[itempl] >= ('L' + str(DIVISIONS[idiv])) \
                        and labels[itempl] < ('L' + str(DIVISIONS[idiv+1])):
                xs = templ['col1']
                ys = templ['col2']
                ax.plot(xs, ys, color=tmpplotColors[icolor], label=labels[itempl], \
                        linewidth=1.3)
                #ax.plot(xs, ys, color=plotColors[icolor], label=labels[itempl])
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
                plt.setp(lgdtxt, color=tmpplotColors[ilgdtxt])
        
        # Clean up axes
        ax.spines['left'].set_color('none')
        ax.spines['right'].set_color('none')
        ax.yaxis.set_ticks([])
    
    fig.savefig(FOLDER_OUT_PLT + 'sequence' + str(idiv) + '_' + grav + '.pdf', dpi=300)