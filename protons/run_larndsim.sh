# run larnd-sim
inFile=$1
outFile=$2

shifter --image=mjkramer/sim2x2:genie_edep.3_04_00.20230620 --module=None -- /bin/bash << EOF
set +o posix
source /environment

rm -rf convert.venv
python3 -m venv convert.venv
source convert.venv/bin/activate
pip install --upgrade pip
pip install -r requirements_larndsim.txt

cd ../larnd-sim/cli
python3 simulate_pixels.py --input_filename "$inFile" \
    --output_filename "$outFile" \
    --detector_properties ../larndsim/detector_properties/2x2.yaml \
    --pixel_layout ../larndsim/pixel_layouts/multi_tile_layout-2.4.16.yaml \
    --response_file ../larndsim/bin/response_44.npy \
    --light_lut_filename ../larndsim/bin/lightLUT.npz \
    --light_det_noise_filename ../larndsim/bin/light_noise-2x2-example.npy \
    --simulation_properties ../larndsim/simulation_properties/singles_sim.yaml
EOF
