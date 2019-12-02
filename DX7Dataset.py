from synth import Synth
from preset import DX7PresetLoader
import argparse
from utils import get_files_ext
from tqdm import tqdm

parser = argparse.ArgumentParser()
parser.add_argument("--preset_dir", type=str, default="/Users/naotake/Datasets/DX7_no_dup", help='Preset directory')
parser.add_argument("--vst_dir", type=str, default="/Library/Audio/Plug-Ins/VST/Dexed.vst", help='vst directory')
parser.add_argument("--default_json", type=str, default="settings/Dexed/dexed_default.json", help='vst directory')
parser.add_argument('-p', nargs='+', help='<Required> List of pitches to render', required=True)
parser.add_argument('-v', nargs='+', help='<Required> List of velocities to render', required=True)

args = parser.parse_args()

# get directories of all ".SYX" files under --preset_dir
preset_files = get_files_ext(args.preset_dir, ".SYX")

#initialize synthesizer
a.load_synth("/Library/Audio/Plug-Ins/VST/Dexed.vst", sample_rate=44100)

DX7PresetLoader(args.default_json)

for pf in tqdm(preset_files):
    