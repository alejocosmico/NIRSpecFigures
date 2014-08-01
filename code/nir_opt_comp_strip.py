''' 
The main() procedure plots normalized spectral data in the Optical, J, H, and K bands
(sorted by J-K magnitudes) for a given spectral type. It combines all spectra into an average template and a range strip. It can overplot excluded objects on top of the template & strip.

NEEDED: 1) FILE_IN: ASCII tab-delimited txt file with data for each object
           (Access query is "nir_spex_prism_with_optical")
           (columns are in HDR_FILE_IN).
        2) FILE_IN_STD: ASCII tab-delimited txt file with data for standard NIR objects
           (columns are in HDR_FILE_IN_STD).
        3) FOLDER_ROOT: Folder containing all .fits files (which are stored in two folders: OPT and NIR.
        4) FOLDER_IN: Folder containing (1)-(3) above
        5) FOLDER_OUT: Folder to store output.

INPUT:  1) spInput: String, spectral type to select (e.g. L0).
        2) grav:   string, Low: lg, Field: f, Gamma: g, Beta: b.
        3) plot: Boolean, whether to plot result
        4) templ: Boolean, whether to get the average template spectrum
        5) std: Boolean, whether to get the spectral type NIR standard spectrum
        6) excluded: Boolean, whether to overplot excluded objects
        7) normalize: Boolean, whether to normalize spectra or not. Used for standard spectrum really.

        
OUTPUT: 1) template (if templ=True) and NIR standard (if std=True)
           of selected spectra.
        2) (if plot=True) PDF file with four plots for selected spectral type.
'''

def addannot(specData, subPlot, bandName, classType):
# Adds annotations to indicate spectral absorption lines
    
    import numpy as np
    from scipy.stats import nanmean
    
    # 1) Initialize strings
    TXT_SIZE = 9
    H2O   = 'H' + '$\sf_2$' + 'O'
    COH2O = 'CO+' + H2O
    H2OH2 = H2O + ' + H' + '$\sf_2$' + ' CIA'
    EARTH = r'$\oplus$'
    
    # 2) Define the spectral lines to annotate
    if bandName == 'OPT':
        # Location exceptions of some annotations for some spectral types
        if classType == 'L0' or classType == 'L1' or classType == 'L8':
            offRb = 45
        else:
            offRb = 65
        if classType >= 'L5':
            offK = 25
        else:
            offK = 65
        
        ANNOT = [None] * 10
        # [Name, wavelength, offset of annotation from plot, type]
        # Offset: For Line/Doublet, if < 0 then annotation below line
        #         For Band, if < 1 then annotation below line
        ANNOT[0]  = ['VO',   (0.7300,0.7550),    0, 'Band']
        ANNOT[1]  = ['K I',  (0.7665,0.7699), offK, 'Doublet']
        ANNOT[2]  = ['Rb I', (0.7800,0.7948),   60, 'Doublet']
        ANNOT[3]  = ['VO',   (0.7850,0.8000),    0, 'Band']
        ANNOT[4]  = ['Na I', (0.8176,0.8200),   45, 'Doublet']
        ANNOT[5]  = ['TiO',  (0.8410,0.8550),    0, 'Band']
        ANNOT[6]  = ['Cs I',  0.8521,          -25, 'Line']
        ANNOT[7]  = ['CrH',  (0.8610,0.8780),    0, 'Band']
        ANNOT[8]  = ['FeH',  (0.8640,0.8744),    0, 'Band']
        ANNOT[9]  = ['Cs I',  0.8943,          -40, 'Line']
    
    elif bandName == 'J':
        ANNOT = [None] * 11
        ANNOT[0]  = [H2O,   (0.890,0.990),   0, 'Band']
        ANNOT[1]  = ['FeH', (0.980,1.017),   0, 'Band']
        ANNOT[2]  = ['VO',  (1.050,1.080),   0, 'Band']
        ANNOT[3]  = [H2O,   (1.090,1.200),   0, 'Band']
        ANNOT[4]  = ['Na I', 1.141,         25, 'Line']
        ANNOT[5]  = ['K I',  1.170,        -30, 'Line']
        ANNOT[6]  = ['VO',  (1.160,1.200),   0, 'Band']
        ANNOT[7]  = ['FeH', (1.194,1.239),   0, 'Band']
        ANNOT[8]  = ['K I',  1.250,        -25, 'Line']
        ANNOT[9]  = [r'Pa $\beta$', 1.280, -30, 'LineT']
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
        ANNOT[3] = ['Na I',  2.210,        -15, 'Line']
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
                wlRange = np.where(objSpec[0] <= annotation[1])
                if len(wlRange[0]) == 0:
                    objsFluxIdxs[objIdx] = 0
                else:
                    objsFluxIdxs[objIdx] = wlRange[0][-1]
                objsFluxes[objIdx] = objSpec[1][objsFluxIdxs[objIdx]]
            
            if offLine > 0:
                xtremeObj = np.array(objsFluxes).argmax()
            else:
                xtremeObj = np.array(objsFluxes).argmin()
            
            # Set the coordinate location for the annotated point
            annotWL  = specData[xtremeObj][0][objsFluxIdxs[xtremeObj]]
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
                xLoRange = np.where(objSpec[0] <= annotation[1][0])
                if len(xLoRange[0]) == 0:
                    xPos[objIdx,0] = objSpec[0][0]
                else:
                    xPos[objIdx,0] = xLoRange[0][-1]
                
                xHiRange = np.where(objSpec[0] >= annotation[1][1])
                if len(xHiRange[0]) == 0:
                    xPos[objIdx,1] = objSpec[0][-1]
                else:
                    xPos[objIdx,1] = xHiRange[0][0]
                    
                    # Set up limits of section with which to calculate average flux
                    firstxPos = xPos[objIdx,0]
                    lastxPos  = xPos[objIdx,1]
                
                objsFluxAvgs[objIdx] = nanmean(objSpec[1][firstxPos:lastxPos])
            
            if offLine > 1:
                textLoc = (0,1)
                xtremeObj = np.array(objsFluxAvgs).argmax()
            else:
                textLoc = (0,-8)
                xtremeObj = np.array(objsFluxAvgs).argmin()
        
            # Set the coordinate locations for horizontal line & annotated point
            # X-coordinates
            xMin = specData[xtremeObj][0][xPos[xtremeObj][0]]
            xMax = specData[xtremeObj][0][xPos[xtremeObj][1]]
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
                    mult1 = 0.948
                    mult2 = 0.01
                elif annotation[0] == COH2O:
                    mult1 = 0.900
                    mult2 = 0.01
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
                    mult1 = 0.820
                    mult2 = 0.007
                elif annotation[0] == 'FeH':
                    mult1 = 0.080
                    mult2 = 0.031
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
                wlRange = np.where(objSpec[0] <= annotation[1][0])
                if len(wlRange[0]) == 0:
                    objsFluxIdxs[objIdx] = 0
                else:
                    objsFluxIdxs[objIdx] = wlRange[0][-1]
                objsFluxes[objIdx] = objSpec[1][objsFluxIdxs[objIdx]]
            
            if offLine > 0:
                xtremeObj = np.array(objsFluxes).argmax()
            else:
                xtremeObj = np.array(objsFluxes).argmin()
            
            # Set the coordinate location of the first annotated point
            loc1      = np.where(specData[xtremeObj][0] <= annotation[1][0])
            annotLoc1 = (specData[xtremeObj][0][loc1[0][-1]], \
                         specData[xtremeObj][1][loc1[0][-1]])
            txtLoc = (0, offText)
            
            # Add first annotation (with no text)
            subPlot.annotate(' ', xy=annotLoc1, xycoords='data', xytext=txtLoc, \
                             textcoords='offset points', ha='center', \
                             arrowprops=annLineType)
            
            # Set the coordinate location of the second annotated point
            loc2      = np.where(specData[xtremeObj][0] <= annotation[1][1])
            annotLoc2 = (specData[xtremeObj][0][loc2[0][-1]], annotLoc1[1])
            txtLoc = (0, offText)
            
            # Add second annotation (with no text)
            subPlot.annotate(' ', xy=annotLoc2, xycoords='data', xytext=txtLoc, \
                             textcoords='offset points', ha='center', \
                             arrowprops=annLineType)
            
            # Set the coordinate location of the third annotated point
            loc3center = (annotation[1][0] + annotation[1][1]) / 2
            loc3       = np.where(specData[xtremeObj][0] <= loc3center)
            annotLoc3  = (specData[xtremeObj][0][loc3[0][-1]], annotLoc1[1])
            txtLoc     = (0,offText)
            
            # Add third annotation
            subPlot.annotate(annotation[0], xy=annotLoc3, xycoords='data', \
                             xytext=txtLoc, textcoords='offset points', \
                             fontsize=TXT_SIZE, fontname='Times New Roman', \
                             ha='center', arrowprops=annLineType2)
            
    return


