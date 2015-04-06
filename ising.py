from ipythonblocks import BlockGrid, Block
from IPython.display import clear_output
import time

import random as rand
import numpy as np

from images2gif import writeGif
from PIL import Image
import os
import re
import sys

def natural_sort(l): 
    convert = lambda text: int(text) if text.isdigit() else text.lower() 
    alphanum_key = lambda key: [ convert(c) for c in re.split('([0-9]+)', key) ] 
    return sorted(l, key = alphanum_key)

def make_png(array, size, fname):
    """turn an rgb array into a png"""
    newimage = Image.new('RGB', (len(array[0]), len(array)))  # type, size
    newimage.putdata([tuple(pixel) for row in array for pixel in row])
    return newimage.resize(size, Image.LINEAR)
    if save == True:
        newimage.save(fname)  # takes type from filename extension
    if show == True:
        plt.imshow(newimage)
        plt.show()

def Es2Cv(T,U,U2):
    """Convert potential energies to heat capacity
    Parameters
    ----------
    T : list
        list of temperatures
    U : list
        list of average potentials at each temp
    U2 : list
        list of averages of the squared potentials at each temp"""
    Cv = list()
    for i in range(len(T)):
        Cv.append(float(U2[i]-U[i]**2)/T[i]**2)
    return Cv

class Lattice(BlockGrid):

    def __init__(self, y, x, dist, T=2.5, nghbrs=4, size=10):
        """Create a lattice of spin up and down electrons
        Parameters
        ----------
        y : int
            length of the lattice's y dimension
        x : int
            length of the lattice's x dimension
        dist : float
            the distribution of spin up to spin down (between 0 and 1)
        T : float or list
            Given a number, the lattice will remain at a constant temp
            throughout anamations and analysis. However given a list of
            temperatures the lattice will progress through them during
            animation.
        nghbrs : int
            the number of neighbors influencing a particular unit (4 or 8)
        size : int
            size of the rendered units
        """
        super(Lattice,self).__init__(x, y, fill=(0,0,0), block_size=size, lines_on=False)
        self.nghbrs = nghbrs
        self.size = size
        self.dist = dist
        for unit in self:
            self._unit_init(unit, dist, nghbrs)
        self.rgbs= list()
        self.U = list()
        self.S = list()
        if isinstance(T, (list,int,float)):
            self.T = T
        else:
            raise ValueError("'T' must be a list or a number")
        self.directory = None
        self.fnames = None

    def _initialize_grid(self, fill):
        grid = [[Unit(*fill, size=self._block_size)
                for col in range(self.width)]
                for row in range(self.height)]
        self._grid = grid
    
    def _unit_init(self, unit, dist, nghbrs):
        """initialize a single unit"""
        prob = rand.random()
        if prob<dist:
            unit.set_colors(255,255,255)
        elif prob==0.5:
            self.assign(unit,dist)
        unit.lattice = self
        if nghbrs in (4,8):
            unit.nghbrs = nghbrs
        else:
            raise ValueError('nghbrs (or number of neighbors considered) must be 4 or 8')

    def iterate(self, iterations, index=None):
        """Iterate through random flips at a particular temperature
        Parameters
        ----------
        iterations : int
            the number of flips performed
        index : int
            index of the temperature in self.T (if it's a list)"""
        for its in range(iterations):
            if isinstance(self.T,list):
                temp = self.T[index]
            else:
                temp = self.T
            shape = self.shape
            i=rand.randrange(0,shape[0])
            j=rand.randrange(0,shape[1])

            unit = self[i,j]
            local_spin = unit.local_spin()
            U_diff = 2*unit.spin*local_spin

            if U_diff<=0:
                unit.flip()
            elif rand.random()<np.exp(-U_diff/temp):
                unit.flip()

        spins = list()
        potentials = list()
        for i in range(shape[0]):
            for j in range(shape[1]):
                u = self[i,j]
                s = u.spin
                ls = u.local_spin()
                potentials.append(-2*s*ls)
                spins.append(s)
        self.S.append(spins)
        self.U.append(potentials)
        self.rgbs.append(self.rgb())

    def rgb(self):
        """return an rgb array representation of self"""
        rgb=[]
        ishape=self.shape[0]
        jshape=self.shape[1]
        for i in range(ishape):
            col=[]
            for j in range(jshape):
                col.append(self[j,i].rgb)
            rgb.append(col)
        rgb=np.array(rgb)
        return rgb

    def animate(self, iterations, frames=None, display=False, stop=0.2):
        """animate the model
        Parameters
        ----------
        iterations : int
            the number of iterations performed at each frame
        frames : int
            if self.T is not a list then frames specifies how many times
            to run the model at the given temperature with each from
            continuing from the state of the last. otherwise, the number
            of frames is equivalent to the number of temps in self.T
        display : bool
            if True perform a crude animation inside the notebook
        stop : float
            if display is True, this this is the time gap between each frame
        """
        if isinstance(self.T,list):
            frames = len(self.T)
        for frame in range(frames):
            if display:
                clear_output()
            self.iterate(iterations, frame)
            if display:
                self.show()
                time.sleep(stop)

    def make_pngs(self, size=(500,500), directory='frames', fnames='nbim'):
        """create a set of png's using the states generated during animation
        Parameters
        ----------
        size : tuple
            dimensions of the png's
        directory : str
            the name of the directory the images should be stored in
        fnames : str
            the base name of the png image files
        Notes
        -----
        directory must already exist in order to save the images
        """
        if len(self.rgbs)==0:
            raise ValueError('no lattice states: initialize with `self.animate(display=False)`')
        for i in range(len(self.rgbs)):
            rgb = self.rgbs[i]
            fname = directory+'/'+fnames+str(i)+'.png'
            im = make_png(rgb, size, fname)
            im.save(fname)
        self.directory = directory
        self.fnames = fnames

    def make_gif(self, fname, duration=0.1, size=(500,500)):
        """create a gif of up to 160 frames using images from a directory
        Parameters
        ----------
        fname : str
            name of the new gif file
        duration : float
            duration of each frame
        size : tuple
            dimensions of the new gif"""
        if self.directory is None or self.fnames is None:
            raise IOError("must initialize frames with `self.make_pngs()`")
        raw = [fn for fn in os.listdir(self.directory) if fn.startswith(self.fnames)]
        file_names = sorted(raw)
        file_names = natural_sort(file_names)
        images = [Image.open(self.directory+'/'+fn) for fn in file_names]
        
        for im in images:
            im.thumbnail(size, Image.ANTIALIAS)

        writeGif(fname+'.GIF', images, duration)

    def get_potentials(self):
        """return average energy squared energy lists after animation"""
        u_avg = list()
        u_sqrd_avg = list()
        if len(self.rgbs)==0:
            raise ValueError('no lattice states: initialize with `self.animate(display=False)`')
        for iteration in self.U:
            u_avg.append(np.mean(iteration))
            u_sqrd_avg.append(np.mean([u**2 for u in iteration]))
        return u_avg, u_sqrd_avg

    def analyze(self):
        """return avg magnitization, avg energy, and heat capacity lists"""
        s_avg = list()
        for iteration in self.S:
            s_avg.append(np.mean(iteration))
        u_avg, u_sqrd_avg = self.get_potentials()
        cv = Es2Cv(self.T,u_avg,u_sqrd_avg)
        return s_avg, u_avg, cv

    def reset(self):
        """reinitialize the lattice and clear animation history"""
        args = (self.shape[0],self.shape[1],self.dist,
            self.T,self.size,self.nghbrs)
        self.__init__(*args)

