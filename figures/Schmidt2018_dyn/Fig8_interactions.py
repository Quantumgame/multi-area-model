import csv
import correlation_toolbox.helper as ch
import json
import numpy as np
import os
import pyx
import scipy.io

from helpers import original_data_path
from multiarea_model.multiarea_model import MultiAreaModel
from plotcolors import myred, myblue
from scipy.spatial.distance import pdist
from scipy.spatial.distance import squareform

import matplotlib.pyplot as pl
from matplotlib import gridspec
from matplotlib import rc_file
rc_file('plotstyle.rc')

import sys
sys.path.append('../Schmidt2018')
from graph_helpers import apply_map_equation

"""
Figure layout
"""
cmap = pl.cm.coolwarm
cmap = cmap.from_list('mycmap', [myblue, 'white', myred], N=256)
cmap2 = cmap.from_list('mycmap', ['white', myred], N=256)


width = 7.0866
n_horz_panels = 2.
n_vert_panels = 3.

axes = {}
gs1 = gridspec.GridSpec(1, 3)
gs1.update(left=0.05, right=0.95, top=0.95,
           bottom=0.52, wspace=0., hspace=0.4)
axes['A'] = pl.subplot(gs1[:, 0])
axes['B'] = pl.subplot(gs1[:, 1])
axes['C'] = pl.subplot(gs1[:, 2])

gs1 = gridspec.GridSpec(1, 1)
gs1.update(left=0.18, right=0.8, top=0.44,
           wspace=0., bottom=0.27, hspace=0.2)
axes['D'] = pl.subplot(gs1[:, :])

gs1 = gridspec.GridSpec(1, 1)
gs1.update(left=0.165, right=0.6, top=0.15,
           wspace=0., bottom=0.075, hspace=0.2)
axes['E'] = pl.subplot(gs1[:, :])

gs1 = gridspec.GridSpec(1, 1)
gs1.update(left=0.688, right=0.95, top=0.15,
           wspace=0., bottom=0.075, hspace=0.2)
axes['F'] = pl.subplot(gs1[:, :])

for label in ['A', 'B', 'C', 'D', 'E', 'F']:
    if label in ['E', 'F']:
        label_pos = [-0.08, 1.01]
    else:
        label_pos = [-0.2, 1.01]
    pl.text(label_pos[0], label_pos[1], r'\bfseries{}' + label,
            fontdict={'fontsize': 16, 'weight': 'bold',
                      'horizontalalignment': 'left', 'verticalalignment':
                      'bottom'}, transform=axes[label].transAxes)
    axes[label].spines['right'].set_color('none')
    axes[label].spines['top'].set_color('none')
    axes[label].yaxis.set_ticks_position("left")
    axes[label].xaxis.set_ticks_position("bottom")

for label in ['E', 'F']:
    axes[label].spines['right'].set_color('none')
    axes[label].spines['top'].set_color('none')
    axes[label].spines['left'].set_color('none')
    axes[label].spines['bottom'].set_color('none')

    axes[label].yaxis.set_ticks_position("none")
    axes[label].xaxis.set_ticks_position("none")
    axes[label].set_yticks([])
    axes[label].set_xticks([])

"""
Load data
"""

"""
Create MultiAreaModel instance to have access to data structures
"""
M = MultiAreaModel({})


# Load experimental functional connectivity
func_conn_data = {}
with open('Fig8_exp_func_conn.csv', 'r') as f:
    myreader = csv.reader(f, delimiter='\t')
    # Skip first 3 lines
    next(myreader)
    next(myreader)
    next(myreader)
    areas = next(myreader)
    for line in myreader:
        dict_ = {}
        for i in range(len(line)):
            dict_[areas[i]] = float(line[i])
        func_conn_data[areas[myreader.line_num - 5]] = dict_

exp_FC = np.zeros((len(M.area_list),
                   len(M.area_list)))
for i, area1 in enumerate(M.area_list):
    for j, area2 in enumerate(M.area_list):
        exp_FC[i][j] = func_conn_data[area1][area2]


"""
Simulation data
"""
LOAD_ORIGINAL_DATA = True

