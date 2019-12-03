from __future__ import division
from synth import Synth
from preset import DX7PresetLoader, PresetFixer
import argparse, os
from utils import get_files_ext
from tqdm import tqdm
import numpy as np

parser = argparse.ArgumentParser()
parser.add_argument("--preset_dir", type=str, default="/Users/naotake/Datasets/DX7_no_dup", help='Preset directory')
parser.add_argument("--vst_dir", type=str, default="/Library/Audio/Plug-Ins/VST/Dexed.vst", help='vst directory')
parser.add_argument("--default", type=str, default="settings/Dexed/dexed_default.json", help='default values for parameters')
parser.add_argument("--move", type=str, default="settings/Dexed/dexed_use_params.txt", help='default values for parameters')
parser.add_argument('-p', nargs='+', type=int, help='<Required> List of pitches to render', required=True)
parser.add_argument('-v', nargs='+', type=int, help='<Required> List of velocities to render 0~128', required=True)
parser.add_argument("-out", type=str, help='output directory', required=True)


args = parser.parse_args()

# get directories of all ".SYX" files under --preset_dir
preset_files = get_files_ext(args.preset_dir, ".SYX")

#initialize synthesizer
dexed = Synth("Dexed")
dexed.load_synth("/Library/Audio/Plug-Ins/VST/Dexed.vst", sample_rate=44100, buffer_size=32) #only short buffer_size works for some reason

loader = DX7PresetLoader(args.default)
fixer = PresetFixer(args.default, args.move)
config_name = os.path.basename(args.move)[:-4] +"_"+ os.path.basename(args.default)[:-5]
config_name += "_p_"+"-".join([str(n) for n in args.p]) +"_v_"+"-".join([str(n) for n in args.v])
output_dir = os.path.join(args.out, config_name)
if not os.path.exists(output_dir):
    os.mkdir(output_dir)

hashes = set()
preset_count = 0
for pf in tqdm(preset_files):
    presets = loader.load_file(pf)
    for preset in presets:
        if preset.hash in hashes: # skip duplicates
            continue
        else:
            hashes.add(preset.hash)

        if preset.params["ALGORITHM"] != 4:
            continue
        
        fixed_preset = fixer.fix_preset(preset)
        dexed.preset_to_midicc(fixed_preset)
        if dexed.oor > 2: # skip if there are too many out of range parameters
            continue
        
        preset_count += 1
        for pitch in args.p:
            for velocity in args.v:
                audio = dexed.play_note(pitch, velocity, 3.0, 4.0, output_rate=22050)
                out_name = preset.hash + "_" + str(pitch) + "_" + str(velocity)
                np.savez_compressed(os.path.join(output_dir, out_name) + ".npz", params=preset.params, audio=audio)
print("loaded {0} presets".format(preset_count))