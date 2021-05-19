import argparse
import json
import numpy as np
import tempfile
import tarfile
import urllib.request
import os.path

#import tensorflow as tf
import numpy as np
import pandas as pd

np.random.seed(0)

AA_atoms = 22

def _float(x):
    try:
        return float(x)
    except:
        return 0


def qm9_prepare_records(lines):
    pt = {'C': 6, 'H': 1, 'O': 8, 'N': 7, 'F': 9}
    N = int(lines[0])
    pre_labels = lines[1].split('gdb')
    labels = [float(x) for x in pre_labels[1].split()]
    coords = np.empty((N, 4), dtype=np.float64)
    elements = [pt[x.split()[0]] for x in lines[2:N+2]]
    for i in range(N):
        coords[i] = [_float(x) for x in lines[i + 2].split()[1:]]
    feature = {
        "id": f"gdb_{int(labels[0])}",
        'atom_num': N,
        'labels': labels[1:],
        'elements': json.dumps(elements),
        'coords': json.dumps(coords.flatten().tolist()),
    }
    return feature


def qm9_fetch():
    raw_filepath = "qm9.tar.bz2"


    if not os.path.isfile(raw_filepath):
        print('Downloading qm9 data...', end='')
        urllib.request.urlretrieve(
            'https://ndownloader.figshare.com/files/3195389', raw_filepath)
        print('File downloaded')

    tar = tarfile.open(raw_filepath, 'r:bz2')

    print('')
    features = []
    labels = []
    ids = []
    for i in range(1, 133886):
        if i % 100 == 0:
            print('\r {:.2%}'.format(i / 133886), end='')
        with tar.extractfile(f'dsgdb9nsd_{i:06d}.xyz') as f:
            lines = [l.decode('UTF-8') for l in f.readlines()]
            try:
                res = qm9_prepare_records(lines)
                labels.append(res.pop("labels"))
                ids.append(res["id"])
                features.append(res)
            except ValueError as e:
                print(i)
                raise e
    feat_df = pd.DataFrame.from_records(features, coerce_float=True)

    print(labels)
    labels_df = pd.DataFrame(labels, columns=["A", "B", "C", "mu", "alpha", "homo", "lumo", "gap", "r2", "zpve", "U0", "U", "H", "G", "Cv"])
    labels_df["id"] = ids
    print('')
    return feat_df, labels_df


if __name__=="__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("feature_path")
    parser.add_argument("labels_path")
    args = parser.parse_args()

    feature_path = args.feature_path
    labels_path = args.labels_path
    print(feature_path, labels_path)
    exit

    feat_df, labels_df = qm9_fetch()
    feat_df.to_csv(feature_path, index=False)
    labels_df.to_csv(labels_path, index=False)
