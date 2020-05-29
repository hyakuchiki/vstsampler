from __future__ import division
import os, csv, ast, codecs
from util import is_number
import re

"""
This is a mess

"""
script_dir = os.path.dirname(__file__)
# data_dir = os.path.join(script_dir, "data")
data_dir = script_dir
def get_divah2p_info():
    diva_param_infos={}
    with codecs.open(os.path.join(data_dir,"divaparam.csv"), encoding='utf-8-sig') as f:
        reader = csv.DictReader(f)
        for row in reader:
            param_info = {}
            name = row["h2p"].strip("'")
            if name == "":
                continue
            param_info["MIDI"] = None if row["MIDI"] in ["x", ""] else row["MIDI"]
            param_info["type"] = None if row["type"] == "" else row["type"]
            if row["min"] == "" or not row["type"] in ["c", "d"]:
                param_info["range"] = None 
            elif param_info["type"] == "c":
                param_info["range"] = [float(row["min"]), float(row["max"])]
            elif param_info["type"] == "d":
                if float(row["min"]) < -999:
                    param_info["range"] = ast.literal_eval(row["max"])
                else:
                    param_info["range"] = list(range(int(row["min"]), int(row["max"])+1))
            diva_param_infos[name] = param_info
    return diva_param_infos

rev_diva_midi_idx = {0: "main: Output", 1: "main: Active #FX1", 2: "main: Active #FX2", 3: "PCore: LED Colour", 4: "VCC: Voices", 5: "VCC: Voice Stack", 6: "VCC: Mode", 7: "VCC: GlideMode", 8: "VCC: Glide", 9: "VCC: Glide2", 10: "VCC: GlideRange", 11: "VCC: PitchBend Up", 12: "VCC: PitchBend Down", 13: "VCC: TuningMode", 14: "VCC: Transpose", 15: "VCC: FineTuneCents", 16: "VCC: Note Priority", 17: "VCC: MultiCore", 18: "OPT: Accuracy", 19: "OPT: OfflineAcc", 20: "OPT: TuneSlop", 21: "OPT: CutoffSlop", 22: "OPT: GlideSlop", 23: "OPT: PWSlop", 24: "OPT: EnvrateSlop", 25: "OPT: V1Mod", 26: "OPT: V2Mod", 27: "OPT: V3Mod", 28: "OPT: V4Mod", 29: "OPT: V5Mod", 30: "OPT: V6Mod", 31: "OPT: V7Mod", 32: "OPT: V8Mod", 33: "ENV1: Attack", 34: "ENV1: Decay", 35: "ENV1: Sustain", 36: "ENV1: Release", 37: "ENV1: Velocity", 38: "ENV1: Model", 39: "ENV1: Trigger", 40: "ENV1: Quantise", 41: "ENV1: Curve", 42: "ENV1: Release On", 43: "ENV1: KeyFollow", 44: "ENV2: Attack", 45: "ENV2: Decay", 46: "ENV2: Sustain", 47: "ENV2: Release", 48: "ENV2: Velocity", 49: "ENV2: Model", 50: "ENV2: Trigger", 51: "ENV2: Quantise", 52: "ENV2: Curve", 53: "ENV2: Release On", 54: "ENV2: KeyFollow", 55: "LFO1: Sync", 56: "LFO1: Restart", 57: "LFO1: Waveform", 58: "LFO1: Phase", 59: "LFO1: Delay", 60: "LFO1: DepthMod Src1", 61: "LFO1: DepthMod Dpt1", 62: "LFO1: Rate", 63: "LFO1: FreqMod Src1", 64: "LFO1: FreqMod Dpt", 65: "LFO2: Sync", 66: "LFO2: Restart", 67: "LFO2: Waveform", 68: "LFO2: Phase", 69: "LFO2: Delay", 70: "LFO2: DepthMod Src1", 71: "LFO2: DepthMod Dpt1", 72: "LFO2: Rate", 73: "LFO2: FreqMod Src1", 74: "LFO2: FreqMod Dpt", 75: "MOD: Quantise", 76: "MOD: Slew Rate", 77: "MOD: RectifySource", 78: "MOD: InvertSource", 79: "MOD: QuantiseSource", 80: "MOD: LagSource", 81: "MOD: AddSource1", 82: "MOD: AddSource2", 83: "MOD: MulSource1", 84: "MOD: MulSource2", 85: "OSC: Model", 86: "OSC: Tune1", 87: "OSC: Tune2", 88: "OSC: Tune3", 89: "OSC: Vibrato", 90: "OSC: PulseWidth", 91: "OSC: Shape1", 92: "OSC: Shape2", 93: "OSC: Shape3", 94: "OSC: FM", 95: "OSC: Sync2", 96: "OSC: OscMix", 97: "OSC: Volume1", 98: "OSC: Volume2", 99: "OSC: Volume3",100: "OSC: PulseShape",101: "OSC: SawShape",102: "OSC: SuboscShape",103: "OSC: Tune1ModSrc",104: "OSC: Tune1ModDepth",105: "OSC: Tune2ModSrc",106: "OSC: Tune2ModDepth",107: "OSC: PWModSrc",108: "OSC: PWModDepth",109: "OSC: ShapeSrc",110: "OSC: ShapeDepth",111: "OSC: Triangle1On",112: "OSC: Sine2On",113: "OSC: Saw1On",114: "OSC: Pwm1On",115: "OSC: Triangle2On",116: "OSC: Saw2On",117: "OSC: Pulse2On",118: "OSC: PWM2On",119: "OSC: Noise1On",120: "OSC: ShapeModel",121: "OSC: Sync3",122: "OSC: NoiseVol",123: "OSC: NoiseColor",124: "OSC: TuneModOsc1",125: "OSC: TuneModOsc2",126: "OSC: TuneModOsc3",127: "OSC: ShapeModOsc1",128: "OSC: ShapeModOsc2",129: "OSC: ShapeModOsc3",130: "OSC: TuneModMode",131: "OSC: EcoWave1",132: "OSC: EcoWave2",133: "OSC: RingmodPulse",134: "OSC: Drift",135: "OSC: FmModSrc",136: "OSC: FmModDepth",137: "OSC: NoiseVolModSrc",138: "OSC: NoiseVolModDepth",139: "HPF: Model",140: "HPF: Frequency",141: "HPF: Resonance",142: "HPF: Revision",143: "HPF: KeyFollow",144: "HPF: FreqModSrc",145: "HPF: FreqModDepth",146: "HPF: Post-HPF Freq",147: "VCF1: Model",148: "VCF1: Frequency",149: "VCF1: Resonance",150: "VCF1: FreqModSrc",151: "VCF1: FreqModDepth",152: "VCF1: FreqMod2Src",153: "VCF1: FreqMod2Depth",154: "VCF1: KeyFollow",155: "VCF1: FilterFM",156: "VCF1: LadderMode",157: "VCF1: LadderColor",158: "VCF1: SlnKyRevision",159: "VCF1: SvfMode",160: "VCF1: Feedback",161: "VCF1: ResModSrc",162: "VCF1: ResModDepth",163: "VCF1: FmAmountModSrc",164: "VCF1: FmAmountModDepth",165: "VCF1: FeedbackModSrc",166: "VCF1: FeedbackModDepth",167: "VCA1: Pan",168: "VCA1: Volume",169: "VCA1: VCA",170: "VCA1: Modulation",171: "VCA1: ModDepth",172: "VCA1: PanModulation",173: "VCA1: PanModDepth",174: "VCA1: Mode",175: "VCA1: Offset",176: "Scope1: Frequency",177: "Scope1: Scale",178: "FX1: Module",179: "Chrs1: Type",180: "Chrs1: Rate",181: "Chrs1: Depth",182: "Chrs1: Wet",183: "Phase1: Type",184: "Phase1: Rate",185: "Phase1: Feedback",186: "Phase1: Stereo",187: "Phase1: Sync",188: "Phase1: Phase",189: "Phase1: Wet",190: "Plate1: PreDelay",191: "Plate1: Diffusion",192: "Plate1: Damp",193: "Plate1: Decay",194: "Plate1: Size",195: "Plate1: Dry",196: "Plate1: Wet",197: "Delay1: Left Delay",198: "Delay1: Center Delay",199: "Delay1: Right Delay",200: "Delay1: Side Vol",201: "Delay1: Center Vol",202: "Delay1: Feedback",203: "Delay1: HP",204: "Delay1: LP",205: "Delay1: Dry",206: "Delay1: Wow",207: "Rtary1: Mode",208: "Rtary1: Mix",209: "Rtary1: Balance",210: "Rtary1: Drive",211: "Rtary1: Stereo",212: "Rtary1: Out",213: "Rtary1: Slow",214: "Rtary1: Fast",215: "Rtary1: RiseTime",216: "Rtary1: Controller",217: "FX2: Module",218: "Chrs2: Type",219: "Chrs2: Rate",220: "Chrs2: Depth",221: "Chrs2: Wet",222: "Phase2: Type",223: "Phase2: Rate",224: "Phase2: Feedback",225: "Phase2: Stereo",226: "Phase2: Sync",227: "Phase2: Phase",228: "Phase2: Wet",229: "Plate2: PreDelay",230: "Plate2: Diffusion",231: "Plate2: Damp",232: "Plate2: Decay",233: "Plate2: Size",234: "Plate2: Dry",235: "Plate2: Wet",236: "Delay2: Left Delay",237: "Delay2: Center Delay",238: "Delay2: Right Delay",239: "Delay2: Side Vol",240: "Delay2: Center Vol",241: "Delay2: Feedback",242: "Delay2: HP",243: "Delay2: LP",244: "Delay2: Dry",245: "Delay2: Wow",246: "Rtary2: Mode",247: "Rtary2: Mix",248: "Rtary2: Balance",249: "Rtary2: Drive",250: "Rtary2: Stereo",251: "Rtary2: Out",252: "Rtary2: Slow",253: "Rtary2: Fast",254: "Rtary2: RiseTime",255: "Rtary2: Controller",256: "CLK: Multiply",257: "CLK: TimeBase",258: "CLK: Swing",259: "ARP: Direction",260: "ARP: Octaves",261: "ARP: Multiply",262: "ARP: Restart",263: "ARP: OnOff",264: "OSC: DigitalShape2",265: "OSC: DigitalShape3",266: "OSC: DigitalShape4",267: "VCF1: ShapeMix",268: "VCF1: ShapeModSrc",269: "VCF1: ShapeModDepth",270: "VCF1: UhbieBandpass",271: "ARP: Order",272: "LFO1: Polarity",273: "LFO2: Polarity",274: "Phase1: Depth",275: "Phase1: Center",276: "Phase2: Depth",277: "Phase2: Center",278: "OSC: DigitalType1",279: "OSC: DigitalType2",280: "OSC: DigitalAntiAlias"}

