import majoranaJJ.operators.sparse_operators as spop #sparse operators
import majoranaJJ.lattice.nbrs as nb #neighbor arrays
import majoranaJJ.lattice.shapes as shps #lattice shapes
import majoranaJJ.modules.plots as plots #plotting functions
import numpy as np

Nx = 20
Ny = 20
Wj = 6  #Junction width
cutx = 2 #nodule size in x
cuty = 2 #nodule size in y

coor = shps.square(Nx, Ny)
NN = nb.NN_Arr(coor)
NNb = nb.Bound_Arr(coor)

D_test = spop.Delta(coor, Wj = Wj, delta = 0.3, phi = np.pi, cutx = cutx, cuty = cuty)
plots.junction(coor, D_test, savenm = 'nodule.jpg')