def plotspec(specData, bandNames, limits, objID, classType, grav=None, plotInstructions=None, plotExcluded=False, figNum=1):
# Plots set of spectral data and saves plots in a PDF file.
# specData and limits must be dictionaries.
    
    import numpy as np
    import matplotlib.pyplot as plt
    import scipy.stats as sps
    
    import types
    import pdb
    
    # 1) Check data consistency ===============================================
    # Stop if specData or limits are not dictionaries
    try:
        specData.keys()
        limits.keys()
    except AttributeError:
        print 'PLOTSPEC: Data not received as dictionaries.'
        return
    
    # 2) Initialize variables & color sets (hex codes) ========================
    GRAYS = ['#585858', '#686868', '#707070', '#808080', '#909090', \
             '#A0A0A0', '#B0B0B0', '#C0C0C0', '#D0D0D0', '#E0E0E0']
    COLOR_SET = np.array(['#CC3333','#FF0000','#CC0000','#990000','#CC3300', \
                          '#FF3333','#FF6666','#FF3399','#CC0099','#FF0066', \
                          '#663300','#CC9900','#FFCC33','#666600','#669966', \
                          '#666666','#99CC99','#66CC99','#CCFF00','#66FF33', \
                          '#009933','#006600','#003300','#000066','#3333FF', \
                          '#33CCFF','#00FFFF','#9999FF','#3399CC','#0000CC'])
                # 0-plum, 1-red, 2-indian red, 3-maroon, 4-brick,
                # 5-tomato, 6-salmon, 7-fuchsia, 8-deep pink, 9-pink,
                # 10-brown, 11-chocolate, 12-wheat, 13-dk olive, 14-olive,
                # 15-silver, 16-lt green, 17-aquamarine, 18-yellow green, 19-lime,
                # 20-green, 21-forest, 22-dk green, 23-navy, 24-blue
                # 25-sky blue, 26-lt blue, 27-orchid, 28-steel blue, 29-royal blue
    
    colors = [None] * 31
    colors[30] = COLOR_SET.copy().tolist()
    colors[29] = COLOR_SET[[0,1,3,4,5,6,7,8,9,10,11,12,13,14,15,16,17,18, \
                            19,20,21,22,23,24,25,26,27,28,29]].tolist()
    colors[28] = COLOR_SET[[0,1,3,4,5,6,7,8,9,10,11,12,13,14,15,16,17,18, \
                            19,20,21,23,24,25,26,27,28,29]].tolist()
    colors[27] = COLOR_SET[[0,1,3,4,5,6,7,8,10,11,12,13,14,15,16,17,18, \
                            19,20,21,23,24,25,26,27,28,29]].tolist()
    colors[26] = COLOR_SET[[0,1,3,4,5,6,7,8,10,11,12,14,15,16,17,18, \
                            19,20,21,23,24,25,26,27,28,29]].tolist()
    colors[25] = COLOR_SET[[1,3,4,5,6,7,8,10,11,12,14,15,16,17,18, \
                            19,20,21,23,24,25,26,27,28,29]].tolist()
    colors[24] = COLOR_SET[[1,3,4,5,6,7,8,10,11,12,14,15,16,17,18, \
                            19,20,21,24,25,26,27,28,29]].tolist()
    colors[23] = COLOR_SET[[1,3,4,5,6,7,8,10,11,12,14,15,16,18, \
                            19,20,21,24,25,26,27,28,29]].tolist()
    colors[22] = COLOR_SET[[1,3,4,6,7,8,10,11,12,14,15,16,18, \
                            19,20,21,24,25,26,27,28,29]].tolist()
    colors[21] = COLOR_SET[[1,3,4,6,7,8,10,11,12,14,15,16,18, \
                            19,20,21,24,25,27,28,29]].tolist()
    colors[20] = COLOR_SET[[1,3,4,6,7,8,10,11,12,14,16,18, \
                            19,20,21,24,25,27,28,29]].tolist()
    colors[19] = COLOR_SET[[1,3,4,6,7,8,10,11,12,16,18, \
                            19,20,21,24,25,27,28,29]].tolist()
    colors[18] = COLOR_SET[[1,3,4,6,7,10,11,12,16,18, \
                            19,20,21,24,25,27,28,29]].tolist()
    colors[17] = COLOR_SET[[1,3,4,6,7,10,11,12,18,19,20,21,24,25,27,28,29]].tolist()
    colors[16] = COLOR_SET[[1,3,6,7,10,11,12,18,19,20,21,24,25,27,28,29]].tolist()
    colors[15] = COLOR_SET[[1,3,6,7,10,11,12,18,19,20,21,24,25,27,29]].tolist()
    colors[14] = COLOR_SET[[1,3,6,7,11,12,18,19,20,21,24,25,27,29]].tolist()
    colors[13] = COLOR_SET[[1,3,6,7,11,12,19,20,21,24,25,27,29]].tolist()
    colors[12] = COLOR_SET[[1,3,6,7,11,12,19,20,21,25,27,29]].tolist() 
    colors[11] = COLOR_SET[[1,3,6,11,12,19,20,21,25,27,29]].tolist()
    colors[10] = COLOR_SET[[1,6,11,12,19,20,21,25,27,29]].tolist()
    colors[9]  = COLOR_SET[[1,6,11,12,19,20,25,27,29]].tolist()
    colors[8]  = COLOR_SET[[1,6,11,12,19,20,25,29]].tolist()
    colors[7]  = COLOR_SET[[1,6,12,19,20,25,29]].tolist()
    colors[6]  = COLOR_SET[[1,6,12,20,25,29]].tolist()
    colors[5]  = COLOR_SET[[1,6,12,20,29]].tolist()
    colors[4]  = COLOR_SET[[1,12,20,29]].tolist()
    colors[3]  = COLOR_SET[[1,20,29]].tolist()
    colors[2]  = COLOR_SET[[1,29]].tolist()
    colors[1]  = COLOR_SET[[29]].tolist()
    BLACK = '#000000'
    GRAY  = GRAYS[6] #'#CCCCCC'
    DGRAY = GRAYS[0] #'#666666'
    WHITE = '#FFFFFF'
    BLUE = '#00FFFF'
    X_LABEL = 'Wavelength ($\mu$m)'
    Y_LABEL = 'Normalized Flux (F$_{\lambda}$)'
    
    # 3) Initialize Figure ====================================================
    plt.close()
    plt.rc('font', size=10)
    fig = plt.figure(figNum, figsize=(12,4.25))
    plt.clf()
    
    # 4) Generate Subplots ====================================================
    for bandIdx, band in enumerate(bandNames):
        
        # 4a) If band data is only one set, convert into array of sets --------
        if specData[band][0] is not None:
            if len(specData[band][0]) > 3:
                specData[band] = [specData[band],]
        
        # 4b) Initialize variables --------------------------------------------
        spLines = []
        minPlot = 1
        maxPlot = 1
        
        # Count the number of plots in order to select color set
        tmpSp = np.where(np.array(plotInstructions) == 'excluded')
        specNum = len(tmpSp[0])
        
        # Select color set based on count above
        if specNum > len(COLOR_SET):
            plotColors = colors[len(COLOR_SET)][:]
        elif specNum == 0:
            plotColors = None
        else:
            plotColors = colors[specNum][:]
        
        # Legend is added when loop is for the J band
        if band == 'J':
            textColors = [] # For legend purposes only
        
        # 4c) Initialize Subplot ----------------------------------------------
        subPlot = plt.figure(figNum).add_subplot(1,4,4 - bandIdx, \
                            position=[0.19 + (3 - bandIdx) * 0.205,0.1,0.18,0.83])
                                                       # [left,bottom,width,height]
        subPlot.set_autoscale_on(False)
        
        # Create dummy axes instance to be able to later manipulate upper axis
        # *This does not work properly as of latest matplotlib version (1.2.0)*
        # ax2 = subPlot.axes.twiny()
        
        # Set figure and axes labels
        if grav == 'lg':
            plotType = 'low'
        elif grav == 'f':
            plotType = 'field'
        elif grav == 'g':
            plotType = r'$\gamma$'
        elif grav == 'b':
            plotType = r'$\beta$'
        else:
            plotType = ''
        
        title1 = classType
        if plotType != '':
            title2 = plotType + ' gravity'
        if bandIdx == 2:
            subPlot.set_xlabel(X_LABEL, position=(1.1,0.08))
        if bandIdx == 3:
            subPlot.set_ylabel(Y_LABEL, position=(-0.04,0.5))
            subPlot.set_title(title1, fontsize=13, fontweight='bold', \
                              position=(0.01,0.92), ha='left')
            subPlot.text(0.01,0.885, title2, fontsize=12, transform=subPlot.transAxes)
            subPlot.text(0.01,0.835, 'templates', fontsize=12, transform=subPlot.transAxes)
            if plotExcluded:
                subPlot.text(0.01, 0.788, '& excluded', fontsize=11, \
                             transform=subPlot.transAxes)
                subPlot.text(0.01, 0.745, 'objects', fontsize=11, \
                             transform=subPlot.transAxes)
        
        # 4d) Determine order of spectra plotting -----------------------------
        zOrders = [None] * len(plotInstructions)
        countColor = specNum
        for plotIdx,plot in enumerate(plotInstructions):
            if plot == 'excluded':
                zOrders[plotIdx] = 10 + specNum - countColor
                countColor = countColor - 1
            elif plot == 'template':
                zOrders[plotIdx] = 10000 # Template plotted on top of all others
        
        # 4e) Fetch spectral strip --------------------------------------------
        # Pull wls, flux, min, max, and vars from template
        stripExists = True
        templIdx = np.where(np.array(plotInstructions) == 'template')[0][0]
        if templIdx.size != 0:
            if specData[band][templIdx] is not None:
                templWls = specData[band][templIdx][0]
                templFlux = specData[band][templIdx][1]
                templVar = specData[band][templIdx][2]
                templMin = specData[band][templIdx][3]
                templMax = specData[band][templIdx][4]
            else:
                stripExists = False
        else:
            stripExists = False
        
        # 4g) Plot STRIPS -----------------------------------------------------
        if stripExists:
            # Min-max strip
            subPlot.fill_between(templWls, templMin, templMax, facecolor=GRAY, \
                                 edgecolor='none', zorder=9)
            # 1-sigma strip
            if band != 'OPT':
                templSigmaLow = templFlux - np.sqrt(templVar)
                templSigmaUp = templFlux + np.sqrt(templVar)
                subPlot.fill_between(templWls, templSigmaLow, templSigmaUp, facecolor=DGRAY, \
                                     edgecolor='none', zorder=10)
        
        # 4h) Plot spectral LINES ---------------------------------------------
        countColors = specNum - 1
        for specIdx, spec in enumerate(specData[band]):
            if spec is None:
                continue
            
            plotInstr = plotInstructions[specIdx]
            if plotInstr == 'no':
                continue
            # Skip excluded objects if only template requested to be plotted
            if not plotExcluded and plotInstr == 'excluded':
                continue
            # Skip field/low-g objects if excluded objects are to be plotted
            if plotExcluded and (plotInstr != 'template' and plotInstr != 'excluded'):
                continue
            
            # Set lines styles
            lnStyle = '-'
            if plotInstr == 'template':
                lnWidth = 0.9 #1.1
            elif plotInstr == 'excluded':
                lnWidth = 0.5
            else:
                lnWidth = 0.1
            
            # Identify particular objects in legends
            if plotInstr == 'template':
                objLabel = ''
            else:
                objLabel = objID[specIdx]
            
            # Consolidate color plot and legend designation
            if plotInstr == 'template':
                plotColor = BLACK
                legColor  = DGRAY
                alpha     = 0.8
            elif plotInstr == 'excluded':
                plotColor   = plotColors[countColors] # Color for plot line
                legColor    = plotColor               # Color for legend text
                alpha       = 1.0
                countColors = countColors - 1
            else:
                plotColor = WHITE
                legColor = BLACK
                alpha = 0
            
            # Plot the damned thing
            if band == 'OPT' and plotInstr == 'template':
                continue
            if band == 'J':
                textColors.append(legColor) # Colors for legend labels
            
            # Manually skip drawing OPT spectrum of some specific targets, 
            # which use the same NIR fits file as both the OPT and NIR spectrum, 
            # so OPT spectrum is very bad
            if band == 'OPT':
                if objID[specIdx].startswith('0034-0706'):
                    continue
                elif objID[specIdx].startswith('0328+2302'):
                    continue
            
            subPlot.plot(spec[0], spec[1], color=plotColor, linestyle=lnStyle, \
                         dash_joinstyle='round', linewidth=lnWidth, \
                         label=objLabel, drawstyle='steps-mid', \
                         zorder=zOrders[specIdx], alpha=alpha)
            
            # Plot a dummy line on secondary axis to later modify upper x-axis
            # *Does not work properly as of latest matplotlib version*
            # if specIdx == 0:
            # ax2.plot(spec[0],[-0.5] * len(spec[0]), color=WHITE)
                
            # Track the highest & lowest y-axis values to fix y-axis limits later
            if plotInstr != 'no':
                tmpMin = np.nanmin(spec[1])
                if tmpMin < minPlot:
                    minPlot = tmpMin
                tmpMax = np.nanmax(spec[1])
                if tmpMax > maxPlot:
                    maxPlot = tmpMax
        
        # 4i) Fix axes limits -------------------------------------------------
        minPlot = minPlot - minPlot * 0.1
        if band == 'J':
            maxOff = 0.12
        elif band == 'K' and classType == 'L0' and grav == 'G':
            maxOff = 0.01
        else:
            maxOff = 0.07
        maxPlot = maxPlot + maxPlot * maxOff
        plt.ylim(ymin=minPlot, ymax=maxPlot)
        subPlot.set_xlim(xmin=limits[band]['lim'][0], \
                         xmax=limits[band]['lim'][1] * 1.001)
        # ax2.set_xlim(xmin=limits[band]['lim'][0], \
        #              xmax=limits[band]['lim'][1] * 1.001)
        
        # 4j) Customize y axis ------------------------------------------------
        subPlot.spines['left'].set_color('none')
        subPlot.spines['right'].set_color('none')
        subPlot.yaxis.set_ticks([])
        
        # 4k) Create and format legend (for J band only) ----------------------
        if band == 'J':
            objLegends = subPlot.legend(handlelength=0, handletextpad=0.1, \
                                      loc='upper left', \
                                      bbox_to_anchor=(-2.2,0.97), \
                                      labelspacing=0.3, numpoints=1)
            objLegends.draw_frame(True)
            
            for legendIdx, legendText in enumerate(objLegends.get_texts()):                
                plt.setp(legendText, color=textColors[legendIdx], \
                         fontsize=9, fontname='Andale Mono')
            
            # Add Titles for the legends
            legendTitles1 = 'Optical'
            legendTitles2 = 'Coords.   SpType      J-K'
            xCoord1 = -1.76
            xCoord2 = -2.03
            yCoord1 = 1.0
            yCoord2 = 0.964
            subPlot.text(xCoord1, yCoord1, legendTitles1, fontsize=9, \
                         transform=subPlot.transAxes)
            subPlot.text(xCoord2, yCoord2, legendTitles2, fontsize=9, \
                         transform=subPlot.transAxes)
        
        # 4l) Add absorption annotations to Subplots --------------------------
        # Sent to addannot only spectra plotted
        specsAnnot = []
        for idxSpec,spec in enumerate(specData[band]):
            if plotInstructions[idxSpec] != 'no':
                specsAnnot.append(spec)
        addannot(filter(None, specsAnnot), subPlot, band, classType)
    
    return fig


