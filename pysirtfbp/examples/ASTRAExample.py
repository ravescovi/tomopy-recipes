#-----------------------------------------------------------------------
#Copyright 2015 Daniel M. Pelt
#
#Contact: D.M.Pelt@cwi.nl
#Website: http://www.dmpelt.com
#
#
#This file is part of the PySIRT-FBP, a Python implementation of the
#SIRT-FBP tomographic reconstruction method.
#
#PySIRT-FBP is free software: you can redistribute it and/or modify
#it under the terms of the GNU General Public License as published by
#the Free Software Foundation, either version 3 of the License, or
#(at your option) any later version.
#
#PySIRT-FBP is distributed in the hope that it will be useful,
#but WITHOUT ANY WARRANTY; without even the implied warranty of
#MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
#GNU General Public License for more details.
#
#You should have received a copy of the GNU General Public License
#along with PySIRT-FBP. If not, see <http://www.gnu.org/licenses/>.
#
#-----------------------------------------------------------------------
import sirtfbp
import phantom
import astra
import numpy as np
import os

nd = 256
na = 32

# Create ASTRA geometries
vol_geom = astra.create_vol_geom(nd,nd)
proj_geom = astra.create_proj_geom('parallel',1.0,nd,np.linspace(0,np.pi,na,False))
pi = astra.create_projector('linear', proj_geom, vol_geom) # change 'linear' to 'cuda' for GPU
p = astra.OpTomo(pi)

# Load the phantom from disk
testPhantom = phantom.phantom(nd)

# Calculate the forward projection of the phantom
testSino = (p*testPhantom).reshape((na,nd))

# Add some noise to the sinogram
testSino = astra.add_noise_to_sino(testSino,10**3)

# Register plugin with ASTRA
astra.plugin.register(sirtfbp.plugin)

# Reconstruct the image using SIRT-FBP, FBP, and SIRT.
sfbpRec = p.reconstruct('SIRT-FBP',testSino,200, extraOptions={'filter_dir':os.getcwd()})
if astra.projector.is_cuda(pi):
    fbpRec = p.reconstruct('FBP_CUDA',testSino)
    sirtRec = p.reconstruct('SIRT_CUDA',testSino,200)
else:
    fbpRec = p.reconstruct('FBP',testSino)
    sirtRec = p.reconstruct('SIRT',testSino,200)

# Show the different reconstructions on screen
import pylab
pylab.gray()
pylab.subplot(221)
pylab.axis('off')
pylab.title('Phantom')
pylab.imshow(testPhantom,vmin=0,vmax=1)
pylab.subplot(222)
pylab.axis('off')
pylab.title('SIRT-FBP')
pylab.imshow(sfbpRec,vmin=0,vmax=1)
pylab.subplot(223)
pylab.axis('off')
pylab.title('FBP')
pylab.imshow(fbpRec,vmin=0,vmax=1)
pylab.subplot(224)
pylab.axis('off')
pylab.title('SIRT-200')
pylab.imshow(sirtRec,vmin=0,vmax=1)
pylab.tight_layout()
pylab.show()

