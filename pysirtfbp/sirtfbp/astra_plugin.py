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
import astra
import numpy as np
from six.moves import range
import six
from scipy.signal import fftconvolve
import scipy.ndimage.filters as snf

import os, errno

import base64, hashlib

def mkdir_p(path):
    try:
        os.makedirs(path)
    except OSError as exc: # Python >2.5
        if exc.errno == errno.EEXIST and os.path.isdir(path):
            pass
        else: raise

def getFilterFile(saveDir, proj_geom, ss, nIters, reg_grad):
    """Creates a filename in ``saveDir`` that is unique
    to the combination of input parameters.

    :param saveDir: Folder to save file in.
    :type saveDir: :class:`string`
    :param proj_geom: ASTRA projection geometry.
    :type proj_geom: :class:`dict`
    :param ss: Supersampling that is used.
    :type ss: :class:`int`
    :param nIters: Number of iterations that is used.
    :type nIters: :class:`int`
    """
    hs = ""
    for i,j in sorted(proj_geom.items()):
        try:
            for k,l in sorted(j.items()):
                try:
                    hs = hs + k + ": " + l.tostring().encode('ascii') + "; "
                except (AttributeError,UnicodeDecodeError):
                    hs = hs + k + ": " + str(l) + "; "
        except AttributeError:
            try:
                hs = hs + i + ": " + j.tostring().encode('ascii') + "; "
            except (AttributeError,UnicodeDecodeError):
                hs = hs + i + ": " + str(j) + "; "
    hs = hs + 'ss: ' + str(ss) + "; "
    hs = hs + 'nIters: ' + str(nIters) + "; "
    hs = hs + 'reg_grad: ' + str(reg_grad) + "; "
    fn = base64.b64encode(six.b(hashlib.md5(six.b(hs)).hexdigest())).decode('utf-8') + ".npy"
    ffn = os.path.join(saveDir,fn)
    return ffn

class plugin(astra.plugin.ReconstructionAlgorithm2D):
    """Reconstructs using the SIRT-FBP method [1].

    Options:

    'filter_dir': folder to cache computed filtes in
    'ss' (optional): supersampling to use during filter computation
    'reg_grad' (optional): amount of l2 gradient minimization
    
    [1] Pelt, D. M., & Batenburg, K. J. (2015). Accurately approximating algebraic 
        tomographic reconstruction by filtered backprojection. In
        Proceedings of the 13th International Meeting on Fully Three-Dimensional 
        Image Reconstruction in Radiology and Nuclear Medicine.
    """
    
    astra_name="SIRT-FBP"
    
    def customFBP(self, f):
        sf = np.zeros_like(self.s)
        padded = np.zeros(self.s.shape[1]*2)
        l = int(self.s.shape[1]/2.)
        r = l+self.s.shape[1]
        for i in range(sf.shape[0]):
            padded[l:r] = self.s[i]
            padded[:l] = padded[l]
            padded[r:] = padded[r-1]
            sf[i] = fftconvolve(padded,f[i],'same')[l:r]
        return (self.W.T*sf).reshape(self.v.shape)
    
    def initialize(self, cfg, filter_dir, ss=8, reg_grad=None):
        self.W = astra.OpTomo(self.pid)
        self.ang = self.pg['ProjectionAngles']
        self.fd = filter_dir
        mkdir_p(filter_dir)
        self.nd = self.pg['DetectorCount']
        if self.nd%2==0: self.nd += 1
        self.ss = ss
        self.rg = reg_grad
        self.iscuda = astra.projector.is_cuda(self.pid)

    def run(self, iterations):
        self.fn = getFilterFile(self.fd, self.pg, self.ss, iterations, self.rg)
        if os.path.exists(self.fn):
            flt = np.load(self.fn)
            self.v[:] = self.customFBP(flt)
            return
        nd = self.nd
        na = len(self.ang)
        pgc = astra.create_proj_geom('parallel',1.0,nd,self.ang)
        vgc = astra.create_vol_geom((nd,nd))
        if not self.iscuda:
            pidc = astra.create_projector('strip',pgc,vgc)
        x = np.zeros((nd,nd))
        xs = np.zeros((nd,nd))
        sf = np.zeros((na,nd))
        vid = astra.data2d.create('-vol',vgc)
        sid = astra.data2d.create('-sino',pgc)
        if self.iscuda:
            cfg = astra.astra_dict('FP_CUDA')
            cfg['options'] = {'DetectorSuperSampling':self.ss}
        else:
            cfg = astra.astra_dict('FP')
            cfg['ProjectorId']=pidc
        cfg['ProjectionDataId']=sid
        cfg['VolumeDataId']=vid
        fpid = astra.algorithm.create(cfg)
        if self.iscuda:
            cfg = astra.astra_dict('BP_CUDA')
            cfg['options'] = {'PixelSuperSampling':self.ss}
        else:
            cfg = astra.astra_dict('BP')
            cfg['ProjectorId']=pidc
        cfg['ProjectionDataId']=sid
        cfg['ReconstructionDataId']=vid
        bpid = astra.algorithm.create(cfg)
        vc = astra.data2d.get_shared(vid)
        sc = astra.data2d.get_shared(sid)
        x[nd//2,nd//2]=1
        alp = 1./self.s.size
        if self.rg:
            if self.rg*alp >=0.1:
                alp = 0.1/self.rg
        astra.log.info('Computing filter...')
        for i in range(iterations):
            if i%10==0: astra.log.info('{:.2f} % done'.format(100*float(i)/iterations))
            xs+=x
            vc[:] = x
            astra.algorithm.run(fpid)
            astra.algorithm.run(bpid)
            if self.rg:
                dx = x[:-1,:] - x[1:,:]
                dy = x[:,:-1] - x[:,1:]
                x[:-1,:] -= self.rg*dx*alp
                x[1:,:] += self.rg*dx*alp
                x[:,:-1] -= self.rg*dy*alp
                x[:,1:] += self.rg*dy*alp
            x -= vc*alp
        vc[:] = xs
        astra.algorithm.run(fpid)
        flt = sc.copy()/self.s.size
        astra.algorithm.delete([fpid,bpid])
        astra.algorithm.delete([vid,sid])
        np.save(self.fn,flt)
        self.v[:] = self.customFBP(flt)
        if not self.iscuda:
            astra.projector.delete(pidc)