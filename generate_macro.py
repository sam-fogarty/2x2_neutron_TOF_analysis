import os
import numpy as np

bins = 50
E_start = 1 # MeV
E_stop = 1000
output_filepath = f'protons_2x2_uniform_{E_start}MeV_to_{E_stop}MeV.txt'

x_diff = (E_stop-E_start)/bins
energies = np.arange(E_start, E_stop, x_diff)
fraction = np.ones(len(energies))*1/len(energies)

f = open(output_filepath, "w+")
f.write('/edep/random/timeRandomSeed\n')
f.write('/edep/gdml/read Merged2x2MINERvA_v3_withRock.gdml\n')
f.write('/edep/phys/ionizationModel 0\n')
f.write('/edep/hitSeparation volLArActive -1 mm\n')
f.write('/edep/update\n')
f.write('/gps/pos/type Volume\n')
f.write('/gps/pos/shape Para\n')
f.write('/gps/pos/centre 0.0 -268.0 1300 cm\n')
f.write('/gps/pos/halfx 64.365 cm\n')
f.write('/gps/pos/halfy 62.288 cm\n')
f.write('/gps/pos/halfz 64.750 cm\n')
f.write('/gps/ang/type iso\n')
f.write('/gps/particle proton\n')
f.write('/gps/ene/type User\n')
f.write('/gps/hist/type energy\n')

for i in range(len(energies)):
    f.write('/gps/hist/point '+str("%.6f" % (energies[i]))+' '+str("%.6f" % fraction[i]) + '\n')

f.write('/gps/hist/inter Lin')
f.close()
