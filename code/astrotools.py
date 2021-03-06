# I ++++++++++++++++++++++ GENERAL DOCUMENTATION ++++++++++++++++++++++++++++++
'''
The module **astrotools** is a set of functions for astrophysical analysis developed by Kelle Cruz's team at Hunter College and the American Museum of Natural History in New York City. It consists of an amalgamation of functions tailored primordialy to handle fits file spectral data.

:Authors:
	Dan Feldman, Alejandro N |uacute| |ntilde| ez, Damian Sowinski, Jocelyn Ferrara

:Date:
    2012/08/24

:Repository:
    https://github.com/BDNYC/astrotools

:Contact: bdnyc.labmanager@gmail.com
     
:Requirements:
    The following modules should already be installed in your computer: `asciidata`_, `matplotlib`_, `numpy`_, `pyfits`_, and `scipy`_.

'''

# II ++++++++++++++++++++++++ EXTERNAL MODULES ++++++++++++++++++++++++++++++++
# External Python modules used by functions and classes

# Basic Python modules
import os
import pdb
import types

# Third party Python modules
import matplotlib
import matplotlib.pyplot as plt
import numpy as np
import astropy.io.fits as pf
import scipy.interpolate as spi
import scipy.ndimage as spn
import scipy.stats as sps

# III +++++++++++++++++++++++ PUBLIC FUNCTIONS ++++++++++++++++++++++++++++++++
# Functions meant to be used by end users of astrotools. Use only lower case characters to name functions.
def avg_flux(startW, endW, SpecData, median=False, verbose=True):
    '''
    (by Damian, Dan, & Jocelyn)
    
    Calculate the average (or median) flux value on a spectral
    wavelength range. The output is a list of two numpy float values containing
    either the average or median flux value in the provided wavelength
    range, and the standard deviation. If the uncertainty array is included in 
    SpecData (position 2), a weighted standard deviation for the average flux is 
    calculated. If not, the sample variance is used to estimate uncertainty.
    
    This function mimics IDL avgflux (by Kelle Cruz).
    
    *startW*
      The lower limit of the wavelength range.
    *endW*
      The upper limit of the wavelength range.
    *SpecData*
      Spectrum as a Python list or array with wavelength in position 0
      and flux in position 1. Optional: uncertainty in position 2.
    *median*
      Boolean: Find the median instead of the average.
    *verbose*
      Boolean: Print warning messages.
    
    '''
    
    Wavelength_big = SpecData[0]
    Flux_big = SpecData[1]
    
    if not(isinstance(Wavelength_big, np.ndarray)):
        Wavelength_big = np.array( Wavelength_big)
    if not(isinstance(Flux_big, np.ndarray)):
        Flux_big = np.array( Flux_big)
    
    if len(SpecData) >= 3:
        Sigma_big = SpecData[2]
        if not(isinstance(Sigma_big, np.ndarray)):
            Sigma_big = np.array( Sigma_big)
    
    # See if the wavelength range falls inside the wavelength array
    if np.min(Wavelength_big) > startW or np.max(Wavelength_big) < endW:
        if verbose == True:
            print('avg_flux: wavelength interval out of range')
        return
    # See that wavelength range does not fall between data points in 
    # wavelength array
    set1 = set(list(np.where( Wavelength_big >= startW)[0]))
    newEnd = endW + .0022
    set2 = set(list(np.where(Wavelength_big <= endW + .0022)[0]))
    temp = np.array(list(set1.intersection(set2)))
    if len(temp) == 0:
        if verbose == True:
            print('avg_flux: there is no data in the selected interval')
        return
    
    # Winds the pixel scale
    temp = np.where(Wavelength_big >= startW)[0]
    pix_scale = Wavelength_big[temp[0]+1] - Wavelength_big[temp[0]]
    
    # Find wavelengths in array that are in interval and make a new array
    set1 = set(list(np.where(Wavelength_big + pix_scale / 2 >= startW)[0]))
    set2 = set(list(np.where(Wavelength_big - pix_scale / 2 <= endW)[0]))
    # For some reason, temp1 may be slightly out of order, so sort it:
    temp1 = np.array(list(set1.intersection(set2)))
    temp  = np.sort(temp1)
    Wavelength = Wavelength_big[temp]
    Flux = Flux_big[temp]
    if len(SpecData) >= 3:
        Sigma = Sigma_big[temp]
    num_pixels = len(Wavelength)
    first = 0
    last = num_pixels - 1
    if num_pixels >= 1:
    # Determine fractional pixel value on the edge of the region
        frac1 = (Wavelength[first] + pix_scale / 2 - startW) / pix_scale
        frac2 = (endW - Wavelength[last] + pix_scale / 2) / pix_scale
        #sums the fluxes in the interval
        sumflux = 0
        sumsigma2 = 0
        for n in np.arange(first, num_pixels):
            if n == first:
                pixflux = frac1 * Flux[n]
            elif n == last:
                pixflux = frac2 * Flux[n]
            else:
                pixflux = Flux[n]
            sumflux = sumflux + pixflux
            
            if len(SpecData) >= 3:
                if n == first:
                    sigflux2 = frac1**2 * Sigma[n]**2
                if n == last:
                    sigflux2 = frac2**2 * Sigma[n]**2
                else:
                    sigflux2 = Sigma[n]**2
                sumsigma2 += sigflux2
        
        realpix = num_pixels - 2 + frac1 + frac2
        avgflux = sumflux / realpix
        
        #Use the sample variance if the sigma spectrum is not present
        #to estimate uncertainty
        if len(SpecData) >= 3:
            sigflux = np.sqrt(sumsigma2) / realpix
        else:
            elementdev = 0
            sumdev = 0
            for x in range(len(Flux)):
                elementdev = Flux[x] - np.mean(Flux)
                sumdev += elementdev**2
            sigflux = np.sqrt((sumdev)/(num_pixels-1)) \
                      / np.sqrt(num_pixels)
    
    else:
        frac = (endW - startW) / pix_scale
        avgflux = frac * Flux[0]
    
    if median == True and num_pixels > 5:
        if verbose == True:
            print('median worked')
        old = avgflux
        avgflux = np.median(Flux)
        
        if 100 * np.abs(avgflux - old) / old > 3:
            print('avg_flux: WARNING: difference between average and median ' \
                  & 'is greater than 3%')
            print('avg_flux: median = ' + str(avgflux) + ',\t' + ' average = ' \
                  + str(old))
            print('avg_flux: difference % = ' + \
                  str(100 * np.abs(avgflux - old) / old))
        else:
            if verbose == True:
                print('median worked')
        
    return [avgflux, sigflux]