diva_midi_idx = {rev_diva_midi_idx[key]: key for key in rev_diva_midi_idx}

#Accuracy exists sometime but not in init h2p
#Env Trigger & VCA1: Mode, 0ffset, ARP: Restart, ARP: Multiply are meaningless but exists in init h2p

diva_midi_only = {'VCC: MultiCore':0.0, 'OPT: OfflineAcc':0, 'OPT: Accuracy':0, 'VCC: TuningMode':0.0, 'ENV1: Trigger':0.0, 'ENV2: Trigger':0.0, "VCA1: Mode":0.0, "VCA1: Offset":0.0, "ARP: Restart":0.0, "ARP: Multiply":0.0} 


rev_dexed_midi_idx = {0: "Cutoff",  1: "Resonance",  2: "Output",  3: "MASTER TUNE ADJ",  4: "ALGORITHM",  5: "FEEDBACK",  6: "OSC KEY SYNC",  7: "LFO SPEED",  8: "LFO DELAY",  9: "LFO PM DEPTH", 10: "LFO AM DEPTH", 11: "LFO KEY SYNC", 12: "LFO WAVE", 13: "MIDDLE C", 14: "P MODE SENS.", 15: "PITCH EG RATE 1", 16: "PITCH EG RATE 2", 17: "PITCH EG RATE 3", 18: "PITCH EG RATE 4", 19: "PITCH EG LEVEL 1", 20: "PITCH EG LEVEL 2", 21: "PITCH EG LEVEL 3", 22: "PITCH EG LEVEL 4", 23: "OP1 EG RATE 1", 24: "OP1 EG RATE 2", 25: "OP1 EG RATE 3", 26: "OP1 EG RATE 4", 27: "OP1 EG LEVEL 1", 28: "OP1 EG LEVEL 2", 29: "OP1 EG LEVEL 3", 30: "OP1 EG LEVEL 4", 31: "OP1 OUTPUT LEVEL", 32: "OP1 MODE", 33: "OP1 F COARSE", 34: "OP1 F FINE", 35: "OP1 OSC DETUNE", 36: "OP1 BREAK POINT", 37: "OP1 L SCALE DEPTH", 38: "OP1 R SCALE DEPTH", 39: "OP1 L KEY SCALE", 40: "OP1 R KEY SCALE", 41: "OP1 RATE SCALING", 42: "OP1 A MOD SENS.", 43: "OP1 KEY VELOCITY", 44: "OP1 SWITCH", 45: "OP2 EG RATE 1", 46: "OP2 EG RATE 2", 47: "OP2 EG RATE 3", 48: "OP2 EG RATE 4", 49: "OP2 EG LEVEL 1", 50: "OP2 EG LEVEL 2", 51: "OP2 EG LEVEL 3", 52: "OP2 EG LEVEL 4", 53: "OP2 OUTPUT LEVEL", 54: "OP2 MODE", 55: "OP2 F COARSE", 56: "OP2 F FINE", 57: "OP2 OSC DETUNE", 58: "OP2 BREAK POINT", 59: "OP2 L SCALE DEPTH", 60: "OP2 R SCALE DEPTH", 61: "OP2 L KEY SCALE", 62: "OP2 R KEY SCALE", 63: "OP2 RATE SCALING", 64: "OP2 A MOD SENS.", 65: "OP2 KEY VELOCITY", 66: "OP2 SWITCH", 67: "OP3 EG RATE 1", 68: "OP3 EG RATE 2", 69: "OP3 EG RATE 3", 70: "OP3 EG RATE 4", 71: "OP3 EG LEVEL 1", 72: "OP3 EG LEVEL 2", 73: "OP3 EG LEVEL 3", 74: "OP3 EG LEVEL 4", 75: "OP3 OUTPUT LEVEL", 76: "OP3 MODE", 77: "OP3 F COARSE", 78: "OP3 F FINE", 79: "OP3 OSC DETUNE", 80: "OP3 BREAK POINT", 81: "OP3 L SCALE DEPTH", 82: "OP3 R SCALE DEPTH", 83: "OP3 L KEY SCALE", 84: "OP3 R KEY SCALE", 85: "OP3 RATE SCALING", 86: "OP3 A MOD SENS.", 87: "OP3 KEY VELOCITY", 88: "OP3 SWITCH", 89: "OP4 EG RATE 1", 90: "OP4 EG RATE 2", 91: "OP4 EG RATE 3", 92: "OP4 EG RATE 4", 93: "OP4 EG LEVEL 1", 94: "OP4 EG LEVEL 2", 95: "OP4 EG LEVEL 3", 96: "OP4 EG LEVEL 4", 97: "OP4 OUTPUT LEVEL", 98: "OP4 MODE", 99: "OP4 F COARSE",100: "OP4 F FINE",101: "OP4 OSC DETUNE",102: "OP4 BREAK POINT",103: "OP4 L SCALE DEPTH",104: "OP4 R SCALE DEPTH",105: "OP4 L KEY SCALE",106: "OP4 R KEY SCALE",107: "OP4 RATE SCALING",108: "OP4 A MOD SENS.",109: "OP4 KEY VELOCITY",110: "OP4 SWITCH",111: "OP5 EG RATE 1",112: "OP5 EG RATE 2",113: "OP5 EG RATE 3",114: "OP5 EG RATE 4",115: "OP5 EG LEVEL 1",116: "OP5 EG LEVEL 2",117: "OP5 EG LEVEL 3",118: "OP5 EG LEVEL 4",119: "OP5 OUTPUT LEVEL",120: "OP5 MODE",121: "OP5 F COARSE",122: "OP5 F FINE",123: "OP5 OSC DETUNE",124: "OP5 BREAK POINT",125: "OP5 L SCALE DEPTH",126: "OP5 R SCALE DEPTH",127: "OP5 L KEY SCALE",128: "OP5 R KEY SCALE",129: "OP5 RATE SCALING",130: "OP5 A MOD SENS.",131: "OP5 KEY VELOCITY",132: "OP5 SWITCH",133: "OP6 EG RATE 1",134: "OP6 EG RATE 2",135: "OP6 EG RATE 3",136: "OP6 EG RATE 4",137: "OP6 EG LEVEL 1",138: "OP6 EG LEVEL 2",139: "OP6 EG LEVEL 3",140: "OP6 EG LEVEL 4",141: "OP6 OUTPUT LEVEL",142: "OP6 MODE",143: "OP6 F COARSE",144: "OP6 F FINE",145: "OP6 OSC DETUNE",146: "OP6 BREAK POINT",147: "OP6 L SCALE DEPTH",148: "OP6 R SCALE DEPTH",149: "OP6 L KEY SCALE",150: "OP6 R KEY SCALE",151: "OP6 RATE SCALING",152: "OP6 A MOD SENS.",153: "OP6 KEY VELOCITY",154: "OP6 SWITCH"}

