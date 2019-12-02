from __future__ import division
from tqdm import tqdm
import numpy as np
from utils import resample
from synth_data import midi_indices, preset_info, midi_only
class Synth():
    synth = None
    preset = None
    midi_params = {}
    midi_cc = None

    def __init__(self, synth_name):
        if synth_name in midi_indices.keys():
            self.synth_name = synth_name
        else:
            print("Wrong name for synth")
        # load plugin preset-midicc info
        self.preset_desc = preset_info[synth_name]
        self.midi_idx = midi_indices[synth_name]

    def load_synth(self, synth_dir, init_fxp=None, sample_rate=44100, buffer_size=512, fft_size=512):
        import librenderman as rm
        self.engine = rm.RenderEngine(sample_rate, buffer_size, fft_size)
        self.engine.load_plugin(synth_dir)
        if init_fxp:
            self.engine.load_preset(init_fxp)
        self.sample_rate = sample_rate

    def play_note(self, pitch, velocity, note_length=3.8, render_length=4.0, output_rate=22050):
        self.engine.set_patch(self.midi_cc)
        self.engine.render_patch(pitch, 0, 0.5, 1.0, True) # render a really quiet sound to remove blip
        self.engine.render_patch(pitch, velocity, note_length, render_length, True)
        audio = np.array(self.engine.get_audio_frames())
        # return resample(audio, self.sample_rate, output_rate)
        return audio

    def preset_to_midicc(self, preset):
        """
            Loads preset object and sets midi-cc ex.) [(0,0.3), (1,0.8),...]
            also sets midi_params dictionary with cc names as key
        """
        self.preset = preset
        midi_params = {}
        pd = self.preset_desc
        midi_params.update(midi_only[self.synth_name]) 
        for p_name, v in preset.params.items():
            if pd[p_name]["MIDI"]:
                midi_params[pd[p_name]["MIDI"]] = value2midi(v, pd[p_name]["type"], pd[p_name]["range"], p_name)
        self.midi_params = midi_params
        self.midi_cc = [(self.midi_idx[pn], v) for pn, v in self.midi_params.items()]

def value2midi(value, param_type, param_range, name=None):
    """
    assumes parameter values are mapped linearly to 0.0 - 1.0 (should be for most synths)
    Parameters
    ----------
    value: real value of param, string/int/float
    param_type: parameter type, can be c or d
    param_range: parameter range, if type==c: [min,max] elif type==d: [possible values]
    Returns
    ----------
    v: MIDI CC value (0.0-1.0)
    """
    if param_type == "c": # continuous
        min_v, max_v = param_range
        v = (value - min_v) / (max_v - min_v)
        if value < min_v or value > max_v:
            tqdm.write("{0}: {1} not in {2}".format(name, value, param_range))
    elif param_type == "d": #categorical/discrete
        if value not in param_range:
            tqdm.write("{0}: {1} not in {2}".format(name, value, param_range))
            v = param_range[0] if value < param_range[0] else param_range[-1]
        else:
            v = param_range.index(value) / (len(param_range) - 1)
    else: # ?
        v = 0.0
    if v < 0 or v > 1:
        v = min(1, max(0, v))

    return v