def clean_outliers(data, thresh):
    '''
    (by Alejandro N |uacute| |ntilde| ez)
    
    Cleans a data from outliers by replacing them with numpy nans. A point *x* is identified as an outlier if \| *x* - *med* \| / *MAD* > *thresh*, where *med* is the median of the data values and *MAD* is the median absolute deviation, defined as 1.482 * median(\| *x* - *med* \|).
    
    This function mimics IDL mc_findoutliers (by Mike Cushing), with output differences.
    
    *data*
      Array with data values.
    *thresh*
      The sigma threshold that defines data outliers.
    '''
    # Check inputs
    try:
        data[0]
    except TypeError:
        print('Data invalid.')
        return
    
    # Calculate median and median absolute deviation
    med = sps.nanmedian(data)
    mad = 1.482 * sps.nanmedian(abs(data-med))
    
    dataClean = np.array(data).copy()
    if mad == 0:
        print('MAD is equal to zero.')
    else:
        outlierIdx = np.where(abs((dataClean - med) / mad) > thresh)
        if len(outlierIdx) != 0:
            dataClean[outlierIdx] = np.nan
    
    return dataClean


def create_ascii(listObj, saveto=None, delimiter='\t'):
    '''
    (by Alejandro N |uacute| |ntilde| ez)
    
    Save data from a Python list into an ascii file. It returns an asciidata type instance defined in the *ascii* module of astropy.
    
    *listObj*
        Python list object with data to be saved.
    *saveto*
        String with name for ascii file. If no full path is provided, ascii file is created in the current directory. If no name is provided, ascii file is not created, only asciidata type instance is returned. This file name does not need to include extension (e.g. ".txt").
    *delimiter*
        String specifying the delimiter desired for the ascii file. The default is *tab delimited*.
    '''
    import astropy.io.ascii as asc
    
    # Initialize variables
    DELIMITER = '\t'
    
    # Determine important parameters
    numCols = len(listObj)
    numRows = 0
    for col in listObj:
        if len(col) > numRows:
            numRows = len(col)
    
    # Create ascii table
    asciiObj = np.zeros((numRows, numCols))
    #asciiObj = ascii.create(numCols, numRows, delimiter=DELIMITER)
    
    # Populate the asciidata table
    for rowIdx in range(numRows):
    #for colIdx in range(asciiObj.ncols):
        for colIdx in range(numCols):
        #for rowIdx in range(len(listObj[colIdx])):
            asciiObj[rowIdx,colIdx] = listObj[colIdx][rowIdx]
    
    # Save file
    if saveto is not None:
        fileTp = '.txt'
        try:
            asc.write(asciiObj, saveto + fileTp, delimiter=DELIMITER, format='no_header')
            #asciiObj.writeto(saveto + fileTp)
        except IOError:
            print('Invalid name/location to save ascii file.')
    
    return asciiObj


def integrate(xyData):
    '''
    (by Damian)
    
    Integrate x and y data treating it as a scatter plot with the trapezoid rule. the output is a float number.
    
    *xyData*
        2-D array with x-data in position 0 and y-data in position 1, can be a Python list or a numpy array.
    '''
    
    try:
        if len(xyData) != 2:
            print('Cannot integrate, object does not have necessary parameters.')
            return 
        else:
            xData = xyData[1]
            yData = xyData[0]
            integral = 0.
            try:
                length = len(xData)
                for n in range (0, length - 1):
                    integral = integral + (xData[n + 1] - xData[n]) * \
                               (yData[n + 1] + yData[n]) * 0.5
            except ValueError:
                print('Data type cannot be integrated')
                return
    except TypeError:
        print('Cannot integrate.')
        return
    
    return integral


