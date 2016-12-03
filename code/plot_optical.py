#to run this, at terminal, >import plot_optical
from astrodbkit import astrodb
from matplotlib import pyplot as plt
import numpy as np


db=astrodb.get_db('/Users/kelle/Dropbox/BDNYCdb/BDNYCv1.0.db')

#may need to query unums to get source_ids.
#unums=['U20487','U20098','U20098', 'U20993', 'U20026',  'U10141' ,'U11684', 'U20869', 'U10074' , 'U10381' ,'U10397', 'U20048','U11704'  ,'U12096', 'U20622', 'U20636', 'U40005','U11538', 'U11946', 'U10372']
#unums=['U20487','U20098','U20098', 'U20993', 'U20026',  'U10141' ,'U11684', 'U20869', 'U10074' , 'U10381' ,'U10397', 'U20048','U11704'  ,'U12096', 'U20622', 'U20636', 'U40005','U11538', 'U11946', 'U10372']

# source_ids=[383,579,430,594,98,420,871,317,91,720,108,840,313,366,14,854,852,791]
#
# names=[]

#go from unums to sourceids
# for source_id in source_ids:
#     #source_id_i=db.query.execute("SELECT id from sources where unum='{}'".format(unum)).fetchone()
#     #source_ids.append(source_id_i[0])
#     name_i=db.query("SELECT shortname from sources where id={}".format(source_id),fetch='one')
#     names.append(name_i[0])

#print names
#print unums, type(unums[0])
#print source_ids, type(source_ids[0])

#convert tuple returned by query to a list
#index=0
#source_ids=[]
#while index<len(source_ids2):
#    source_ids.append(source_ids2[index][0])
#    index+=1
    
#print source_ids,type(source_ids[0])

#spectra_ids2=[]
#spectra_ids=[]

#LDSS3


#GET KECK LRIS DATA 
# for i,source_id in enumerate(source_ids):
#     try:
#         #print source_id
#         spectra_ids_i= db.query("SELECT id from spectra where source_id={} AND (telescope_id = 8 AND instrument_id = 5)".format(source_id))
#         #print spectra_ids_i
#         n_spec = len(spectra_ids_i)
#         print 'number of spectra for ' + names[i] + ':', n_spec
#         print i, source_id, spectra_ids_i
#         for j,spectra_id in enumerate(spectra_ids_i):
#             spectra_ids.append(spectra_id[0])
#     except: pass
#
# # print spectra_ids2
#
# index=0
# spectra_ids=[]
# while index<len(spectra_ids2):
#     spectra_ids.append(spectra_ids2[index][0])
#     index+=1
#

#Explictly decide which spectra to plot
spectra_ids = [1093,1103,470,1125,496,578,586,1301,400,401,1353,403,874,404,405,420,408,1521,1503]

#print spectra_ids
names=[]

#look up names for the spectra
names2=[]
obsdates=[]
for spectra_id in spectra_ids:
    source_id2 = db.query("SELECT source_id from spectra where id={} ".format(spectra_id))[0][0]
    name2 = db.query("SELECT shortname from sources where id={} ".format(source_id2))[0][0]
    obsdate = db.query("SELECT obs_date from spectra where id={} ".format(spectra_id))[0][0]
    names2.append(name2)
    obsdates.append(obsdate)
    print name2,source_id2,spectra_id,obsdate
    
print names2

for j,spectra_id in enumerate(spectra_ids):
#for name in names:
        #i = spectra_ids[0]
        #j = names[0]
        #print i
        #print j
        #wave,flux=db.query.execute("SELECT wavelength,flux from spectra where id='{}'".format(i)).fetchone()
        spectrum = db.query("SELECT spectrum from spectra where id='{}'".format(spectra_id),fetch='one')[0]
        wave = spectrum.data[0]
        flux = spectrum.data[1]
        #flux=db.query.execute("SELECT flux from spectra where id='{}'".format(spectra_id)).fetchone()
        #normalize?
        
        plt.plot(wave,flux/np.mean(flux))
        #plt.show() #go to screen

        plt.xlim(6000,10000)
        plt.ylim(0.0,4.0)
        plt.xlabel(r'Wavelength ($\AA$)')
        plt.ylabel('Normalized Flux')
        plt.text(6500,3.5,'{}'.format(names2[j]))
        plt.text(6500,3.2,'obs date: ' '{}'.format(obsdates[j]),size='smaller')
        
        plt.savefig('/Users/kelle/Dropbox/Pubs IN PROGRESS/Paper XII NIR DATA/Cruz-Nunez/figures/opt2/' +'{}'.format(names2[j])+ '_{}'.format(spectra_id)+'.pdf')
        #plt.savefig('/Users/kelle/Desktop/test.pdf')

        plt.close()
