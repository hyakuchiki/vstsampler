from __future__ import division
import argparse, os, shutil, sys
from vstsampler.synth import Synth
from vstsampler.preset import DivaPresetLoader, PresetFixer
from vstsampler.util import get_files_ext, resample
from tqdm import tqdm
import numpy as np
import librosa
import soundfile

if __name__ == '__main__':

    parser = argparse.ArgumentParser()
    parser.add_argument("out_dir", type=str, help='output directory')
    parser.add_argument("--preset_dir", type=str, default="/Users/naotake/Datasets/DX7_no_dup", help='Preset directory')
    parser.add_argument("--sr", type=int, default=16000, help='sample rate of saved audio')

    # synth settings
    parser.add_argument("--vst_dir", type=str, default="/home/n_masuda/.u-he/Diva/Diva.64.so", help='vst directory')
    parser.add_argument("--default", type=str, default="settings/Diva/diva_32par.json", help='default values for parameters')
    parser.add_argument("--move", type=str, default="settings/Diva/use_32parH2P.txt", help='list of parameters to move')
    parser.add_argument("--init_fxb", type=str, default="settings/Diva/Init_osc_reset.FXB", help='Initial FXB',)
    parser.add_argument('-p', nargs='+', type=int, help='<Required> List of pitches (MIDI) to render', required=True)
    parser.add_argument('-v', nargs='+', type=int, help='<Required> List of velocities to render 0~128', required=True)


    args = parser.parse_args()

    # get directories of all ".SYX" files under --preset_dir
    preset_files = get_files_ext(args.preset_dir, ".h2p")

    #initialize synthesizer
    diva = Synth("Diva")

    diva.load_synth(args.vst_dir,  init_fxb=args.init_fxb, sample_rate=44100, buffer_size=32) #only short buffer_size works for some reason

    loader = DivaPresetLoader(args.default)
    fixer = PresetFixer(args.default, args.move)

    output_dir = args.out_dir
    audio_dir = os.path.join(output_dir, "audio/")
    if not os.path.exists(output_dir):
        os.mkdir(output_dir)
    if not os.path.exists(audio_dir):
        os.mkdir(audio_dir)
        
    # save setting files with the dataset
    shutil.copyfile(args.default, os.path.join(output_dir, "default.json"))
    shutil.copyfile(args.move, os.path.join(output_dir, "use_params.txt"))
    shutil.copyfile(args.init_fxb, os.path.join(output_dir, "init.fxb"))

    hashes = set()
    preset_count = 0

    for pf in tqdm(preset_files):
        preset = loader.load_file(pf)
        if not preset:
            continue
        if preset.hash in hashes: # skip duplicates
            continue
        else:
            hashes.add(preset.hash)
        
        fixed_preset = fixer.fix_preset(preset)
        diva.preset_to_midi(fixed_preset)
        # if diva.oor > 2: # skip if there are too many out of range parameters
        #     continue
        preset_count += 1
        for pitch in args.p:
            for velocity in args.v:
                audio = diva.play_note(pitch, velocity, 3.0, 4.0, output_rate=args.sr)
                out_name = preset.hash + "_" + str(pitch) + "_" + str(velocity) + '.wav'
                soundfile.write(os.path.join(audio_dir, out_name), audio, args.sr) # PCM_16
                

    print('played {0} out of {1} presets'.format(preset_count, len(preset_files)))