class Unit(Block):

    def __init__(self, *args, **kwargs):
        super(Unit,self).__init__(*args, **kwargs)
        self.lattice = None
        self.nghbrs = 4

    def get_neighbors(self):
        """return neighboring units in the lattice"""
        i = self.row
        j = self.col
        lattice = self.lattice
        limits = lattice.shape
        nghbrs = self.nghbrs
        neighbors = list()
        for n in range(0, nghbrs):
            new_i = i+int(round(np.cos(2*n*np.pi/nghbrs),0))
            new_j = j+int(round(np.sin(2*n*np.pi/nghbrs),0))
            if new_i!=limits[0] and new_j!=limits[1]:
                unit = lattice[new_i,new_j]
            else:
                if i==limits[0]:
                    unit = lattice[0,new_j]
                elif j==limits[1]:
                    unit = lattice[new_i,0]
                else:
                    unit = lattice[0,0]
            neighbors.append(unit)
        return neighbors
        
    def local_spin(self):
        """return the total spin of neighboring units in the lattice"""
        total = 0
        for u in self.get_neighbors():
            dist = np.sqrt((self.row-u.row)**2+(self.col-u.col)**2)
            total += float(u.spin)/dist
        return total

    def flip(self):
        """flip the spin of the unit"""
        rgb = tuple(abs(np.array(self.rgb)-255))
        self.set_colors(*rgb)

    @property
    def spin(self):
        if self.rgb==(255,255,255):
            return -1
        elif self.rgb==(0,0,0):
            return 1
        else:
            raise ValueError('improper initialize: rgb must be black or white')

    @spin.setter
    def spin(self, value):
        if value==-1:
            self.set_colors(255,255,255)
        elif value==1:
            self.set_colors(0,0,0)
        else:
            ValueError('spin must be 1 or -1')