def mean_comb(spectra, mask=None, robust=None, forcesimple=False, extremes=False, renormalize=False):
    '''
    (by Alejandro N |uacute| |ntilde| ez)
    
    Combine spectra using a (weighted) mean. The output is a python list with mask wavelength in position 0, mean flux in position 1, and variance in position 2. If flux uncertainties are given, then mean is a weighted mean, and variance is the "variance of the mean" (|sigma|  :sub:`mean`  :sup:`2`). If no flux uncertainties are given, then mean is a straight mean (<x>), and variance is the square of the standard error of the mean (|sigma| :sup:`2`/n). If no mask is given, the wavelength array of the first spectrum will be used as mask.
    
    This function mimics IDL mc_meancomb (by Mike Cushing), with some restrictions.
    
    *spectra*
        Python list of spectra, where each spectrum is an array having wavelength in position 0, flux in position 1, and optional uncertainties in position 2.
    *mask*
      Array of wavelengths to be used as mask for all spectra. If none, then the wavelength array of the first spectrum is used as mask.
    *robust*
      Float, the sigma threshold to throw bad flux data points out. If none given, then all flux data points will be used.
    *forcesimple*
      Boolean, whether to calculate a straight mean and variance even if weights are available.
    *extremes*
      Boolean, whether to include the min and max flux values at each masked pixel.
    *renormalize*
      Boolean, whether to re-normalized the spectra agains the calculated combined spectrum, in which case the spectra will be returned in a list, with masked values.
    
    '''
    # Check inputs
    try:
        spectra[0]
    except TypeError:
        print('Spectra invalid.')
        return
    if mask is not None:
        try:
            mask[0]
        except TypeError:
            print('Mask invalid.')
            return
    if robust is not None:
        try:
            float(robust)
        except TypeError:
            print('Robust invalid.')
            return
    
    # 1. Generate mask using the first spectrum given
    if mask is None:
        # Use x-axis (i.e. wl) values of first spectrum as mask for all others
        wl_mask = spectra[0][0]
    else:
        wl_mask = mask
    numPoints = len(wl_mask)
    numSpec = len(spectra)
    
    # 2. Check if uncertainties were given
    uncsGiven = True
    if forcesimple:
        uncsGiven = False
    for spec in spectra:
        if uncsGiven:
            try:
                uncs = spec[2]
            except IndexError:
                uncsGiven = False
                continue
            nanIdx = np.where(np.isfinite(uncs))
            if len(nanIdx[0]) == 0:
                uncsGiven = False
    
    # 3D-array that will hold interpolated spectra
    # (it omits wavelength dimension, since all spectra have the same one)
    if uncsGiven:
        dims = 2
    else:
        dims = 1
    ip_spectra = np.zeros((numPoints, dims, numSpec)) * np.nan
    
    # 3. Interpolate spectra using mask
    for spIdx, spec in enumerate(spectra):
        wl = spec[0]
        fluxRaw= spec[1]
        if uncsGiven:
            unc = spec[2]
        
        # Eliminate outliers if requested
        if robust is not None:
            flux = clean_outliers(fluxRaw, robust)
        else:
            flux = fluxRaw
        
        if spIdx == 0:
            # No need to interpolate first spectrum
            flux_new = flux
            if uncsGiven:
                unc_new = unc
        else:
            ip_func_flux = spi.interp1d(wl, flux, bounds_error=False)
            flux_new = ip_func_flux(wl_mask.tolist())
            if uncsGiven:
                ip_func_unc = spi.interp1d(wl, unc, bounds_error=False)
                unc_new = ip_func_unc(wl_mask.tolist())
        
        ip_spectra[:,0,spIdx] = flux_new
        if uncsGiven:
            ip_spectra[:,1,spIdx] = unc_new
    
    # 4. Calculate mean and variance of flux values
    if uncsGiven:
        mvarraw = 1. / np.nansum(1. / ip_spectra[:,1,:], axis=1) # 1/Sum(1/sigma_i^2)
        wmean = np.nansum(ip_spectra[:,0,:] / ip_spectra[:,1,:], axis=1) # Sum(x_i/sigma_i^2)
        mean = wmean * mvarraw
        mvar = mvarraw
        # Correct weighted sample variance for small sample
        #meantile = np.tile(mean, (numSpec,1)).T
        #V1 = 1 / mvarraw
        #V2 = np.nansum(ip_spectra[:,1,:]**2, axis=1)
        #mvar = V1 / (V1**2 - V2) * \
        #       np.nansum((ip_spectra[:,0,:] - meantile)**2 / ip_spectra[:,1,:], axis=1)
    else:
        mvar = sps.nanstd(ip_spectra[:,0,:], axis=1) ** 2 # /numSpec -- I think I dont need this
        mean = sps.nanmean(ip_spectra[:,0,:], axis=1)
    
    # 5. Calculate extreme flux values if requested
    if extremes:
        minF = np.nanmin(ip_spectra[:,0,:], axis=1)
        maxF = np.nanmax(ip_spectra[:,0,:], axis=1)
    
    # 5. Create the combined spectrum
    if extremes:
        specComb = [wl_mask, mean, mvar, minF, maxF]
    else:
        specComb = [wl_mask, mean, mvar]
    
    # 6. Re-normalize spectra to calculated combined spectrum, if requested
    if renormalize:
        renorm_spectra = []
        for ispec in range(0, numSpec):
            tmpflux = ip_spectra[:,0,ispec]
            renormfac = np.median(tmpflux / mean) # mean is the flux of the combined spectrum
            if uncsGiven:
                tmpunc = ip_spectra[:,1,ispec]
                renorm_spectra.append([wl_mask, tmpflux / renormfac, tmpunc / renormfac])
            else:
                renorm_spectra.append([wl_mask, tmpflux / renormfac])
        
        return specComb, renorm_spectra
    else:
        return specComb


