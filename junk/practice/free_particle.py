H = ksq
num = 5
sigma = 0
which = 'LM' #largest magnitude, LA = largest absolute
eigs, vecs = sparLA.eigsh(H, k=num, sigma=sigma, which=which)
idx_sort = np.argsort(eigs)
eigs = eigs[idx_sort]
