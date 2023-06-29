import numpy as np
from tqdm import tqdm
import h5py
import yaml

def find_neutrons_MC(light_trig, hits, light_spillIDs, trajectories, tracks,genie_hdr_all):
    eventIDs_keep = []
    detprop_path = '/sdf/home/s/sfogarty/Desktop/RadDecay/neutron_TOF/analysis_tools_2x2/2x2.yaml'
    with open(detprop_path) as df:
        detprop = yaml.load(df, Loader=yaml.FullLoader)
    tpc_to_op_channel = detprop['tpc_to_op_channel']
    
    # select only vertices occurring inside active volume
    target_mask = (genie_hdr_all['target'] == 18)
    position_mask_x = np.abs(genie_hdr_all['vertex'][:,0]*10) < 655
    position_mask_y = np.abs(genie_hdr_all['vertex'][:,1]*10 - 420) < 655
    position_mask_z = np.abs(genie_hdr_all['vertex'][:,2]*10) < 655
    genie_hdr_cut = genie_hdr_all[target_mask & position_mask_x & position_mask_y & position_mask_z]
    eventIDs = np.unique(genie_hdr_cut['eventID'])
    
    for eventID in eventIDs:
        close_to_vertex_and_hits = False
        
        genie_hdr = genie_hdr_cut[genie_hdr_cut['eventID'] == eventID]
        hits_event = hits[hits['edep_event_ids'] == eventID]
        hits_event_x = np.array(hits_event['z'])
        hits_event_y = np.array(hits_event['y'])
        hits_event_z = np.array(hits_event['x'])
        hits_event_t = np.array(hits_event['t'])
        hits_event_q = np.array(hits_event['q'])

        # need to get t0 for each module to get drift coordinate
        light_trig_event = light_trig[light_spillIDs == eventID]
        light_spillIDs_event = light_trig_event['op_channel'][:,0]

        # for each module, find the light trig with the smallest timestamp -> use for t0 calculation.
        # modules without a light trigger are indicated by a -1 in place of timestamp
        ts_sync_min_event = [] # ns
        for min_op_channel in np.unique(light_trig['op_channel'][:,0]):
            module_ts_sync = light_trig_event[light_spillIDs_event == min_op_channel]['ts_sync']
            if module_ts_sync.size > 0:
                module_tlight = int(np.min(module_ts_sync)) * 0.1 * 1e3 
                ts_sync_min_event.append(module_tlight)
            else:
                ts_sync_min_event.append(-1)
        ts_sync_min_event = np.array(ts_sync_min_event)
        #print(ts_sync_min_event)
        

        # get relationship between module to op channel
        i,j = 0,0
        module_to_op_channel = np.zeros((int(len(tpc_to_op_channel)/2), len(tpc_to_op_channel[0]*2)))
        while i < len(tpc_to_op_channel):
            module_to_op_channel[j] = np.concatenate((tpc_to_op_channel[i], tpc_to_op_channel[i+1]))
            j += 1
            i += 2

        module_to_io_group =detprop['module_to_io_groups']
        io_group_to_module = {value: key for key, values in module_to_io_group.items() for value in values}

        # calculate drift coordinate
        v_drift = 1.6 / 1e3 # mm/ns
        for i,light_ts_sync in enumerate(ts_sync_min_event):
            IOs = module_to_io_group[i+1]
            for IO in IOs:
                hits_event_mask = (hits_event['io_group'] == IO)
                if IO % 2 == 1:
                    hits_event_x[hits_event_mask] = hits_event_x[hits_event_mask] + v_drift * np.abs(hits_event_t[hits_event_mask] - light_ts_sync)
                else:
                    hits_event_x[hits_event_mask] = hits_event_x[hits_event_mask] - v_drift * np.abs(hits_event_t[hits_event_mask] - light_ts_sync)

        trajectories_event = trajectories[(trajectories['eventID'] == eventID) & (trajectories['pdgId'] == 2112)]

        traj_event = trajectories_event
        for i,traj in enumerate(traj_event):
            # find neutrons that start near nu vertex
            #close_to_vertex = np.zeros(len(genie_hdr_event), dtype=bool)
            for k in range(len(genie_hdr)):
                traj_to_vertex_distance = np.sqrt(np.sum((np.array(genie_hdr[k]['vertex'][0:3]) - np.array(traj['xyz_start']))**2))
                xyz_end_traj = np.array(traj['xyz_end'])
                traj_to_hits_distance = np.sqrt((xyz_end_traj[0]*10 - hits_event_x)**2 + (xyz_end_traj[1]*10-420 - hits_event_y)**2 + (xyz_end_traj[2]*10 - hits_event_z)**2)
                if traj_to_vertex_distance < 2 and np.sum(traj_to_hits_distance < 20) > 0:
                    close_to_vertex_and_hits = True
            
        #print('close_to_vertex_and_hits: ', close_to_vertex_and_hits)
        #print('np.sum(ts_sync_min_event != -1) > 1:', np.sum(ts_sync_min_event != -1) > 1)
        if close_to_vertex_and_hits and np.sum(ts_sync_min_event != -1) > 1:
            eventIDs_keep.append(eventID)
    return eventIDs_keep