def norm_spec(specData, limits, flag=False):
    '''
    (by Alejandro N |uacute| |ntilde| ez)
    
    Normalize a spectrum using a band (i.e. a portion) of the spectrum specified by *limits*.
    
    *specData*
      Spectrum as a Python list with wavelength in position 0, flux in position 1, and (optional) error values in position 2. More than one spectrum can be provided simultaneously, in which case *specData* shall be a list of lists.
    *limits*
      Python list with lower limit in position 0 and upper limit in position 1. If more than one spectrum provided, these limits will be applied to all spectra.
    *flag*
      Boolean, whether to warn if normalization limits were shrinked in the case when they fall outside spectrum. If set to *True*, *norm_spec* returns the normalized spectra AND a boolean flag.
    '''
    
    # Convert specData to list or spectra if it consists only of one
    if len(specData) <= 3 and len(specData[0]) > 10:
        specData = [specData]
    
    # Initialize objects
    finalData = [None] * len(specData)
    
    # Check that given limits are reasonable
    if limits[0] >= limits[1]:
        print('norm_spec: the Min and Max values specified are not reasonable.')
        return None
    
    # Re-define normalizing band (specified in limits) for each spectrum in case
    # the limits fall outside of the spectrum range
    all_lims = [None] * len(specData)
    flagged = False
    for spIdx, spData in enumerate(specData):
        smallest = limits[0]
        largest  = limits[1]
        if spData is None:
            continue
        
        tmpNans = np.where(np.isfinite(spData[1]))
        if len(tmpNans[0]) != 0:
            if spData[0][tmpNans[0][0]] > smallest:
                smallest = spData[0][tmpNans[0][0]]
                flagged = True
            if spData[0][tmpNans[0][-1]] < largest:
                largest = spData[0][tmpNans[0][-1]]
                flagged = True
        
        all_lims[spIdx] = [smallest, largest]
    lims = [smallest, largest]
    
    # Loop through each spectral data set
    for spIdx, spData in enumerate(specData):
        
        # 1) Skip if data is missing
        if spData is None:
            continue
        
        # 2) Determine if spectra come with error values
        if len(spData) == 3:
            errors = True
        else:
            errors = False
        
        # 3) Determine minimum wavelength value for band
        smallIdx = np.where(spData[0] < all_lims[spIdx][0])
        
        # If lower limit < all values in spectrum wavelength points, then
        # make band's minimum value = first data point in spectrum
        try:
            smallIdx[0]
        except IndexError:
            minIdx = 0
            smallIdx = [None]
        
        # If lower limit > all values in spectrum wavelength points, then
        # no band can be selected
        if smallIdx != [None]:
            if len(smallIdx[0]) == len(spData[0]):
                print('norm_spec: the wavelength data for object is outside limits.' )
                continue
            else:
                minIdx = smallIdx[0][-1] + 1
        
        # 4) Determine maximum wavelength value for band
        largeIdx = np.where(spData[0] > all_lims[spIdx][1])
        
        # If upper limit > all values in spectrum wavelength points, then
        # make band's maximum value = last data point in spectrum
        try:
            largeIdx[0]
        except IndexError:
            maxIdx = len(spData[0])
            largeIdx = [None]
        
        # If upper limit < all values in spectrum wavelength points, then
        # no band can be selected
        if largeIdx != [None]:
            if len(largeIdx[0]) == len(spData[0]):
                print('norm_spec: the wavelength data for object is outside limits.')
                continue
            else:
                maxIdx = largeIdx[0][0]
        
        # 5) Check for consistency in the computed band limits
        if maxIdx - minIdx < 2:
            print('norm_spec: The Min and Max values specified yield no band.')
            continue
            
        # 6) Select flux band from spectrum
        fluxSelect = spData[1][minIdx:maxIdx]
        fluxSelect = np.array(fluxSelect)
        
        # 7) Select error value band from spectrum
        if errors is True:
            errorSelect = spData[2][minIdx:maxIdx]
            errorSelect = np.array(errorSelect)
        
        # 8) Normalize spectrum using arithmetic mean
        notNans = np.where(np.isfinite(fluxSelect))
        avgFlux = np.mean(fluxSelect[notNans])
        finalFlux = spData[1] / avgFlux
        
        finalData[spIdx] = [spData[0], finalFlux]
        
        if errors is True:
            #notNans  = np.where(np.isfinite(errorSelect))
            #avgError = np.mean(errorSelect[notNans])
            finalErrors = spData[2] / avgFlux
            
            finalData[spIdx] = [spData[0], finalFlux, finalErrors]
    
    if flag:
        return finalData, flagged
    else:
        return finalData


