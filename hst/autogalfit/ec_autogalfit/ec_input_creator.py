#automating the creation and running of galfit input files
#trying to make it loop through all of 'withfinepsf' files

import os
import numpy as np
from astropy.io import ascii
import datetime

galaxies = ['J0826', 'J0901', 'J0905', 'J0944', 'J1107', 'J1219', 'J1341', 'J1506', 'J1558', 'J1613', 'J2116', 'J2140']
filters = ['F475W','F814W']
longgal = ['J0826+4305','J0901+0314','J0905+5759','J0944+0930','J1107+0417','J1219+0336','J1341+0321','J1506+5402','J1558+3957','J1613+2834','J2116-0634','J2140+1209']
photzeromag = ['25.613','25.027']
model = ['psf','sersic']
kind = ['independent','simultaneous']
now = datetime.datetime.now()
time = now.strftime("%Y%m%d-%H%M")

for m in range(0,2):
    for w in range(0,12):
        for i in range(0,2):
            if not os.path.exists(time+'_'+model[m]+'_'+kind[0]):
                os.makedirs(time+'_'+model[m]+'_'+kind[0])


            file = time+'_'+model[m]+'_'+kind[0]+'/'+galaxies[w]+'_'+filters[i]+'_'+model[m]+'_input.txt'
            text = open(file,'w')
            text.write('#  Input menu file: '+galaxies[w]+'_'+filters[i]+'_coarse_withfinepsf\n') #probably not essential
            text.write('#  Chi^2/nu = ,  Chi^2 = ,  Ndof = \n') #probably not essential
            text.write('# IMAGE and GALFIT CONTROL PARAMETERS\n') #will not change , probably not essential
            text.write('A) /Volumes/physics/linux-lab/data/hst/'+longgal[w]+'/coarse/'+filters[i]+'/final_'+filters[i]+'_drc_sci.fits\n')
            text.write('B) '+galaxies[w]+'_'+filters[i]+'_'+model[m]+'_output.fits\n')
            text.write('C) none\n') #will not change
            text.write('D) /Volumes/physics/linux-lab/data/hst/'+longgal[w]+'/fine/'+filters[i]+'/final_psf.fits\n')
            text.write('E) 2\n') #will not change
            text.write('F) none\n') #will not change

            if m == 0:
                text.write('G) \n')
            if m == 1:
                text.write('G) /Volumes/physics/linux-lab/data/galfit/eves_files/constraints_sersic_indep.txt\n')

                
            galcoords = 'galcoords.dat'
            catalog = ascii.read(galcoords)
        
            xcoor = str(catalog[w][1])
            ycoor = str(catalog[w][2])
            xcoorlow = str(catalog[w][1]-200)
            ycoorlow = str(catalog[w][2]-200)
            xcoorhigh = str(catalog[w][1]+200)
            ycoorhigh = str(catalog[w][2]+200)
        
            text.write('H) '+xcoorlow+' '+xcoorhigh+' '+ycoorlow+' '+ycoorhigh+'\n')
            text.write('I) 150    150\n') 
            text.write('J) '+photzeromag[i]+'\n')
            text.write('K) 0.050  0.050\n')
            text.write('O) regular\n') #will not change
            text.write('P) 0\n') #will not change
            text.write('#   par)    par value(s)    fit toggle(s)    # parameter description \n')
            text.write('# Component number: 1\n')

            if m == 0:
                text.write(' 0) psf\n')
                text.write(' 1) '+xcoor+' '+ycoor+' 1 1  # position x, y        [pixel]\n')
                text.write(' 3) 19.5     1\n')
                text.write(' Z) 0                  #  Skip this model in output image?  (yes=1, no=0)\n')
            if m ==1:
                text.write(' 0) sersic\n')
                text.write(' 1) '+xcoor+' '+ycoor+' 1 1  # position x, y        [pixel]\n')
                text.write(' 3) 19.5     1\n')
                text.write(' 4) 0.3      1\n')
                text.write(' 5) 4.0      1\n')
                text.write(' 6) 0      0\n')
                text.write(' 7) 0      0\n')
                text.write(' 8) 0      0\n')
                text.write(' 9) 0.9      1\n')
                text.write(' 10) 0     1\n')
                text.write(' Z) 0      \n')

            text.close()

#below we create shell scripts to run galfit on the input files (need to type "sh name of the shell script" in the terminal)
file = time+'_'+model[0]+'_'+kind[0]+'/'+'psf_independent_run_files.sh'
text = open(file,'w')
text.write('shopt -s expand_aliases\n')
text.write('source ~/.bash_profile\n')
for w in range(0,12):
    for i in range(0,2):
        text.write('galfitm '+galaxies[w]+'_'+filters[i]+'_'+model[0]+'_input.txt\n')
text.close()

file = time+'_'+model[1]+'_'+kind[0]+'/'+'sersic_independent_run_files.sh'
text = open(file,'w')
text.write('shopt -s expand_aliases\n')
text.write('source ~/.bash_profile\n')
for w in range(0,12):
    for i in range(0,2):
        text.write('galfitm '+galaxies[w]+'_'+filters[i]+'_'+model[1]+'_input.txt\n')
text.close()



