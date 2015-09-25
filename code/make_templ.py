''' This generates separate ascii files for all templates, by band (J, H, and K). The files contain five columns: wavelength, average flux, standard deviation, min flux, max flux.'''

import nir_opt_comp_strip as nocs
import astrotools as at

with open("def_constants.py") as f:
    code = compile(f.read(), "def_constants.py", "exec")
    exec(code)
GRAVS = ['f','g','b']

for sptp in SPTYPES:
    print(sptp)
    for grav in GRAVS:
        templ = nocs.main(sptp, grav, templ=True, plot=False)
        if templ is None:
            continue
        
        print(' ' + grav)
        for bdidx, band in enumerate(templ):
            # Create template spectrum file
            # columns are: wavelength, mean flux, standard deviation, min flux, max flux
            at.create_ascii(band, FOLDER_OUT_TMPL + sptp + BANDS[bdidx] + '_' + grav)

