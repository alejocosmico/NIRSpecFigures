''' 
Plots each NIR young L template against all NIR field L templates using nir_opt_comp_strip.
'''
def plotspec(specData, bandNames, limits, objID, plotInstructions, compName, requestedColor, grav):
    
    # Plots set of spectral data and saves plots in a PDF file.
    # specData and limits must be dictionaries.
    
    import matplotlib.patches as mpatches
    import types
    
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
    plt.rc('font', size=8)
    fig = plt.figure(1, figsize=(6.5,6.5))
    plt.subplots_adjust(wspace=0.1, hspace=0.001, top=0.99, \
                        bottom=0.06, right=0.98, left=0.03)
    plt.clf()
    
    # 4) Generate Subplots ====================================================
    bandNames.reverse()
    for bandIdx, band in enumerate(bandNames):
        
        # 4.2) Initialize variables -------------------------------------------
        spLines = []
        minPlot = 1
        maxPlot = 1
        
        # 4.3) Initialize Subplot ---------------------------------------------
        subPlot = plt.figure(1).add_subplot(1,3,3 - bandIdx)
        subPlot.set_autoscale_on(False)
        
        # Set figure and axes labels
        if bandIdx == 2:
            subPlot.set_xlabel(X_LABEL, position=(1.65,0.08))
            subPlot.set_ylabel(Y_LABEL, labelpad=0)
        
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
            
            wls = np.array(spec.columns[0])
            fluxes = np.array(spec.columns[1])
            
            # Plot spectral strip
            if plotInstructions[specIdx] == 'field':
                errs = np.array(spec.columns[2])
                mins = np.array(spec.columns[3])
                maxs = np.array(spec.columns[4])
            
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
                    rect_patch = mpatches.Rectangle(xy=(rect_x, rect_y), \
                                                    width=rect_width, \
                                                    height=rect_height, \
                                                    color=rect_color)
                    subPlot.add_patch(rect_patch)
            
            # Plot spectral lines
            subPlot.plot(wls, fluxes + offset, color=plotColor, linestyle=lnStyle, \
                    dash_joinstyle='round', linewidth=lnWidth, label=objLabel, \
                    drawstyle='steps-mid')
            
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
        if grav == 'b':
            maxOff = 0.027
        else:
            maxOff = 0.01
        maxPlot = maxPlot + maxPlot * maxOff
        
        plt.ylim(ymin=minPlot, ymax=maxPlot)
        subPlot.set_xlim(xmin=limits[band]['lim'][0], \
                         xmax=limits[band]['lim'][1] * 1.001)
        
        # 4.6) Customize y axis -----------------------------------------------
        subPlot.spines['left'].set_color('none')
        subPlot.spines['right'].set_color('none')
        subPlot.yaxis.set_ticks([])
        
        # 5) Add legend =======================================================
        if bandIdx == 2:
            xp = 0. # where 0 is left, 0.5 is middle, and 1 is right
            yp = 0.983
            
            # add lines
            subPlot.plot((xp,xp+.05),(yp,yp), color=BLACK, transform=subPlot.transAxes)
            subPlot.plot((xp,xp+.05),(yp*.977,yp*.977), color=plotColor, \
                         transform=subPlot.transAxes)
            #subPlot.axhline(y=ypos, xmin=xp, xmax=xp+0.07, color=BLACK)
            #subPlot.axhline(y=ypos*.988, xmin=xp, xmax=xp+0.07, color=plotColor)
            # add texts
            subPlot.text(xp + 0.06, yp*.991, 'field grav. templates', \
                         color=BLACK, transform=subPlot.transAxes)
            subPlot.text(xp + 0.06, yp*.97, youngName + ' template', \
                         color=plotColor, transform=subPlot.transAxes)
    
    return fig

# ============================= PROCEDURE =====================================

# 1. LOAD RELEVANT MODULES ----------------------------------------------------
import nir_opt_comp_strip as nocs
import astropy.io.ascii as ad
import astrotools as at
import numpy as np
import matplotlib.pyplot as plt
import os
import pdb

with open("def_constants.py") as f:
    code = compile(f.read(), "def_constants.py", "exec")
    exec(code)

# 2. SET UP VARIABLES ---------------------------------------------------------
grav = input('Enter young gravity (lg, g, b): ').lower()
if grav == 'lg':
    YOUNG_SPTYPES = ['L0', 'L1', 'L2', 'L3', 'L4', 'L5']
    # Color order goes from reds to blues
    colors = colorSet[len(YOUNG_SPTYPES)]
elif grav == 'b':
    YOUNG_SPTYPES = ['L0', 'L1']
    colors = colorSet[len(YOUNG_SPTYPES)]
elif grav == 'g':
    YOUNG_SPTYPES = ['L0', 'L1', 'L2', 'L3', 'L4'] #, 'L5']
    colors = colorSet[len(YOUNG_SPTYPES)]

# 3. LOOP THROUGH YOUNG NIR TEMPLATES -----------------------------------------
for ysptp in YOUNG_SPTYPES:
    # 3.1 Initialize structure to hold young template
    youngTempl = {}.fromkeys(BANDS)
    for band in BANDS:
        youngTempl[band] = []
    
    # 3.2 Read young template from ascii files (generated by make_templ.py)
    for bdIdx, band in enumerate(BANDS):
        fileNm = ysptp + band + '_' + grav + '.txt'
        templRaw = ad.read(FOLDER_OUT_TMPL + fileNm, format='no_header', \
                           delimiter='\t')
        #templLs = np.array(templRaw).tolist()
        #templRaw = ''
        youngTempl[band].append(templRaw)
    
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
            templRaw = ad.read(FOLDER_OUT_TMPL + fileNm, delimiter='\t', \
                               format='no_header')
            #templLs = np.array(templRaw).tolist()
            #templRaw = ''
            spectra[band].append(templRaw)
        
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