def main(spInput, grav='', plot=True, templ=False, std=False, excluded=False, normalize=True):
    # 1. LOAD RELEVANT MODULES ---------------------------------------------------------
    from astropy.io import ascii
    import astrotools as at
    import numpy as np
    import sys
    import os
    import pdb
    import matplotlib.pyplot as plt
    
    # 2. SET UP VARIABLES --------------------------------------------------------------
    # Customizable variables <><><><><><><><><><><><><><><><><><><><><><><><><><><>
    FOLDER_ROOT = '/Users/alejo/Dropbox/Project_0/more data/'  # Location of NIR and OPT folders
    FOLDER_IN = '/Users/alejo/Dropbox/Project_0/data/' # Location of input files
    FOLDER_OUT = '/Users/alejo/Dropbox/Project_0/plots/' # Location to save output figures
    FILE_IN = 'nir_spex_prism_with_optical.txt' # ASCII file w/ data
    # <><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><>
    
    # For TXT objects file (updatable here directly)
    HDR_FILE_IN = ('Ref','Designation`','J','H','K','SpType','SpType_T','NIRFobs',\
                   'NIRFtel','NIRfile','OPTobs','OPTtel','OPTinst','OPTfile',\
                   'Young?','Dusty?','Blue?','Binary?','Pec?')
    
    # For TXT standards file
    FILE_IN_STD = 'NIR_Standards.txt'   # ASCII file w/ standards
    HDR_FILE_IN_STD = ('Ref','Designation','NIR SpType','OPT SpType')
    colNameNIRS = HDR_FILE_IN_STD[2]
    colNameOPTS = HDR_FILE_IN_STD[3]
    
    OPTNIR_KEYS = ['OPT','NIR']
    BANDS_NAMES = ['K','H','J','OPT']
    data       = ''
    dataRaw    = ''
    specFiles  = ''
    spectraRaw = ''
    spectra    = ''
    
    colNameRef   = HDR_FILE_IN[0]
    colNameDesig = HDR_FILE_IN[1]
    colNameJ     = HDR_FILE_IN[2]
    colNameK     = HDR_FILE_IN[4]
    colNameJK    = 'J-K'
    colNameType  = HDR_FILE_IN[6]
    colNameNIRfile = HDR_FILE_IN[9]
    colNameYng   = HDR_FILE_IN[14]
    colNameDust  = HDR_FILE_IN[15]
    colNameBlue  = HDR_FILE_IN[16]
    colNameBin   = HDR_FILE_IN[17]
    colNamePec   = HDR_FILE_IN[18]
    
    # Initialize dictionary to store NIR bands limits and normalizing sections
    BAND_LIMS = {}.fromkeys(BANDS_NAMES)
    for bandKey in BANDS_NAMES:
        BAND_LIMS[bandKey] = dict(lim = [None] * 2, limN = [None] * 2)
    
    # Set wavelength limits for bands
    # Limits are in microns
    BAND_LIMS['OPT']['lim'][0] = 0.65
    BAND_LIMS['OPT']['lim'][1] = 0.90
    BAND_LIMS['J'  ]['lim'][0] = 0.8
    BAND_LIMS['J'  ]['lim'][1] = 1.4 
    BAND_LIMS['H'  ]['lim'][0] = 1.4
    BAND_LIMS['H'  ]['lim'][1] = 1.9
    BAND_LIMS['K'  ]['lim'][0] = 1.9
    BAND_LIMS['K'  ]['lim'][1] = 2.4
    
    # Set wl limits for normalizing sections
    # Limits are in microns
    BAND_LIMS['OPT']['limN'][0] = 0.66
    BAND_LIMS['OPT']['limN'][1] = 0.89
    BAND_LIMS['J'  ]['limN'][0] = 0.87
    BAND_LIMS['J'  ]['limN'][1] = 1.39
    BAND_LIMS['H'  ]['limN'][0] = 1.41
    BAND_LIMS['H'  ]['limN'][1] = 1.89
    BAND_LIMS['K'  ]['limN'][0] = 1.91
    BAND_LIMS['K'  ]['limN'][1] = 2.39
    
    
    # 3. READ DATA FROM MAIN INPUT FILE -------------------------------------------------
    DELL_CHAR = '\t' # Delimiter character
    COMM_CHAR = '#'  # Comment character
    
    # File with ALL objects (source: query in Access)
    dataRaw = ascii.read(FOLDER_IN + FILE_IN, format='no_header', \
                         delimiter=DELL_CHAR, comment=COMM_CHAR, data_start=1)
    
    # Store data in a dictionary-type object
    data = {}.fromkeys(HDR_FILE_IN)
    for colIdx,colname in enumerate(dataRaw.colnames):
        data[HDR_FILE_IN[colIdx]] = np.array(dataRaw[colname])
    
    # File with standards (source: manually generated)
    dataRawS = ascii.read(FOLDER_IN + FILE_IN_STD, data_start=0)
    
    # Store standard data in a dictionary-type object
    dataS = {}.fromkeys(HDR_FILE_IN_STD)
    for colIdx,colname in enumerate(dataRawS.colnames):
        dataS[HDR_FILE_IN_STD[colIdx]] = np.array(dataRawS[colname])
    
    
    # 4. FORMAT SOME ASCII COLUMNS -----------------------------------------------------
    # 4.1 Convert into unicode the Spectral Type-Text column
    uniSpType = [None] * len(data[colNameType])
    for sIdx,sType in enumerate(data[colNameType]):
        uniSpType[sIdx] = sType.decode('utf-8')
    data[colNameType] = np.array(uniSpType)
    
    # 4.2 Calculate J-K Color
    data[colNameJK] = data[colNameJ] - data[colNameK]
    
    # 4.3 Format Designation Number from Designation Column
    #     (From "XX XX XX.X +XX XX XX.X" to "XXXX+XXXX")
    for desigIdx,desig in enumerate(data[colNameDesig]):
        desig    = ''.join(desig.split())
        signType = '+'
        signPos  = desig.find(signType)
        if signPos == -1:
            signType = '-'
            signPos  = desig.find(signType)
        
        desigProper = desig[:4] + signType + desig[signPos+1:signPos+5]
        data[colNameDesig][desigIdx] = desigProper
    
    
    # 5. FILTER DATA BY USER INPUT IN spInput -------------------------------------------
    specIdx = []
    # Find all spectra of same spectral type
    for spIdx,spType in enumerate(data[colNameType]):
        if spType.upper().startswith(spInput.upper()):
            specIdx.append(spIdx)
    if not specIdx:
        print 'No targets found for given input.'
        if std is False:
            return
    spTypeInput = spInput.upper()
    
    # Find NIR standard target that matches user's spectral type
    stdIdx = []
    for spIdx,spType in enumerate(dataS[colNameNIRS]):
        if spType.upper().startswith(spTypeInput):
            stdIdx.append(spIdx)
    
    # Add NIR standard target to list of filtered objects if not there already
    # (It may not be included in first filter because OPT SpT != NIR SpT)
    if dataS[colNameNIRS][stdIdx] != dataS[colNameOPTS][stdIdx]:
        for spIdx,spRef in enumerate(data[colNameRef]):
            if spRef == int(dataS[colNameRef][stdIdx][0]):
                if spIdx not in specIdx:
                    specIdx.append(spIdx)
    
    # Sort relevant objects by JKmag value
    specIdx     = np.array(specIdx)
    specSortIdx = data[colNameJK][specIdx].argsort()
    
    
    # 6. READ SPECTRAL DATA FROM SPECTRAL FILES ----------------------------------------
    spectraRaw    = {}.fromkeys(OPTNIR_KEYS) # Used to store the raw data from fits files
    specFilesDict = {}.fromkeys(OPTNIR_KEYS) # Used for reference purposes
    
    for key in OPTNIR_KEYS:
        specFiles = [None] * len(specSortIdx)
        
        for sortIdx,specSort in enumerate(specSortIdx):
            if data[key + 'file'][specIdx[specSort]][-4:] == '.dat': continue
            if data[key + 'file'][specIdx[specSort]] == 'include': continue
            tmpFullName = FOLDER_ROOT + key + '/' + data[key + 'file'][specIdx[specSort]]
            specFiles[sortIdx] = tmpFullName
        specFilesDict[key] = specFiles
        
        spectraRaw[key] = at.read_spec(specFiles, atomicron=True, negtonan=True, \
                                       errors=True, verbose=False)
    
    # Clear out spectral data for objects missing either OPT or NIR data
    allNone = True
    for spIdx in range(0,len(spectraRaw['OPT'])):
        if spectraRaw['OPT'][spIdx] is None:
            spectraRaw['NIR'][spIdx] = None
        elif spectraRaw['NIR'][spIdx] is None:
            spectraRaw['OPT'][spIdx] = None
        else:
            allNone = False
    
    if allNone:
        print 'No spectral data found for objects of the given spectral type.'
        if std is False:
            return
    
    # Convert spectraRaw contents into lists if only one spectral data
    # (This reduces the dimensions of the object holding the data)
    for key in spectraRaw.keys():
        if spectraRaw[key][0] is not None:
            if len(spectraRaw[key][0]) > 3:
                spectraRaw[key] = [spectraRaw[key],]
    
    
    # 7. GATHER OBJECTS' NAMES ---------------------------------------------------------
    # Filtered objects
    refs = [None] * len(specSortIdx)
    NIRfilenames = [None] * len(specSortIdx)
    for idx,spIdx in enumerate(specSortIdx):
        tmpRef    = data[colNameRef][specIdx[spIdx]]
        refs[idx] = str(int(tmpRef))
        NIRfilenames[idx] = data[colNameNIRfile][specIdx[spIdx]]
    
    # Standard objects
    refsStd = [None] * len(dataS[colNameRef])
    for idx,spIdx in enumerate(dataS[colNameRef]):
        tmpRef       = dataS[colNameRef][idx]
        refsStd[idx] = str(int(tmpRef))
    
    # Gather reference numbers of objects
    objRef = data[colNameRef][specIdx[specSortIdx]]
    
    
    # 8. SMOOTH SPECTRA -----------------------------------------------------------------
    # Smooth the flux data to a reasonable resolution
    spectraS = {}.fromkeys(OPTNIR_KEYS)
    tmpSpOPT = at.smooth_spec(spectraRaw['OPT'], specFile=specFilesDict['OPT'], \
                              winWidth=10)
    tmpSpNIR = at.smooth_spec(spectraRaw['NIR'], specFile=specFilesDict['NIR'], \
                              winWidth=0)
    
    spectraS['OPT'] = tmpSpOPT
    spectraS['NIR'] = tmpSpNIR
    
    # 9. SELECT SPECTRAL DATA FOR THE DIFFERENT BANDS ----------------------------------
    # Initialize variables
    spectra  = {}.fromkeys(BANDS_NAMES)
    spectraN = {}.fromkeys(BANDS_NAMES)
    
    for bandKey in BANDS_NAMES:
        if bandKey == 'OPT':
            optNIR = 'OPT'
        else:
            optNIR = 'NIR'
        
        # Select band
        spectra[bandKey] = at.sel_band(spectraS[optNIR], BAND_LIMS[bandKey]['lim'], \
                                       objRef)
        if spectra[bandKey] is None:
            break
        
        # Normalize band
        spectraN[bandKey], flagN = at.norm_spec(spectra[bandKey], \
                                               BAND_LIMS[bandKey]['limN'], flag=True)
        if flagN:
            print bandKey + ' LIMITS for normalization changed!'
        if spectraN[bandKey] is None:
            break
    
    
    # 10. CHARACTERIZE TARGETS (i.e. identify young, field, and excluded) ---------------
    grav = grav.lower()
    toInclude = [False] * len(refs)
