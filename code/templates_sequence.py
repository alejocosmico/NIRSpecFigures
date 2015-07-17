'''
Reads templates files in templates/folder and plots them as sequences. The variable DIVISIONS defines the breakdown. e.g. DIVISIONS=[0,5,9] means that templates are divided into 2 sequences: L0-L4 and L5-L8.
'''

def addannot(specData, subPlot, bandName, classType):
    # Adds annotations to indicate spectral absorption lines
    
    import numpy as np
    from scipy.stats import nanmean
    import pdb
    
    # 1) Initialize strings
    TXT_SIZE = 7
    H2O   = 'H' + '$\sf_2$' + 'O'
    COH2O = 'CO+' + H2O
    H2OH2 = H2O + ' + H' + '$\sf_2$' + ' CIA'
    EARTH = r'$\oplus$'
    
    # 2) Define the spectral lines to annotate
    if bandName == 'J':
        ANNOT = [None] * 11
        ANNOT[0]  = [H2O,   (0.890,0.990),   0, 'Band']
        ANNOT[1]  = ['FeH', (0.980,1.017),   0, 'Band']
        ANNOT[2]  = ['VO',  (1.050,1.080),   0, 'Band']
        ANNOT[3]  = [H2O,   (1.090,1.200),   0, 'Band']
        ANNOT[4]  = ['Na I', 1.141,         15, 'Line']
        ANNOT[5]  = ['K I',  1.170,        -30, 'Line']
        ANNOT[6]  = ['VO',  (1.160,1.200),   0, 'Band']
        ANNOT[7]  = ['FeH', (1.194,1.239),   0, 'Band']
        ANNOT[8]  = ['K I',  1.250,        -25, 'Line']
        ANNOT[9]  = [r'Pa $\beta$', 1.280, -20, 'LineT']
        ANNOT[10] = [H2O,   (1.310,1.390),   0, 'Band']
    
    elif bandName == 'H':
        ANNOT = [None] * 4
        ANNOT[0] = [H2O,   (1.410,1.510), 0, 'Band']
        ANNOT[1] = ['FeH', (1.583,1.750), 0, 'Band']
        ANNOT[2] = ['Br 14', 1.588,     -15, 'LineT']
        ANNOT[3] = [H2O,   (1.750,1.890), 0, 'Band']
    
    elif bandName == 'K': 
        ANNOT = [None] * 5
        ANNOT[0] = [H2O,    (1.910,2.050),   0, 'Band']
        ANNOT[1] = [H2OH2,  (2.150,2.390),   0, 'Band']
        ANNOT[2] = [r'Br $\gamma$', 2.160, -25, 'LineT']
        ANNOT[3] = ['Na I',  2.210,        -10, 'Line']
        ANNOT[4] = [COH2O,  (2.293,2.390),   0, 'Band']
    
    else:
        return
    
    # 3) Add annotation for each absorption feature
    for annotation in ANNOT:
        # Skip Na I in K-band after L1
        if bandName == 'K' and annotation[0] == 'Na I' and int(classType[1]) > 1:
            continue
        
        # Determine distances between annotated point and annotation's objects
        offLine = annotation[2]     # Distance betw. annotation line & plot
        if offLine > 0:
            offText = offLine + 10  # Distance betw. text & plot
        else:
            offText = offLine - 15
        
        # Create annotation line style
        # Rb I, Na I, Rb I: shift text a little bit from center
        if annotation[1] == 0.8943 or annotation[1] == 0.7800 \
                                   or annotation[1] == 1.141:
            annLineType = dict(arrowstyle='-', shrinkB=offLine, shrinkA=0.5, \
                               connectionstyle='angle,angleA=0,angleB=90,rad=0')
        else:
            annLineType = dict(arrowstyle='-', shrinkB=offLine, shrinkA=0.5)
        annLineType2 = dict(arrowstyle='-', shrinkB=offLine, shrinkA=0.5, color='w')
        
        annotType = annotation[3]
        # <><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><>
        if annotType.startswith('Line'):
        # For Line absorption: Add annotation with vertical connector
            # Initialize variables
            objsFluxIdxs = [np.nan] * len(specData)
            objsFluxes   = [np.nan] * len(specData)
            
            # Find spectrum with the highest/lowest flux @ absorption wavelength
            for objIdx, objSpec in enumerate(specData):
                wlRange = np.where(objSpec.columns[0] <= annotation[1])
                if len(wlRange[0]) == 0:
                    objsFluxIdxs[objIdx] = 0
                else:
                    objsFluxIdxs[objIdx] = wlRange[0][-1]
                objsFluxes[objIdx] = objSpec.columns[1][objsFluxIdxs[objIdx]]
            
            if offLine > 0:
                xtremeObj = np.array(objsFluxes).argmax()
            else:
                xtremeObj = np.array(objsFluxes).argmin()
            
            # Set the coordinate location for the annotated point
            annotWL  = specData[xtremeObj].columns[0][objsFluxIdxs[xtremeObj]]
            annotLoc = (annotWL, objsFluxes[xtremeObj])
            
            # Set the coordinate location for the annotation's text
            if annotation[1] == 0.8943:   # Rb I
                textLoc = (-5, offText)
            elif annotation[1] == 1.141:  # Na I
                textLoc = (-2, offText)
            else:
                textLoc = (0, offText)
            
            # Add the Earth symbol to telluric features
            if annotType.endswith('T'):
                tellTextLoc = (textLoc[0], textLoc[1] - 7)
                subPlot.annotate(EARTH, xy=annotLoc, xycoords='data', \
                             xytext=tellTextLoc, textcoords='offset points', \
                             fontsize=TXT_SIZE, ha='center', arrowprops=annLineType2)
            
            # Add the damned annotation
            subPlot.annotate(annotation[0], xy=annotLoc, xycoords='data', \
                             xytext=textLoc, textcoords='offset points', \
                             fontsize=TXT_SIZE, fontname='Times New Roman', \
                             ha='center', arrowprops=annLineType)
        
        # <><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><>
        elif annotType == 'Band':  # Draw a horizontal line
        # For band absorption: Add horizontal line AND annotation with no connector
            # Initialize variables
            objsFluxIdxs = [np.nan] * len(specData)
            objsFluxAvgs = [np.nan] * len(specData)
            xPos = np.zeros([len(specData),2])
            xPos.fill(np.nan)
        
            # Find spectrum with the highest/lowest flux average @ absorption wls
            for objIdx, objSpec in enumerate(specData):
                xLoRange = np.where(objSpec.columns[0] <= annotation[1][0])
                if len(xLoRange[0]) == 0:
                    xPos[objIdx,0] = objSpec.columns[0][0]
                else:
                    xPos[objIdx,0] = xLoRange[0][-1]
                
                xHiRange = np.where(objSpec.columns[0] >= annotation[1][1])
                if len(xHiRange[0]) == 0:
                    xPos[objIdx,1] = objSpec.columns[0][-1]
                else:
                    xPos[objIdx,1] = xHiRange[0][0]
                    
                    # Set up limits of section with which to calculate average flux
                    firstxPos = xPos[objIdx,0]
                    lastxPos  = xPos[objIdx,1]
                
                objsFluxAvgs[objIdx] = nanmean(objSpec.columns[1][firstxPos:lastxPos])
            
            if offLine > 1:
                textLoc = (0,1)
                xtremeObj = np.array(objsFluxAvgs).argmax()
            else:
                textLoc = (0,-8)
                xtremeObj = np.array(objsFluxAvgs).argmin()
        
            # Set the coordinate locations for horizontal line & annotated point
            # X-coordinates
            xMin = specData[xtremeObj].columns[0][xPos[xtremeObj][0]]
            xMax = specData[xtremeObj].columns[0][xPos[xtremeObj][1]]
            if annotation[0] == H2OH2:
                xMid = xMin + (xMax - xMin) / 3
            else:
                xMid = xMin + (xMax - xMin) / 2
            # Y-coordinate
            annotY = objsFluxAvgs[xtremeObj] * offLine
        
            txtCoords = 'offset points'
            annotLoc  = (xMid, annotY)
            
            # Some band annotations go on fixed locations
            if annotation[2] == 0:
                sign = 1
                ylims = subPlot.get_ylim()
                y_range = ylims[1] - ylims[0] 
                
                if annotation[0] == H2O or annotation[0] == H2OH2:
                    mult1 = 0.94
                    mult2 = 0.017
                elif annotation[0] == COH2O:
                    mult1 = 0.87
                    mult2 = 0.017
                elif annotation[0] == 'TiO':
                    mult1 = 0.930
                    mult2 = 0.007
                elif annotation[0] == 'CrH':
                    mult1 = 0.900
                    mult2 = 0.007
                elif annotation[0] == 'VO' and bandName == 'OPT':
                    mult1 = 0.640
                    mult2 = 0.007
                elif annotation[0] == 'VO' and bandName == 'J':
                    mult1 = 0.89
                    mult2 = 0.007
                elif annotation[0] == 'FeH':
                    mult1 = 0.080
                    mult2 = 0.039
                    sign = -1
                annotY = ylims[0] + y_range * mult1
                
                annotLoc = (xMid, annotY)
                txtCoords = 'data'
                textLoc = (xMid, annotY + sign * y_range * mult2)
            
            # Add horizontal line
            if annotation[0] == H2OH2:
                style = 'dashed'
            else:
                style = 'solid'
            subPlot.plot([xMin,xMax],[annotY,annotY], color='k', \
                         linestyle=style, linewidth=1, label='_ann')
                         
            # Add annotation
            subPlot.annotate(annotation[0], xy=annotLoc, \
                             xycoords='data', xytext=textLoc, \
                             textcoords=txtCoords, fontsize=TXT_SIZE, \
                             fontname='Times New Roman', ha='center')
        
        # <><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><>
        elif annotType == 'Doublet':  # Draw two vertical lines
        # For Doublet absorption: Add two annotations with vertial connectors
        # and a third invisible one in the center with name of annotation
            
            # Initialize variables
            objsFluxIdxs = [np.nan] * len(specData)
            objsFluxes   = [np.nan] * len(specData)
            
            # Find spectrum with highest/lowest flux @ doublet's first absorption wl
            for objIdx, objSpec in enumerate(specData):
                wlRange = np.where(objSpec.columns[0] <= annotation[1][0])
                if len(wlRange[0]) == 0:
                    objsFluxIdxs[objIdx] = 0
                else:
                    objsFluxIdxs[objIdx] = wlRange[0][-1]
                objsFluxes[objIdx] = objSpec.columns[1][objsFluxIdxs[objIdx]]
            
            if offLine > 0:
                xtremeObj = np.array(objsFluxes).argmax()
            else:
                xtremeObj = np.array(objsFluxes).argmin()
            
            # Set the coordinate location of the first annotated point
            loc1      = np.where(specData[xtremeObj].columns[0] <= annotation[1][0])
            annotLoc1 = (specData[xtremeObj].columns[0][loc1[0][-1]], \
                         specData[xtremeObj].columns[1][loc1[0][-1]])
            xycrds = 'data'
            txtLoc = (0, offText)
            
            # Add first annotation (with no text)
            subPlot.annotate(' ', xy=annotLoc1, xycoords=xycrds, xytext=txtLoc, \
                             textcoords='offset points', ha='center', \
                             arrowprops=annLineType)
            
            # Set the coordinate location of the second annotated point
            loc2      = np.where(specData[xtremeObj].columns[0] <= annotation[1][1])
            annotLoc2 = (specData[xtremeObj].columns[0][loc2[0][-1]], annotLoc1[1])
            xyrcds = 'data'
            txtLoc = (0, offText)
            
            # Add second annotation (with no text)
            subPlot.annotate(' ', xy=annotLoc2, xycoords=xycrds, xytext=txtLoc, \
                             textcoords='offset points', ha='center', \
                             arrowprops=annLineType)
            
            # Set the coordinate location of the third annotated point
            loc3center = (annotation[1][0] + annotation[1][1]) / 2
            loc3       = np.where(specData[xtremeObj].columns[0] <= loc3center)
            annotLoc3  = (specData[xtremeObj].columns[0][loc3[0][-1]], annotLoc1[1])
            xyrcds = 'data'
            txtLoc     = (0,offText*1.01)
            
            # Add third annotation
            subPlot.annotate(annotation[0], xy=annotLoc3, xycoords=xycrds, \
                             xytext=txtLoc, textcoords='offset points', \
                             fontsize=TXT_SIZE, fontname='Times New Roman', \
                             ha='center', arrowprops=annLineType2)
            
    return

