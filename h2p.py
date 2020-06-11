from __future__ import division
import codecs, os, traceback
from .util import is_number
"""
    Utilities for reading parameters and metadata from h2p (u-he synths preset format)
"""
def get_h2p_params(file, plug_name=None):
    """
    Reads h2p files and gets the parameters
    Only tested for Diva
    
    Parameters
    ----------
    file: file object of h2p (f = open("h2pfile"))

    Returns
    ----------
    param_dict: dictionary of parameters (ex. {"OSC1: Tune": 12.0, ...})
    """
    param_dict={}
    mode = 0 #skip the meta section
    for line in file:
        if line.rstrip() == "// Section for ugly compressed binary Data":
            break
        if "//" in line: # just for weird presets with lines commented out 
            line = line.split("//")[0].rstrip()
        elif line[:4] == "#AM=": #check what plugin it is
            if plug_name:
                assert line.strip().lower() == ("#am="+plug_name).lower(), "Not {0} but {1}".format(plug_name, line)
        elif line == "#cm=main\n": # 
            mode = "main" #beginning of parameters
        elif mode == 0 or line.strip() == "":
            continue
        elif line[:3] == "#cm": #marks new section (OSC, VCF, etc.)
            mode = line.split("=")[1].rstrip()
        else:
            if "=" in line:
                suffix, value = line.split("=")
                value = value.rstrip().strip("'")
                value = float(value) if is_number(value) else value
                param_dict[mode+"_"+suffix] = value
    return param_dict

def get_h2p_meta(file):
    """
    Gets metadata (Character, Description, Author) of h2p and returns
    Parameters
    ----------
    file: file object of h2p (f = open("h2pfile"))

    Returns
    ----------
    param_dict: dictionary of metadata (ex. {"Author": "Howard Scarr", ...})
    """
    metad={}
    for line in file:
        if line.endswith(":\n"):
            n_line = next(file)
            field_name = line.strip("':\n")
            if "," in n_line and field_name != "Description": #Character, 
                metad[field_name] = n_line.strip("'\n").split(", ")
            else:
                metad[field_name] = [n_line.strip("'\n")]
        if line == "*/\n":
            break
    return metad

def read_h2p_file(filename, plug_name, init_conf=None):
    with codecs.open(filename, encoding="ISO-8859-1") as f:
        try:
            params = get_h2p_params(f, plug_name)
            f.seek(0)
            meta = get_h2p_meta(f)
        except KeyboardInterrupt:
            exit()
        except Exception as e:
            print("{0}, {1}".format(filename, e))
            traceback.print_exc()
            return None, None
        else:
            return params, meta