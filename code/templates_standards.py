''' 
Plots the NIR Kirkpatrick L standards against the NIR L templates calculated using nir_opt_comp_strip.
'''
def plotspec(specData, bandNames, limits, objID, plotInstructions, figNum=1):
    # Plots set of spectral data and saves plots in a PDF file.
    # specData and limits must be dictionaries.
    
    #import numpy as np
    #import matplotlib.pyplot as plt
    import matplotlib.patches as mpatches
    import types
    
    # 2) Initialize variables and color sets to use in plots ==================
    GRAYS = ['#585858', '#686868', '#707070', '#808080', '#909090', \
             '#A0A0A0', '#B0B0B0', '#C0C0C0', '#D0D0D0', '#E0E0E0']
    # Color order goes from reds to blues
    colors = ['#FF0000','#990000','#FF6699','#CC9900','#FFCC33', \
              '#66FF33','#009933','#99FFFF','#33CCFF','#0066FF']
    colors = colorSet[9]
    colors.reverse()
    colors[0] = '#0000CC'
    #BLACK = '#000000'
    #GRAY  = '#CCCCCC'
    #WHITE = '#FFFFFF'
    #RED   = '#FF0000'
    X_LABEL = 'Wavelength ($\mu$m)'
    Y_LABEL = 'Normalized Flux (F$_{\lambda}$) + constant'
    
    # 3) Initialize Figure ====================================================
    plt.close()
    plt.rc('font', size=8)
    fig = plt.figure(figNum, figsize=(6.5,8))
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
        copyColors = list(colors)
        
        # 4.3) Initialize Subplot ---------------------------------------------
        subPlot = plt.figure(figNum).add_subplot(1,3,3 - bandIdx)
        subPlot.set_autoscale_on(False)
        
        # Set figure and axes labels
        if bandIdx == 2:
            subPlot.set_xlabel(X_LABEL, position=(1.65,0.08))
            subPlot.set_ylabel(Y_LABEL, labelpad=0)
        
        # 4.4) Plot spectra ---------------------------------------------------
        offset = 0
        for specIdx, spec in enumerate(specData[band]):
            if spec is None:
                continue
            
            # Define plot parameters
            plotType = plotInstructions[specIdx]
            lnStyle = '-'
            objLabel = objID[specIdx]
            if plotType == 'template':
                plotColor = BLACK
                lnWidth = 0.8
            elif plotType == 'standard':
                plotColor = copyColors.pop()
                lnWidth = 1.0
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
            if plotInstructions[specIdx] == 'template':
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
                    rect_patch = mpatches.Rectangle(xy=(rect_x, rect_y), \
                                                    width=rect_width, \
                                                    height=rect_height, \
                                                    color=rect_color)
                    subPlot.add_patch(rect_patch)
            
            # Plot spectral lines
            subPlot.plot(wls, fluxes + offset, color=plotColor, linestyle=lnStyle, \
                    dash_joinstyle='round', linewidth=lnWidth, label=objLabel, \
                    drawstyle='steps-mid')
            
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
            
            # Add annotation to template plot
            if specIdx % 2 == 1:
                textLoc = (0, 15)
                annotLoc = (wls[-10], tailMax + offset)
                #if objLabel != 'L9':
                annotTxt = objLabel
                #else:
                #    annotTxt = objLabel + '*'
                subPlot.annotate(annotTxt, xy=annotLoc, xycoords='data', color=BLACK, \
                                 xytext=textLoc, textcoords='offset points')
        
        # 4.5) Fix axes limits ------------------------------------------------
        minPlot = minPlot - minPlot * 0.1
        maxOff = 0.02
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
            xpos = 0.9 # in wavelength units
            ypos = 0.45 # in flux units
            xp = 0.3   # where 0 is left, 0.5 is middle, and 1 is right
            
            # add lines
            subPlot.axhline(y=ypos, xmin=xp, xmax=xp+0.18, color=BLACK)
            subPlot.axhline(y=ypos-0.18, xmin=xp, xmax=xp+0.03, color=colors[0])
            subPlot.axhline(y=ypos-0.18, xmin=xp+0.03, xmax=xp+0.06, color=colors[2])
            subPlot.axhline(y=ypos-0.18, xmin=xp+0.06, xmax=xp+0.09, color=colors[3])
            subPlot.axhline(y=ypos-0.18, xmin=xp+0.09, xmax=xp+0.12, color=colors[4])
            subPlot.axhline(y=ypos-0.18, xmin=xp+0.12, xmax=xp+0.15, color=colors[5])
            subPlot.axhline(y=ypos-0.18, xmin=xp+0.15, xmax=xp+0.18, color=colors[8])
            
            # add texts
            subPlot.text(xpos + 0.2, ypos - 0.05, 'Templates', fontsize=8, color=BLACK)
            subPlot.text(xpos + 0.2, ypos - 0.23, 'NIR Standards (K10)', fontsize=8, \
                         color=BLACK)
            #subPlot.text(xpos + 0.08, ypos - 0.4, '* L9 NIR standard vs L8 template', \
            #             fontsize=6, color=BLACK)
        
    return fig

