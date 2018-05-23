import numpy as np
import os
import sys


data_path = sys.argv[1]
label = sys.argv[2]
area = sys.argv[3]

load_path = os.path.join(data_path,
                         label,
                         'Analysis',
                         'synaptic_input')

save_path = os.path.join(data_path,
                         label,
                         'Analysis',
                         'bold_signal')

try:
    os.mkdir(save_path)
except FileExistsError:
    pass

fn = os.path.join(load_path,
                  'synaptic_input_{}.npy'.format(area))
synaptic_input = np.load(fn)


def bold_R_parser(fn):
    f = open(fn, 'r')
    # skip first line
    f.readline()

    bold_signal = []
    for l in f:
        bold_signal.append(float(l.split(' ')[-1]))
    f.close()
    return np.array(bold_signal)


fn = os.path.join(save_path,
                  'syn_input_{}.txt'.format(area))
out_fn = os.path.join(save_path,
                      'bold_syn_input_{}.txt'.format(area))

np.savetxt(fn, synaptic_input / np.max(synaptic_input))
os.system('Rscript --vanilla compute_bold_signal.R {} {}'.format(fn, out_fn))

bold_signal = bold_R_parser(out_fn)
fn = os.path.join(save_path,
                  'bold_signal_{}.npy'.format(area))
np.save(fn, bold_signal)