dexed_midi_idx = {rev_dexed_midi_idx[key]: key for key in rev_dexed_midi_idx}

dexed_midi_only = {"MASTER TUNE ADJ":0.5, "OP1 SWITCH":1.0, "OP2 SWITCH":1.0, "OP3 SWITCH":1.0, "OP4 SWITCH":1.0, "OP5 SWITCH":1.0, "OP6 SWITCH":1.0, "Cutoff":1.0, "Resonance":0.0, "Output":1.0} #default midi values

def get_syx_info():
    syx_param_infos={}
    for k in dexed_midi_idx:
        cats = {"ALGORITHM":32, "LFO WAVE":6, "L KEY SCALE":4, "R KEY SCALE":4,
        "LFO KEY SYNC":2, "OSC KEY SYNC":2, "MODE": 2, "SWITCH": 2} # n classes
        cont = {"OSC DETUNE":[-7,7], "RATE SCALING": [0,7], "KEY VELOCITY":[0,7],
        "A MOD SENS.":[0,3], "F COARSE":[0,31], "FEEDBACK":[0,7],
        "P MODE SENS.":[0,7], "MIDDLE C":[0,48]} 
        param_info = {}
        param_name = re.sub(r'OP[0-6] ', '', k)
        param_info["MIDI"] = k
        if param_name in dexed_midi_only:
            # dexed only parameters are not in syx files
            continue
            # param_info["type"] = "c"
            # param_info["name"] = None
            # param_info["MIDI"] = k
            # param_info["range"] = None
        elif param_name in cats:
            param_info["type"] = "d"
            param_info["range"] = list(range(0,cats[param_name]))
        else:
            param_info["type"] = "c"
            if param_name in cont:
                param_info["range"] = cont[param_name]
            else:
                param_info["range"] = [0,99]
        syx_param_infos[k] = param_info
    return syx_param_infos

preset_info = {"Dexed": get_syx_info(), "Diva": get_divah2p_info()}

midi_indices = {"Diva": diva_midi_idx, "Dexed": dexed_midi_idx}

midi_only = {"Dexed": dexed_midi_only, "Diva": diva_midi_only}

preset_ext = {"Dexed": ".syx", "Diva": ".h2p"}
