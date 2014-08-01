''' 
Plots each NIR young L template against all NIR field L templates using nir_opt_comp_strip.
'''
def plotspec(specData, bandNames, limits, objID, plotInstructions, compName, requestedColor, grav):
    
    # Plots set of spectral data and saves plots in a PDF file.
    # specData and limits must be dictionaries.
    
    import matplotlib.patches as mpatches
    import types
    
    # 1) Check data consistency ===============================================
    try:
        specData.keys()
    except AttributeError:
        print 'Spectra not received as dictionaries.'
        return
    try:
        limits.keys()
    except AttributeError:
        print 'Limits not received as dictionaries.'
        return
    
    # 2) Initialize variables and color sets to use in plots ==================
    GRAYS = ['#585858', '#686868', '#707070', '#808080', '#909090', \
             '#A0A0A0', '#B0B0B0', '#C0C0C0', '#D0D0D0', '#E0E0E0']
    X_LABEL = 'Wavelength ($\mu$m)'
    Y_LABEL = 'Normalized Flux (F$_{\lambda}$) + constant'
    if grav == 'lg':
        plttplbl = 'low'
    elif grav == 'g':
        plttplbl = r'$\gamma$'
    elif grav == 'b':
        plttplbl = r'$\beta$'
    youngName = compName + ' ' + plttplbl + ' grav.'
    
    # 3) Initialize Figure ====================================================
    plt.close()
    plt.rc('font', size=9)
    fig = plt.figure(1, figsize=(7.33,7.1))
    plt.clf()
    
    # 4) Generate Subplots ====================================================
    bandNames.reverse()
    for bandIdx, band in enumerate(bandNames):
        
        # 4.1) If band data is only one set, convert it into array of sets ----
        if specData[band][0] is not None:
            if len(specData[band][0]) > 6:
                specData[band] = [specData[band],]
        
        # 4.2) Initialize variables -------------------------------------------
        spLines = []
        minPlot = 1
        maxPlot = 1
        
        # 4.3) Initialize Subplot ---------------------------------------------
        tmpLeft = 0.06 + (2 - bandIdx) * 0.32
        subPlot = plt.figure(1).add_subplot(1,3,3 - bandIdx, \
                            position=[tmpLeft,0.07,0.265,0.91])
                                   # [left,bottom,width,height]
        subPlot.set_autoscale_on(False)
        
        # Create dummy axes instance to be able to later manipulate upper axis
