# Aleks Diamond-Stanic
# May 31, 2019
# Copied from cp_dap_plates_mpl# Imports


import os
import numpy as np
from astropy.io import fits
import matplotlib.pyplot as plt
from matplotlib import cm
import matplotlib.colors as colors
from matplotlib.backends.backend_pdf import PdfPages
import glob
from astropy.cosmology import FlatLambdaCDM
import astropy.units as u

# function for plotting maps of relevant quantities
def daplot(quantity, qmin, qmax):
        ax.set_xlim(0, size)
        ax.set_ylim(0, size)
        ax.set_xticklabels(())
        ax.set_yticklabels(())
        plt.imshow(quantity, origin='lower', interpolation='nearest',
                   norm=colors.LogNorm(vmin=qmin, vmax=qmax), cmap=cm.coolwarm)
        plt.colorbar()

# minimum and maximum emission-line fluxes for plot ranges
fmin = 1e-19
fmax = 1e-16

# define a standard cosmology
cosmo = FlatLambdaCDM(H0=70 * u.km / u.s / u.Mpc, Om0=0.3)

# directory for relevant Data Reduction Pipeline (drp) and Data Analysis Pipeline (DAP) information
mpl7_dir = os.environ['MANGADIR_MPL7'] #Be aware that this directory syntax might need revision
drp = fits.open(mpl7_dir+'drpall-v2_4_3.fits')
drpdata = drp[1].data

# specific the plate of interest
from os.path import isdir, join
all_plates = [f for f in os.listdir(mpl7_dir+'HYB10-GAU-MILESHC/') if isdir(join(mpl7_dir+'HYB10-GAU-MILESHC/', f))]
print('List of plates: \n',all_plates,'\n')
plate = int(input('Please enter plate number: '))
lines = glob.glob(mpl7_dir+'HYB10-GAU-MILESHC/*/*/*'+ str(plate) +'*MAPS-HYB10-GAU-MILESHC.fits*')
filename = 'MPL7_dap_multi_'+str(plate)+'_quicklook.pdf'

# for bookkeeping purposes, here's an array of emission-line names
eml = ['OIId---3728', 'Hb-----4862', 'OIII---4960', 'OIII---5008', 'OI-----6302', 'OI-----6365', 'NII----6549', 'Ha-----6564', 'NII----6585', 'SII----6718', 'SII----6732']

