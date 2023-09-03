#!/usr/bin/env bash
nevents=1000
physics_list=QGSP_BERT
macro=protons_2x2_uniform_1MeV_to_1000MeV.mac
output_folder=/global/cfs/cdirs/dune/users/sfogarty
edep_filename=protons_${nevents}_events_2x2.root

shifter --image=mjkramer/sim2x2:genie_edep.3_04_00.20230620 --module=None -- /bin/bash << EOF
set +o posix
source /environment

edep-sim -C -e ${nevents} -p ${physics_list} -o ${output_folder}/${edep_filename} ${macro}

EOF
