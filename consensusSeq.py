#! /usr/bin/env python

import matplotlib
matplotlib.use('Agg')
from math import log
import logging
import argparse
import numpy as np
import numpy as np
import scipy.interpolate as interpolate
import matplotlib.pyplot as plt
import copy
import operator
from matplotlib.font_manager import FontProperties
#from scipy.interpolate import spline #this one is obsolete
import matplotlib.patheffects

#from PIL import ImageFont


import sys
import itertools


#from CIAlign import FastaToArray


# python3 consensus Seq.py --infile /Users/lotti/Documents/Test_Case/gap_test/SevenJEV.afa


def FastaToArray(infile):
    '''
    Convert an alignment into a numpy array.
    Parameters
    ----------
    fasta_dict: dict
        dictionary based on a fasta file with sequence names as keys and
        sequences as values

    Returns
    -------
    arr: np.array
        2D numpy array in the same order as fasta_dict where each row
        represents a single column in the alignment and each column a
        single sequence.
    '''

    nams = []
    seqs = []
    nam = ""
    seq = ""
    with open(infile) as input:
        for line in input:
            line = line.strip()
            if line[0] == ">":
                    seqs.append(seq)
                    nams.append(nam)
                    seq = []
                    nam = line.replace(">", "")
            else:
                seq += list(line)
    seqs.append(seq)
    nams.append(nam)
    arr = np.array(seqs[1:])
    return (arr, nams[1:])


# class Scale(matplotlib.patheffects.RendererBase):
#     #Credits: Markus Piotrowski See: https://github.com/biopython/biopython/issues/850#issuecomment-225708297
#     def __init__(self, sx, sy=None):
#         self._sx = sx
#         self._sy = sy
#
#     def draw_path(self, renderer, gc, tpath, affine, rgbFace):
#         affine=affine.identity().scale(self._sx, self._sy)+affine
#         renderer.draw_path(gc, tpath, affine, rgbFace)

def findConsensus(alignment, consensus_type="majority"):
    '''
    '''
    consensus = []
    coverage = []
    numberOfSequences = len(alignment[:,0])

    #need the reverse of array to access every column
    for i in range(0,len(alignment[0,:])):
        unique, counts = np.unique(alignment[:,i], return_counts=True)
        count = dict(zip(unique, counts))
        unique_ng = unique[unique != "-"]
        counts_ng = counts[unique != "-"]
        if counts_ng.size == 0:
            count_ng = {"N": len(alignment[:,i])}
            nonGapContent = 0
        else:
            count_ng = dict(zip(unique_ng, counts_ng))
            if '-' in count:
                nonGapContent = 1-(count['-']/numberOfSequences)
            else:
                nonGapContent = 1

        # dealing with gap only collumns
        maxChar, maxCount = max(count.items(), key=operator.itemgetter(1))
        maxChar_ng, maxCount_ng = max(count_ng.items(), key=operator.itemgetter(1))

        # if there are an equal number of gap and non-gap characters at the
        # site, keep the non-gap character

        if maxCount_ng == maxCount or consensus_type == "majority_nongap":
            maxChar = maxChar_ng
        consensus.append(maxChar)
        coverage.append(nonGapContent)

    return consensus, coverage


def makePlot(consensus, coverage):

    x = np.arange(0, len(coverage), 1);
    y = coverage
    print(len(x), len(y))

    f = plt.figure()
    a = f.add_subplot('311')
    a.plot(x,y)
    a.get_xaxis().set_visible(False)

    b = f.add_subplot('312')

    #xnew = np.linspace(x.min(),x.max(),300) #300 represents number of points to make between T.min and T.max

    t, c, k = interpolate.splrep(x, y, s=0, k=4)
    N = 100
    xmin, xmax = x.min(), x.max()
    xx = np.linspace(xmin, xmax, N)
    spline = interpolate.BSpline(t, c, k, extrapolate=False)
    b.plot(xx, spline(xx))
    b.get_xaxis().set_visible(False)
    f.savefig('blub.png')


