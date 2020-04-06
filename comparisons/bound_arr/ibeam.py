import time

import majoranaJJ.lattice.shapes as shp
import majoranaJJ.junk.lattice.neighbors as nb2
import majoranaJJ.lattice.neighbors as nb
import majoranaJJ.etc.plots as plot

print("")
xbase = 40
xcut = 5
y1 = 10
y2 = 10

#Making square lattice, nothing has changed with this method
coor = shp.ibeam(xbase, xcut, y1, y2)
NN = nb.NN_Arr(coor)
print("size: ", coor.shape[0])
print("")
###################################

#Using old method, scaled by N^2 due to a loop within a loop
start = time.time()
NNb2 = nb2.Bound_Arr(NN, coor)
end = time.time()
print("Time to create Bound_Arr with original method = {} [s]".format(end-start))
print(NNb2[0:5, :])

idx = 0
plot.lattice(idx, coor, NNb = NNb2)
print(" ")

###################################
start = time.time()
NNb = nb.Bound_Arr(coor)
end = time.time()
print("Time to create Bound_Arr with revised method = {} [s]".format( end-start))
print(NNb[0:5, :])

idx = 0
plot.lattice(idx, coor, NNb = NNb)
print(" ")

###################################

#Verifying that the new method creates the same neighbor array as the old one
for i in [0,1,2,3]:
    print("Same Values? ", all(NNb[:,i] == NNb2[:,i]))
