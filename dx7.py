#%%
from __future__ import division
import os, struct
from synth_data import preset_info, dexed_midi_only

#https://github.com/asb2m10/dexed/blob/73a266dd70e58e7def14a52bf2a53b5486d083dc/Documentation/sysex-format.txt

def read_patch(bankname, patch_num, patchData): # reads 128 byte patch data
    operators={}
    if patchData is "":
        return None, None
    try:
        data = struct.unpack("B"*128, patchData)
    except:
        return None, None
    for i in range(6):
        op={}
        startidx=(5-i)*17
        opdata = data[startidx:startidx+17]
        for j in range(4):
            op["EG RATE " + str(j+1)] = opdata[j]
            op["EG LEVEL "+ str(j+1)] = opdata[j+4]
        op["BREAK POINT"] = opdata[8]
        op["L SCALE DEPTH"] = opdata[9]
        op["R SCALE DEPTH"] = opdata[10]
        op["L KEY SCALE"] = opdata[11]&3
        op["R KEY SCALE"] = opdata[11]>>2&3
        op["RATE SCALING"] = opdata[12]&7
        op["OSC DETUNE"] = (opdata[12]>>3) -7 #values are 0 to 14 but -7 to 7 on synth
        op["A MOD SENS."] = opdata[13]&3 
        op["KEY VELOCITY"] = opdata[13]>>2
        op["OUTPUT LEVEL"] = opdata[14]
        op["MODE"] = opdata[15]&1
        op["F COARSE"] = opdata[15]>>1
        op["F FINE"] = opdata[16]
        operators[str(i+1)] = op
    
    patch = {}
    for op_num in operators:
        for param in operators[op_num]:
            patch["OP"+op_num+" "+param] = operators[op_num][param]

    for i in range(4):
        patch["PITCH EG RATE "+ str(i+1)] = data[102+i]
        patch["PITCH EG LEVEL "+ str(i+1)] = data[106+i]
    
    patch["ALGORITHM"] = data[110] # displayed as 1-32 but we will treat it as 0-31
    patch["FEEDBACK"] = data[111]&7
    patch["OSC KEY SYNC"] = data[111]>>3
    patch["LFO SPEED"] = data[112]
    patch["LFO DELAY"] = data[113]
    patch["LFO PM DEPTH"] = data[114]
    patch["LFO AM DEPTH"] = data[115]
    patch["P MODE SENS."] = data[116]>>4 #[1] contradicts with [2]
    patch["LFO WAVE"] = (data[116]>>1)&7
    patch["LFO KEY SYNC"] = data[116] & 1
    patch["MIDDLE C"] = data[117]
    voiceData = bankname+"_" + str(patch_num).zfill(2) + "_" +"".join(chr(i) for i in data[118:128]) # name of bank+patch no. in bank + name of patch
    return patch, voiceData


if __name__ == "__main__":
    p = read_syx_dump("test/CJSP5.SYX")
    print(p)