def main(grav):
    
    import astropy.io.ascii as asc
    import numpy as np
    import matplotlib.pyplot as plt
    import pdb

    # Initialize variables --------------------------------------------------------
    with open("def_constants.py") as f:
        code = compile(f.read(), "def_constants.py", "exec")
        exec(code)
    
    SKIPL1 = True
    DELL_CHAR = '\t' # Delimiter character
    COMM_CHAR = '#'  # Comment character

    #grav = raw_input('Enter gravity (f, lg, g, b): ').lower()

    # Break down template sequence for plotting
    if grav == 'f':
        DIVISIONS = [0,5,9] # EDIT THIS ARRAY TO BREAK DOWN FIELD SEQUENCE
        TITLE = 'Field gravity'
        plotColors = colorSet[9]
        suffix = ''
    elif grav == 'lg':
        DIVISIONS = [0,5] # EDIT THIS ARRAY TO BREAK DOWN LOW-G SEQUENCE [0,3,6]
        TITLE = r'low gravity'
        if SKIPL1:
            plotColors = colorSet[5]
        else:
            plotColors = colorSet[6]
        suffix = 'low-g'
    elif grav == 'g':
        DIVISIONS = [0,5] # EDIT THIS ARRAY TO BREAK DOWN LOW-G SEQUENCE
        TITLE = r'$\gamma$ gravity'
        plotColors = colorSet[5]
        suffix = r'$\gamma$'
    elif grav == 'b':
        DIVISIONS = [0,2] # EDIT THIS ARRAY TO BREAK DOWN LOW-G SEQUENCE
        TITLE = r'$\beta$ gravity'
        plotColors = colorSet[2]
        suffix = r'$\beta$'

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
                tmpdata = asc.read(FOLDER_OUT_TMPL + filename, format='no_header', \
                                   delimiter=DELL_CHAR, comment=COMM_CHAR)
            except:
                tmpdata = []
            if len(tmpdata) != 0:
                data[band].append(tmpdata)
                if band == 'J':
                    labels.append(spType + suffix)
    
    # Plot templates --------------------------------------------------------------
    plotColorsPop = list(plotColors)
    for idiv in range(len(DIVISIONS) - 1):
        plt.close()
        plt.rc('font', size=8)
        fig = plt.figure(idiv, figsize=(6.5,2.8))
        plt.subplots_adjust(wspace=0.1, hspace=0.001, top=0.98, \
                            bottom=0.1, right=0.98, left=0.03)
        plt.clf()
        
        # Choose colors (colorSet defined in def_constants.py)
        numtempls = DIVISIONS[idiv+1] - DIVISIONS[idiv]
        if grav== 'lg' and (SKIPL1 and idiv == 0):
            numtempls = numtempls - 1
        tmpplotColors = []
        for ipop in range(0,numtempls):
            tmpplotColors.append(plotColorsPop.pop())
        
        for iband, band in enumerate(BANDS):
            ax = fig.add_subplot(131 + iband)
            
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
                ax.set_xlabel('Wavelength ($\mu$m)', labelpad=0)
            if iband == 0:
                ax.text(0.01, 0.82, TITLE, fontsize=11, transform=ax.transAxes)
                ax.text(0.01, 0.76, 'templates', fontsize=11, transform=ax.transAxes)
                ax.set_ylabel('Normalized Flux (F$_{\lambda}$)', labelpad=-1)
                lgd = ax.legend(handlelength=0, handletextpad=0.1, loc='upper left', \
                                bbox_to_anchor=(0,0.71), labelspacing=0.3, \
                                frameon=False, numpoints=1)
                for ilgdtxt,lgdtxt in enumerate(lgd.get_texts()):
                    plt.setp(lgdtxt, color=tmpplotColors[ilgdtxt])
            
            # Clean up axes
            ax.spines['left'].set_color('none')
            ax.spines['right'].set_color('none')
            ax.yaxis.set_ticks([])
            ax.set_ylim(ymax=ax.get_ylim()[1]*1.05)
            
            # Add annotations
            addannot(data[band], ax, band, 'L0')
        
        fig.savefig(FOLDER_OUT_PLT + 'sequence' + str(idiv) + '_' + grav + '.pdf', \
                    dpi=300)