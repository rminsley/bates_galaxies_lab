# Sophia C W Gottlieb I
# 20170125
#
# This code is the general, optimal version of jr_compilation
# 
# This code produces three graphs: Mass in an annulus as a function of radius for annular MLRs, and for a broad MLR, and mass density as a function of radius (the more important graph)
# It also prints out several different estimates of mass for each galaxy (though it mass / 1e11)
# This is hopefully the last version of this code. We will begin a new code for the pixel by pixel analysis.
#
# import relevant Python modules
import os
import numpy as np
from astropy.io import fits
from photutils import CircularAperture
from photutils import aperture_photometry
import glob
import matplotlib.pyplot as plt
from matplotlib import cm
from matplotlib.backends.backend_pdf import PdfPages
import math
import matplotlib.lines as mlines
from matplotlib.legend_handler import HandlerLine2D
from scipy import integrate
from astropy.cosmology import WMAP9 as cosmo
from astropy import units as u
from astropy import constants as const

# define the directory that contains the images
dir = os.environ['HSTDIR']

#these are not what you want
solarLum = 3.846*10**33    #solar Mass is the mass of the sun in kg
radToKpc = 0.05*7.194       #converts radius to kpc

#setting up arrays with three elements, all zeros - placeholders
wavelengths = [4,8,1]
data = [0 for x in range(len(wavelengths))]
header = [0 for x in range(len(wavelengths))]
fnu = [0 for x in range(len(wavelengths))]
exp = [0 for x in range(len(wavelengths))]


#set up two-dimensional arrays for the a and b coefficients based on the luminosity and color
#this will be in the same format ish as the table in Josh's blue notebook
Ba = [-1.019,-1.113,-1.026,-.990,-1.110,-.994,-.888]
Bb = [1.937,2.065,1.954,1.883,2.018,1.804,1.758]
B_coeff = [Ba,Bb]
Va = [-.759,-.853,-.766,-.730,-.850,-.734,-.628]
Vb = [1.537,1.665,1.554,1.483,1.618,1.404,1.358]
V_coeff = [Va,Vb]
Ja = [-.540,-.658,-.527,-.514,-.659,-.621,-.550]
Jb = [.757,.907,.741,.704,.878,.794,.801]
J_coeff = [Ja,Jb]

# specify the position of the science target and the size of the region around the science target to consider
filters = np.array([475, 814, 1600]) #*u.nm
galaxies = ['J0826', 'J0901', 'J0905', 'J0944', 'J1107', 'J1219', 'J1341', 'J1506', 'J1558', 'J1613', 'J2116', 'J2140']
xcen = [3628, 3933, 3386.5, 3477.5, 3573, 3802, 3886, 4149, 3787, 4174, 3565, 4067]
ycen = [4153, 4136, 3503.2, 3404.3, 3339, 4169, 4164, 3921, 4187, 3826, 3434, 4054]

#xcen = [3628.7, 3934, 3386.5, 3477.539, 3572.9, 3801.2, 3885.6, 4149.15, 3787, 3825.89, 3566.9, 4067]
#ycen = [4153.8, 4137, 3503.2, 3404.342, 3339.1, 4171.6, 4164.336, 3921.748, 4187, 4451.805, 3435.9, 4054.4]

zs = [0.603, 0.459, 0.712, 0.514, 0.467, 0.451, 0.658, 0.608, 0.402, 0.449, 0.728, 0.752]
#Ldcm is the luminosity distance in cm, even though astropy thinks it is in Mpc. 
Ldcm = cosmo.luminosity_distance(zs)*u.Mpc.to(u.cm) / u.Mpc

# define the radii to be used for aperture photometry
radii = np.arange(40)+1
aMLR_BV_Vk_ab = [[0 for x in range(40)] for y in range(7)]
aLnuNu = [0 for x in range(len(wavelengths))]
#make an array for the calculation of the area of each bagel (annulus)
area = [0 for x in range(len(radii))]

#calculate area of each bagel
for i in range(0, len(area)):
    if i == 0:
        area[i] = math.pi*math.pow(radii[0],2)
    else:
        area[i] = math.pi*(math.pow(radii[i],2)-math.pow(radii[i-1],2))
# Now, we loop through all galaxies
with PdfPages('sg_compover.pdf') as pdf:

