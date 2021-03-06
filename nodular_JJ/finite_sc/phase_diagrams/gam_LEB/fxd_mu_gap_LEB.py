import sys
import time
import os
import gc

import numpy as np
import matplotlib.pyplot as plt
import matplotlib.cm as cm
from scipy.signal import argrelextrema
import scipy.linalg as LA
import scipy.sparse.linalg as spLA

import majoranaJJ.operators.sparse_operators as spop #sparse operators
from majoranaJJ.operators.potentials import Vjj #potential JJ
import majoranaJJ.lattice.nbrs as nb #neighbor arrays
import majoranaJJ.lattice.shapes as shps #lattice shapes
import majoranaJJ.modules.plots as plots #plotting functions
import majoranaJJ.modules.gamfinder as gamfinder
from majoranaJJ.modules.checkers import boundary_check as bc
import majoranaJJ.modules.checkers as check
###################################################
#Defining System
Nx = 3 #Number of lattice sites along x-direction
Ny = 60 #Number of lattice sites along y-direction
ax = 50 #lattice spacing in x-direction: [A]
ay = 50 #lattice spacing in y-direction: [A]
Wj = 8 #Junction region
cutx = 0 #width of nodule
cuty = 0 #height of nodule
Nx, Ny, cutx, cuty, Wj = check.junction_geometry_check(Nx, Ny, cutx, cuty, Wj)
print("Nx = {}, Ny = {}, cutx = {}, cuty = {}, Wj = {}".format(Nx, Ny, cutx, cuty, Wj))

Junc_width = Wj*ay*.10 #nm
SC_width = ((Ny - Wj)*ay*.10)/2 #nm
Nod_widthx = cutx*ax*.1 #nm
Nod_widthy = cuty*ay*.1 #nm
print("Nodule Width in x-direction = ", Nod_widthx, "(nm)")
print("Nodule Width in y-direction = ", Nod_widthy, "(nm)")
print("Junction Width = ", Junc_width, "(nm)")
print("Supercondicting Lead Width = ", SC_width, "(nm)")
###################################################
coor = shps.square(Nx, Ny) #square lattice
NN = nb.NN_sqr(coor)
NNb = nb.Bound_Arr(coor)
lat_size = coor.shape[0]
print("Lattice Size: ", lat_size)

Lx = (max(coor[:, 0]) - min(coor[:, 0]) + 1)*ax #Unit cell size in x-direction
Ly = (max(coor[:, 1]) - min(coor[:, 1]) + 1)*ay #Unit cell size in y-direction
###################################################
#Defining Hamiltonian parameters
alpha = 100 #Spin-Orbit Coupling constant: [meV*A]
phi = np.pi #SC phase difference
delta = 1 #Superconducting Gap: [meV]
Vsc = 0 #SC potential: [meV]
Vj = 0 #Junction potential: [meV]
V = Vjj(coor, Wj = Wj, Vsc = Vsc, Vj = Vj, cutx = cutx, cuty = cuty)

mu = 10 #meV

gi = 0
gf = 5.0
res = 0.01
steps_gam = int((gf - gi)/(0.5*res)) + 1
gx = np.linspace(gi, gf, steps_gam)

q_steps = 501
qx = np.linspace(0, np.pi/Lx, q_steps) #kx in the first Brillouin zone

k = 200
LE_Bands = np.zeros((qx.shape[0], gx.shape[0]))
###################################################
dirS = 'gap_data'
if not os.path.exists(dirS):
    os.makedirs(dirS)
try:
    PLOT = str(sys.argv[1])
except:
    PLOT = 'F'
