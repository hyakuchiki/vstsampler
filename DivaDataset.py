from __future__ import division
import argparse, os, shutil, sys
from .synth import Synth
from .preset import DivaPresetLoader, PresetFixer
from .util import get_files_ext
from tqdm import tqdm
import numpy as np
import librosa

antonyms = [("Bright", "Dark"), ("Clean", "Dirty"), ("Modern", "Vintage"), ("Phat", "Thin"), ("Soft", "Aggressive"), ("Constant", "Moving"),
("Natural", "Synthetic"), ("Wide", "Narrow"), ("Harmonic", "Inharmonic"), ("Dynamic", "Static")]

#based on Diva_Presets.tags
syn_d = {"Evolving": "Moving", "Rich & Phat": "Phat", "Distorted": "Dirty", "Defined & Sparse": "Thin"}

char_vocab = ['Bright', 'Dark', 'Clean', 'Dirty', 'Modern', 'Vintage', 'Phat', 'Thin', 'Soft', 'Aggressive', 'Constant', 'Moving', 'Natural', 'Synthetic', 'Wide', 'Narrow', 'Harmonic', 'Inharmonic', 'Dynamic', 'Static']
def proc_synonyms(chars):
    """
    Converts synonyms to words in vocab (ex. Defined&Sparse -> Thin)
    """
    return [syn_d[c]  if c in syn_d else c for c in chars]

def get_char_vector(chars):
    """
    Gets one-hot vectors of characteristics and puts them back to list of chars
    ex.)
    [u'Dark', u'Aggressive', u'Rich & Phat', u'Modern', u'Electric', u'Synthetic']
    =>
array([[0., 1., 0.], # Dark
       [0., 0., 1.], # Unknown (Neither clean nor dirty)
       [1., 0., 0.], # Modern
       [1., 0., 0.], # Phat (Rich&Phat is a synonym of Phat)
       [0., 1., 0.], # Aggressive
       [0., 0., 1.], # Unknown (Neither constant nor moving)
       [0., 1., 0.], # Synthetic
       [0., 0., 1.], # Unknown (Neither wide nor narrow)
       [0., 0., 1.], # Unknown (Neither harmonic nor inharmonic)
       [0., 0., 1.]])# Unknown (Neither dynamic nor static)
    """
    chars = set(proc_synonyms(chars))
    vec = []
    for a in antonyms:
        if set(a)<=chars:
            print("both antonyms in chars")
            k = 2
        elif a[0] in chars:
            k = 0
        elif a[1] in chars:
            k = 1
        else:
            k = 2
        v = np.eye(3)[k]
        vec.append(v)
    return np.array(vec)

if __name__ == '__main__':

    parser = argparse.ArgumentParser()
    parser.add_argument("--preset_dir", type=str, default="/Users/naotake/Datasets/DX7_no_dup", help='Preset directory')
    parser.add_argument("--vst_dir", type=str, default="/Library/Audio/Plug-Ins/VST/Diva.vst", help='vst directory')
    parser.add_argument("--default", type=str, default="settings/Diva/diva_32par.json", help='default values for parameters')
    parser.add_argument("--move", type=str, default="settings/Diva/use_32parH2P.txt", help='list of parameters to move')
    parser.add_argument("--init_fxb", type=str, default="settings/Diva/Init_osc_reset.FXB", help='output directory',)
    parser.add_argument('-p', nargs='+', type=int, help='<Required> List of pitches to render', required=True)
    parser.add_argument('-v', nargs='+', type=int, help='<Required> List of velocities to render 0~128', required=True)
    parser.add_argument("--out_dir", type=str, help='output directory', required=True)
    parser.add_argument("--dataset_name", type=str, default="", help='dataset name')

    args = parser.parse_args()

    # get directories of all ".SYX" files under --preset_dir
    preset_files = get_files_ext(args.preset_dir, ".h2p")

    #initialize synthesizer
    diva = Synth("Diva")

    diva.load_synth(args.vst_dir,  init_fxb=args.init_fxb, sample_rate=44100, buffer_size=32) #only short buffer_size works for some reason

    loader = DivaPresetLoader(args.default)
    fixer = PresetFixer(args.default, args.move)
    # Dataset names start with [synth_name]

    if args.dataset_name != "":
        dataset_name = "Diva_"+args.dataset_name
    else:
        dataset_name = "Diva_"+os.path.basename(args.move)[:-4] +"_"+ os.path.basename(args.default)[:-5]
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
        if 'Character' in preset.meta:
            meta_vec = get_char_vector(preset.meta["Character"])
        else:
            meta_vec = get_char_vector([])
        preset_count += 1
        for pitch in args.p:
            for velocity in args.v:
                audio = diva.play_note(pitch, velocity, 3.0, 4.0, output_rate=22050)
                out_name = preset.hash + "_" + str(pitch) + "_" + str(velocity)
                np.savez_compressed(os.path.join(raw_dir, out_name) + ".npz", param=diva.midi_params, audio=audio, pitch = pitch, velocity=velocity, cat_param=diva.one_hots, chars=meta_vec)
                # save mel and mfcc
                b_mel = librosa.feature.melspectrogram(audio, sr=22050, n_fft=2048, n_mels=64, hop_length=1024, fmin=30, fmax=11000) #(64,87)
                b_mel = b_mel[:64,:80]
                np.save(os.path.join(mel_dir, out_name) + ".npy", b_mel)
                b_mfcc = librosa.feature.mfcc(audio, sr=22050, n_mfcc=16, hop_length=256) #(16,346)
                b_mfcc = b_mfcc[:16,:320]
                np.save(os.path.join(mfcc_dir, out_name) + ".npy", b_mfcc)
        
    print('played {0} out of {1} presets'.format(preset_count, len(preset_files)))