def sequence_logo(alignment):

    plt.figure(figsize=(len(alignment[0,:]),2.5))

    #plt.xkcd()
    axes = plt.gca()
    axes.set_xlim([0,len(alignment[0,:])+1])
    axes.set_ylim([0,3])
    seq_count = len(alignment[:,0])
    x = 0
    font = FontProperties()
    font.set_size(80)
    #print("fuck die henne", font.ascent())

    for i in range(0,len(alignment[0,:])):
        unique, counts = np.unique(alignment[:,i], return_counts=True)
        count = dict(zip(unique, counts))
        height_per_base, info_per_base = calc_entropy(count, seq_count)
        print('height', height_per_base)

        height_sum_higher = 0
        for base, height in height_per_base.items():
            if height > 0:
                txt = plt.text(x, height_sum_higher, base, fontsize=70, color='red')
                #txt = plt.text(x, height_sum_higher, base, fontsize=80, color='red')
                #txt.set_path_effects([Scale(1,height)])
                height_sum_higher += height
            elif height < 0:
                #todo
                print('jo')
        # coordinates and then scale aha aha aha
        # txt = plt.text(0, 0, "T", fontsize=64,color='red')
        # txt.set_path_effects([Scale(1,5)])
        # txt = plt.text(0, 0.1, "G", fontsize=64,color='green')
        # txt.set_path_effects([Scale(1,3)])
        # txt = plt.text(0.2, 0, "B", fontsize=64,color='blue')
        # txt.set_path_effects([Scale(1,7)])
        x += 1

    plt.show()
    plt.savefig('plotileini.png')


def sequence_bar_logo(alignment):

    for seq in alignment:
        print(type(seq))
        if np.any(seq == "U"):
            that_letter = "U"
        if np.any(seq == "T"):
            that_letter = "T"
    # if len(alignment[0,:]) < 65536:
    #     plt.figure(figsize=(len(alignment[0,:]) + 1,4))
    # else:
    plt.figure(1, figsize=(len(alignment[0,:]),4), frameon=False, dpi=100)
    fig, ax = plt.subplots()

    #plt.xkcd()
    axes = plt.gca()
    axes.set_xlim([-1,len(alignment[0,:])+1])
    axes.set_ylim([0,3])
    seq_count = len(alignment[:,0])
    x = 0
    width = 0.75

    ind = np.arange(len(alignment[0,:]))
    A_height = []
    G_height = []
    C_height = []
    U_height = []

    for i in range(0,len(alignment[0,:])):
        unique, counts = np.unique(alignment[:,i], return_counts=True)
        count = dict(zip(unique, counts))
        height_per_base, info_per_base = calc_entropy(count, seq_count, that_letter)
        print('height', height_per_base)
        # todo: multiple with non gap count

        A_height.append(height_per_base["A"])
        G_height.append(height_per_base["G"])
        C_height.append(height_per_base["C"])
        U_height.append(height_per_base[that_letter])


    bar_plot = plt.bar(ind, A_height, width, color='#f43131')
    # for idx,rect in enumerate(bar_plot):
    #     height = rect.get_height()
    #     ax.text(rect.get_x() + rect.get_width(), height, "A", ha='center', va='bottom')
    plt.bar(ind, G_height, width, bottom=A_height, color='#f4d931')
    plt.bar(ind, C_height, bottom=[i+j for i,j in zip(A_height, G_height)], width=width, color='#1ed30f')
    plt.bar(ind, U_height, bottom=[i+j+k for i,j,k in zip(A_height, G_height, C_height)], width=width, color='#315af4')



    plt.savefig('plotileini_bar.png')


def calc_entropy(count, seq_count, that_letter):

    # total number of Sequences - gap number
    # adjust total height later to make up for gaps - i think that's covered (?)
    sample_size_correction = (1/log(2)) * (3/(2*seq_count))
    if count.get("-"):
        seq_count -= count.get("-")
    info_per_base = {"A": 0, "G": 0, that_letter: 0, "C": 0}
    freq_per_base = {"A": 0, "G": 0, that_letter: 0, "C": 0}
    height_per_base = {"A": 0, "G": 0, that_letter: 0, "C": 0}
    entropy_per_base = {"A": 0, "G": 0, that_letter: 0, "C": 0}
    entropy = 0
    if seq_count == 0:
        return height_per_base, info_per_base

    for base, quantity in count.items():
        if base != "-":
            frequency = quantity/seq_count
            freq_per_base[base] = frequency
            entropy -= frequency*log(frequency, 2)
            info_per_base[base] = 2 + frequency*log(frequency, 2)
            entropy_per_base[base] = -frequency*log(frequency,2)
    information_per_column = 2-entropy-sample_size_correction
    print("info", info_per_base)
    for base, quantity in info_per_base.items():
        if freq_per_base[base]*information_per_column < 0:
            height_per_base[base] = 0
        else:
            height_per_base[base] = freq_per_base[base]*information_per_column

    return height_per_base, info_per_base

def main():
    # this is just for testing purposes
    print('consensus test')
    parser = argparse.ArgumentParser(
            description='''Improve a multiple sequence alignment''')

    parser.add_argument("--infile", dest='infile', type=str,
                        help='path to input alignment')

    args = parser.parse_args()

    arr, orig_nams = FastaToArray(args.infile)

    consensus, coverage = findConsensus(arr)
    sequence_bar_logo(arr)
    makePlot(consensus, coverage)
    print(consensus)
    print(coverage)



if __name__ == "__main__":
    main()