if LOAD_ORIGINAL_DATA:
    tmin = 500.
    tmax = 10000.

    cc_weights_factor = [1.0, 1.4, 1.5, 1.6, 1.7, 1.75, 1.8, 1.9, 2., 2.1, 2.5]
    labels = ['33fb5955558ba8bb15a3fdce49dfd914682ef3ea',
              '783cedb0ff27240133e3daa63f5d0b8d3c2e6b79',
              '380856f3b32f49c124345c08f5991090860bf9a3',
              '5a7c6c2d6d48a8b687b8c6853fb4d98048681045',
              'c1876856b1b2cf1346430cf14e8d6b0509914ca1',
              'a30f6fba65bad6d9062e8cc51f5483baf84a46b7',
              '1474e1884422b5b2096d3b7a20fd4bdf388af7e0',
              '99c0024eacc275d13f719afd59357f7d12f02b77',
              'f18158895a5d682db5002489d12d27d7a974146f',
              '08a3a1a88c19193b0af9d9d8f7a52344d1b17498',
              '5bdd72887b191ec22a5abcc04ca4a488ea216e32']

    sim_FC = {}
    for label in labels:
        fn = os.path.join(original_data_path,
                          label,
                          'Analysis',
                          'functional_connectivity_synaptic_input.npy')
        sim_FC[label] = np.load(fn)

    label = '99c0024eacc275d13f719afd59357f7d12f02b77'
    fn = os.path.join(original_data_path,
                      label,
                      'Analysis',
                      'FC_synaptic_input_communities.json')
    with open(fn, 'r') as f:
        part_sim = json.load(f)
    part_sim_list = [part_sim[area] for area in M.area_list]
    part_sim_index = np.argsort(part_sim_list, kind='heapsort')


# """
# Load bold signals
# """
# label = '99c0024eacc275d13f719afd59357f7d12f02b77'
# bold_load_path = '../data/'
# bold = {}
# base_fn = 'bold_signal_syn_input/bold_signal_syn_input_{}'.format(label)
# for area in M.area_list:
#     bold[area] = np.load('{}_{}.npy'.format(base_fn, area))

# data[label].bold_signal = bold


def matrix_plot(ax, matrix, index, vlim, pos=None):
    ax.yaxis.set_ticks_position('none')
    ax.xaxis.set_ticks_position('none')

    x = np.arange(0, len(M.area_list) + 1)
    y = np.arange(0, len(M.area_list[::-1]) + 1)
    X, Y = np.meshgrid(x, y)

    ax.set_xlim((0, 32))
    ax.set_ylim((0, 32))

    ax.set_aspect(1. / ax.get_data_ratio())

    vmax = vlim
    vmin = -vlim

    # , norm = LogNorm(1e-8,1.))
    im = ax.pcolormesh(matrix[index][:, index][::-1],
                       cmap=cmap, vmin=vmin, vmax=vmax)

    cbticks = [-1., -0.5, 0., 0.5, 1.0]
    cb = pl.colorbar(im, ax=ax, ticks=cbticks, fraction=0.046)
    cb.ax.tick_params(labelsize=12)
    ax.set_yticks([i + 0.5 for i in np.arange(0, len(M.area_list) + 1)])
    ax.set_yticklabels(np.array(M.area_list)[index][::-1], size=8.)

    if pos != (0, 2):
        cb.remove()
    else:
        ax.text(1.25, 0.52, r'FC', rotation=90,
                transform=ax.transAxes, size=12)
    ax.set_xticks([i + 0.5 for i in np.arange(0, len(M.area_list) + 1)])
    ax.set_xticklabels(np.array(M.area_list)[index], rotation=90, size=8.)
    ax.tick_params(pad=1.5)


"""
Plotting
"""
ax = axes['A']
label = '99c0024eacc275d13f719afd59357f7d12f02b77'


matrix_plot(ax, sim_FC[label],
            part_sim_index[::-1], 1., pos=(0, 0))

ax = axes['B']
matrix_plot(ax, FC_exp,
            louvain_sim_mat_index[::-1], 1., pos=(0, 1))

# ax = axes['C']

# matrix_plot(ax, exp_FC, louvain_sim_mat_index[::-1], 1., pos=(0, 2))

# indices = np.array(1. - np.eye(32), dtype=np.bool)


# def compute_cc(label, cmp_matrix, measure='synaptic_input'):
#     ts = []
#     if measure == 'synaptic_input':
#         d = data[label].synaptic_input
#     elif measure == 'bold':
#         d = data[label].bold_signal
#     for area in M.area_list:
#         ts.append(ch.centralize(d[area], units=True))

#     D = pdist(ts, metric='correlation')
#     correlation_matrix = 1. - squareform(D)
#     for i in range(32):
#         correlation_matrix[i][i] = 0.

#     cc = np.corrcoef(correlation_matrix[indices].flatten(),
#                      cmp_matrix[indices].flatten())[0][1]
#     return cc

# for k in labels:
#     cc_exp = compute_cc(k, func_conn)
#     corrcoeffs['sim_exp'].append(cc_exp)
#     cc_struct = compute_cc(label, conn_matrix)
#     corrcoeffs['sim_struct'].append(cc_struct)

# label = '99c0024eacc275d13f719afd59357f7d12f02b77'
# cc_exp = compute_cc(label, func_conn)
# cc_struct = compute_cc(label, conn_matrix)
# ##########################################################################

# ax = axes['D']
# ax.spines['right'].set_color('none')
# ax.spines['top'].set_color('none')
# ax.yaxis.set_ticks_position("left")
# ax.xaxis.set_ticks_position("bottom")

