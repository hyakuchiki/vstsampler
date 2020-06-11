from __future__ import division
import hashlib
from .h2p import read_h2p_file
from .dx7 import read_patch
import json, os
import abc
from copy import deepcopy
ABC = abc.ABCMeta('ABC', (object,), {'__slots__': ()}) #https://stackoverflow.com/a/38668373

class Preset():
    def __init__(self, synth_name, preset_name=None, preset_path=None, params=None, meta=None):
        """
        params: dict of parameter values {"Param name": value, ...}
        
        """
        self.preset_name = preset_name
        self.preset_path = preset_path
        self.synth_name = synth_name
        self.params = params #dictionary of parameters in original preset format not MIDI
        self.hash = hashlib.md5(str(sorted(self.params.items(), key=lambda x: x[0])).encode("UTF-8")).hexdigest()
        self.meta = meta #Metadata object?
            
    def __len__(self):
        return len(self.params)

class PresetLoader(ABC): 
    def __init__(self, default_json):
        """
        default_json: json dictionary with default preset to fill in when presets are missing
        """
        with open(default_json) as f:
            self.default_params = json.load(f)
    
    @abc.abstractmethod
    def load_file(self, file_path):
        pass

class DivaPresetLoader(PresetLoader):
    def load_file(self, file_path):
        params, meta = read_h2p_file(file_path, "Diva")
        if params is None:
            return None
        else:
            # fill in missing data
            param_dict = self.default_params.copy()
            for key in params:
                param_dict[key] = params[key] 
            #TODO: check for out of range values?
        return Preset("Diva", preset_name=os.path.basename(file_path)[:-4], preset_path=file_path, params=param_dict, meta=meta)

class DX7PresetLoader(PresetLoader):
    def load_file(self, file_path):
        size = os.path.getsize(file_path)
        if size not in [4104, 4096]:
            return []
        with open(file_path, "rb") as f:
            presets = []
            if size == 4104:
                f.seek(6)
            bankname, _ = os.path.splitext(file_path)      
            for patch_num in range(32):
                patchData = f.read(128)
                patch, voicedata = read_patch(bankname, patch_num, patchData)
                #TODO: check for out of range values?
                if patch is None:
                    break
                # DX7 SYX files don't have missing data
                # param_dict = self.default_params.copy()
                # param_dict.update(patch)
                preset = Preset("Dexed", preset_name = voicedata, preset_path=file_path, params=patch)
                presets.append(preset)
        return presets

class PresetFixer():
    def __init__(self, default_json, moving_setting):
        """
        class to 'fix' certain parameters of presets to default settings in place
        default_json: json with default preset to fill in when presets are missing
        json and not a preset file b/c somehow preset files are often missing certain fields...
        moving_setting: txt file with params to move and not fix
        """
        with open(default_json) as f:
            self.default_params = json.load(f)
        with open(moving_setting) as f:
            self.moving_param_names = set([line.strip() for line in f])
        self.fixed_param_names = set(self.default_params.keys()) - self.moving_param_names
    
    def fix_preset(self, preset):
        fixed_preset = deepcopy(preset)
        for k in self.fixed_param_names:
            fixed_preset.params[k] = self.default_params[k]
        return fixed_preset