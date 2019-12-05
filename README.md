# vst-sampler
VST Sampler with preset loading capabilities
## How it works
Loads presets by converting to MIDI CC. 
Only works for Diva and [Dexed](https://github.com/asb2m10/dexed) (a DX7 emulator) for now.
Plays vsts using renderman.

# Usage
```python
from synth import Synth 
from preset import DX7PresetLoader, DivaPresetLoader

dexed = Synth("Dexed")
# Load the vst
dexed.load_synth("/Library/Audio/Plug-Ins/VST/Dexed.vst", sample_rate=44100, buffer_size=512)
# Load presets
dx7loader = DX7PresetLoader("settings/Dexed/dexed_default.json") # default values for missing parameters
basic2 = dx7loader.load_file("test/DXBASIC2.SYX") # SYX dumps for DX7 has 32 presets inside
a.preset_to_midi(basic2[20]) #loading preset and setting midi_params for synth

note = a.play_note(pitch=50, velocity=60, note_length=3.0, render_length=4.0, output_rate=22050) #outputs np.array of audio
```