def plot_spec(specData, ploterrors=False):
    '''
    (by Alejandro N |uacute| |ntilde| ez)
    
    Plot a spectrum. If more than one spectrum is provided simultaneously, it will plot all spectra on top of one another.
    
    This is a quick and dirty tool to visualize a set of spectra. It is not meant to be a paper-ready format. You can use it, however, as a starting point.
    
    *specData*
      Spectrum as a Python list with wavelength in position 0, flux in position 1, and (optional) error values in position 2. More than one spectrum can be provided simultaneously, in which case *specData* shall be a list of lists.
    *ploterrors*
      Boolean, whether to include flux error bars when available. This will work only if all spectra have error values.
    
    '''
    
    # Check that there is data to plot
    allNone = True
    for spData in specData:
        if spData is not None:
            allNone = False
            break
    if allNone:
        return
    
    # Fix specData list dimensions when necessary
    if len(specData) == 2 or len(specData) == 3:
        if len(specData[0]) > 3:
            specData = [specData]
    
    # Initialize figure
    plt.close()
    fig = plt.figure(1)
    fig.clf()
    
    # Set plot titles
    TITLE   = 'SPECTRAL DATA'
    X_LABEL = 'Wavelength'
    Y_LABEL = 'Flux'
    
    # Initialize plot within figure
    subPlot = fig.add_subplot(1,1,1)
    subPlot.set_title(TITLE)
    subPlot.set_xlabel(X_LABEL)
    subPlot.set_ylabel(Y_LABEL)
    
    # Check if all spectra have error values
    errorsOK = True
    for spData in specData:
        if len(spData) != 3:
            errorsOK = False
    
    # Plot spectra
    for spData in specData:
        if spData is not None:
            if errorsOK and ploterrors:
                subPlot.errorbar(spData[0], spData[1], spData[2], \
                          capsize=2)
            else:
                subPlot.plot(spData[0], spData[1], drawstyle='steps-mid')
    
    return fig