# create a PDF file for the plots    
    
    for w in range (0, len(galaxies)):
        print(galaxies[w])
        fig = plt.figure()
    
        collection = ['F475W','F814W','F160W']
    
        flux = np.zeros([len(collection),len(radii)]) #*u.Jy
        subflux = np.zeros([len(collection),len(radii)])
    
        for i in range (0, len(collection)):
            
            # read in the images
            file = glob.glob(dir+galaxies[w]+'_final_'+collection[i]+'*sci.fits')
            hdu = fits.open(file[0])
            data[i], header[i] = hdu[0].data, hdu[0].header
            fnu[i] = header[i]['PHOTFNU']
            exp[i] = header[i]['EXPTIME']
    
            #define positions for photometry
            positions = [(xcen[w], ycen[w])]
    
            #do photometry on images
            #convert to proper units
            for j in range(0,len(radii)):
                aperture = CircularAperture(positions, radii[j])
                phot_table = aperture_photometry(data[i], aperture)
                flux[i,j] = phot_table['aperture_sum'][0]*(fnu[i]/exp[i])
                if j == 0:
                    subflux[i,j] = flux[i,j]
                else:
                    subflux[i,j] = flux[i,j]-flux[i,j-1]
            
    
        #calculating galaxy-wide
        
        #finding total flux in galaxy in Jy 19 mag. 
        tflux = np.array([flux[0,len(radii)-1],flux[1,len(radii)-1],flux[2,len(radii)-1]])
    
        #finding magnitudes and color for M/L ratio
        mag = -2.5*np.log10(tflux / 3631)
        colorUV = mag[0]-mag[1]
        colorVJ = mag[1]-mag[2]
    
        #determining M/L ratio using Table 3 of Bell & de Jong, seven coefficients for each luminosity for BV color
        MLR_BV_Bk = np.zeros([len(Ba)])
        MLR_BV_Vk = np.zeros([len(Va)])
        MLR_BV_Jk = np.zeros([len(Ja)])
        for k in range(0,len(Ba)):
            MLR_BV_Bk[k] = 10**(Ba[k]+(Bb[k]*colorUV))
            MLR_BV_Vk[k] = 10**(Va[k]+(Vb[k]*colorUV))
            MLR_BV_Jk[k] = 10**(Ja[k]+(Jb[k]*colorUV))
    
        #calculating nu_e * L_nu_e luminosity in erg Hz units from Hogg eq (24), only three values depending on filter
        LnuNu = (const.c*u.s/u.m/(filters*10**-9))*tflux*10**-23*(4*math.pi*Ldcm[w]**2)
        
        #convert luminosity to solar units
        Lsol = LnuNu / solarLum
        
        #calculate mass of galaxy in solar units, 3 arrays of masses for each coefficient for 3 different filters will yield a total of 21 galaxy masses, 7 values for each luminosity in the BV color
        M_BV_Bk = np.zeros([len(Ba)])
        M_BV_Vk = np.zeros([len(Va)])
        M_BV_Jk = np.zeros([len(Ja)])
        
        M_BV_Bk = Lsol[0]*MLR_BV_Bk
        M_BV_Vk = Lsol[1]*MLR_BV_Vk
        M_BV_Jk = Lsol[2]*MLR_BV_Jk
    
        #calculating best values and uncertainties
        mass = (M_BV_Bk, M_BV_Vk, M_BV_Jk)
        Msic_475_BV = np.mean(mass[0])
        Msic_814_BV = np.mean(mass[1])
        Msic_160_BV = np.mean(mass[2])
        
        Msic_475_BV_std = np.std(mass[0])
        Msic_814_BV_std = np.std(mass[1])
        Msic_160_BV_std = np.std(mass[2])
        
        #print('Msic,475W,B-V', Msic_475_BV/1e11)
        #print('Msic,475W,B-V std', Msic_475_BV_std/1e11)
        
        #print('Msic,814W,B-V', Msic_814_BV/1e11)
        #print('Msic,814W,B-V std', Msic_814_BV_std/1e11)
        
        #print('Msic,160W,B-V', Msic_160_BV/1e11)
        #print('Msic,160W,B-V std', Msic_160_BV_std/1e11)
        
        #calculation annulus-based
    
        #calculation of flux for each annulus, given in an array, for each filter, in erg/s units
        aflux = subflux*10**-23
        #calculation of magnitudes and color for each annulus
        #I do not think I need to calculate 'acolorUV', but rather simply use the 'colorUV' calculation to determine MLR, however I have left this in the code in case we need to refer to it later. I did not comment it out since it isn't used later in the code.
        amag = -2.5*np.log10(aflux / 3631)
        acolorUV = amag[0]-amag[1]
        acolorVJ = amag[1]-amag[2]
    
        #now it is my intention to run the code with seven ab value sets for each annulus (ONLY CONSDIERING THE F814W FILTER) and add up the total mass based on these values to get an array of seven values for mass, and then get the mean and std for this
        aMLR_BV_B = 10**(-.994+(1.804*acolorUV))
        aMLR_BV_V = 10**(-.734+(1.404*acolorUV))
        aMLR_BV_J = 10**(-.621+(.794*acolorUV))
    
        #setting up to calculate Msrc_814_BV_ab0-6

        for k in range(len(Va)):
            aMLR_BV_Vk_ab[k] = 10**(Va[k]+(Vb[k]*acolorUV))
    
        #calculation of annular MLR based on one MLR for the entire galaxy, since we plan to overlay polots of both. this will be denoted 'bMLR...'
        bMLR_BV_B = 10**(-.994+(1.804*colorUV))
        bMLR_BV_V = 10**(-.734+(1.404*colorUV))
        bMLR_BV_J = 10**(-.621+(.794*colorUV))
    
        #calculating nu_e * L_nu_e luminosity in erg/s units for each annulus from Hogg eq (24)
        for i in range (0, len(filters)):
            aLnuNu[i] = (const.c*u.s/u.m/(filters[i]*10**-9))*aflux[i,:]*(4*math.pi*Ldcm[w]**2)
            
        
        #convert luminosity for each annulus to solar units
        aLsol814 = aLnuNu[1] / solarLum
        aLsol = (aLnuNu[0]/ solarLum,aLnuNu[1]/ solarLum,aLnuNu[2]/ solarLum) 
    
        #calculate mass associated with each annulus, based on individualized MLRs for each annulus, in solar units, based on individualized MLRs
        aMLR_BV = (aMLR_BV_B, aMLR_BV_V, aMLR_BV_J)
        amass = (aLsol[0]*aMLR_BV[0],aLsol[1]*aMLR_BV[1],aLsol[2]*aMLR_BV[2])
        
        #calculating the Msrc values for each annulus
        aMsrc_814_BV_ab0 = aLsol814*aMLR_BV_Vk_ab[0]
        aMsrc_814_BV_ab1 = aLsol814*aMLR_BV_Vk_ab[1]
        aMsrc_814_BV_ab2 = aLsol814*aMLR_BV_Vk_ab[2]
        aMsrc_814_BV_ab3 = aLsol814*aMLR_BV_Vk_ab[3]
        aMsrc_814_BV_ab4 = aLsol814*aMLR_BV_Vk_ab[4]
        aMsrc_814_BV_ab5 = aLsol814*aMLR_BV_Vk_ab[5]
        aMsrc_814_BV_ab6 = aLsol814*aMLR_BV_Vk_ab[6]
        aMsrc_814_BV_ab = (aMsrc_814_BV_ab0,aMsrc_814_BV_ab1,aMsrc_814_BV_ab2,aMsrc_814_BV_ab3,aMsrc_814_BV_ab4,aMsrc_814_BV_ab5,aMsrc_814_BV_ab6)
    
        #calculating the 7 Msrc values, one from each set of ab values
        Msrc_814_BV_ab0 = np.sum(aMsrc_814_BV_ab[0])
        Msrc_814_BV_ab1 = np.sum(aMsrc_814_BV_ab[1])
        Msrc_814_BV_ab2 = np.sum(aMsrc_814_BV_ab[2])
        Msrc_814_BV_ab3 = np.sum(aMsrc_814_BV_ab[3])
        Msrc_814_BV_ab4 = np.sum(aMsrc_814_BV_ab[4])
        Msrc_814_BV_ab5 = np.sum(aMsrc_814_BV_ab[5])
        Msrc_814_BV_ab6 = np.sum(aMsrc_814_BV_ab[6])
        Msrc_814_BV_ab = (Msrc_814_BV_ab0,Msrc_814_BV_ab1,Msrc_814_BV_ab2,Msrc_814_BV_ab3,Msrc_814_BV_ab4,Msrc_814_BV_ab5,Msrc_814_BV_ab6)
    
        #best value for each annulus
        bestval_annular_Msrc = np.zeros(40)
        for j in range(len(radii)):
            bestval_annular_Msrc[j] = ((aMsrc_814_BV_ab0[j]+aMsrc_814_BV_ab1[j]+aMsrc_814_BV_ab2[j]+aMsrc_814_BV_ab3[j]+aMsrc_814_BV_ab4[j]+aMsrc_814_BV_ab5[j]+aMsrc_814_BV_ab6[j])/7)
    
        #best value and std, printed
        Msrc_814_BV = np.mean(Msrc_814_BV_ab)
        Msrc_814_BV_std = np.std(Msrc_814_BV_ab)
        #print('Msrc,814W,B-V',Msrc_814_BV/1e11)
        #print('Msrc,814W,B-V std',Msrc_814_BV_std/1e11)
    
        #calculate mass associated with each annulus in solar units, based on one MLR estimate for the entire galaxy
        bM_BV_B = aLsol[0]*bMLR_BV_B
        bM_BV_V = aLsol[1]*bMLR_BV_V
        bM_BV_J = aLsol[2]*bMLR_BV_J
        bmass = (bM_BV_B,bM_BV_V,bM_BV_J)
    
        #best values
        annular_Msic_814_BV_ab0 = aLsol814*MLR_BV_Vk[0]
        annular_Msic_814_BV_ab1 = aLsol814*MLR_BV_Vk[1]
        annular_Msic_814_BV_ab2 = aLsol814*MLR_BV_Vk[2]
        annular_Msic_814_BV_ab3 = aLsol814*MLR_BV_Vk[3]
        annular_Msic_814_BV_ab4 = aLsol814*MLR_BV_Vk[4]
        annular_Msic_814_BV_ab5 = aLsol814*MLR_BV_Vk[5]
        annular_Msic_814_BV_ab6 = aLsol814*MLR_BV_Vk[6]
        annular_Msic_814_BV_ab = (annular_Msic_814_BV_ab0,annular_Msic_814_BV_ab1,annular_Msic_814_BV_ab2,annular_Msic_814_BV_ab3,annular_Msic_814_BV_ab4,annular_Msic_814_BV_ab5,annular_Msic_814_BV_ab6)
        
        #best value for each annulus
        bestval_annular_Msic = np.zeros(40)
        for j in range(len(radii)):
            bestval_annular_Msic = (annular_Msic_814_BV_ab[0]+annular_Msic_814_BV_ab[1]+annular_Msic_814_BV_ab[2]+annular_Msic_814_BV_ab[3]+annular_Msic_814_BV_ab[4]+annular_Msic_814_BV_ab[5]+annular_Msic_814_BV_ab[6])/7
    
        #getting seven values for total mass of the galaxy
        Msic_814_BV_ab0 = np.sum(annular_Msic_814_BV_ab0)
        Msic_814_BV_ab1 = np.sum(annular_Msic_814_BV_ab1)
        Msic_814_BV_ab2 = np.sum(annular_Msic_814_BV_ab2)
        Msic_814_BV_ab3 = np.sum(annular_Msic_814_BV_ab3)
        Msic_814_BV_ab4 = np.sum(annular_Msic_814_BV_ab4)
        Msic_814_BV_ab5 = np.sum(annular_Msic_814_BV_ab5)
        Msic_814_BV_ab6 = np.sum(annular_Msic_814_BV_ab6)
        Msic_814_BV_ab = (Msic_814_BV_ab0,Msic_814_BV_ab1,Msic_814_BV_ab2,Msic_814_BV_ab3,Msic_814_BV_ab4,Msic_814_BV_ab5,Msic_814_BV_ab6)
        #NOTE: taking the mean of Msic_814_BV_ab will give you the same thing as Msic_814_BV
    
        #plotting mass vs radius
        acolors = ['b--','g--','r--']
        bcolors = ['b', 'g', 'r']
        dot = ['bo','go','ro']
        labeling = ['475 nm','814 nm','1600 nm']
        
        ax = fig.add_subplot(1,1,1)
        
        # FIG 1: plotting the specific annular (specific aMLR) mass
        for k in range(0,len(acolors)):
            ax.plot(radii, amass[k], acolors[k], marker='o', label=str(labeling[k]))
            ax.plot(radii, amass[k], dot[k])
        plt.xlabel('Radius (pixels)',fontsize=14)
        plt.ylabel('Mass (solar masses)',fontsize=14)
        plt.title(galaxies[w] + ' Mass vs. Radius, (Mass Profile)',fontsize=16)
        plt.tight_layout()
        legend = ax.legend(loc='upper right')
        # here is some new stuff for you
        pdf.savefig()
        plt.close()
            
        # FIG 2: plotting the broad (single bMLR) annular mass, the 'light mass' as I call it
        fig = plt.figure()
        bx = fig.add_subplot(1,1,1)
        for k in range(0,len(bcolors)):
            #we changed from bmass[k] to bmass[0][k] to fix dimensions, it may not be what we actually we want to plot
            bx.plot(radii, bmass[k], bcolors[k], marker='o', label=str(labeling[k]))
            bx.plot(radii, bmass[k], dot[k])
            
        plt.xlabel('Radius (pixels)',fontsize=14)
        plt.ylabel('Mass (solar masses)',fontsize=14)
        plt.tight_layout()
        plt.title(galaxies[w] + ' Mass vs. Radius, (Light Profile)',fontsize=16)
        #adding the legend
        legend = bx.legend(loc='upper right')
        
        # plotting the mass/area vs radius, converting radius units from pixels to kpc to get mass surface density units
        
        # first creating an array with areas of shells in proper units of kpc
        kpc_area = np.zeros(len(area))
        bestval_annular_Msrc_ovr_area = np.zeros(len(area))
        bestval_annular_Msic_ovr_area = np.zeros(len(area))
        for j in range(0,len(area)):
            kpc_area[j] = area[j]*radToKpc**2
           
        # now calculating mass/area (mass surface density) in units of solar masses/kpc for bestval_annular_Msrc and bestval_annular_Msic and also radius in kpc units
        bestval_annular_Msrc_ovr_area = bestval_annular_Msrc /kpc_area
        bestval_annular_Msic_ovr_area = bestval_annular_Msic /kpc_area
        kpc_radius = radii*radToKpc
        pdf.savefig()
        plt.close()

        fig = plt.figure()
        # FIG 3:  now plotting bestval_annular_Msrc_ovr_area and bestval_annular_Msic_ovr_area vs radius in kpc
        ax = fig.add_subplot(1,1,1)
        ax.plot(kpc_radius, bestval_annular_Msrc_ovr_area, 'g--', marker='s', label='Mass Profile')#label=str(alabeling[1]))
        ax.plot(kpc_radius, bestval_annular_Msrc_ovr_area, 'g--')
        plt.xlabel('Radius (kpc)',fontsize=14)
        plt.ylabel('Mass Density (M_sol/area)',fontsize=14)
        plt.tight_layout()
        plt.title(galaxies[w] + ' Mass Density vs. Radius, Mass and Light Profiles',fontsize=15)
        legend = bx.legend(loc='upper right')
        
        #plotting bestval_annular_Msic_ovr_area vs radius in kpc
        ax.plot(kpc_radius, bestval_annular_Msic_ovr_area, 'yellowgreen', marker='o', label='Light Profile')#label=str(blabeling[1]))
        ax.plot(kpc_radius, bestval_annular_Msic_ovr_area, 'yellowgreen')
        plt.xlabel('Radius (kpc)',fontsize=14)
        plt.ylabel('Mass Density (M_sol/kpc^2)',fontsize=14)
        plt.tight_layout()
        plt.title(galaxies[w] + ' Mass Density vs. Radius, Mass and Light Profiles',fontsize=15)
        legend = ax.legend(loc='upper right')
            
        #calculating total mass (Msrc) for annular MLR (814 filter only)
        total_annular_Msrc_F814W = np.sum(bestval_annular_Msrc)
        print('Msrc,814,BV total', np.round(total_annular_Msrc_F814W/1e11,2),'+/-', np.round(Msrc_814_BV_std/1e11,2))
    
        #calculating total mass (Msic) for single MLR (814 filter only)
        total_singular_Msic_F814W = np.sum(bestval_annular_Msic)
        print('Msic,814,BV total', np.round(total_singular_Msic_F814W/1e11,2), '+/-', np.round(Msic_814_BV_std/1e11,2))
    
        #calculating %amass and %bmass in first 5 annuli
        Msrc_first_5 = np.sum(bestval_annular_Msrc[0:4])
        pct_Msrc_first_5 = Msrc_first_5/total_annular_Msrc_F814W*100
        Msic_first_5 = np.sum(bestval_annular_Msic[0:4])
        pct_Msic_first_5 = Msic_first_5/total_singular_Msic_F814W*100
        
        print('% Msrc first 5', round(pct_Msrc_first_5,2))
        print('% Msic first 5', np.round(pct_Msic_first_5,2))
    
        pdf.savefig()
        plt.close()
    
