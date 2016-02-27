'''
Initialize variables used in all other scripts.
'''

import numpy as np

# Folders
global ROOT, FOLDER_MAIN, FOLDER_GIT, FOLDER_DATA, FOLDER_DATASPEC
global FOLDER_OUT_PLT, FOLDER_OUT_TMPL
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
L_RED = '#FF6666'

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
global colorSet
colorSet = [None] * 31
colorSet[30] = COLOR_SET.copy().tolist()
colorSet[29] = COLOR_SET[[0,1,3,4,5,6,7,8,9,10,11,12,13,14,15,16,17,18, \
                        19,20,21,22,23,24,25,26,27,28,29]].tolist()
colorSet[28] = COLOR_SET[[0,1,3,4,5,6,7,8,9,10,11,12,13,14,15,16,17,18, \
                        19,20,21,23,24,25,26,27,28,29]].tolist()
colorSet[27] = COLOR_SET[[0,1,3,4,5,6,7,8,10,11,12,13,14,15,16,17,18, \
                        19,20,21,23,24,25,26,27,28,29]].tolist()
colorSet[26] = COLOR_SET[[0,1,3,4,5,6,7,8,10,11,12,14,15,16,17,18, \
                        19,20,21,23,24,25,26,27,28,29]].tolist()
colorSet[25] = COLOR_SET[[1,3,4,5,6,7,8,10,11,12,14,15,16,17,18, \
                        19,20,21,23,24,25,26,27,28,29]].tolist()
colorSet[24] = COLOR_SET[[1,3,4,5,6,7,8,10,11,12,14,15,16,17,18, \
                        19,20,21,24,25,26,27,28,29]].tolist()
colorSet[23] = COLOR_SET[[1,3,4,5,6,7,8,10,11,12,14,15,16,18, \
                        19,20,21,24,25,26,27,28,29]].tolist()
colorSet[22] = COLOR_SET[[1,3,4,6,7,8,10,11,12,14,15,16,18, \
                        19,20,21,24,25,26,27,28,29]].tolist()
colorSet[21] = COLOR_SET[[1,3,4,6,7,8,10,11,12,14,15,16,18, \
                        19,20,21,24,25,27,28,29]].tolist()
colorSet[20] = COLOR_SET[[1,3,4,6,7,8,10,11,12,14,16,18, \
                        19,20,21,24,25,27,28,29]].tolist()
colorSet[19] = COLOR_SET[[1,3,4,6,7,8,10,11,12,16,18, \
                        19,20,21,24,25,27,28,29]].tolist()
colorSet[18] = COLOR_SET[[1,3,4,6,7,10,11,12,16,18, \
                        19,20,21,24,25,27,28,29]].tolist()
colorSet[17] = COLOR_SET[[1,3,4,6,7,10,11,12,18,19,20,21,24,25,27,28,29]].tolist()
colorSet[16] = COLOR_SET[[1,3,4,7,10,11,12,18,19,20,21,24,25,27,28,29]].tolist()
colorSet[15] = COLOR_SET[[1,3,4,7,10,11,12,18,19,20,21,24,25,27,29]].tolist()
colorSet[14] = COLOR_SET[[1,3,4,7,11,12,18,19,20,21,24,25,27,29]].tolist()
colorSet[13] = COLOR_SET[[1,3,4,7,11,12,19,20,21,24,25,27,29]].tolist()
colorSet[12] = COLOR_SET[[1,3,4,7,11,12,19,20,21,25,27,29]].tolist()
colorSet[11] = COLOR_SET[[1,3,4,11,12,19,20,21,25,27,29]].tolist()
colorSet[10] = COLOR_SET[[1,4,11,12,19,20,21,25,27,29]].tolist()
#colorSet[9]  = ['#67001f','#b2182b','#d6604d','#f4a582','#fddbc7', \
#                '#92c5de','#4393c3','#2166ac','#053061']
colorSet[9]  = ['#67001f','#b2182b','#d6604d','#f4a582','#f4a582', \
                '#92c5de','#4393c3','#2166ac','#053061'] # Use this one to make field-L4 brighter orange.
colorSet[8]  = ['#67001f','#b2182b','#d6604d','#f4a582', \
                '#92c5de','#4393c3','#2166ac','#053061']
colorSet[7]  = ['#b2182b','#d6604d','#f4a582','#fddbc7','#92c5de', \
                '#4393c3','#2166ac']
colorSet[6]  = ['#b2182b','#d6604d','#f4a582','#92c5de','#4393c3','#2166ac']
colorSet[5]  = ['#b2182b','#d6604d','#f4a582','#4393c3','#053061']
#['#b2182b','#ef8a62','#fddbc7','#67a9cf','#2166ac']
colorSet[4]  = ['#ca0020','#f4a582','#92c5de','#0571b0']
colorSet[3]  = ['#ca0020','#f4a582','#0571b0']
colorSet[2]  = ['#ca0020','#0571b0']
colorSet[1]  = ['#2166ac']

# Spectral variables
global SPTYPES
SPTYPES = ('L0','L1','L2','L3','L4','L5','L6','L7','L8')
SPTYPESN = (10,11,12,13,14,15,16,17,18)
global BANDS
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