#        ax2 = subPlot.axes.twiny()
        
        # Set figure and axes labels
        if bandIdx == 2:
            subPlot.set_xlabel(X_LABEL, position=(1.65,0.08), fontsize=10)
            subPlot.set_ylabel(Y_LABEL, fontsize=10)
        
        # 4.4) Plot spectra ---------------------------------------------------
        offset = 0
        for specIdx, spec in enumerate(specData[band]):
            plotType = plotInstructions[specIdx]
            objLabel = objID[specIdx]
            
            # Determine which field templates to highlight as similar to young ones
            similar = False # to indicate young template that resembles field one
            # if plotType == 'template':
            #     if compName == 'L0' and specIdx:
            #         if bandIdx == 0:
            #             if objLabel == 'L0':
            #                 similar = True
            #     elif compName == 'L2':
            #         if bandIdx == 0:
            #             if objLabel == 'L0' or objLabel == 'L1' or objLabel == 'L2':
            #                 similar = True
            #         elif bandIdx == 1:
            #             if objLabel == 'L7':
            #                 similar = True
            #     elif compName == 'L3':
            #         if bandIdx == 0:
            #             if objLabel == 'L1' or objLabel == 'L2' or objLabel == 'L3':
            #                 similar = True
            #         elif bandIdx == 2:
            #             if objLabel == 'L3' or objLabel == 'L4':
            #                 similar = True
            #     elif compName == 'L4':
            #         if bandIdx == 0:
            #             if objLabel == 'L1' or objLabel == 'L2' or objLabel == 'L3':
            #                 similar = True
            #         elif bandIdx == 1:
            #             if objLabel == 'L7':
            #                 similar = True
            #         elif bandIdx == 2:
            #             if objLabel == 'L4' or objLabel == 'L5':
            #                 similar = True
            
            # Define plot parameters
            lnStyle = '-'
            if plotType == 'field':
                plotColor = BLACK
                lnWidth = 0.7
            elif plotType == 'young':
                plotColor = requestedColor
                if similar:
                    lnWidth = 1.6
                else:
                    lnWidth = 1.2
            if specIdx > 0 and specIdx % 2 == 0:
                if bandIdx == 0:
                    offset = offset + 0.55
                elif bandIdx == 1:
                    offset = offset + 0.75
                else:
                    offset = offset + 1
            
            wls = np.array(spec[0])
            fluxes = np.array(spec[1])
            
            # Plot spectral strip when available
            if plotType == 'field' and len(spec) > 3:
                errs = np.array(spec[2])
                mins = np.array(spec[3])
                maxs = np.array(spec[4])
                
                for wlIdx, wl in enumerate(wls):
                    # Skip first and last points
                    if wlIdx == 0:
                        continue
                    elif wlIdx == len(wls) - 1:
                        continue
                    elif not np.isfinite(mins[wlIdx]):
                        continue
                    
                    # Set location of lower left corner of rectangle
                    rect_x = wl - ((wl - wls[wlIdx - 1]) / 2)
                    rect_y = mins[wlIdx] + offset
                    
                    # Set dimensions of rectangle
                    rect_width = ((wl - wls[wlIdx - 1]) / 2) + \
                                 ((wls[wlIdx + 1] - wl) / 2)
                    rect_height = maxs[wlIdx] - mins[wlIdx]
                    
                    rect_color = GRAYS[6]
                    
                    # Add rectangle to plot
                    rect_patch = mpatches.Rectangle(xy=(rect_x, rect_y), width=rect_width, \
                                                    height=rect_height, color=rect_color)
                    subPlot.add_patch(rect_patch)
            
            # Plot spectral lines
            subPlot.plot(wls, fluxes + offset, color=plotColor, linestyle=lnStyle, \
                    dash_joinstyle='round', linewidth=lnWidth, label=objLabel, \
                    drawstyle='steps-mid')
            
            # Plot a dummy line on secondary axis to later modify upper x-axis
#            if specIdx == 0:
#                ax2.plot(wls, [-0.5] * len(wls), color=WHITE)
                
            # Track the highest & lowest y-axis values to fix y-axis limits later            
            tmpMin = np.nanmin(fluxes)
            if tmpMin < minPlot:
                minPlot = tmpMin
            tmpMax = np.nanmax(fluxes + offset)
            if tmpMax > maxPlot:
                maxPlot = tmpMax
            
            # Track the highest y-axis value for the tail of each band
            if specIdx % 2 == 0:
                tailMax = np.nanmax(fluxes[-8:-1])
            else:
                currMax = np.nanmax(fluxes[-8:-1])
                if currMax > tailMax:
                    tailMax = currMax
            
            # Add annotation to template plot (skip H band)
            if bandIdx != 1 and specIdx % 2 == 0:
                textLoc = (0, 15)
                annotLoc = (wls[-10], tailMax + offset)
                annotTxt = objLabel
                subPlot.annotate(annotTxt, xy=annotLoc, xycoords='data', color=BLACK, \
                                 xytext=textLoc, textcoords='offset points')
                                
        # 4.5) Fix axes limits ------------------------------------------------
        minPlot = minPlot - minPlot * 0.1
        maxOff = 0.02
        maxPlot = maxPlot + maxPlot * maxOff
        
        plt.ylim(ymin=minPlot, ymax=maxPlot)
        subPlot.set_xlim(xmin=limits[band]['lim'][0], \
                         xmax=limits[band]['lim'][1] * 1.001)
