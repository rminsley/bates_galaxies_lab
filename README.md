# bates_galaxies_lab

This repository includes code developed by members of the Bates
Galaxies Lab (sometimes called "the bagel," which in principle could
stand for Bates Astrophysics Galaxy Evolution Lab) at Bates College in
Lewiston, Maine.  Current lab members (as of the Fall 2016 semester),
include Aleks Diamond-Stanic (Assistant Professor of Physics and
Astronomy), Sophia Gottlieb (senior physics major, class of 2017), and
Joshua Rines (senior physics major, class of 2017).

# bgl_aper_phot.py

This code makes "postage stamp" visualizations of a galaxy in three
different filters, performs aperture photometry on each image, and
plots the flux (energy/area/time) in circular apertures centered on
the galaxy.

# bgl_gau_bkg.py

This code analyzes the distribution of pixel values for an entire
image and quantifies the mean background flux and its dispersion
by fitting a Gaussian function to a binned histogram of pixel values.

# bgl_image_stamp.py

This code reads in images of the same galaxy in three filters and
makes "postage stamp" visualizations with the goal of providing a
qualitative sense for how the morphology of the galaxy and its
luminosity change as a function of wavelength.  This code is expanded
upon in bgl_aper_phot.py and bgl_pix_vis.py.

# bgl_pix_vis.py

The code makes "postage stamp" visualizations of a galaxy in three
different filters and then produces color-magntidue diagrams that show
the relationship between flux in a given filter and the color measured
with respect to an adjacent filter for all pixels in the postage stamps.

# sg_*.py

Awesome code being developed by Sophia Gottlieb

# jr_*.py

Aweseome code being developed by Josh Rines

