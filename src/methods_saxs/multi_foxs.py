# prepare_data()
# make_experiment()
# collect_result()
import logging
import pathlib
import re
import shutil
import subprocess
import sys
from os import listdir


def prepare_data(all_files, tmpdir, method, verbose_logfile):
    for file in all_files:  # not strict format for pdbs file
        shutil.copy(file, f'{tmpdir}/pdbs/')


def make_experiment(all_files, tmpdir, verbose, verbose_logfile, method):
    # RUN Multi_foxs
    files_for_multifoxs = [str(tmpdir + '/pdbs/' + file) for file in all_files]
    if verbose_logfile:
        logpipe = LogPipe(logging.DEBUG)
        logpipe_err = LogPipe(logging.DEBUG)
        call = subprocess.run(['multi_foxs', f'{tmpdir}/method/curve.modified.dat',
                               *files_for_multifoxs], cwd=f'{tmpdir}/results/',
                              stdout=logpipe, stderr=logpipe_err)
        logpipe.close()
        logpipe_err.close()
    else:
        call = subprocess.run(['multi_foxs', f'{tmpdir}/method/curve.modified.dat',
                               *files_for_multifoxs], cwd=f'{tmpdir}/results/',
                              stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    if call.returncode:  # multifoxs don't get right returnvalue
        print(f'ERROR: multifoxs failed', file=sys.stderr)
        logging.error(f'Multifoxs failed.')
        sys.exit(1)

        # Process with result from Multi_foxs


def collect_results(tmpdir):
    multifoxs_files = []
    files = listdir(f'{tmpdir}/results/')
    for line in files:
        line = line.rstrip()
        if re.search('\d.txt$', line):
            multifoxs_files.append(line)
    result = []
    chi2 = 0
    for filename in multifoxs_files:
        with open(tmpdir + '/results/' + filename) as file:
            weight_structure = []
            for line in file:
                # 1 |  3.05 | x1 3.05 (0.99, 0.20)
                #    0   | 1.000 (1.000, 1.000) | /tmp/tmpnz7dbids/pdbs/mod13.pdb  (0.062)
                if not line.startswith(' '):
                    if weight_structure:
                        result.append((chi2, weight_structure))
                    chi2 = float(line.split('|')[1])
                    weight_structure = []

                else:
                    weight = float(line[line.index('|') + 1:line.index('(')])
                    structure = line.split('pdbs/')[1].split('(')[0].strip()
                    weight_structure.append((structure, weight))
            result.append((chi2, weight_structure))
    # ((chi2, [('mod10.pdb', 0.3), ('mod15.pdb', 0.7)]),(chi2, [(strucutre, weight),(strucutre, weight),...)])
    return result
