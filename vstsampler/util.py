from __future__ import division
import os
import numpy as np
import scipy.signal
def is_number(s):
    try:
        float(s)
        return True
    except ValueError:
        return False

def get_files_ext(top_dir, extension):
    presets_dirs = []

    for root, _, files in os.walk(top_dir):
        for filename in files:
            if filename.lower().endswith(extension.lower()):
                presets_dirs.append(os.path.join(root,filename))
    return presets_dirs

def resample(y, orig_sr, target_sr):
    if orig_sr == target_sr:
        return y
    ratio = float(target_sr) / orig_sr
    n_samples = int(np.ceil(y.shape[-1] * ratio))
    y_hat = scipy.signal.resample(y, n_samples, axis=-1)
    return np.ascontiguousarray(y_hat)