def read_spec(specFiles, errors=True, atomicron=False, negtonan=False, plot=False, linear=False, templ=False, verbose=True):
    '''
    (by Alejandro N |uacute| |ntilde| ez, Jocelyn Ferrara)
    
    Read spectral data from fits or ascii files. It returns a list of numpy arrays with wavelength in position 0, flux in position 1 and error values (if requested) in position 2. More than one file name can be provided simultaneously.
    
    **Limitations**: Due to a lack of set framework for ascii file headers, this function assumes ascii files to have wavelength in column 1, flux in column 2, and (optional) error in column 3. Ascii spectra are assumed to be linear, so the kwarg *linear* is disabled for ascii files. Fits files that have multiple spectral orders will not be interpreted correctly with this function.
    
    *specFiles*
      String with fits file name (with full path); it can also be a python list of file names.
    *errors*
      Boolean, whether to return error values for the flux data; return nans if unavailable.
    *atomicron*
      Boolean, if wavelength units are in Angstrom, whether to convert them to microns.
    *negtonan*
      Boolean, whether to set negative flux values equal to zero.
    *plot*
      Boolean, whether to plot the spectral data, including error bars when available.
    *linear*
      Boolean, whether to return spectrum only if it is linear. If it cannot verify linearity, it will assume linearity.
    *templ*
      Boolean, whether data to extract is of a template spectrum, which means it includes avg flux, flux variance, min and max flux at each wavelength.
    *verbose*
      Boolean, whether to print warning messages.
    '''
    
    # 1. Convert specFiles into a list type if it is only one file name
    if isinstance(specFiles, str):
        specFiles = [specFiles,]
    
    try:
        specFiles[0]
    except TypeError:
        print('File name(s) in invalid format.')
        return
    
    # 2. Initialize array to store spectra
    specData = [None] * len(specFiles)
    
    # 3. Loop through each file name:
    for spFileIdx,spFile in enumerate(specFiles):
        if spFile is None: continue
        # 3.1 Determine the type of file it is
        isFits = False
        ext = spFile[-4:].lower()
        if ext == 'fits' or ext == '.fit':
            isFits = True
            
        # 3.2. Get data from file
        if isFits:
            try:
                fitsData, fitsHeader = pf.getdata(spFile, header=True)
            except IOError:
                print('Could not open ' + str(spFile) + '.')
                continue
        # Assume ascii file otherwise (isFits = False)
        else:
            try:
                import astropy.io.ascii as ad
                aData = ad.read(spFile)
                specData[spFileIdx] = [aData.columns[0], \
                                       aData.columns[1]]
                if len(aData) >= 3 and errors:
                    specData[spFileIdx].append(aData.columns[2])
            except IOError:
                print('Could not open ' + str(spFile) + '.')
                continue
        
        # 3.3. Check if data in fits file is linear
        if isFits:
            KEY_TYPE = ['CTYPE1']
            setType  = set(KEY_TYPE).intersection(set(fitsHeader.keys()))
            if len(setType) == 0:
                if verbose:
                    print('Data in ' + spFile + ' assumed to be linear.')
                isLinear = True
            else:
                valType = fitsHeader[setType.pop()]
                if valType.strip().upper() == 'LINEAR':
                    isLinear = True
                else:
                    isLinear = False
            if linear and not isLinear:
                if verbose:
                    print('Data in ' + spFile + ' is not linear.')
                return
        
        # 3.4. Get wl, flux & error data from fits file
        #      (returns wl in pos. 0, flux in pos. 1, error values in pos. 2)
        #      (If template spec: min flux in pos. 3, max flux in pos. 4)
        if isFits:
            specData[spFileIdx] = __get_spec(fitsData, fitsHeader, spFile, errors, \
                                             templ=templ, verb=verbose)
            if specData[spFileIdx] is None:
                continue
            
            # Generate wl axis when needed
            if specData[spFileIdx][0] is None:
                specData[spFileIdx][0] = __create_waxis(fitsHeader, \
                                         len(specData[spFileIdx][1]), spFile, \
                                         verb=verbose)
            # If no wl axis generated, then clear out all retrieved data for object
            if specData[spFileIdx][0] is None:
                specData[spFileIdx] = None
                continue
        
        # 3.5. Convert units in wl-axis from Angstrom into microns if desired
        if atomicron:
            if specData[spFileIdx][0][-1] > 8000:
                specData[spFileIdx][0] = specData[spFileIdx][0] / 10000
        
        # 3.6. Set negative flux values equal to zero (next step sets them to nans)
        if negtonan:
            negIdx = np.where(specData[spFileIdx][1] < 0)
            if len(negIdx[0]) > 0:
                specData[spFileIdx][1][negIdx] = 0
                if verbose:
                    print('%i negative data points found in %s.' \
                            % (len(negIdx[0]), spFile))
        
        # 3.7. Set zero flux values as nans (do this always)
        zeros = np.where(specData[spFileIdx][1] == 0)
        if len(zeros[0]) > 0:
            specData[spFileIdx][1][zeros] = np.nan
        
    
    # 4. Plot the spectra if desired
    if plot:
        plot_spec(specData, ploterrors=True)
    
    # 5. Clear up memory
    fitsHeader = ''
    fitsData   = ''
    
    return specData


def sel_band(specData, limits, objID='NA'):
    '''
    (by Alejandro N |uacute| |ntilde| ez)
    
    Select a band (i.e. a portion) from a spectrum specified by *limits*.
    
    *specData*
        Spectrum as a Python list with wavelength in position 0, flux in position 1, and (optional) error values in position 2. More than one spectrum can be provided simultaneously, in which case *specData* shall be a list of lists.
    *limits*
        Python list with lower limit in position 0 and upper limit in position 1.
    *objID*
        String with ID for spectrum; if dealing with several spectra, *objID* shall be a list of strings. For error printing purposes only.
    '''
    
    # Convert specData to list or spectra if it consists only of one
    if len(specData) <= 3 and len(specData[0]) > 10:
        specData = [specData]
    
    # Initialize objects
    finalData = [None] * len(specData)
    
    # Check that given limits are reasonable
    if limits[0] >= limits[1]:
        print('sel_band: the Min and Max values specified are not reasonable.')
        return None
    
    # Loop through each spectral data set
    for spIdx, spData in enumerate(specData):
        
        # 1) Skip if data is missing
        if spData is None:
            continue
        
        # 2) Determine if spectra come with error values
        if len(spData) == 3:
            errors = True
        else:
            errors = False
        
        # 3) Determine minimum wavelength value for band
        smallIdx = np.where(spData[0] < limits[0])
        
        # If lower limit < all values in spectrum wavelength points, then
        # make band's minimum value = first data point in spectrum
        if len(smallIdx[0]) == 0:
            minIdx = 0
        
        # If lower limit > all values in spectrum wavelength points, then
        # no band can be selected
        elif len(smallIdx[0]) == len(spData[0]):
            print('sel_band: the wavelength data for object ', objID[spIdx], \
                  ' is outside the given limits.')
            continue
        else:
            minIdx = smallIdx[0][-1] + 1
        
        # 4) Determine maximum wavelength value for band
        largeIdx = np.where(spData[0] > limits[1])
        
        # If upper limit > all values in spectrum wavelength points, then
        # make band's maximum value = last data point in spectrum
        if len(largeIdx[0]) == 0:
            maxIdx = len(spData[0])
        
        # If upper limit < all values in spectrum wavelength points, then
        # no band can be selected
        elif len(largeIdx[0]) == len(spData[0]):
            print('sel_band: the wavelength data for object %s is outside  ' \
                  + 'the given limits.' %objID[spIdx])
            continue
        else:
            maxIdx = largeIdx[0][0]
        
        # 5) Check for consistency in the computed band limits
        if maxIdx - minIdx < 2:
            print('sel_band: The Min and Max values specified for object %s ' \
                  + 'yield no band.' %objID[spIdx])
            continue
            
        # 6) Select flux band from spectrum
        fluxSelect = spData[1][minIdx:maxIdx]
        
        # 7) Select error value band from spectrum
        if errors is True:
            errorSelect = spData[2][minIdx:maxIdx]
            
            finalData[spIdx] = [spData[0][minIdx:maxIdx], fluxSelect, \
                                errorSelect]
        else:
            finalData[spIdx] = [spData[0][minIdx:maxIdx], fluxSelect]
    
    return finalData


