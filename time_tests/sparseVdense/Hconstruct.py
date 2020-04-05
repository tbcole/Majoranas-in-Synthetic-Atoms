import time
import numpy as np

import majoranaJJ.lattice.neighbors as nb #neighbor arrays
import majoranaJJ.lattice.shapes as shps #lattice shapes
import majoranaJJ.etc.plots as plots #plotting functions

#Compared packages
import majoranaJJ.operators.sparsOP as spop #sparse operators
import majoranaJJ.operators.densOP as dpop
#dense operators

Nx = 100 #Number of lattice sites allong x-direction
Ny = 100 #Number of lattice sites along y-direction
ax = 2 #lattice spacing in x-direction: [A]
ay = 2 #lattice spacing in y-direction: [A]

start = time.time()
coor = shps.square(Nx, Ny) #square lattice
NN = nb.NN_Arr(coor) #neighbor array
NNb = nb.NN_Bound(coor) #boundary array
end = time.time()
print("Time to create lattice matrices, implemented using NumPy with revised algorithms", end-start)
print("-------- ")
num = 2 # This is the number of eigenvalues and eigenvectors you want
steps = 30 #Number of kx and ky values that are evaluated

start = time.time()
H_dense = dpop.H0(coor, ax, ay, NN)
end = time.time()
print("Time for DENSE OPERATOR (Numpy) for size {} = {}".format(H_dense.shape, end-start),"[s]")

print("----------")

start = time.time()
H_sparse = spop.H0(coor, ax, ay, NN)
end = time.time()
print("Time for SPARSE OPERATOR (Scipy) for size {} = {}".format(H_sparse.shape, end-start), "[s]")
