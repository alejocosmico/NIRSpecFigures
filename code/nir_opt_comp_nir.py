''' 
The main() procedure plots normalized spectral data in the NIR band (sorted by J-K magnitudes) for a given spectral type.

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

OUTPUT: PDF file with four plots for selected spectral type.
'''

def addannot(specData, subPlot, classType):
    # Adds annotations to indicate spectral absorption lines
    
    import numpy as np
    from scipy.stats import nanmean
    
    # 1) Initialize strings
    BLACK = '#000000'
    GRAY  = '#666666'
    TXT_SIZE = 7
    H2O   = 'H' + '$\sf_2$' + 'O'
    COH2O = 'CO+' + H2O
    H2OH2 = H2O + ' + H' + '$\sf_2$' + ' CIA'
    EARTH = r'$\oplus$'
    
    # 2) Define the spectral lines to annotate
    ANNOT = [None] * 21
    ANNOT[0]  = [H2O,   (0.890,0.990),   0, 'Band']
    ANNOT[1]  = ['FeH', (0.980,1.017),   0, 'Band']
    ANNOT[2]  = ['VO',  (1.050,1.080),   0, 'Band']
    ANNOT[3]  = [H2O,   (1.090,1.200),   0, 'Band']
    ANNOT[4]  = ['Na I', 1.141,         25, 'Line']
    ANNOT[5]  = ['K I',  1.170,        -15, 'Line']
    ANNOT[6]  = ['VO',  (1.160,1.200),   0, 'Band']
    ANNOT[7]  = ['FeH', (1.194,1.239),   0, 'Band']
    ANNOT[8]  = ['K I',  1.250,        -15, 'Line']
    ANNOT[9]  = [r'Pa $\beta$', 1.280, -15, 'LineT']
    ANNOT[10] = ['normalization\nband', (1.27,1.33), 0, 'BandN'] #(1.28,1.32)
    ANNOT[11] = [H2O,   (1.310,1.390),   0, 'Band']

    ANNOT[12] = [H2O,   (1.410,1.510), 0, 'Band']
    ANNOT[13] = ['FeH', (1.583,1.750), 0, 'Band']
    ANNOT[14] = ['Br 14', 1.588,     -15, 'LineT']
    ANNOT[15] = [H2O,   (1.750,1.890), 0, 'Band']

    ANNOT[16] = [H2O,    (1.910,2.050),   0, 'Band']
    ANNOT[17] = [H2OH2,  (2.150,2.390),   0, 'Band']
    ANNOT[18] = [r'Br $\gamma$', 2.160, -15, 'LineT']
    ANNOT[19] = ['Na I',  2.210,        -10, 'Line']
    ANNOT[20] = [COH2O,  (2.293,2.390),   0, 'Band']
    
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
        elif annotType.startswith('Band'):  # Draw a horizontal line
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
                    mult1 = 0.85
                    mult2 = 0.01
                elif annotation[0] == 'FeH':
                    mult1 = 0.06
                    mult2 = 0.031
                    sign = -1
                elif annotation[0] == 'normalization\nband':
                    mult1 = 0.2
                    mult2 = 0.08
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
            if annotType == 'BandN':
                clr = GRAY
                lnwdth = 4
                txtstl = 'italic'
                txtnm = 'Helvetica'
            else:
                clr = BLACK
                lnwdth = 1
                txtstl = 'normal'
                txtnm = 'Times new Roman'
            subPlot.plot([xMin,xMax],[annotY,annotY], color=clr, \
                         linestyle=style, linewidth=lnwdth, label='_ann')
                         
            # Add annotation
            subPlot.annotate(annotation[0], xy=annotLoc, color=clr, \
                             xycoords='data', xytext=textLoc, \
                             textcoords=txtCoords, fontsize=TXT_SIZE, \
                             fontname=txtnm, ha='center', fontstyle=txtstl)
        
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
    
    import matplotlib.pyplot as plt
    import types
    import numpy as np
    import cubehelix
    import matplotlib as mpl
    
    # 2) Initialize variables & color sets ====================================
    cx = cubehelix.cmap(start=0.5, rot=-1.5, sat=1, gamma=1.5)
    BLACK = '#000000'
    GRAY  = '#999999'
    WHITE = '#FFFFFF'
    X_LABEL = 'Wavelength ($\mu$m)'
    Y_LABEL = 'Normalized Flux (F$_{\lambda}$)'
    
    # 3) Initialize Figure ====================================================
    plt.close()
    plt.rc('font', size=8)
    fig = plt.figure(figNum, figsize=(6.61417, 3.54)) # 168mm x 90mm (9,6))
    plt.clf()
    
    # 4) Generate Subplots ====================================================
    for bandIdx, band in enumerate(bandNames):
        
        # 4a) If band data is only one set, convert into array of sets --------
        if specData[band][0] is not None:
            if len(specData[band][0]) > 3:
                specData[band] = [specData[band],]
        
        # 4b) Initialize variables --------------------------------------------
        spLines  = []
        minPlot  = 1
        maxPlot  = 1
        
        # Count the number of plots in order to select color set
        if plotInstructions is not None:
            tmpFld  = np.where(np.array(plotInstructions) == 'field')
            tmpYng  = np.where(np.array(plotInstructions) == 'young')
            numFld  = len(tmpFld[0])
            numYng  = len(tmpYng[0])
            specNum = numFld + numYng
        else:
            specNum  = len(filter(None, specData[band]))
        
        plotcolors = cx(np.linspace(0,1,specNum))
        cxmap = mpl.cm.coolwarm(np.linspace(0,1,specNum))
        #plt.rc('axes', color_cycle=list(cxmap))
        
        # 4c) Initialize Subplot ----------------------------------------------
        # Determine position of Subplot
        multH = 0
        multV = 1
        
        gapHoriz   = 0.03
        gapVertic  = 0.04
        plotHeight = 0.9  # proportion of total height (11 inches)
        plotWidth  = 0.95  # proportion of total width (8.5 inches)
        edgeLeft   = 0.03 #+ (plotWidth + gapVertic) * multH
        edgeBottom = 0.08 #+ (plotHeight + gapHoriz) * multV
        plotLoc    = [edgeLeft, edgeBottom, plotWidth, plotHeight]
        
        subPlot = plt.figure(figNum).add_axes(plotLoc)
        
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
        
        subPlot.set_xlabel(X_LABEL, labelpad=0)
        subPlot.set_ylabel(Y_LABEL, labelpad=0)
        subPlot.set_title(title, fontsize=15, fontweight='bold', \
                          position=(0.01,0.75), ha='left')
        
        # 4d) Determine order of spectra plotting -----------------------------
        zOrders = [None] * len(plotInstructions)
        countColor = specNum
        for plotIdx,plot in enumerate(plotInstructions):
            zOrders[plotIdx] = specNum - countColor
            countColor = countColor - 1
        
        # 4e) Plot spectral data in Subplot -----------------------------------
        icolor = 0
        for specIdx, spec in enumerate(filter(None,specData[band])):
            if spec is None:
                continue
            if plotInstructions[specIdx] == 'exclude':
                continue
            
            # Determine line parameters
            lnWidth = 0.5
            objLabel  = objID[specIdx]
            clr = plotcolors[icolor]
            icolor = icolor + 1
            
            subPlot.plot(spec[0], spec[1], dash_joinstyle='round', \
                         linewidth=lnWidth, label=objLabel, \
                         drawstyle='steps-mid', zorder=zOrders[specIdx])
            
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
        maxOff = 0.1
        maxPlot = maxPlot + maxPlot * maxOff
        plt.ylim(ymin=minPlot, ymax=maxPlot)
        plt.xlim(xmin=limits[band]['lim'][0], \
                 xmax=limits[band]['lim'][1] * 1.001)
        
        # 4g) Customize y axis ------------------------------------------------
        subPlot.spines['left'].set_color('none')
        subPlot.spines['right'].set_color('none')
        subPlot.yaxis.set_ticks([])
        
        # Add colorbar manually
        ax1 = fig.add_axes([0.73, 0.7, 0.23, 0.04])
        cb1 = mpl.colorbar.ColorbarBase(ax1, orientation='horizontal', \
                            cmap=mpl.cm.coolwarm)
        cb1.dividers=False
        cb1.outline.set_edgecolor(WHITE)
        cb1.set_ticks((0.01,0.5,0.99))
        cb1.set_ticklabels(('1.1','1.45','1.8'))
        subPlot.text(0.861, 0.742, r'$J-K$', transform=subPlot.transAxes, ha='center')
        
        # objLegends = subPlot.legend(handlelength=0, handletextpad=0.1, \
        #                           loc='upper right', ncol=2, \
        #                           labelspacing=0.3, numpoints=1)
        # objLegends.draw_frame(True)
        #
        # for legendIdx, legendText in enumerate(objLegends.get_texts()):
        #     plt.setp(legendText, \
        #              fontsize=7, fontname='Andale Mono')
        
        # 4h) Add absorption annotations to Subplots
        addannot(specData[band], subPlot, classType)
        
    return fig


