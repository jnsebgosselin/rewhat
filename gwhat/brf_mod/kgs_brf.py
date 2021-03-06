# -*- coding: utf-8 -*-

# Copyright © 2014-2018 GWHAT Project Contributors
# https://github.com/jnsebgosselin/gwhat
#
# This file is part of GWHAT (Ground-Water Hydrograph Analysis Toolbox).
# Licensed under the terms of the GNU General Public License.

# ---- Standard library imports
import os
import os.path as osp
import csv

# ---- Third party imports
import pandas as pd
import numpy as np
from xlrd import xldate_as_tuple

# ---- Local imports
from gwhat.brf_mod import __install_dir__


def produce_BRFInputtxt(well, time, wl, bp, et):

    comment = 'No comment men'
    wlu = 'feet'
    bpu = 'feet'
    etu = 'NONE'
    sampleinterval = time[1]-time[0]
    timeunits = 'days'
    N = len(time)

    yr, mth, day, hr, mn, sec = xldate_as_tuple(time[0], 0)
    dst = '%02d/%02d/%d, %02d:%02d:%02d' % (yr, mth, day, hr, mn, sec)

    yr, mth, day, hr, mn, sec = xldate_as_tuple(time[-1], 0)
    det = '%02d/%02d/%d, %02d:%02d:%02d' % (yr, mth, day, hr, mn, sec)

    fcontent = []
    fcontent.append(['Comment: %s' % comment])
    fcontent.append(['Well: %s' % well])
    fcontent.append(['WL Units: %s' % wlu])
    fcontent.append(['BP Units: %s' % bpu])
    fcontent.append(['ET Units: %s' % etu])

    fcontent.append(['Sample Interval: %f' % sampleinterval])
    fcontent.append(['Time Units: %s' % timeunits])
    fcontent.append(['Data Start Time: %s' % dst])
    fcontent.append(['Data End Time: %s' % det])

    fcontent.append(['Number of Data: %d' % N])
    fcontent.append(['Time WL BP ET'])

    # Add the data to the file content.
    wl = (np.max(wl) - wl) * 3.28084
    bp = bp * 3.28084
    fcontent.extend([[time[i], wl[i], bp[i], et[i]] for i in range(N)])

    filename = os.path.join(__install_dir__, 'BRFInput.txt')
    with open(filename, 'w', encoding='utf8') as f:
        writer = writer = csv.writer(f, delimiter='\t', lineterminator='\n')
        writer.writerows(fcontent)


def produce_par_file(lagBP, lagET, detrend_waterlevels=True,
                     correct_waterlevels=True):
    """
    Create the parameter file requires by the KGS_BRF program.
    """
    brfinput = os.path.join(__install_dir__, 'BRFInput.txt')
    brfoutput = os.path.join(__install_dir__, 'BRFOutput.txt')
    wlcinput = os.path.join(__install_dir__, 'WLCInput.txt')
    wlcoutput = os.path.join(__install_dir__, 'WLCOutput.txt')

    detrend = 'Yes' if detrend_waterlevels else 'No'
    correct = 'No'

    par = []
    par.append(['BRF Option (C[ompute] or R[ead]): Compute'])
    par.append(['BRF Input Data File: %s' % brfinput])
    par.append(['Number of BP Lags:  %d' % lagBP])
    par.append(['Number of BP ET:  %d' % lagET])
    par.append(['BRF Output Data File: %s' % brfoutput])
    par.append(['Detrend data? (Y[es] or N[o]): %s' % detrend])
    par.append(['Correct WL? (Y[es] or N[o]): %s' % correct])
    par.append(['WLC Input Data File: %s' % wlcinput])
    par.append(['WLC Output Data File: %s' % wlcoutput])

    filename = os.path.join(__install_dir__, 'kgs_brf.par')
    with open(filename, 'w', encoding='utf8') as f:
        writer = csv.writer(f, delimiter='\t',  lineterminator='\n')
        writer.writerows(par)


def run_kgsbrf():
    exename = os.path.join(__install_dir__, 'kgs_brf.exe')
    parname = os.path.join(__install_dir__, 'kgs_brf.par')
    if os.path.exists(exename) and os.path.exists(parname):
        if os.name == 'nt':
            os.system('""%s" < "%s""' % (exename, parname))


def read_brf_output(filename=None):
    """
    Read the barometric response function from the output file produced
    by kgs_brf.exe.
    """
    if filename is None:
        filename = osp.join(__install_dir__, 'BRFOutput.txt')

    with open(filename, 'r') as f:
        reader = list(csv.reader(f))

    for i, row in enumerate(reader):
        if 'LagNo Lag A sdA SumA sdSumA B sdB SumB sdSumB' in row[0]:
            columns = row[0].split()
            break

    data = []
    count = 1
    for row in reader[i+1:]:
        if count == 1:
            data.append([float(i) for i in row[0].split()])
            count += 1
        elif count in [2, 3]:
            data[-1].extend([float(i) for i in row[0].split()])
            count += 1
        elif count == 4:
            data[-1].extend([float(i) for i in row[0].split()])
            count = 1

    # Cast the data into a pandas dataframe.
    dataf = pd.DataFrame(data, columns=columns)
    dataf['LagNo'] = dataf['LagNo'].astype(int)
    dataf.set_index(['LagNo'], drop=True, inplace=True)
    dataf[(dataf <= -999.999) & (dataf >= -999.9999)] = np.nan

    return dataf


if __name__ == "__main__":
#    plt.close('all')
    # produce_par_file()
    run_kgsbrf()
    load_BRFOutput(show_ebar=True, msize=5, draw_line=False)
#    plt.show()