with PdfPages(filename) as pdf:
    for i in range(0, len(lines)):
        name = lines[i]


        # THIS PART NEEDS ADJUSTING. THERE IS ONE PLATE WITH MORE THAN 4 NUMBERS
        # parse the plate and galaxy information from the filename
        start = name.find('manga-')
        plt1 = start + 6
        plt2 = plt1 + 4
        if str(name[plt2]) != str('-'):
            plt2 = plt2+1
        plate = int(name[plt1:plt2])

        end = name.find('-MAPS-HYB10-GAU-MILESHC')
        gal2 = end
        gal1 = plt2+1
        galaxy = int(name[gal1:gal2])
        print(plate, galaxy)

        # find the index of this galaxy in the drpall file
        match = np.where((drpdata.field('plate') == plate) & (drpdata.field('ifudsgn') == str(galaxy)))

        # read in the appropriate DAP file and Halpha flux information
        hdu_dap = fits.open(name)
        #hdu_dap.info()
        dap_ha_sflux = hdu_dap['EMLINE_SFLUX'].data[18,:,:]
        dap_ha_sivar = hdu_dap['EMLINE_SFLUX_IVAR'].data[18,:,:]

        # create arrays that correspond to x and y coordinates for each spaxel
        size = len(hdu_dap['EMLINE_GFLUX'].data[0,:])
        xpos = np.zeros([size, size])
        ypos = np.zeros([size, size])

        for j in range(0, size):
            for k in range(0, size):
                xpos[j,k] = k
                ypos[j,k] = j

        # read in the position angle and axis from from the NSA
        theta = drpdata.field('nsa_sersic_phi')[match][0]
        ba = drpdata.field('nsa_sersic_ba')[match][0]
        inc = np.arccos(ba)
        re_sersic = drpdata.field('nsa_sersic_th50')[match]
        
        # redefine x=0 and y=0 to be in the center of the field
        xprime = xpos - np.median(xpos)
        yprime = ypos - np.median(ypos)

        # compute the on-sky x and y coordiates defined by the major axis
        trad = np.radians(theta-90)
        xproj = xprime * np.cos(trad) + yprime * np.sin(trad)
        yproj = xprime * np.sin(trad) * (-1.) + yprime * np.cos(trad)
        zproj = yproj / np.sin(inc) * np.cos(inc)

        # calculate the radius of each pixel in the plane of the disk [units: pixels]
        radpix = np.sqrt(xproj**2 + (yproj/ba)**2)

       	#identify all pixels wihtin a galactocentric radius of two times the half-light radius

 	# figure out the conversion between pixel size and kpc
        z = drpdata.field('nsa_z')[match][0]
        radkpc = radpix / cosmo.arcsec_per_kpc_proper(z) * (0.5 * u.arcsec)
        re_sersic_kpc = re_sersic / cosmo.arcsec_per_kpc_proper(z)

        # compute values along the x and y axis of the disk and the z axis above the disk
        xproj_kpc = xproj / cosmo.arcsec_per_kpc_proper(z) * (0.5 * u.arcsec)
        yproj_kpc = yproj / ba / cosmo.arcsec_per_kpc_proper(z) * (0.5 * u.arcsec)
        zproj_kpc = zproj / ba / cosmo.arcsec_per_kpc_proper(z) * (0.5 * u.arcsec)
        cen = abs(xproj_kpc) < (1. * u.kpc)

        radkpc_map = np.zeros([size, size])
        xproj_kpc_map = np.zeros([size, size])
        yproj_kpc_map = np.zeros([size, size])
        zproj_kpc_map = np.zeros([size, size])

        for j in range(0, size):
            for k in range(0, size):
                if (dap_ha_sivar[j,k] > 0.):
                    radkpc_map[j,k] = radkpc[j,k] / u.kpc
                    yproj_kpc_map[j,k] = yproj_kpc[j,k] / u.kpc
                    zproj_kpc_map[j,k] = zproj_kpc[j,k] / u.kpc
                else:
                    radkpc_map[j,k] = radkpc[j,k] / u.kpc * (-1.)
        double_re_sersic_kpc = re_sersic_kpc * 1.0 *u.arcsec/u.kpc
        small = (radkpc_map < double_re_sersic_kpc)
        zproj_kpc_map_filtered = zproj_kpc_map
        zproj_kpc_map_filtered[small] = 0
        #zproj_kpc_map_filtered[small] = zproj_kpc_map_filtered[small]* -1
        
        # hdu_dap['EMLINE_GFLUX'].header
        #C01     = 'OII-3727'           / Data in channel 1                      
        #C02     = 'OII-3729'           / Data in channel 2                      
        #C03     = 'Hthe-3798'          / Data in channel 3                      
        #C04     = 'Heta-3836'          / Data in channel 4                      
        #C05     = 'NeIII-3869'         / Data in channel 5                      
        #C06     = 'Hzet-3890'          / Data in channel 6                      
        #C07     = 'NeIII-3968'         / Data in channel 7                      
        #C08     = 'Heps-3971'          / Data in channel 8                      
        #C09     = 'Hdel-4102'          / Data in channel 9                      
        #C10     = 'Hgam-4341'          / Data in channel 10                     
        #C11     = 'HeII-4687'          / Data in channel 11                     
        #C12     = 'Hb-4862 '           / Data in channel 12                     
        #C13     = 'OIII-4960'          / Data in channel 13                     
        #C14     = 'OIII-5008'          / Data in channel 14                     
        #C15     = 'HeI-5877'           / Data in channel 15                     
        #C16     = 'OI-6302 '           / Data in channel 16                     
        #C17     = 'OI-6365 '           / Data in channel 17                     
        #C18     = 'NII-6549'           / Data in channel 18                     
        #C19     = 'Ha-6564 '           / Data in channel 19                     
        #C20     = 'NII-6585'           / Data in channel 20                     
        #C21     = 'SII-6718'           / Data in channel 21                     
        #C22     = 'SII-6732'           / Data in channel 22   

        # hdu_dap['EMLINE_GFLUX'].data.shape # (22, 74, 74)

        
        #for j in range(0, len(hdu_dap['EMLINE_GVEL'].data)):
        # focus on the [O II] emisison line
        for j in range(0, 1):
            print(eml[j])

            # DAP: emission-line quantities
            dap_vel = hdu_dap['EMLINE_GVEL'].data[j,:,:]
            dap_vel_ivar = hdu_dap['EMLINE_GVEL_IVAR'].data[j,:,:]
            dap_vel_err = np.sqrt(1./dap_vel_ivar)
            dap_sig = hdu_dap['EMLINE_GSIGMA'].data[j,:,:]
            dap_sig_ivar = hdu_dap['EMLINE_GSIGMA'].data[j,:,:]
            dap_sig_err = np.sqrt(1./dap_sig_ivar)
            dap_flux = hdu_dap['EMLINE_GFLUX'].data[j,:,:]
            dap_mask = hdu_dap['EMLINE_GFLUX_MASK'].data[j,:,:]
            dap_ivar = hdu_dap['EMLINE_GFLUX_IVAR'].data[j,:,:]
            dap_err = np.sqrt(1./dap_ivar)
            dap_sflux = hdu_dap['EMLINE_SFLUX'].data[j,:,:]
            dap_smask = hdu_dap['EMLINE_SFLUX_MASK'].data[j,:,:]
            dap_sivar = hdu_dap['EMLINE_SFLUX_IVAR'].data[j,:,:]
            dap_serr = np.sqrt(1./dap_sivar)#*1.e-4

            # plot 1: galaxy coordinates in kpc
            fig = plt.figure()
            ax = fig.add_subplot(3,3,1)
            ax.set_xlim(0, size)
            ax.set_ylim(0, size)
            ax.set_xticklabels(())
            ax.set_yticklabels(())
            plt.imshow(zproj_kpc_map_filtered,#zproj_kpc_map[large],
                       origin='lower',
                       interpolation='nearest',
                       cmap=cm.coolwarm)
            plt.colorbar()
            plt.title('vertical distance [kpc]', fontsize=10)
            plt.suptitle(name)

            # plot 2/3: emission-line flux vs vertical distance
            ax = fig.add_subplot(4,2,2)
            ax.set_yscale("log", nonposy='clip')
            ax.set_ylim(fmin, fmax)
            ax.set_xlim(np.max(zproj_kpc_map)*(-1.), np.max(zproj_kpc_map))
            ax.scatter(zproj_kpc[cen], dap_ha_sflux[cen]*1.e-17, lw = 0, s=1)
            ax.scatter(zproj_kpc, dap_ha_sflux*1.e-17, lw = 0, s=0.2)
            ax.scatter(zproj_kpc[cen],  dap_sflux[cen]*1.e-17, lw = 0, color='red', s=1)
            ax.scatter(zproj_kpc,  dap_sflux*1.e-17, lw = 0, color='red', s=0.2)
            plt.title('emission-line flux vs vertical distance', fontsize=9)
            plt.text(0.,fmin*2.,'i='+str(round(inc * 180. / np.pi,2)), fontsize=9)

            # plot 4: emission-line SFLUX
            ax = fig.add_subplot(3,3,4)
            daplot(dap_sflux*1.e-17, fmin, fmax)
            plt.title(eml[j]+' SFLUX', fontsize=10)

            # plot 5: emission-line SFLUX serror
            ax = fig.add_subplot(3,3,5)
            daplot(dap_serr*1.e-17, fmin, fmax)
            plt.title(eml[j]+' SFLUX Error', fontsize=10)

            # plot 6: emission-line SFLUX signal-to-noise ratio
            ax = fig.add_subplot(3,3,6)
            daplot(dap_sflux/dap_serr, 0.1, 10.)
            plt.title(eml[j]+' SFLUX S/N', fontsize=10)

            # plot 7: emission-line flux / Halpha flux
            ax = fig.add_subplot(3,3,7)
            daplot(dap_sflux/dap_ha_sflux, 0.1, 10.)
            plt.title(eml[j]+'/HA', fontsize=10)

            #plot 8: emission-line velocity
            ax = fig.add_subplot(3,3,8)
            ax.set_xlim(0, size)
            ax.set_ylim(0, size)
            ax.set_xticklabels(())
            ax.set_yticklabels(())
            plt.imshow(dap_vel, origin='lower',
                       interpolation='nearest',
                       cmap=cm.coolwarm, vmin=-250, vmax=250)
            plt.colorbar()
            plt.title(eml[j]+' GVEL', fontsize=10)

            # plot 9: emission-line dispersion
            ax = fig.add_subplot(3,3,9)
            ax.set_xlim(0, size)
            ax.set_ylim(0, size)
            ax.set_xticklabels(())
            ax.set_yticklabels(())
            plt.imshow(dap_sig, origin='lower',
                       interpolation='nearest',
                       cmap=cm.YlOrRd, vmin=0, vmax=250)
            plt.colorbar()
            plt.title(eml[j]+' GSIGMA', fontsize=10)

            pdf.savefig()
            plt.close()


    print("KEEP IN MIND SOMETIMES YOU GET AN ERROR WHEN THE PROGRAM TRIES TO OPEN THE PDF. JUST GO TO THE DIRECTORY WHERE IT WAS CREATED AND OPEN IT MANUALLY.")
    os.system("open %s &" % filename)