# ============================= PROCEDURE =====================================

# 1. LOAD RELEVANT MODULES ----------------------------------------------------
import nir_opt_comp_strip as nocs
import astrotools as at
import astropy.io.ascii as ad
import numpy as np
import matplotlib.pyplot as plt
import pdb

with open("def_constants.py") as f:
    code = compile(f.read(), "def_constants.py", "exec")
    exec(code)

# 2. SET UP VARIABLES ---------------------------------------------------------
GRAV = 'f'
SPECIAL_H_NORM_LIM = [1.41,1.89] #[1.41, 1.81] these are the special values

# 3. GET SPECTRAL NIR STANDARDS & TEMPLATES -----------------------------------
spTypes = []
spectra = {}.fromkeys(BANDS)
for band in BANDS:
    spectra[band] = []

for idxTp, spTp in enumerate(SPTYPES):
    # Fetch standard
    tmpStd = nocs.main(spTp, GRAV, plot=False, std=True, normalize=False)
    # Normalize standard
    for bdIdx, band in enumerate(BANDS):
        if idxTp in [1,2,3] and band == 'H':
            norm_lims = SPECIAL_H_NORM_LIM
        else:
            norm_lims = NORM_LIMS[band]['lim']
        stdToPlot = at.norm_spec(tmpStd[bdIdx], norm_lims)[0]
        spectra[band].append(stdToPlot)
        #spectra[band].append(tmpStd[bdIdx])
    
    # Fetch template from ascii files generated by make_templ.py in templates/ folder.
    for bdIdx, band in enumerate(BANDS):
        fileNm = spTp + band + '_' + GRAV + '.txt'
        templRaw = ad.read(FOLDER_OUT_TMPL + fileNm, delimiter='\t', \
                           format='no_header')
        templRawToPlot = np.array([templRaw.columns[i] for i in range(5)])
        
        # Normalize when necessary
        if len(templRawToPlot) <= 3:
            if idxTp in [1,2,3] and band == 'H':
                norm_lims = SPECIAL_H_NORM_LIM
            else:
                norm_lims = NORM_LIMS[band]['lim']
            templToPlot = at.norm_spec(templRawToPlot, norm_lims)[0]
        else:
            templToPlot = templRawToPlot
        spectra[band].append(templToPlot)
    
    # Append plot label list
    spTypes.append(SPTYPES[idxTp])
    spTypes.append(SPTYPES[idxTp])

spTypes.reverse()
for band in BANDS:
    spectra[band].reverse()

# 4. PLOT ALL SPECTRA ---------------------------------------------------------
plotInstructions = ['template','standard'] * len(spTypes)

figure = plotspec(spectra, BANDS, BAND_LIMS, spTypes, plotInstructions)
                  
plt.savefig(FOLDER_OUT_PLT + '/templates-stds.pdf', dpi=300)