def main(spInput, grav=''):
    # 1. LOAD RELEVANT MODULES ---------------------------------------------------------
    import astrotools as at
    from astropy.io import ascii
    import matplotlib.pyplot as plt
    import numpy as np
    import sys
    import pdb
    
    
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
    
    OPTNIR_KEYS  = ['OPT', 'NIR']
    BAND_NAME  = ['NIR']
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
    BAND_LIMS = {}.fromkeys(BAND_NAME)
    for bandKey in BAND_NAME:
        BAND_LIMS[bandKey] = dict(lim = [None] * 2, limN = [None] * 2)
    
    # Set wl limits for band
    # Limits are in microns
    BAND_LIMS['NIR']['lim'][0] = 0.8
    BAND_LIMS['NIR']['lim'][1] = 2.4
    
    # Set wl limits for normalizing sections; this is the peak of the J band
    # Limits are in microns
    BAND_LIMS['NIR']['limN'][0] = 1.28
    BAND_LIMS['NIR']['limN'][1] = 1.32
    
    
    # 3. READ DATA FROM INPUT FILES ----------------------------------------------------
    DELL_CHAR = '\t' # Delimiter character
    COMM_CHAR = '#'  # Comment character
    
    # File with objects (source: query in Access)
    dataRaw = ascii.read(FOLDER_IN + FILE_IN, format='no_header', \
                         delimiter=DELL_CHAR, comment=COMM_CHAR, data_start=1)
    
    # Store data in a dictionary-type object
    data = {}.fromkeys(HDR_FILE_IN)
    for colIdx,colname in enumerate(dataRaw.colnames):
        data[HDR_FILE_IN[colIdx]] = np.array(dataRaw[colname])
    
    
    # 4. FORMAT SOME ASCII COLUMNS -----------------------------------------------------
    # 4.1 Convert into unicode the Spectral Type-Text column
    uniSpType = [None] * len(data[colNameType])
    for sIdx,sType in enumerate(data[colNameType]):
        uniSpType[sIdx] = sType#.decode('utf-8')
    
    data[colNameType] = np.array(uniSpType)
    
    # 4.2 Calculate J-K Color
    data[colNameJK] = data[colNameJ] - data[colNameK]
    
    # 4.3 Format Designation Number from Designation Column
    for desigIdx,desig in enumerate(data[colNameDesig]):
        desig = ''.join(desig.split())
        signType = '+'
        signPos = desig.find(signType)
        if signPos == -1:
            signType = '-'
            signPos  = desig.find(signType)
        
        desigProper = desig[:4] + signType + desig[signPos+1:signPos+5]
        data[colNameDesig][desigIdx] = desigProper
    
    
    # 5. FILTER DATA BY USER INPUT IN spInput ------------------------------------------
    # Find all spectra of same spectral type
    specIdx = []
    for spIdx,spType in enumerate(data[colNameType]):
        if spType.upper().startswith(spInput.upper()):
            specIdx.append(spIdx)
    
    if not specIdx:
        print('No target found for given input.')
        return
    spTypeInput = spInput.upper()
    
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
        return
    
    # Convert spectraRaw contents into lists if only one spectral data
    for key in spectraRaw.keys():
        if spectraRaw[key][0] is not None:
            if len(spectraRaw[key][0]) > 3:
                spectraRaw[key] = [spectraRaw[key],]
    
    
    # 7. GATHER OBJECTS' NAMES ---------------------------------------------------------
    # Filtered objects
    refs = [None] * len(specSortIdx)
    for idx,spIdx in enumerate(specSortIdx):
        tmpRef    = data[colNameRef][specIdx[spIdx]]
        refs[idx] = str(int(tmpRef))
    
    
    #8. SMOOTH SPECTRA -----------------------------------------------------------------
    # Smooth the flux data to a reasonable resolution
    spectraS = at.smooth_spec(spectraRaw['NIR'], specFile=specFilesDict['NIR'], \
                              winWidth=0)
    
    
    # 9. SELECT SPECTRAL DATA FOR NIR BAND --------------------------------------------
    # Initialize variables
    spectraN = {}.fromkeys(BAND_NAME)
    
    # Gather reference numbers of objects
    objRef = data[colNameRef][specIdx[specSortIdx]]
    
    # Select band
    spectra = at.sel_band(spectraS, BAND_LIMS['NIR']['lim'], objRef)
    
    # Normalize band
    spectraN['NIR'] = at.norm_spec(spectra, BAND_LIMS['NIR']['limN'])
    
    
    # 11. CHARACTERIZE TARGETS (i.e. identify young, blue, to exclude...) --------------
    # Force to include all targerts
    toExclude = [False] * len(refs)
    
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
    
    # Determine which targets are peculiar
    pecObjs = [False] * len(refs)
    for idx,spIdx in enumerate(specIdx[specSortIdx]):
        if data[colNamePec][spIdx].upper() == 'YES':
            pecObjs[idx] = True
    
    # Determine which plots are young objects
    youngObjs = [False] * len(refs)
    for idx,spIdx in enumerate(specSortIdx):
        if data[colNameYng][specIdx[spIdx]].upper() == 'YES':
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
    # Consolidate plotting instructions
    grav = grav.upper()
    plotInstructions = ['exclude'] * len(refs)
    if grav == 'Y': # If plot request is Young, include gamma, beta & young targets
        for plotIdx in range(len(refs)):
            if toExclude[plotIdx]:
                continue
            if gammaObjs[plotIdx] or betaObjs[plotIdx] or youngObjs[plotIdx]:
                if blueObjs[plotIdx] or dustyObjs[plotIdx] or pecObjs[plotIdx]:
                    continue
                plotInstructions[plotIdx] = 'young'
    
    elif grav == 'G': # If plot request is Gamma, include only gamma targets
        for plotIdx in range(len(plotInstructions)):
            if toExclude[plotIdx]:
                continue
            if gammaObjs[plotIdx]:
                if blueObjs[plotIdx] or dustyObjs[plotIdx] or pecObjs[plotIdx]:
                    continue
                plotInstructions[plotIdx] = 'young'
    
    elif grav == 'B': # If plot request is Beta, include only beta targets
        for plotIdx in range(len(plotInstructions)):
            if toExclude[plotIdx]:
                continue
            if betaObjs[plotIdx]:
                if blueObjs[plotIdx] or dustyObjs[plotIdx] or pecObjs[plotIdx]:
                    continue
                plotInstructions[plotIdx] = 'young'
    
    elif grav == 'F': # If plot request is Field, include Field & Standard targets
        for plotIdx in range(len(plotInstructions)):
            if toExclude[plotIdx]:
                continue
            if betaObjs[plotIdx] or gammaObjs[plotIdx] or youngObjs[plotIdx]:
                continue
            plotInstructions[plotIdx] = 'field'
    
    else:   # Otherwise, print Field, gamma, beta, young & Standard targets
        for plotIdx in range(len(plotInstructions)):
            if toExclude[plotIdx]:
                continue
            if blueObjs[plotIdx] or dustyObjs[plotIdx] or pecObjs[plotIdx]:
                continue
            if youngObjs[plotIdx]:
                plotInstructions[plotIdx] = 'young'
            else:
                plotInstructions[plotIdx] = 'field'
    
    # If all plot instructions are "exclude", then stop procedure
    allExcl = True
    for instr in plotInstructions:
        if instr != 'exclude':
            allExcl = False
    if allExcl:
        if not uniqueSpec:
            print('No spectral data to plot based on your request.')
            return
    
    
    # 11. PLOT DATA --------------------------------------------------------------------
    # Gather info on each object (for legend purposes)
    objInfo = [None] * len(refs)
    for posIdx,spIdx in enumerate(specIdx[specSortIdx]):
        tmpDesig  = data[colNameDesig][spIdx]
        tmpJK     = data[colNameJK][spIdx]
        tmpSPtype = data[colNameType][spIdx]
        tmpSPtype = tmpSPtype + ' ' * (5 - len(tmpSPtype))  # For alignment purposes
        
        objInfo[posIdx] = (tmpDesig + ' ' + tmpSPtype + ' ' + '%.2f' %tmpJK)
        
    # Create Figure with Subplots
    figObj = plotspec(spectraN, BAND_NAME, BAND_LIMS, objInfo, spTypeInput, grav, \
                        plotInstructions)
    
    figObj.savefig(FOLDER_OUT + spTypeInput + grav + '_fan.pdf', \
                   dpi=800)
