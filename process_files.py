#!/usr/bin/python
# -*- coding: utf-8 -*-

import numpy as np
import os

import general_tools, get_data, plotting_tools, ep_tools, measure_ki

config=general_tools.configuration("demux_tools_cfg")

datadirname = os.path.join(os.path.normcase(config.config['path']), config.config['dir_data'])

drawline = '\n#---------------------'

"""
Processing dumps files ###############################################
"""
dumpfilenames = [f for f in os.listdir(datadirname) \
                if os.path.isfile(os.path.join(datadirname, f)) \
                and f[-4:]==".dat" \
                and f[-13:]!="_er_calib.dat" \
                and f[-13:]!="_er_measu.dat" ]

t0=0
duration=0.1
pix_zoom=0
spectral=True
noise=True
sav_noise_spectra=True
for file in dumpfilenames:
    print(drawline)
    d=get_data.data(file, config.config)
    d.print_dumptype()
    sav_spectra = False
    if file[-13:]=="_er_noise.dat" or d.dumptype==5:
        sav_spectra = sav_noise_spectra
    d.plot(t0, duration, pix_zoom, spectral, noise, sav_spectra)

"""
Processing ki measurements data #####################################
"""
kifilename = [f for f in os.listdir(datadirname) \
                if os.path.isfile(os.path.join(datadirname, f)) \
                and f[-13:]=="_ki_check.dat" ]
if len(kifilename)>0:
    print(drawline)
    d=get_data.data(kifilename[0], config.config)
    measure_ki.measure_ki(d)

"""
Processing energy resolution data ###################################
"""
prebuffer=180
record_len=4096
rec_extension='_rec.npy'

"""
Making noise records
"""
pix=0
filename_er_noise = [f for f in os.listdir(datadirname) \
                if os.path.isfile(os.path.join(datadirname, f)) \
                and f[-13:]=="_er_noise.dat"]
filename_er_noise_rec = [f for f in os.listdir(datadirname) \
                if os.path.isfile(os.path.join(datadirname, f)) \
                and f[-17:]=="_er_noise_rec.npy"]
if len(filename_er_noise)>0 and len(filename_er_noise_rec)==0:
    noise = ep_tools.get_noise_records(filename_er_noise[0], config.config, pix, record_len)
    # saving noise records
    noise_npy_file = os.path.join(datadirname, filename_er_noise[0][:-4]+rec_extension)
    with open(noise_npy_file, 'wb') as file:
        np.save(file, noise)
    
"""
Triggering calibration pulses
"""
pix = 100 # if 100 the routine will look for pixels with pulses
filename_er_calib = [f for f in os.listdir(datadirname) \
                if os.path.isfile(os.path.join(datadirname, f)) \
                and f[-13:]=="_er_calib.dat"]
filename_er_calib_rec = [f for f in os.listdir(datadirname) \
                if os.path.isfile(os.path.join(datadirname, f)) \
                and f[-17:]=="_er_calib_rec.npy"]
if len(filename_er_calib)>0 and len(filename_er_calib_rec)==0:
    calib, t_calib, pix_calib = ep_tools.get_pulse_records(filename_er_calib[0], config.config, pix, record_len, prebuffer)
    # saving pulse records
    calib_npy_file = os.path.join(datadirname, filename_er_calib[0][:-4]+rec_extension)
    with open(calib_npy_file, 'wb') as file:
        np.save(file, t_calib)
        np.save(file, calib)

"""
Triggering pulses
"""
filename_er_measu = [f for f in os.listdir(datadirname) \
                if os.path.isfile(os.path.join(datadirname, f)) \
                and f[-13:]=="_er_measu.dat"]
filename_er_measu_rec = [f for f in os.listdir(datadirname) \
                if os.path.isfile(os.path.join(datadirname, f)) \
                and f[-17:]=="_er_measu_rec.npy"]
if len(filename_er_measu)>0 and len(filename_er_measu_rec)==0:
    measu, t_measu, _ = ep_tools.get_pulse_records(filename_er_measu[0], config.config, pix_calib, record_len+4, prebuffer+2)
    # saving pulse records
    measu_npy_file = os.path.join(datadirname, filename_er_measu[0][:-4]+rec_extension)
    with open(measu_npy_file, 'wb') as file:
        np.save(file, t_measu)
        np.save(file, measu)

"""
Computing energy resolution
"""
filename_er_noise_rec = [f for f in os.listdir(datadirname) \
                if os.path.isfile(os.path.join(datadirname, f)) \
                and f[-17:]=="_er_noise_rec.npy"]
filename_er_calib_rec = [f for f in os.listdir(datadirname) \
                if os.path.isfile(os.path.join(datadirname, f)) \
                and f[-17:]=="_er_calib_rec.npy"]
filename_er_measu_rec = [f for f in os.listdir(datadirname) \
                if os.path.isfile(os.path.join(datadirname, f)) \
                and f[-17:]=="_er_measu_rec.npy"]

if len(filename_er_noise_rec)>0 and len(filename_er_calib_rec)>0 and len(filename_er_measu_rec)>0:
    print(drawline)
    print("Processing energy resolution data...")
    verbose=False
    _, _= ep_tools.ep(filename_er_noise_rec[0], filename_er_calib_rec[0], filename_er_measu_rec[0], config.config, prebuffer, verbose)

"""
#####################################################################
"""
