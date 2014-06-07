'''
Initialize variables used in all other scripts.
'''

# Folders
ROOT = '/Users/alejo/Dropbox/'
FOLDER_MAIN = ROOT + 'Project_0/'
FOLDER_GIT = ROOT + 'Python/BDNYC_specfigures/' # Folder with ACCESS table (git-linked)
FOLDER_DATA = FOLDER_MAIN + 'data/'
FOLDER_DATASPEC = FOLDER_MAIN + 'more data/'
FOLDER_OUT_PLT = FOLDER_MAIN + 'plots/'
FOLDER_OUT_TMPL = FOLDER_MAIN + 'templates/'

# Colors
BLACK = '#000000'
GRAY = '#999999'
L_GRAY = '#CCCCCC'
D_GRAY = '#666666'
WHITE = '#FFFFFF'
PURPLE = '#660099'
BLUE = '#0033FF'
L_BLUE = '#66CCFF'
GREEN = '#006633'
L_GREEN = '#66CC00'
ORANGE = '#FF9933'
RED = '#FF0000'
L_RED = '#CC6666'

# Spectral variables
SPTYPES = ('L0','L1','L2','L3','L4','L5','L6','L7','L8')
SPTYPESN = (10,11,12,13,14,15,16,17,18)
BANDS = ['J','H','K']
BAND_LIMS = {}.fromkeys(BANDS)
NORM_LIMS = {}.fromkeys(BANDS)
for bandKey in BANDS:
    BAND_LIMS[bandKey] = dict(lim = [None] * 2)
BAND_LIMS['J']['lim'][0] = 0.8
BAND_LIMS['J']['lim'][1] = 1.4 
BAND_LIMS['H']['lim'][0] = 1.4
BAND_LIMS['H']['lim'][1] = 1.9
BAND_LIMS['K']['lim'][0] = 1.9
BAND_LIMS['K']['lim'][1] = 2.4
for bandKey in BANDS:
    NORM_LIMS[bandKey] = dict(lim = [None] * 2)
NORM_LIMS['J']['lim'][0] = 0.87
NORM_LIMS['J']['lim'][1] = 1.39
NORM_LIMS['H']['lim'][0] = 1.41
NORM_LIMS['H']['lim'][1] = 1.89
NORM_LIMS['K']['lim'][0] = 1.91
NORM_LIMS['K']['lim'][1] = 2.39