def smooth_spec(specData, oldres=None, newres=200, specFile=None, winWidth=10):
    '''
    (by Alejandro N |uacute| |ntilde| ez)
    
    Smooth flux data to new resolution specified. The method prefers to know the original spectrum resolution, which can be provided directly as *oldres*. Alternatively, the method can find the original resolution in the fits header of the spectrum, in which case you must provide the fits file name as *specFile*. If original resolution is unknown or no fits file is available, *newres* parameter is inoperable. In that case, use *winWidth* as the smoothing parameter.
    
    *specData*
      Spectrum as a Python list with wavelength in position 0, flux in position 1, and (optional) error values in position 2. More than one spectrum can be provided simultaneously, in which case *specData* shall be a list of lists.
    *oldres*
      Float with the original spectrum resolution, if known.
    *newres*
      Float with resolution desired. If neither *oldres* nor *specFile* is provided, *newres* is inoperable.
    *specFile*
      String with name of the fits file (with full path) from where the spectrum was obtained; if dealing with several spectra, *specFiles* shall be a list of strings.
    *winWidth*
      Float with width of smoothing window; use when original spectrum resolution is unknown.
    '''
    # Define key names for resolution in fits file
    KEY_RES = ['RES','RP']
    
    if specFile is None:
        fitsExist = False
    else:
        fitsExist = True
    
    # Convert into python list type when only one set of spectrum and fits file
    if len(specData) <= 3 and len(specData[0]) > 10:
        specData = [specData]
    if isinstance(specFile, str):
        specFile = [specFile]
    
    smoothData = []
    for specIdx,spec in enumerate(specData):
        if spec is None:
            smoothData.append(None)
        else:
            # Get spectrum columns
            wls = np.array(spec[0])
            fluxes = np.array(spec[1])
            try:
                errs = np.array(spec[2])
            except IndexError:
                errs = None
            
            # Get original resolution from oldres, if provided
            if oldres is not None:
                origRes = oldres
            # If oldres not provided, then get original resolution from fits file
            elif fitsExist and specFile[specIdx] is not None:
                fitsData = pf.open(specFile[specIdx])
                # Find Key names for resolution in fits file header
                setRes = set(KEY_RES).intersection(set(fitsData[0].header.keys()))
                # Get resolution data from fits file header
                if len(setRes) > 0:
                    keyName = setRes.pop()
                    origRes = int(fitsData[0].header[keyName])
                else:
                    origRes = 0
                fitsData.close()
            else:
                origRes = 0
            
            # Determine width of smoothing window
            width = 0
            if origRes > newres:
                width = origRes / newres
            elif origRes == 0:
                width = winWidth
            
            # Reduce spectrum resolution if greater than newres
            if width > 0:
                notNans = np.where(np.isfinite(fluxes))
                fluxes[notNans] = spn.filters.uniform_filter( \
                                  fluxes[notNans], size=width)
                if errs is not None:
                    errs[notNans] = spn.filters.uniform_filter( \
                                  errs[notNans], size=width)
            
            # Append to output
            if errs is None:
                smoothData.append([wls, fluxes])
            else:
                smoothData.append([wls, fluxes, errs])
    
    return smoothData


# IV ++++++++++++++++++++ NON-PUBLIC FUNCTIONS ++++++++++++++++++++++++++++++++
# Functions used by Global Functions; these are not meant to be used directly by end users of astrotools. Precede function names by double underscore.
def __create_waxis(fitsHeader, lenData, fileName, verb=True):
# Function used by read_spec only
# (by Alejo)
# Generates a wavelength (wl) axis using header data from fits file.
    
    # Define key names in
    KEY_MIN  = ['COEFF0','CRVAL1']         # Min wl
    KEY_DELT = ['COEFF1','CDELT1','CD1_1'] # Delta of wl
    KEY_OFF  = ['LTV1']                    # Offset in wl to subsection start
    
    # Find key names for minimum wl, delta, and wl offset in fits header
    setMin  = set(KEY_MIN).intersection(set(fitsHeader.keys()))
    setDelt = set(KEY_DELT).intersection(set(fitsHeader.keys()))
    setOff  = set(KEY_OFF).intersection(set(fitsHeader.keys()))
    
    # Get the values for minimum wl, delta, and wl offset, and generate axis
    if len(setMin) >= 1 and len (setDelt) >= 1:
        nameMin = setMin.pop()
        valMin  = fitsHeader[nameMin]
        
        nameDelt = setDelt.pop()
        valDelt  = fitsHeader[nameDelt]
        
        if len(setOff) == 0:
            valOff = 0
        else:
            nameOff = setOff.pop()
            valOff  = fitsHeader[nameOff]
        
        # generate wl axis
        if nameMin == 'COEFF0':
            # SDSS fits files
            wAxis = 10 ** (np.arange(lenData) * valDelt + valMin)
        else:
            wAxis = (np.arange(lenData) * valDelt) + valMin - (valOff * valDelt)
        
    else:
        wAxis = None
        if verb:
            print('Could not re-create wavelength axis for ' + fileName + '.')
    
    return wAxis