#        ax2.set_xlim(xmin=limits[band]['lim'][0], \
#                         xmax=limits[band]['lim'][1] * 1.001)
        
        # 4.6) Customize y axis -----------------------------------------------
        subPlot.spines['left'].set_color('none')
        subPlot.spines['right'].set_color('none')
        subPlot.yaxis.set_ticks([])
        
        # 5) Add legend =======================================================
        if bandIdx == 2:
            xpos = 0.9 # in wavelength units
            ypos = 0.45 # in flux units
            xp = 0.3   # where 0 is left, 0.5 is middle, and 1 is right
            
            # add lines
            subPlot.axhline(y=ypos, xmin=xp, xmax=xp+0.09, color=BLACK)
            subPlot.axhline(y=ypos-0.18, xmin=xp, xmax=xp+0.09, color=plotColor)
            # add texts
            subPlot.text(xpos + 0.16, ypos - 0.05, 'field grav. templates', fontsize=8, color=BLACK)
            subPlot.text(xpos + 0.16, ypos - 0.23, youngName + ' template', fontsize=8, \
                         color=plotColor)
    
    return fig

# ============================= PROCEDURE =====================================

# 1. LOAD RELEVANT MODULES ----------------------------------------------------
import nir_opt_comp_strip as nocs
import asciidata as ad
import astrotools as at
import numpy as np
import matplotlib.pyplot as plt
import os
import pdb

execfile('def_constants.py')

# 2. SET UP VARIABLES ---------------------------------------------------------
DELL_CHAR = '\t' # Delimiter character
grav = raw_input('Enter young gravity (lg, g, b): ').lower()
if grav == 'lg':
    YOUNG_SPTYPES = ['L0', 'L1', 'L2', 'L3', 'L4']
    # Color order goes from reds to blues
    colors = colorSet[6]
elif grav == 'g' or grav == 'b':
    YOUNG_SPTYPES = ['L0', 'L1']
    colors = colorSet[2]
#COLORS = ['#FF0000','#FF6699','#FFCC33','#009933','#33CCFF','#0066FF']

# 3. LOOP THROUGH YOUNG NIR TEMPLATES -----------------------------------------
for ysptp in YOUNG_SPTYPES:
    # 3.1 Initialize structure to hold young template
    youngTempl = {}.fromkeys(BANDS)
    for band in BANDS:
        youngTempl[band] = []
    
    # 3.2 Read young template from ascii files (generated by make_templ.py)
    for bdIdx, band in enumerate(BANDS):
        fileNm = ysptp + band + '_' + grav + '.txt'
        templRaw = ad.open(FOLDER_OUT_TMPL + fileNm, delimiter=DELL_CHAR)
        templLs = np.array(templRaw).tolist()
        templRaw = ''
        youngTempl[band].append(templLs)
    
    # 3.3 Get field NIR templates
    spTypes = []
    spectra = {}.fromkeys(BANDS)
    for band in BANDS:
        spectra[band] = []
    
    # Choose which field templates to compare with
    if ysptp == 'L0' or ysptp == 'L1' or ysptp == 'L2':
        tmpsptypes = ['L0','L1','L2','L3','L4']
    elif ysptp == 'L3' or ysptp == 'L4':
        tmpsptypes = ['L1','L2','L3','L4','L5']
    #elif ysptp == 'L5':
    #    tmpsptypes = ['L2','L3','L4','L5','L6','L7']
    
    for idxTp, spTp in enumerate(tmpsptypes):
        # Attach copy of young template
        for bdIdx, band in enumerate(BANDS):
            spectra[band].append(youngTempl[band][0])
        
        # Read field template from ascii files (generated by make_templ.py)
        for bdIdx, band in enumerate(BANDS):
            fileNm = spTp + band + '_f.txt'
            templRaw = ad.open(FOLDER_OUT_TMPL + fileNm, delimiter=DELL_CHAR)
            templLs = np.array(templRaw).tolist()
            templRaw = ''
            spectra[band].append(templLs)
        
        # Append plot label list
        spTypes.append(ysptp)
        spTypes.append(tmpsptypes[idxTp])
    
    spTypes.reverse()
    for band in BANDS:
        spectra[band].reverse()
    
    # 3.4 Plot all templates
    plotInstructions = ['field','young'] * len(spTypes)
    pltColor = colors.pop()
    bndNames = list(BANDS)
    figure = plotspec(spectra, bndNames, BAND_LIMS, spTypes, plotInstructions, ysptp, pltColor, grav)
    
    plt.savefig(FOLDER_OUT_PLT + '/templates-' + ysptp + grav + '.pdf', dpi=300)