if PLOT != 'P':
    for i in range(q_steps):
        if i == 0:
            Q = 1e-4*(np.pi/Lx)
        else:
            Q = qx[i]

        H0 = spop.HBDG(coor, ax, ay, NN, NNb=NNb, Wj=Wj, cutx=cutx, cuty=cuty, V=V, mu=mu, alpha=alpha, delta=delta, phi=phi, gamx=1e-4, qx=Q) #gives low energy basis

        eigs_0, vecs_0 = spLA.eigsh(H0, k=k, sigma=0, which='LM')
        vecs_0_hc = np.conjugate(np.transpose(vecs_0)) #hermitian conjugate

        H_G0 = spop.HBDG(coor, ax, ay, NN, NNb=NNb, Wj=Wj, cutx=cutx, cuty=cuty, V=V, mu=mu, gamx=0, alpha=alpha, delta=delta, phi=phi, qx=qx[i]) #Matrix that consists of everything in the Hamiltonian except for the Zeeman energy in the x-direction
        H_G1 = spop.HBDG(coor, ax, ay, NN, NNb=NNb, Wj=Wj, cutx=cutx, cuty=cuty, V=V, mu=mu, gamx=1, alpha=alpha, delta=delta, phi=phi, qx=qx[i]) #Hamiltonian with ones on Zeeman energy along x-direction sites
        HG = H_G1 - H_G0 #the proporitonality matrix for gamma-x, it is ones along the sites that have a gamma value
        HG0_DB = np.dot(vecs_0_hc, H_G0.dot(vecs_0))
        HG_DB = np.dot(vecs_0_hc, HG.dot(vecs_0))
        for g in range(gx.shape[0]):
            print(qx.shape[0]-i,  gx.shape[0]-g)
            H_DB = HG0_DB + gx[g]*HG_DB
            eigs_DB, U_DB = LA.eigh(H_DB)
            LE_Bands[i, g] = eigs_DB[int(k/2)]

    gap = np.zeros((gx.shape[0]))
    q_minima = []
    for i in range(LE_Bands.shape[1]):
        eig_min_idx = np.array(argrelextrema(LE_Bands[:, i], np.less)[0])
        q_minima.append(qx[eig_min_idx])
        gap[i] = min(LE_Bands[:, i])

    q_minima = np.array(q_minima)
    print(gap)
    np.save("%s/gap Lx = %.1f Ly = %.1f Wsc = %.1f Wj = %.1f nodx = %.1f nody = %.1f Vj = %.1f Vsc = %.1f alpha = %.1f delta = %.2f phi = %.3f.npy" % (dirS, Lx*.1, Ly*.1, SC_width, Junc_width, Nod_widthx,  Nod_widthy, Vj, Vsc, alpha, delta, phi), gap)
    gc.collect()

    sys.exit()
else:
    gap = np.load("%s/gap Lx = %.1f Ly = %.1f Wsc = %.1f Wj = %.1f nodx = %.1f nody = %.1f Vj = %.1f Vsc = %.1f alpha = %.1f delta = %.2f phi = %.3f.npy" % (dirS, Lx*.1, Ly*.1, SC_width, Junc_width, Nod_widthx,  Nod_widthy, Vj, Vsc, alpha, delta, phi))
    #q_minima = np.load("%s/q_minima Lx = %.1f Ly = %.1f Wsc = %.1f Wj = %.1f nodx = %.1f nody = %.1f Vj = %.1f Vsc = %.1f alpha = %.1f delta = %.2f phi = %.3f.npy" % (dirS, Lx*.1, Ly*.1, SC_width, Junc_width, Nod_widthx,  Nod_widthy, Vj, Vsc, alpha, delta, phi))

    gap = gap/delta

    plt.plot(gx, gap)

    plt.xlabel(r'$\Gamma_x$ (meV)')
    plt.ylabel(r'$E_{gap}/\Delta$ (meV)')
    plt.xlim(gi, gf)
    title = r"$\mu$ = %.1f $L_x$ = %.1f nm, $L_y$ = %.1f nm, $W_{sc}$ = %.1f nm, $W_j$ = %.1f nm, $nodule_x$ = %.1f nm, $nodule_y$ = %.1f nm, $V_j$ = %.1f meV, $V_{SC}$ = %.1f meV, $\phi$ = %.2f " % (mu, Lx*.1, Ly*.1, SC_width, Junc_width, Nod_widthx, Nod_widthy, Vj, Vsc, phi)
    #title = r"$L_x =$ {} nm, $L_y =$ {} nm, SC width = {} nm, $W_j =$ {} nm, $nodule_x = ${} nm, $nodule_y = ${} nm, $\alpha = $ {} meV*A, $\phi =$ {} ".format(Lx*.1, Ly*.1, SC_width, Junc_width, Nod_widthx, Nod_widthy, alpha, phi)
    plt.title(title, loc = 'center', wrap = True)
    plt.subplots_adjust(top=0.85)
    plt.savefig('gap juncwidth = {} SCwidth = {} nodwidthx = {} nodwidthy = {} phi = {} Vj = {} Vsc = {}.png'.format(Junc_width, SC_width, Nod_widthx, Nod_widthy, delta, alpha, phi, Vj, Vsc))
    plt.show()

    sys.exit()