# ax.plot(cc_weights_factor_100[0], cc_exp, '.',
#         ms=10, markeredgecolor='none', color='k')

# ax.plot(cc_weights_factor[1:], corrcoeffs[
#         'sim_exp'][1:], '.', ms=10, markeredgecolor='none', label='Sim. vs. Exp.', color='k')
# ax.plot(cc_weights_factor[0], corrcoeffs[
#         'sim_exp'][0], '^', ms=5, markeredgecolor='none', label='Sim. vs. Exp.', color='k')

# cc_bold = compute_cc('99c0024eacc275d13f719afd59357f7d12f02b77', func_conn, measure='bold')
# ax.plot(cc_weights_factor_100[0], cc_bold, '.',
#         ms=10, markeredgecolor='none', color=myred)

# print(("Corr. with HiRes",
#        np.corrcoef(correlation_matrix[indices].flatten(),
#                    func_conn[indices].flatten())[0][1]))
# print(("Corr. with HiRes", corrcoeffs['sim_exp']))
# print(("Corr. of structur with HiRes",
#        np.corrcoef(conn_matrix[indices].flatten(),
#                    func_conn[indices].flatten())[0][1]))

# ax.hlines(corrcoeffs['struct_exp'], -0.1,
#           2.5, linestyle='dashed', color='k')
# ax.set_xlabel(r'Cortico-cortical weight factor $\chi$',
#               labelpad=-0.1, size=16)
# ax.set_ylabel(r'$r_{\mathrm{Pearson}}$', size=16)
# ax.set_xlim((0.9, 2.7))
# ax.set_ylim((-0.1, 0.6))
# ax.set_yticks([0., 0.2, 0.4])
# ax.set_yticklabels([0., 0.2, 0.4], size=13)
# ax.set_xticks([1., 1.5, 2., 2.5])
# ax.set_xticklabels([1., 1.5, 2., 2.5], size=13)


"""
Save figure
"""
pl.savefig('Fig8_interactions_mpl.eps')

# """
# We compare the clusters found in the functional connectivity to
# clusters found in the structural connectivity of the network. To
# detect the clusters in the structural connectivity, we repeat the the
# procedure from Fig. 7 of Schmidt et al. 'Multi-scale account of the
# network structure of macaque visual cortex' and apply the map equation
# method (see Materials & Methods in Schmidt et al. 2018) to the
# structural connectivity of the network.

# This requires installation of the infomap executable and defining the
# path to the executable.
# """
# infomap_path = None
# filename = 'Fig8_structural_clusters'
# modules, modules_areas, index = apply_map_equation(M.K_matrix,
#                                                    M.area_list,
#                                                    filename='stab',
#                                                    infomap_path=infomap_path)
# files = 'Fig8_structural_clusters.map'
# map_equation_dict = {}
# with open('{}.map'.format(fn), 'r') as f:
#     line = ''
#     while '*Nodes' not in line:
#         line = f.readline()
#     line = f.readline()
#     map_equation = []
#     map_equation_areas = []
#     while "*Links" not in line:
#         map_equation.append(int(line.split(':')[0]))
#         map_equation_areas.append(line.split('"')[1])
#         line = f.readline()
#     f.close()
#     map_equation = np.array(map_equation)
#     map_equation_dict[label] = dict(
#         list(zip(map_equation_areas, map_equation)))

# To create the alluvial input, we rename the simulated clusters
# 1S --> 2S, 2S ---> 1S
# f = open('alluvial_input.txt', 'w')
# f.write("area,map_equation, louvain, louvain_exp\n")
# for i, area in enumerate(M.area_list):
#     if part_sim_mat[i] == 1:
#         psm = 2
#     elif part_sim_mat[i] == 2:
#         psm = 1
#     s = '{}, {}, {}, {}, {}'.format(area,
#                                     map_equation_dict[area],
#                                     psm,
#                                     part_exp_mat[i])
#     f.write(s)
#     f.write('\n')
# f.close()

# The alluvial plot cannot be created with a script. To reproduce the alluvial
# plot, go to http://app.rawgraphs.io/ and proceed from there.

"""
Merge with alluvial plot
"""
pyx.text.set(cls=pyx.text.LatexRunner)
pyx.text.preamble(r"\usepackage{helvet}")

c = pyx.canvas.canvas()
c.fill(pyx.path.rect(0, 0., 17.9, 17.), [pyx.color.rgb.white])

c.insert(pyx.epsfile.epsfile(0., 6., "Fig8_interactions_mpl.eps", width=17.9))
c.insert(pyx.epsfile.epsfile(
    1.7, 1., "Fig8_alluvial_struct_sim.eps", width=8.8))
c.insert(pyx.epsfile.epsfile(
    11.5, 1.3, "Fig8_alluvial_sim_exp.eps", width=5.4))

c.writeEPSfile("Fig8_interactions.eps")
