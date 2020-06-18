from __future__ import division
from tqdm import tqdm
import numpy as np
from .util import resample
from .data.synth_data import midi_indices, preset_info, midi_only
import random

class Synth():
    synth = None
    preset = None
    midi_params = {}
    
    def __init__(self, synth_name):
        if synth_name in midi_indices.keys():
            self.synth_name = synth_name
        else:
            print("Wrong name for synth")
        # load plugin preset-midicc info
        self.preset_desc = preset_info[synth_name]
        self.midi_idx = midi_indices[synth_name]

    def load_synth(self, synth_dir, init_fxb=None, sample_rate=44100, buffer_size=512, fft_size=512):
        import librenderman as rm
        self.engine = rm.RenderEngine(sample_rate, buffer_size, fft_size)
        self.engine.load_plugin(synth_dir)
        if init_fxb:
            self.engine.load_preset(init_fxb)
        self.sample_rate = sample_rate

    def play_note(self, pitch, velocity, note_length=3.8, render_length=4.0, output_rate=22050):
        """
        makes midi-cc ex.) [(0,0.3), (1,0.8),...] for renderman to use
        and plays a midi note
        """
        midi_cc = [(self.midi_idx[pn], v) for pn, v in self.midi_params.items()]
        self.engine.set_patch(midi_cc)
        # self.engine.render_patch(pitch, 0, 0.5, 1.0, True) # render a really quiet sound to remove blip
        self.engine.render_patch(pitch, velocity, note_length, render_length, True)
        audio = np.array(self.engine.get_audio_frames())
        return resample(audio, self.sample_rate, output_rate)
    
    def preset_to_midi(self, preset):
        """
            Loads preset object
            sets midi_params dictionary with cc names as key
        """
        self.preset = preset
        self.params_to_midi(preset.params)

    def params_to_midi(self, params):
        """ From preset parameters, sets and returns midi parameters with cc names as key 


        Arguments:
            params {dict} -- dict of preset parameters

        Returns:
            dict -- dict of midi parameters
        """
        self.oor = 0 #no. of out of range params
        midi_params = {}
        pd = self.preset_desc
        self.one_hots = {}
        midi_params.update(midi_only[self.synth_name])
        for p_name, v in params.items():
            if not p_name in pd:
                continue
            p_info = pd[p_name]
            if not p_info["MIDI"]: continue
            midi_params[p_info["MIDI"]], oor, one_hot = value2midi(v, p_info["type"], p_info["range"], p_name)
            if p_info["type"] == "d":
                self.one_hots[p_name] = one_hot
            if oor:
                self.oor += 1
        self.midi_params = midi_params
        return midi_params

    def set_random(self, use_params, default_params, rng=None):
        """set synth midi parameters randomly

        Arguments:
            use_params {list} -- list of parameters to set randomly
            default_params {dict} -- default values to fall back to
        """
        self.preset = None
        self.oor = 0        
        self.one_hots = {}
        midi_params = self.params_to_midi(default_params)
        midi_params.update(midi_only[self.synth_name])
        for p_name, p_info in self.preset_desc.items():
            if not p_info["MIDI"]: continue
            if not p_name in use_params: continue
            if p_info["type"] == "c": # continuousな場合は普通にMIDIそのまま生成してもおｋ
                midi_params[p_info["MIDI"]] = random.random()
            elif p_info['type'] == 'd':
                v_range = p_info["range"]
                if rng:
                    idx = rng.integers(0, len(v_range))
                else:
                    idx = random.randrange(0, len(v_range))
                midi_params[p_info["MIDI"]] = idx / (len(v_range)-1)
                self.one_hots[p_name] = np.eye(len(v_range))[idx]
        self.midi_params = midi_params
    
    def gen_random_params(self, use_params, default_params, rng=None):
        """generating random preset parameter dicts

        Arguments:
            use_params {list} -- list of parameters to set randomly
            default_params {dict} -- default preset values to fall back to

        Returns:
            params {dict} -- parameter dict of random preset
        """
        self.preset = None
        self.oor = 0        
        self.one_hots = {}
        params = default_params.copy()
        if rng:
            for p_name, p_info in self.preset_desc.items():
                if not p_name in use_params: continue
                if p_info["type"] == "c": 
                    params[p_name] = rng.integers(*p_info["range"], endpoint=True)
                elif p_info['type'] == 'd':
                    params[p_name] = rng.choice(p_info["range"])
        else:
            for p_name, p_info in self.preset_desc.items():
                if not p_name in use_params: continue
                if p_info["type"] == "c": 
                    params[p_name] = random.randint(*p_info["range"])
                elif p_info['type'] == 'd':
                    params[p_name] = random.choice(p_info["range"])
        return params                


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
    oor: Bool Out of range or not
    (one_hot:
    """
    oor = False
    if param_type == "c": # continuous
        min_v, max_v = param_range
        v = (value - min_v) / (max_v - min_v)
        if value < min_v or value > max_v:
            tqdm.write("{0}: {1} not in {2}".format(name, value, param_range))
            oor = True
            v = min(1, max(0, v))
        return v, oor, None
    elif param_type == "d": #categorical/discrete
        if value not in param_range:
            tqdm.write("{0}: {1} not in {2}".format(name, value, param_range))
            v = param_range[0] if value < param_range[0] else param_range[-1]
            oor = True
            one_hot = np.eye(len(param_range))[0] if value < param_range[0] else np.eye(len(param_range))[-1]
        else:
            loc = param_range.index(value)
            v = loc / (len(param_range) - 1)
            one_hot = np.eye(len(param_range))[loc]
        return v, oor, one_hot
    else: # ?
        return 0, True, None
