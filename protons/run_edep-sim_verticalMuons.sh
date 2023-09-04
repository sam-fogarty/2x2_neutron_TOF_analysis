#!/usr/bin/env bash
nevents=1000
physics_list=QGSP_BERT
macro=vertical_muons_2x2.mac
output_folder=/global/cfs/cdirs/dune/users/sfogarty
edep_filename=verticalMuons_${nevents}_events_2x2_1GeV_to_5GeV.root
h5_filename=verticalMuons_${nevents}_events_2x2_1GeV_to_5GeV.h5

shifter --image=mjkramer/sim2x2:genie_edep.3_04_00.20230620 --module=None -- /bin/bash << EOF
set +o posix
source /environment

rm -rf convert.venv
python3 -m venv convert.venv
source convert.venv/bin/activate
pip3 install -r requirements_h5converter.txt

edep-sim -C -e ${nevents} -p ${physics_list} -o ${output_folder}/${edep_filename} ${macro}

python3 dumpTree.py ${output_folder}/${edep_filename} ${output_folder}/${h5_filename}

EOF
