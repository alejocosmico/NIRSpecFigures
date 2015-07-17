''' 
The main() procedure plots normalized spectral data in the Optical, J, H, and K bands
(sorted by J-K magnitudes) for a given spectral type OR for a specific object identified by its Uname.

NEEDED: 1) FILE_IN: ASCII tab-delimited txt file with data for each object
           (Access query is "nir_spex_prism_with_optical")
           (columns are specified under HDR_FILE_IN).
        2) FILE_IN_STD: ASCII tab-delimited txt file with data for standard NIR objects
           (columns are specified under HDR_FILE_IN_STD).
        3) EXCL_FILE: ASCII tab-delimite txt file with list of unums of objects to exclude
        4) FOLDER_ROOT: Folder containing all .fits files (which are stored in two folders: OPT and NIR.
        5) FOLDER_IN: Folder containing (1)-(3) above
        6) FOLDER_OUT: Folder to store output.

INPUT:  1) spInput: Spectral type to select (e.g. L0); it can also be a single object, identified by unum (e.g. U20268).
        2) grav: All young: y, Gamma: g, Beta: b, Field: f, All: leave blank.
        3) plot: Boolean, whether to plot result
        4) templ: Boolean, whether to return the average template spectrum
        5) std: Boolean, whether to return the NIR standard spectrum
        6) lbl: Boolean, whether to return the labels of the individual spectra
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
        ANNOT[4]  = ['Na I', 1.141,         25, 'Line']
        ANNOT[5]  = ['K I',  1.170,        -15, 'Line']
        ANNOT[6]  = ['VO',  (1.160,1.200),   0, 'Band']
        ANNOT[7]  = ['FeH', (1.194,1.239),   0, 'Band']
        ANNOT[8]  = ['K I',  1.250,        -15, 'Line']
        ANNOT[9]  = [r'Pa $\beta$', 1.280, -10, 'LineT']
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
        ANNOT[2] = [r'Br $\gamma$', 2.160, -15, 'LineT']
        ANNOT[3] = ['Na I',  2.210,        -10, 'Line']
        ANNOT[4] = [COH2O,  (2.293,2.390),   0, 'Band']
    
    # 3) Add annotation for each absorption feature
    for annotation in ANNOT:
        # Determine distances between annotated point and annotation's objects
        offLine = annotation[2]     # Distance betw. annotation line & plot
        if offLine > 0:
            offText = offLine + 10  # Distance betw. text & plot
        else:
            offText = offLine - 15
        
        # Create annotation line style
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
            
            if offLine >= 1:
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
                    mult1 = 0.94
                    mult2 = 0.015
                elif annotation[0] == COH2O:
                    mult1 = 0.88
                    mult2 = 0.015
                elif annotation[0] == 'TiO':
                    mult1 = 0.930
                    mult2 = 0.007
                elif annotation[0] == 'CrH':
                    mult1 = 0.900
                    mult2 = 0.007
                elif annotation[0] == 'VO':
                    mult1 = 0.74
                    mult2 = 0.01
                elif annotation[0] == 'FeH':
                    mult1 = 0.06
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
            txtLoc     = (0,offText*1.01)
            
            # Add third annotation
            subPlot.annotate(annotation[0], xy=annotLoc3, xycoords='data', \
                             xytext=txtLoc, textcoords='offset points', \
                             fontsize=TXT_SIZE, fontname='Times New Roman', \
                             ha='center', arrowprops=annLineType2)
            
    return


def plotspec(specData, bandNames, limits, objID, classType, grav=None, plotInstructions=None, figNum=1):
    # Plots set of spectral data and saves plots in a PDF file.
    # specData and limits must be dictionaries.
    
    import numpy as np
    import matplotlib as mpl
    import matplotlib.pyplot as plt
    import types
    import cubehelix
    import pdb
    
    # 1) Check data consistency ===============================================
    # Stop if specData or limits are not dictionaries
    try:
        specData.keys()
        limits.keys()
    except AttributeError:
        print('PLOTSPEC: Data not received as dictionaries.')
        return
    
    # 2) Initialize variables & color sets (hex codes) ========================
    cx = cubehelix.cmap(start=0.5, rot=-1.5, sat=1, gamma=1.5)
    BLACK = '#000000'
    GRAY  = '#666666'
    WHITE = '#FFFFFF'
    X_LABEL = 'Wavelength ($\mu$m)'
    Y_LABEL = 'Normalized Flux (F$_{\lambda}$)'
    
    # 3) Initialize Figure ====================================================
    plt.close()
    plt.rc('font', size=8)
    fig = plt.figure(figNum, figsize=(6.61417, 3.54)) # 168mm x 90mm (9,6))
    plt.clf()
    plt.subplots_adjust(wspace=0.1, top=0.98, bottom=0.1, right=0.98, left=0.03)
    
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
        if plotInstructions is not None:
            tmpFld  = np.where(np.array(plotInstructions) == 'field')
            tmpYng  = np.where(np.array(plotInstructions) == 'young')
            tmpStd  = np.where(np.array(plotInstructions) == 'standard')
            numFld  = len(tmpFld[0])
            numYng  = len(tmpYng[0])
            numStd  = len(tmpStd[0])
            specNum = numFld + numYng + numStd
        else:
            specNum  = len(filter(None, specData[band]))
        
        plotcolors = cx(np.linspace(0,1,specNum))
        cxmap = mpl.cm.coolwarm(np.linspace(0,1,specNum))
        plt.rc('axes', color_cycle=list(cxmap))
        
        # Legend is added when loop is for the J band
        if band == 'J':
            textColors = [] # For legend purposes only
        
        # 4c) Initialize Subplot ----------------------------------------------
        #subPlot = plt.figure(figNum).add_subplot(1,4,4 - bandIdx, \
        #                    position=[0.16 + (3 - bandIdx) * 0.21,0.1,0.19,0.83])
                                                       # [left,bottom,width,height]
        subPlot = plt.figure(figNum).add_subplot(1,3,3 - bandIdx)
        subPlot.set_autoscale_on(False)
        
        # Set figure and axes labels
        if grav == 'Y':
            plotType = ' young'
        elif grav == 'B':
            plotType = r'$\beta$'
        elif grav == 'G':
            plotType = r'$\gamma$'
        elif grav == 'F':
            plotType = ' field'
        else:
            plotType = ''
        
        title = classType
        if plotType != '':
            title = title + plotType
        
        if bandIdx == 1:
            subPlot.set_xlabel(X_LABEL) #, position=(1.1,0.08))
        if bandIdx == 2:
            subPlot.set_ylabel(Y_LABEL, labelpad=0)
            #subPlot.set_title(title, fontsize=17, fontweight='bold', \
            #                  position=(-0.01,0.88), ha='left')
        if band == 'J':
            tmpband = 'zJ'
        else:
            tmpband = band
        subPlot.set_title(tmpband, fontsize=16, fontstyle='italic', color=GRAY, \
                          position=(0.84, 0.07), transform=subPlot.transAxes, \
                          weight='heavy')
        
        # 4d) Determine order of spectra plotting -----------------------------
        zOrders = [None] * len(plotInstructions)
        countColor = specNum
        for plotIdx,plot in enumerate(plotInstructions):
            if plot == 'young' or plot == 'field' or plot == 'standard':
                zOrders[plotIdx] = specNum - countColor
                countColor = countColor - 1
            elif plot == 'template':
                zOrders[plotIdx] = specNum  # Template plotted on top of all others
        
        # 4e) Plot spectral data in Subplot -----------------------------------
        countColors = specNum - 1
        icolor = 0
        for specIdx, spec in enumerate(specData[band]):
            if spec is None:
                continue
            elif plotInstructions[specIdx] == 'exclude':
                continue
                
            # Set lines styles
            lnStyle = '-'
            if plotInstructions[specIdx] == 'template':
                lnWidth = 0.9
            else:
                lnWidth = 0.5
            
            # Identify particular objects in legends
            if plotInstructions[specIdx] == 'template':
                objLabel = title + ' ' + objID[specIdx]
                #objLabel = objID[specIdx] + '$\diamondsuit$'
            else:
                objLabel = objID[specIdx]
            
            # Consolidate color plot and legend designation
            clr = plotcolors[icolor]
            
            if plotInstructions[specIdx] == 'template':
                plotColor = BLACK
                legColor  = BLACK
            elif plotInstructions[specIdx] == 'young' or \
                        plotInstructions[specIdx] == 'field' or \
                        plotInstructions[specIdx] == 'standard':
                #plotColor   = plotColors[countColors] # Color for plot line
                #legColor    = plotColor               # Color for legend text
                countColors = countColors - 1
            
            #if band == 'J':
            #    textColors.append(legColor) # Colors for legend labels
            
            # Plot the damned thing
            subPlot.plot(spec[0], spec[1], linestyle=lnStyle, drawstyle='steps-mid', \
                         dash_joinstyle='round', linewidth=lnWidth, label=objLabel, \
                         zorder=zOrders[specIdx]) #,color=plotColor)
            
            # Track the highest & lowest y-axis values to fix y-axis limits later
            if plotInstructions[specIdx] != 'exclude':
                tmpMin = np.nanmin(spec[1])
                if tmpMin < minPlot:
                    minPlot = tmpMin
                tmpMax = np.nanmax(spec[1])
                if tmpMax > maxPlot:
                    maxPlot = tmpMax
        
        # 4f) Fix axes limits -------------------------------------------------
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
        
        # 4g) Customize y axis ------------------------------------------------
        subPlot.spines['left'].set_color('none')
        subPlot.spines['right'].set_color('none')
        subPlot.yaxis.set_ticks([])
        
        # 4h) Create and format legend (when loop is for J band) --------------
        # if band == 'J':
        #     objLegends = subPlot.legend(handlelength=0, handletextpad=0.1, \
        #                               loc='upper left', \
        #                               bbox_to_anchor=(-1.88,0.97), \
        #                               labelspacing=0.3, numpoints=1)
        #     objLegends.draw_frame(True)
        #
        #     for legendIdx, legendText in enumerate(objLegends.get_texts()):
        #         plt.setp(legendText, color=textColors[legendIdx], \
        #                  fontsize=7, fontname='Andale Mono')
        #
        #     # Add Titles for the legends
        #     legendTitles1 = 'Optical'
        #     legendTitles2 = 'Coords.   SpType   J-K'
        #     xCoord1 = -1.57
        #     xCoord2 = -1.79
        #     yCoord1 = 0.99
        #     yCoord2 = 0.964
        #     subPlot.text(xCoord1, yCoord1, legendTitles1, fontsize=7, \
        #                  transform=subPlot.transAxes)
        #     subPlot.text(xCoord2, yCoord2, legendTitles2, fontsize=7, \
        #                  transform=subPlot.transAxes)
        
        # 4i) Add absorption annotations to Subplots --------------------------
        # Sent to addannot only spectra plotted
        specsAnnot = []
        for idxSpec,spec in enumerate(specData[band]):
            if plotInstructions[idxSpec] != 'exclude':
                specsAnnot.append(spec)
        #addannot(filter(None, specsAnnot), subPlot, band, classType)
        addannot(specsAnnot, subPlot, band, classType)
    return fig


def main(spInput, grav='', plot=True, templ=False, std=False, lbl=False, normalize=True):
    
    # 1. LOAD RELEVANT MODULES ------------------------------------------------
    #import asciidata
    import astrotools as at
    import numpy as np
    import sys
    import pdb
    import matplotlib.pyplot as plt
    from astropy.io import ascii
    
    # 2. SET UP VARIABLES -----------------------------------------------------
    # Customizable variables <><><><><><><><><><><><><><><><><><><><><><><><><><><>
    FOLDER_ROOT = '/Users/alejo/Dropbox/Project_0/more data/'  # Location of NIR and OPT folders
    FOLDER_IN = '/Users/alejo/Dropbox/Project_0/data/' # Location of input files
    FOLDER_OUT = '/Users/alejo/Dropbox/Project_0/plots/' # Location to save output figures
    FILE_IN = 'nir_spex_prism_with_optical.txt' # ASCII file w/ data
    # <><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><>
    
    # For TXT objects list file
    HDR_FILE_IN = ('Ref','Designation`','J','H','K','SpType','SpType_T','NIRFobs',\
                   'NIRFtel','NIRfile','OPTobs','OPTtel','OPTinst','OPTfile',\
                   'Young?','Dusty?','Blue?','Binary?','Pec?')
    # For TXT standards file
    FILE_IN_STD = 'NIR_Standards.txt'   # ASCII file w/ standards
    HDR_FILE_IN_STD = ('Ref','Designation','NIR SpType','OPT SpType')
    colNameNIRS = HDR_FILE_IN_STD[2]
    colNameOPTS = HDR_FILE_IN_STD[3]
    
    # For TXT exclude-objects file
    EXCL_FILE = 'Exclude_Objs.txt'   # ASCII file w/ unums of objects to exclude
    
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
    BAND_LIMS['J']['lim'][0] = 0.8
    BAND_LIMS['J']['lim'][1] = 1.4 
    BAND_LIMS['H']['lim'][0] = 1.4
    BAND_LIMS['H']['lim'][1] = 1.9
    BAND_LIMS['K']['lim'][0] = 1.9
    BAND_LIMS['K']['lim'][1] = 2.4
    
    # Set wl limits for normalizing sections
    # Limits are in microns
    BAND_LIMS['OPT']['limN'][0] = 0.66
    BAND_LIMS['OPT']['limN'][1] = 0.89
    BAND_LIMS['J']['limN'][0] = 0.87
    BAND_LIMS['J']['limN'][1] = 1.39
    BAND_LIMS['H']['limN'][0] = 1.41
    BAND_LIMS['H']['limN'][1] = 1.89
    BAND_LIMS['K']['limN'][0] = 1.91
    BAND_LIMS['K']['limN'][1] = 2.39
    
    
    # 3. READ DATA FROM INPUT FILES -------------------------------------------
    DELL_CHAR = '\t' # Delimiter character
    COMM_CHAR = '#'  # Comment character
    
    # File with objects (source: query in Access)
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
    
    
    # 4. FORMAT SOME ASCII COLUMNS --------------------------------------------
    # 4.1 Convert into unicode the Spectral Type-Text column
    uniSpType = [None] * len(data[colNameType])
    for sIdx,sType in enumerate(data[colNameType]):
        uniSpType[sIdx] = sType#.decode('utf-8')
    data[colNameType] = np.array(uniSpType)
    
    # 4.2 Calculate J-K Color
    data[colNameJK] = data[colNameJ] - data[colNameK]
    
    # 4.3 Format Designation Number in Designation Column
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
    
    
    # 5. FILTER DATA BY USER INPUT IN spInput ---------------------------------
    uniqueSpec = False
    specIdx = []
    if spInput.upper().startswith('L'):
    # If input is a spectral type, then find all spectra of same spectral type
        for spIdx,spType in enumerate(data[colNameType]):
            if spType.upper().startswith(spInput.upper()):
                specIdx.append(spIdx)
        if not specIdx:
            print('No targets found for given input.')
            if std is False:
                return
        spTypeInput = spInput.upper()
    else:
    # If input is one single spectrum, then find it
        for spIdx,spType in enumerate(data[colNameRef]):
            if str(spType) == spInput.upper():
                specIdx.append(spIdx)
        if not specIdx:
            print('Requested target not found.')
            if std is False:
                return
        else:
            spTypeInput = data[colNameType][specIdx[0]][0:2]
            uniqueSpec = True
    
    # Find NIR standard target that matches user's spectral type
    stdIdx = []
    for spIdx,spType in enumerate(dataS[colNameNIRS]):
        if spType.upper().startswith(spTypeInput):
            stdIdx.append(spIdx)
    
    # Add NIR standard target to list of filtered objects if not there already
    # (It may not be included in first filter because OPT SpT != NIR SpT)
    if not uniqueSpec:
        if dataS[colNameNIRS][stdIdx] != dataS[colNameOPTS][stdIdx]:
            for spIdx,spRef in enumerate(data[colNameRef]):
                if spRef == dataS[colNameRef][stdIdx][0]:
                    if spIdx not in specIdx:
                        specIdx.append(spIdx)
    
    # Sort relevant objects by JKmag value
    specIdx = np.array(specIdx)
    specSortIdx = data[colNameJK][specIdx].argsort()
    
    
    # 6. READ SPECTRAL DATA FROM SPECTRAL FILES -------------------------------
    spectraRaw    = {}.fromkeys(OPTNIR_KEYS) # Used to store the raw data from fits files
    specFilesDict = {}.fromkeys(OPTNIR_KEYS) # Used for reference purposes
    
    for key in OPTNIR_KEYS:
        specFiles = [None] * len(specSortIdx)
        
        for sortIdx,specSort in enumerate(specSortIdx):
            if data[key + 'file'][specIdx[specSort]][-4:] == '.dat': continue
            if data[key + 'file'][specIdx[specSort]] == 'include': continue
            tmpFullName = FOLDER_ROOT + key + '/' + data[key \
                          + 'file'][specIdx[specSort]]
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
        print('No spectral data found for objects of the given spectral type.')
        if std is False:
            return
    
    # Convert spectraRaw contents into lists if only one spectral data
    # (This reduces the dimensions of the object holding the data)
    for key in spectraRaw.keys():
        if spectraRaw[key][0] is not None:
            if len(spectraRaw[key][0]) > 3:
                spectraRaw[key] = [spectraRaw[key],]
    
    
    # 7. GATHER OBJECTS' NAMES ------------------------------------------------
    # Filtered objects
    refs = [None] * len(specSortIdx)
    for idx,spIdx in enumerate(specSortIdx):
        tmpRef    = data[colNameRef][specIdx[spIdx]]
        refs[idx] = str(tmpRef)
    
    # Standard objects
    refsStd = [None] * len(dataS[colNameRef])
    for idx,spIdx in enumerate(dataS[colNameRef]):
        tmpRef       = dataS[colNameRef][idx]
        refsStd[idx] = str(tmpRef)
    
    # Gather reference numbers of objects
    objRef = data[colNameRef][specIdx[specSortIdx]]
    
    
    #8. SMOOTH SPECTRA --------------------------------------------------------
    # Smooth the flux data to a reasonable resolution
    spectraS = {}.fromkeys(OPTNIR_KEYS)
    tmpSpOPT = at.smooth_spec(spectraRaw['OPT'], specFile=specFilesDict['OPT'], \
                              winWidth=10)
    tmpSpNIR = at.smooth_spec(spectraRaw['NIR'], specFile=specFilesDict['NIR'], \
                              winWidth=0)
    
    spectraS['OPT'] = tmpSpOPT
    spectraS['NIR'] = tmpSpNIR
    
    
    # 9. SELECT SPECTRAL DATA FOR THE DIFFERENT BANDS -------------------------
    # Initialize variables
    spectra = {}.fromkeys(BANDS_NAMES)
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
            print('LIMITS for normalization changed!')
        if spectraN[bandKey] is None:
            break
    
    
    # 10. CHARACTERIZE TARGETS (i.e. identify young, blue, to exclude...) -----
    # Determine which targets to exclude
    # (source: file manually generated)
    toExclude = [False] * len(refs) # FORCE TO INCLUDE ALL TARGETS
    # dataExcl = ascii.read(FOLDER_IN + EXCL_FILE, data_start=0, delimiter=DELL_CHAR, \
    #                       comment=COMM_CHAR, names=['ID'])
    # if len(dataExcl['ID']) > 0:
    #     # Extract data from "Exclude_Objs" file
    #     excludeObjs = np.array(dataExcl['ID'], dtype='string')
    #
    #     # Find intersection of exclude-obj list and filtered targets list
    #     setExclude = set(excludeObjs).intersection(set(refs))
    #
    #     # Create list with intersection targets
    #     if len(setExclude) != 0:
    #         for exclIdx in setExclude:
    #             tmpExclIdx = np.where(np.array(refs) == exclIdx)
    #             toExclude[tmpExclIdx[0]] = True
    
    # Determine which target is the NIR Standard object
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
    
    # Determine which targets are blue
    blueObjs = [False] * len(refs)
    for idx,spIdx in enumerate(specIdx[specSortIdx]):
        if data[colNameBlue][spIdx].upper() == 'YES':
            blueObjs[idx] = True
    
    # Determine which targets are dusty
    dustyObjs = [False] * len(refs)
    for idx,spIdx in enumerate(specIdx[specSortIdx]):
        if data[colNameDust][spIdx].upper() == 'YES':
            dustyObjs[idx] = True
    
    # Determine which targets are binary
    binObjs = [False] * len(refs)
    for idx,spIdx in enumerate(specIdx[specSortIdx]):
        if data[colNameBin][spIdx].upper() == 'YES':
            binObjs[idx] = True
    
    # Determine which targets are peculiar
    pecObjs = [False] * len(refs)
    for idx,spIdx in enumerate(specIdx[specSortIdx]):
        if data[colNamePec][spIdx].upper() == 'YES':
            pecObjs[idx] = True
    
    # Determine which targets are young
    youngObjs = [False] * len(refs)
    for idx,spIdx in enumerate(specIdx[specSortIdx]):
        if data[colNameYng][spIdx].upper() == 'YES':
            youngObjs[idx] = True
    
    # Determine which targets are GAMMA
    gammaObjs = [False] * len(refs)
    for idx,spIdx in enumerate(specIdx[specSortIdx]):
        tmpType = data[colNameType][spIdx].encode('utf-8')
        tmpLen  = len(tmpType)
        utcA = tmpType[tmpLen - 2]
        utcB = tmpType[tmpLen - 1]
        # GAMMA in utf-8 code is "\xce\xb3"
        if utcA == '\xce' and utcB == '\xb3':
            gammaObjs[idx] = True
    
    # Determine which targets are BETA
    betaObjs = [False] * len(refs)
    for idx,spIdx in enumerate(specIdx[specSortIdx]):
        tmpType = data[colNameType][spIdx].encode('utf-8')
        tmpLen  = len(tmpType)
        utcA = tmpType[tmpLen - 2]
        utcB = tmpType[tmpLen - 1]
        # GAMMA in utf-8 code is "\xce\xb2"
        if utcA == '\xce' and utcB == '\xb2':
            betaObjs[idx] = True
    
    # Determine which targets to include in plots (based on user input)
    # Consolidate plotting & template-flux instructions
    grav = grav.upper()
    plotInstructions  = ['exclude'] * len(refs)
    templInstructions = [False] * len(refs)
    if grav == 'Y': # If plot request is Young, include gamma, beta & young targets
        for plotIdx in range(len(refs)):
            if toExclude[plotIdx]:
                continue
            if gammaObjs[plotIdx] or betaObjs[plotIdx] or youngObjs[plotIdx]:
                if blueObjs[plotIdx] or dustyObjs[plotIdx] or pecObjs[plotIdx] \
                                                           or binObjs[plotIdx]:
                    continue
                plotInstructions[plotIdx] = 'young'
                templInstructions[plotIdx] = True
    
    elif grav == 'G': # If plot request is Gamma, include only gamma targets
        for plotIdx in range(len(plotInstructions)):
            if toExclude[plotIdx]:
                continue
            if gammaObjs[plotIdx]:
                if blueObjs[plotIdx] or dustyObjs[plotIdx] or pecObjs[plotIdx] \
                                                           or binObjs[plotIdx]:
                    continue
                plotInstructions[plotIdx] = 'young'
                templInstructions[plotIdx] = True
    
    elif grav == 'B': # If plot request is Beta, include only beta targets
        for plotIdx in range(len(plotInstructions)):
            if toExclude[plotIdx]:
                continue
            if betaObjs[plotIdx]:
                if blueObjs[plotIdx] or dustyObjs[plotIdx] or pecObjs[plotIdx] \
                                                           or binObjs[plotIdx]:
                    continue
                plotInstructions[plotIdx] = 'young'
                templInstructions[plotIdx] = True
    
    elif grav == 'F': # If plot request is Field, include Field & Standard targets
        for plotIdx in range(len(plotInstructions)):
            if toExclude[plotIdx]:
                continue
            if betaObjs[plotIdx] or gammaObjs[plotIdx] or youngObjs[plotIdx]:
                continue
            #if blueObjs[plotIdx] or dustyObjs[plotIdx] or pecObjs[plotIdx] \
            #                                           or binObjs[plotIdx]:
            #    continue
            if stdObjs[plotIdx]:
                plotInstructions[plotIdx] = 'standard'
            else:
                plotInstructions[plotIdx] = 'field'
            templInstructions[plotIdx] = True
    
    else:   # Otherwise, print Field, gamma, beta, young & Standard targets
        for plotIdx in range(len(plotInstructions)):
            if toExclude[plotIdx]:
                continue
            if blueObjs[plotIdx] or dustyObjs[plotIdx] or pecObjs[plotIdx] \
                                                       or binObjs[plotIdx]:
                continue
            if youngObjs[plotIdx]:
                plotInstructions[plotIdx] = 'young'
            elif stdObjs[plotIdx]:
                plotInstructions[plotIdx] = 'standard'
            else:
                plotInstructions[plotIdx] = 'field'
            templInstructions[plotIdx] = True
    
    # If all plot instructions are "exclude", then stop procedure (for spectral types)
    allExcl = True
    for instr in plotInstructions:
        if instr != 'exclude':
            allExcl = False
    if allExcl:
        if std:
            return O_standard
        if not uniqueSpec:
            print('No spectral data to plot based on your request.')
            return
    
    
    # 11. CALCULATE TEMPLATE SPECTRA FOR SELECTED SET OF SPECTRA -----------------------
    # Gather spectra to use to calculate template spectrum
    # if not allExcl:
    #     O_template = [None] * 3 # Holds calculated template for output
    #     templCalculated = False
    #     for bandIdx, bandKey in enumerate(BANDS_NAMES):
    #         if bandKey == 'OPT':
    #             continue
    #
    #         templSpecs = []
    #         for spIdx, spex in enumerate(spectraN[bandKey]):
    #             if templInstructions[spIdx]:
    #                 # Check that spectrum exists
    #                 if spex is None:
    #                     templInstructions[spIdx] = False
    #                     continue
    #
    #                 if bandKey == 'OPT':
    #                     templSpecs.append(spex)
    #                 else:
    #                     # Check that spectrum comes with error values (NIR bands only)
    #                     notNansBool = np.isfinite(spex[2])
    #                     notNans     = np.any(notNansBool)
    #                     if notNans:
    #                         templSpecs.append(spex)
    #                     else:
    #                         print(str(objRef[spIdx]) + ' excluded from template')
    #
    #         # Calculate template spectrum
    #         if len(templSpecs) > 1:
    #             template = at.mean_comb(templSpecs)
    #             templCalculated = True
    #
    #             # Append template to list of spectra to plot in the next step
    #             spectraN[bandKey].append(template)
    #             # Append template to output object
    #             if bandIdx == 0:
    #                 tempIdx = 2
    #             elif bandIdx == 2:
    #                 tempIdx = 0
    #             else:
    #                 tempIdx = 1
    #             O_template[tempIdx] = template
    #
    #     if templCalculated:
    #         refs.append('template')
    #         plotInstructions.append('template')
    #     else:
    #         O_template = None
    
    
    # 12. PLOT DATA -----------------------------------------------------------
    if lbl or plot:
        # Gather info on each target
        objInfo = [None] * len(refs)
        for posIdx,spIdx in enumerate(specIdx[specSortIdx]):
            tmpDesig  = data[colNameDesig][spIdx]
            tmpJK     = data[colNameJK][spIdx]
            tmpSPtype = data[colNameType][spIdx]
            tmpSPtype = tmpSPtype + ' ' * (5 - len(tmpSPtype))  # For alignment purposes
            
            objInfo[posIdx] = (tmpDesig + ' ' + tmpSPtype + ' ' + '%.2f' %tmpJK)
        
        if objInfo[-1] is None:
            objInfo[-1] = 'template'
    if plot:
        # Create Figure with Subplots and Annotations
        tmpspectraN = {key:spectraN[key] for key in ['J','H','K']}
        tmpBANDS_NAMES = BANDS_NAMES[:-1]
        tmpBAND_LIMS = {key:BAND_LIMS[key] for key in ['J','H','K']}
        figObj = plotspec(tmpspectraN, tmpBANDS_NAMES, tmpBAND_LIMS, objInfo, \
                          spTypeInput, grav, plotInstructions)
        
        figObj.savefig(FOLDER_OUT + spTypeInput + grav + '.pdf', dpi=600)
    
    
    # 13. DETERMINE OUTPUT ----------------------------------------------------
    if templ:
        if std:
            return O_template, O_standard
        else:
            return O_template
    elif std:
        return O_standard
    else:
        if lbl:
            return spectraN, objInfo
        else:
            return spectraN
