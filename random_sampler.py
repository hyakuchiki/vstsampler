
from __future__ import division
from parameter import Preset, get_random_preset
import argparse, os, pickle
import tqdm
from vst_render import load_synth, play_preset
import numpy as np

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--synth", type=str, default="Dexed", help='Synthesizer to sample')
    parser.add_argument("--num", type=int, default=10000, help='number of random samples to generate')
    parser.add_argument("--init_conf", type=str, default=None, help='json to initialize the presets (values to fall back to)')
    parser.add_argument("--init_fxp", type=str, default=None, help='FXP to initialize the plugin')
    parser.add_argument('--use', type=str, default=None, help="list of parameters to move and not fix")
    parser.add_argument("--out", type=str, default="/Users/naotake/Datasets/Dexed_audio", help='Output npz files directory')
    parser.add_argument("--vst_dir", type=str, default="/Library/Audio/Plug-Ins/VST/Dexed.vst", help='vst directory')
    args = parser.parse_args()
    
    pitches=[60]
    vels=[100]
    if not os.path.exists(args.out):
        os.mkdir(args.out)
    

    engine, origRate = load_synth(args.synth, args.vst_dir, init_fxp=args.init_fxp)
    with open("settings/Diva/use_32par.txt") as f:
        use_param_list = [line.strip() for line in f]

    for i in tqdm.tqdm(range(args.num)):
        p = get_random_preset(args.synth, use_param_list, args.init_conf)
        audio = play_preset(engine, p, pitches, vels, origRate=origRate)
        filename=os.path.join(args.out,p.hash+".npz")
        np.savez_compressed(filename, hash=p.hash, param=p.get_moving_midi_params(), audio=audio)    