#    toInclude_LG = [False] * len(refs)
    toExclude = [False] * len(refs)
    dataIncl = []
#    dataIncl_LG = []
    dataExcl = []
    
    # 10.1 Extract NIR file names from "keepers" file
    fileslist = os.listdir(FOLDER_IN)
    inclFile = ''
    for fl in fileslist:
        if fl.find(spInput) != -1 and fl.find('keepers') != -1 and fl.find(grav) == 7:
            inclFile = fl
            break
    if inclFile != '':
        dataIncl = ascii.read(FOLDER_IN + inclFile, format='no_header', \
                              delimiter=DELL_CHAR, comment=COMM_CHAR)
    if len(dataIncl) > 0:
        includeObjs = np.array(dataIncl['col1']).astype(object)
        includeObjs = includeObjs + np.repeat('.fits', len(dataIncl))
        # Find intersection of include-obj list and filtered targets list
        setInclude = set(includeObjs).intersection(set(NIRfilenames))
        # Create list with intersection targets
        if len(setInclude) != 0:
            for inclIdx in setInclude:
                tmpInclIdx = np.where(np.array(NIRfilenames) == inclIdx)[0]
                toInclude[tmpInclIdx] = True
    
    # 10.2 Extract NIR file names from "rejects" file
    exclFile = ''
    for fl in fileslist:
        if fl.find(spInput) != -1 and fl.find('rejects') != -1 and fl.find(grav) == 7:
                exclFile = fl
                break
    if exclFile != '':
        try:
            dataExcl = ascii.read(FOLDER_IN + exclFile, format='no_header', \
                                  delimiter=DELL_CHAR, comment=COMM_CHAR)
        except:
            dataExcl = []
    if len(dataExcl) == 0 and excluded:
        print 'No objects found in REJECTS file. Nothing to plot.'
        return
    elif len(dataExcl) > 0:
        excludeObjs = np.array(dataExcl['col1']).astype(object)
        excludeObjs = excludeObjs + np.repeat('.fits', len(dataExcl))
        # Find intersection of exclude-obj list and filtered targets list
        setExclude = set(excludeObjs).intersection(set(NIRfilenames))
        # Create list with intersection targets
        if len(setExclude) != 0:
            for exclIdx in setExclude:
                tmpExclIdx = np.where(np.array(NIRfilenames) == exclIdx)[0]
                toExclude[tmpExclIdx] = True
    
    # 10.3 Determine which target is the NIR Standard object
    O_standard = [None] * 3 # Holds standard for output
    stdObjs = [False] * len(refs)
    for idx,spIdx in enumerate(specIdx[specSortIdx]):
        if data[colNameRef][spIdx] == dataS[colNameRef][stdIdx]:
            stdObjs[idx] = True
            
            if normalize:
                O_standard[0] = spectraN['J'][idx]
                O_standard[1] = spectraN['H'][idx]
                O_standard[2] = spectraN['K'][idx]
            else:
                O_standard[0] = spectra['J'][idx]
                O_standard[1] = spectra['H'][idx]
                O_standard[2] = spectra['K'][idx]
    
    # 10.4 Determine which targets to include in plots (based on user input)
    # Consolidate plotting & template-flux instructions
    plotInstructions  = ['no'] * len(refs)
    templInstructions = [False] * len(refs)
    if grav == 'f':
        plotinstlbl = 'field'
    elif grav == 'lg':
        plotinstlbl = 'low'
    elif grav == 'g':
        plotinstlbl = 'gamma'
    elif grav == 'b':
        plotinstlbl = 'beta'
    else:
        print 'Wrong gravity input.'
        return
    for plotIdx in range(len(refs)):
        if toInclude[plotIdx]:
            plotInstructions[plotIdx] = plotinstlbl
            templInstructions[plotIdx] = True
        if toExclude[plotIdx] and excluded:
            plotInstructions[plotIdx] = 'excluded'
    
    # If all plot instructions are "no", then stop procedure (for spectral types)
    allExcl = True
    for instr in plotInstructions:
        if instr != 'no':
            allExcl = False
    if allExcl:
        print 'No spectral data to plot based on your request.'
        return
    
    
    # 11. CALCULATE TEMPLATE SPECTRA FOR SELECTED SET OF SPECTRA -----------------------
    # Gather spectra to use to calculate template spectrum
    if not allExcl:
        O_template = [None] * 3 # Holds calculated template for output
        templCalculated = False
        for bandIdx, bandKey in enumerate(BANDS_NAMES):
            template = None
            templSpecs = []
            for spIdx, spex in enumerate(spectraN[bandKey]):
                if templInstructions[spIdx]:
                    # Check that spectrum exists
                    if spex is None:
                        templInstructions[spIdx] = False
                        continue
                    
                    if bandKey == 'OPT':
                        # Manually skip including OPT spectrum of some specific targets
                        # which use the same NIR fits file as both OPT and NIR spectrum, 
                        # so OPT spectrum is very bad
                        if refs[spIdx] == '50246':
                            continue
                        elif refs[spIdx] == '50061':
                            continue
                        elif refs[spIdx] == '50188':
                            continue
                        templSpecs.append(spex)
                    
                    else:
                        # Check that spectrum comes with error values (NIR bands only)
                        notNansBool = np.isfinite(spex[2])
                        notNans = np.any(notNansBool)
                        if notNans:
                            templSpecs.append(spex)
                        else:
                            print str(objRef[spIdx]) + ' excluded from template'
                            templInstructions[spIdx] = False
            
            # Calculate template spectrum using spec uncertainties as weights
            if len(templSpecs) > 1:
                if bandKey == 'OPT':
                    template = at.mean_comb(templSpecs, extremes=True)
                else:
                    template_first, renormSpecs = at.mean_comb(templSpecs, renormalize=True)
                    # Re-calculate template using re-normalized spectra
                    template = at.mean_comb(renormSpecs, extremes=True)
                
                # To calculate simple standard deviation, recalculate template without
                # any weights, and just use the simple variance that comes out of that.
                tmptempl = at.mean_comb(renormSpecs, forcesimple=True)
                template[2] = tmptempl[2].copy()
                templCalculated = True
            
            # Append template to list of spectra to plot in the next step
            if templCalculated:
                spectraN[bandKey].append(template)
                
                # Append template to output object
                if bandIdx == 0:
                    tempIdx = 2
                elif bandIdx == 2:
                    tempIdx = 0
                elif bandIdx == 1:
                    tempIdx = 1
                else:
                    tempIdx = None
                if tempIdx is not None:
                    O_template[tempIdx] = template
        
        if templCalculated:
            refs.append('template')
            plotInstructions.append('template')
        else:
            O_template = None
    
    
    # 12. PLOT DATA --------------------------------------------------------------------
    if plot:
        # Gather info on each target
        objInfo = [None] * len(refs)
        for posIdx,spIdx in enumerate(specIdx[specSortIdx]):
            tmpDesig  = data[colNameDesig][spIdx]
            tmpJK     = data[colNameJK][spIdx]
            
            # Append description of special object to its spectral type when missing
            spDesc = ''
            try:
                loc = data[colNameType][spIdx].index(spDesc)
            except ValueError:
                loc = None
            if loc is None:
                tmpSPtype = data[colNameType][spIdx] + spDesc
            else:
                tmpSPtype = data[colNameType][spIdx]
            tmpSPtype = tmpSPtype + ' ' * (8 - len(tmpSPtype)) # For alignment purposes
            
            objInfo[posIdx] = (tmpDesig + ' ' + tmpSPtype + ' ' + '%.2f' %tmpJK)
        
        if objInfo[-1] is None:
            objInfo[-1] = 'template' 
        
        # Create Figure with Subplots and Annotations
        figObj = plotspec(spectraN, BANDS_NAMES, BAND_LIMS, objInfo, spTypeInput, \
                          grav, plotInstructions, excluded)
    
    if plot:
        if excluded:
            sptxt = '_excluded'
        else:
            sptxt = ''
        figObj.savefig(FOLDER_OUT + spTypeInput + 'strip_' + \
                       grav + sptxt + '.pdf', dpi=300)
    
    
    # 13. DETERMINE OUTPUT -------------------------------------------------------------
    if templ:
        if std:
            return O_template, O_standard
        else:
            return O_template
    elif std:
        return O_standard
    else:
        return spectraN
