from __future__ import division
import argparse, os, shutil, sys
from synth import Synth
from preset import DX7PresetLoader, PresetFixer
from util import get_files_ext
from tqdm import tqdm
import numpy as np
import librosa

parser = argparse.ArgumentParser()
parser.add_argument("preset_dir", type=str, help='Preset directory')
parser.add_argument("--vst_dir", type=str, default="/Library/Audio/Plug-Ins/VST/Dexed.vst", help='vst directory')
parser.add_argument("--default", type=str, default="settings/Dexed/dexed_default.json", help='default values for parameters')
parser.add_argument("--move", type=str, default="settings/Dexed/dexed_use_params.txt", help='list of parameters to move')
parser.add_argument("--init_fxb", type=str, default="settings/Dexed/DexedInit.FXB", help='output directory',)
parser.add_argument('-p', nargs='+', type=int, help='<Required> List of pitches to render', required=True)
parser.add_argument('-v', nargs='+', type=int, help='<Required> List of velocities to render 0~128', required=True)
parser.add_argument("--out_dir", type=str, help='output directory', required=True)
parser.add_argument("--dataset_name", type=str, default="", help='dataset name')


args = parser.parse_args()

# get directories of all ".SYX" files under --preset_dir
preset_files = get_files_ext(args.preset_dir, ".SYX")

#initialize synthesizer
dexed = Synth("Dexed")

dexed.load_synth(args.vst_dir,  init_fxb=args.init_fxb, sample_rate=44100, buffer_size=32) #only short buffer_size works for some reason

loader = DX7PresetLoader(args.default)
fixer = PresetFixer(args.default, args.move)
# Dataset names start with [synth_name]

if args.dataset_name != "":
    dataset_name = "Dexed_"+args.dataset_name
else:
    dataset_name = "Dexed_"+os.path.basename(args.move)[:-4] +"_"+ os.path.basename(args.default)[:-5]
    dataset_name += "_p_"+"-".join([str(n) for n in args.p]) +"_v_"+"-".join([str(n) for n in args.v])

output_dir = os.path.join(args.out_dir, args.dataset_name)
settings_dir = os.path.join(output_dir, "settings/")
raw_dir = os.path.join(output_dir, "raw/")
mel_dir = os.path.join(output_dir, 'mel/')
mfcc_dir = os.path.join(output_dir, 'mfcc/')
if not os.path.exists(output_dir):
    os.mkdir(output_dir)
    os.mkdir(settings_dir)
    os.mkdir(raw_dir)
    os.mkdir(mel_dir)
    os.mkdir(mfcc_dir)

# save setting files with the dataset
shutil.copyfile(args.default, os.path.join(settings_dir, "default.json"))
shutil.copyfile(args.move, os.path.join(settings_dir, "use_params.txt"))
shutil.copyfile(args.init_fxb, os.path.join(settings_dir, "init.fxb"))

# init fxb?
hashes = set()
preset_count = 0
# takes ~5hrs? for the entire dataset!? >_<
# I would love to use multiprocessing, but somehow it already uses multiple cpus...???? 
# librosa? https://stackoverflow.com/questions/55487391/unable-to-use-multithread-for-librosa-melspectrogram 
# and I don't know about the consequences of using boost libraries in multiple processes either
for pf in tqdm(preset_files):
    presets = loader.load_file(pf)
    for preset in presets:
        if preset.hash in hashes: # skip duplicates
            continue
        else:
            hashes.add(preset.hash)

        # if preset.params["ALGORITHM"] != 4:
            # continue
        
        fixed_preset = fixer.fix_preset(preset)
        dexed.preset_to_midi(fixed_preset)
        if dexed.oor > 2: # skip if there are too many out of range parameters
            continue
        

        preset_count += 1
        for pitch in args.p:
            for velocity in args.v:
                audio = dexed.play_note(pitch, velocity, 3.0, 4.0, output_rate=22050)
                out_name = preset.hash + "_" + str(pitch) + "_" + str(velocity)
                np.savez_compressed(os.path.join(raw_dir, out_name) + ".npz", param=dexed.midi_params, audio=audio, pitch = pitch, velocity=velocity, cat_param=dexed.one_hots)
                # save mel and mfcc
                b_mel = librosa.feature.melspectrogram(audio, sr=22050, n_fft=2048, n_mels=64, hop_length=1024, fmin=30, fmax=11000) #(64,87)
                b_mel = b_mel[:64,:80]
                np.save(os.path.join(mel_dir, out_name) + ".npy", b_mel)
                b_mfcc = librosa.feature.mfcc(audio, sr=22050, n_mfcc=16, hop_length=256) #(16,346)
                b_mfcc = b_mfcc[:16,:320]
                np.save(os.path.join(mfcc_dir, out_name) + ".npy", b_mfcc)
