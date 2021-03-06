import sys
import os
import gc

import numpy as np
import matplotlib.pyplot as plt
import matplotlib.cm as cm
import matplotlib.patches as patches
import scipy.sparse as sparse
import scipy.linalg as LA
import scipy.sparse.linalg as spLA

import majoranaJJ.operators.sparse.qmsops as spop #sparse operators
import majoranaJJ.lattice.nbrs as nb #neighbor arrays
import majoranaJJ.lattice.shapes as shps #lattice shapes
import majoranaJJ.modules.plots as plots #plotting functions

from majoranaJJ.operators.sparse.potentials import Vjj #potential JJ
dir = os.getcwd()
###################################################
#Defining System
Nx = 3 #Number of lattice sites along x-direction
Ny = 408 #Number of lattice sites along y-direction
ax = 50 #lattice spacing in x-direction: [A]
ay = 50 #lattice spacing in y-direction: [A]
Wj = 11 #Junction region
cutx = 0 #width of nodule
cuty = 0 #height of nodule

Junc_width = Wj*ay*.1 #nm
SC_width = ((Ny - Wj)*ay*.10)/2 #nm
Nod_widthx = cutx*ax*.1 #nm
Nod_widthy = cuty*ay*.1 #nm
print("Nodule Width in x-direction = ", Nod_widthx, "(nm)")
print("Nodule Width in y-direction = ", Nod_widthy, "(nm)")
print("Junction Width = ", Junc_width, "(nm)")
print("Supercondicting Lead Width = ", SC_width, "(nm)")
###################################################
coor = shps.square(Nx, Ny) #square lattice
NN = nb.NN_Arr(coor) #neighbor array
NNb = nb.Bound_Arr(coor) #boundary array
lat_size = coor.shape[0]

Lx = (max(coor[:, 0]) - min(coor[:, 0]) + 1)*ax #Unit cell size in x-direction
Ly = (max(coor[:, 1]) - min(coor[:, 1]) + 1)*ay #Unit cell size in y-direction
print("Lattice size in x-direction", Lx*.1, "(nm)")
print("Lattice size in y-direction", Ly*.1, "(nm)")
###################################################
#Hamiltonian Parameters
alpha = 100 #Spin-Orbit Coupling constant: [meV*A]
gx = 0 #parallel to junction: [meV]
gz = 0 #normal to plane of junction: [meV]
delta = 1.0 #Superconducting Gap: [meV]
Vsc = -30 #Amplitude of potential: [meV]
V = Vjj(coor, Wj = Wj, Vsc = Vsc, Vj = 0, cutx = cutx, cuty = cuty)
#####################################
k = 44 #This is the number of eigenvalues and eigenvectors you want
mu_steps = 500 #Number of kx values that are evaluated
mu_i = -50
mu_f = -100
mu = np.linspace(mu_f, mu_i, mu_steps)  #Chemical Potential: [meV]
bands = np.zeros((mu_steps, k))
cmap = cm.get_cmap('Oranges')

dirS = 'e_mu_data'
if not os.path.exists(dirS):
    os.makedirs(dirS)
try:
    PLOT = str(sys.argv[1])
except:
    PLOT = 'F'
if PLOT != 'P':
    for j in range(mu_steps):
        print(mu_steps - j)
        H = spop.HBDG(coor, ax, ay, NN, NNb=NNb, Wj=Wj, cutx=cutx, cuty=cuty, V=V, mu=mu[j], alpha=alpha, delta=delta, phi=0, qx=0, periodicX=True)
        eigs, vecs = spLA.eigsh(H, k=k, sigma=0, which='LM')
        idx_sort = np.argsort(eigs)
        eigs = eigs[idx_sort]

        bands[j, :] = eigs

    np.save("%s/bands_nophase Lx = %.1f Ly = %.1f Wsc = %.1f Wj = %.1f nodx = %.1f nody = %.1f alpha = %.1f delta = %.2f Vj = %.1f  mu_i = %.1f mu_f = %.1f.npy" % (dirS, Lx*.1, Ly*.1, SC_width, Junc_width, Nod_widthx,  Nod_widthy, alpha, delta, Vj, mu_i, mu_f), bands)
    np.save("%s/mu_nophase Lx = %.1f Ly = %.1f Wsc = %.1f Wj = %.1f nodx = %.1f nody = %.1f alpha = %.1f delta = %.2f Vj = %.1f  mu_i = %.1f mu_f = %.1f.npy" % (dirS, Lx*.1, Ly*.1, SC_width, Junc_width, Nod_widthx,  Nod_widthy, alpha, delta, Vj, mu_i, mu_f), mu)
else:
    bands = np.load("%s/bands_nophase Lx = %.1f Ly = %.1f Wsc = %.1f Wj = %.1f nodx = %.1f nody = %.1f alpha = %.1f delta = %.2f Vj = %.1f  mu_i = %.1f mu_f = %.1f.npy" % (dirS, Lx*.1, Ly*.1, SC_width, Junc_width, Nod_widthx,  Nod_widthy, alpha, delta, Vj, mu_i, mu_f))
    mu = np.load("%s/mu_nophase Lx = %.1f Ly = %.1f Wsc = %.1f Wj = %.1f nodx = %.1f nody = %.1f alpha = %.1f delta = %.2f Vj = %.1f  mu_i = %.1f mu_f = %.1f.npy" % (dirS, Lx*.1, Ly*.1, SC_width, Junc_width, Nod_widthx,  Nod_widthy, alpha, delta, Vj, mu_i, mu_f))

    fig = plt.figure()
    ax = fig.add_subplot(1, 1, 1)
    ax.patch.set_facecolor('black')

    for j in range(bands.shape[1]):
        ax.plot(mu, bands[:, j], c = cmap(0), zorder = 0)

    ax.set_xlabel(r"$\mu$ (meV)")
    ax.set_ylabel("E (meV)")
    ax.set_title(r"Lx = %.1f nm, Ly = %.1f nm, $\Delta$ = %.2f meV, $\alpha$ = %.2f meV A, $W_{sc}$ = %.1f nm, $W_J$ = %.1f nm, $Nodule_x$ = %.1f nm, $Nodule_y$ = %.1f nm" % (Lx*.1, Ly*.1, delta, alpha, SC_width, Junc_width, Nod_widthx, Nod_widthy), loc = 'center', wrap=True)
    ax.set_ylim(-1.5, 1.5)
    plt.subplots_adjust(top=0.85)
    plt.savefig("e_mu_phase.png")
    plt.show()