def __get_spec(fitsData, fitsHeader, fileName, errorVals, templ=False, verb=True):
# Function used by read_spec only
# (by Alejo)
# Interprets spectral data from fits file.
# Returns wavelength (wl) data in pos. 0, flux data in pos. 1, and if requested, error values in pos. 2.
# If templ, also returns min flux in pos. 3 and max flux in pos. 4
    
    if templ:
        validData = [None] * 5
    elif errorVals:
        validData = [None] * 3
    else:
        validData = [None] * 2
    
    # Identify number of data sets in fits file
    dimNum = len(fitsData)
    
    # Identify data sets in fits file
    fluxIdx  = None
    waveIdx  = None
    sigmaIdx = None
    
    if dimNum == 1:
        fluxIdx = 0
    elif dimNum == 2:
        if len(fitsData[0]) == 1:
            sampleData = fitsData[0][0][20]
        else:
            sampleData = fitsData[0][20]
        if sampleData < 0.0001:
            # 0-flux, 1-unknown
            fluxIdx  = 0
        else:
            waveIdx = 0
            fluxIdx = 1
    elif dimNum == 3:
        waveIdx  = 0
        fluxIdx  = 1
        sigmaIdx = 2
    elif dimNum == 4:
    # 0-flux clean, 1-flux raw, 2-background, 3-sigma clean
        fluxIdx  = 0
        sigmaIdx = 3
    elif dimNum == 5:
        if templ:
            # 0-wl, 1-avg flux, 2-flux variance, 3-min flux, 4-max flux
            waveIdx = 0
            fluxIdx = 1
            sigmaIdx = 2
            minIdx = 3
            maxIdx = 4
        else:
            # 0-flux, 1-continuum substracted flux, 2-sigma, 3-mask array, 4-unknown
            fluxIdx  = 0
            sigmaIdx = 2
    elif dimNum > 10:
    # Implies that only one data set in fits file: flux
        fluxIdx = -1
        if np.isscalar(fitsData[0]):
            fluxIdx = -1
        elif len(fitsData[0]) == 2:
        # Data comes in a xxxx by 2 matrix (ascii origin)
            tmpWave = []
            tmpFlux = []
            for pair in fitsData:
                tmpWave.append(pair[0])
                tmpFlux.append(pair[1])
            fitsData = [tmpWave,tmpFlux]
            fitsData = np.array(fitsData)
            
            waveIdx = 0
            fluxIdx = 1
        else:
        # Indicates that data is structured in an unrecognized way
            fluxIdx = None
    else:
        fluxIdx = None
        
    # Fetch wave data set from fits file
    if fluxIdx is None:
    # No interpretation known for fits file data sets
        validData = None
        if verb:
            print('Unable to interpret data in ' + fileName + '.')
        return validData
    else:
        if waveIdx is not None:
            if len(fitsData[waveIdx]) == 1:
            # Data set may be a 1-item list
                validData[0] = fitsData[waveIdx][0]
            else:
                validData[0] = fitsData[waveIdx]
    
    # Fetch flux data set from fits file
    if fluxIdx == -1:
        validData[1] = fitsData
    else:
        if len(fitsData[fluxIdx]) == 1:
            validData[1] = fitsData[fluxIdx][0]
        else:
            validData[1] = fitsData[fluxIdx]
    
    # Fetch sigma data set from fits file, if requested
    if errorVals:
        if sigmaIdx is None:
            validData[2] = np.array([np.nan] * len(validData[1]))
        else:
            if len(fitsData[sigmaIdx]) == 1:
                validData[2] = fitsData[sigmaIdx][0]
            else:
                validData[2] = fitsData[sigmaIdx]
        
        # If all sigma values have the same value, replace them with nans
        if validData[2][10] == validData[2][11] == validData[2][12]:
            validData[2] = np.array([np.nan] * len(validData[1]))
    
    # Fetch template data when relevant
    if templ:
        validData[3] = fitsData[minIdx]
        validData[4] = fitsData[maxIdx]
    return validData


# V +++++++++++++++++++++++++ PUBLIC CLASSES ++++++++++++++++++++++++++++++++++
# Classes meant to be used by end users of astrotools. Capitalize class names.
    