dependency = ['semi', 'full']
#now for simultaneous fits
for z in range(0,2): 
    for m in range(0,2):
        for w in range(0,12):

            if not os.path.exists(time+'_'+model[m]+'_'+dependency[z]):
                os.makedirs(time+'_'+model[m]+'_'+dependency[z])
            file = time+'_'+model[m]+'_'+dependency[z]+'/'+galaxies[w]+'_F814WandF475W_'+model[m]+'_input.txt'
            text = open(file,'w')
        
            text.write('#  Input menu file: '+galaxies[w]+'_F814W_F475W_psf_input_mac.txt\n') #propably not essential
            text.write('#  Chi^2/nu = ,  Chi^2 = ,  Ndof = \n') #probably not essential
            text.write('# IMAGE and GALFIT CONTROL PARAMETERS\n') #will not change , probably not essential
            text.write('A) /Volumes/physics/linux-lab/data/hst/'+longgal[w]+'/coarse/'+filters[1]+'/final_'+filters[1]+'_drc_sci.fits,/Volumes/physics/linux-lab/data/hst/'+longgal[w]+'/coarse/'+filters[0]+'/final_'+filters[0]+'_drc_sci.fits\n')
            text.write('A1) V,U\n')
            text.write('A2) 814.000,475.000\n')
            text.write('B) '+galaxies[w]+'_F814WandF475W_'+model[m]+'_'+dependency[z]+'_output.fits\n')
            text.write('C) none,none      0.000\n')
            text.write('D) /Volumes/physics/linux-lab/data/hst/'+longgal[w]+'/fine/'+filters[1]+'/final_psf.fits,/Volumes/physics/linux-lab/data/hst/'+longgal[w]+'/fine/'+filters[0]+'/final_psf.fits\n')
            text.write('E) 1\n')
            text.write('F) none,none\n')
            if m == 0:
                text.write('G) \n')
            if m == 1:
                text.write('G) /Volumes/physics/linux-lab/data/galfit/eves_files/constraints_sersic_indep.txt\n')
            
            xcoor = str(catalog[w][1])
            ycoor = str(catalog[w][2])
            xcoorlow = str(catalog[w][1]-200)
            ycoorlow = str(catalog[w][2]-200)
            xcoorhigh = str(catalog[w][1]+200)
            ycoorhigh = str(catalog[w][2]+200)
            
            text.write('H) '+xcoorlow+' '+xcoorhigh+' '+ycoorlow+' '+ycoorhigh+'\n')
            text.write('I) 100    100\n')
            text.write('J) 25.027,25.613\n')
            text.write('K) 0.05  0.05\n')
            text.write('O) regular\n')
            text.write('P) 0\n')
            text.write('U) 0 0.750000 25 4 40\n')
            text.write('V) 0 0 50 0.800000 0.500000 100000\n')
            text.write('W) input,sigma,psf,component,model,residual\n')

            if m == 0:
                text.write(' 0) psf\n')
                if z == 0:
                    text.write(' 1) '+xcoor+','+xcoor+'    1,1                 band\n')
                    text.write(' 2) '+ycoor+','+ycoor+'    1,1                 band\n')
                if z == 1:
                    text.write(' 1) '+xcoor+','+xcoor+'    1,0                 band\n')
                    text.write(' 2) '+ycoor+','+ycoor+'    1,0                 band\n') 
                text.write(' 3) 19.5,19.5     1,1 band\n')
                text.write(' Z) 0                  #  Skip this model in output image?  (yes=1, no=0)\n')
                
            if m == 1:
                text.write(' 0) sersic\n')
                if z == 0:
                    text.write(' 1) '+xcoor+','+xcoor+'    1,1                 band\n')
                    text.write(' 2) '+ycoor+','+ycoor+'    1,1                 band\n')
                if z == 1:
                    text.write(' 1) '+xcoor+','+xcoor+'    1,0                 band\n')
                    text.write(' 2) '+ycoor+','+ycoor+'    1,0                 band\n')                    
                text.write(' 3) 19.5,19.5     1,1                 band\n')
                text.write(' 4) 0.906,1.110e-16    1,0                 cheb\n')
                text.write(' 5) 4.000,4.441e-16    1,0                 cheb\n')
                text.write(' 6) 0,0               0,0                 cheb\n')
                text.write(' 7) 0,0               0,0                 cheb\n')
                text.write(' 8) 0,0               0,0                 cheb\n')
                text.write(' 9) 0.9,0           1,0                 cheb\n')
                text.write(' 10) 0,0          1,0                 cheb\n')
                text.write(' Z) 0')
            text.close()

file = time+'_'+model[0]+'_'+dependency[0]+'/'+'psf_simultaneous_run_files.sh'
text = open(file,'w')
text.write('shopt -s expand_aliases\n')
text.write('source ~/.bash_profile\n')
for w in range(0,12):
    text.write('galfitm '+galaxies[w]+'_F814WandF475W_'+model[0]+'_input.txt\n')
text.close()


file = time+'_'+model[1]+'_'+dependency[0]+'/'+'sersic_simultaneous_run_files.sh'
text = open(file,'w')
text.write('shopt -s expand_aliases\n')
text.write('source ~/.bash_profile\n')
for w in range(0,12):
    text.write('galfitm '+galaxies[w]+'_F814WandF475W_'+model[1]+'_input.txt\n')
text.close()


file = time+'_'+model[0]+'_'+dependency[1]+'/'+'psf_simultaneous_run_files.sh'
text = open(file,'w')
text.write('shopt -s expand_aliases\n')
text.write('source ~/.bash_profile\n')
for w in range(0,12):
    text.write('galfitm '+galaxies[w]+'_F814WandF475W_'+model[0]+'_input.txt\n')
text.close()


file = time+'_'+model[1]+'_'+dependency[1]+'/'+'sersic_simultaneous_run_files.sh'
text = open(file,'w')
text.write('shopt -s expand_aliases\n')
text.write('source ~/.bash_profile\n')
for w in range(0,12):
    text.write('galfitm '+galaxies[w]+'_F814WandF475W_'+model[1]+'_input.txt\n')
text.close()



