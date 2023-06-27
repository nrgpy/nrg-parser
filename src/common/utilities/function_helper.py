import os
import uuid
import numpy as np


def remove_files_in_dir(local_dir_path):
    if local_dir_path:
        for path in os.listdir(local_dir_path):
            file_path = local_dir_path + '/' + path

            if os.path.isfile(file_path):
                os.remove(file_path)


def adl_path_join(*args):
    return '/'.join(args)


def local_path_join(*args):
    return '/'.join(args)


def try_float(v):
    if v is None:
        return None
    else:
        try:
            return float(v)
        except Exception:
            return None


def try_int(v):
    if v is None:
        return None
    else:
        try:
            return int(v)
        except Exception:
            return None


def try_string(v):
    if v is None or v == '':
        return None
    else:
        return v


def try_uuid(v):
    try:
        return uuid.UUID(str(v))
    except ValueError:
        return None


def calculate_distance_m(lat1, lon1, lat2, lon2):
    """Returns distance, in kilometers, between one set of longitude/latitude coordinates and another"""
    lon1, lat1, lon2, lat2 = map(np.radians, [lon1, lat1, lon2, lat2])

    newlon = lon2 - lon1
    newlat = lat2 - lat1

    haver_formula = np.sin(newlat / 2.0) ** 2 + np.cos(lat1) * np.cos(lat2) * np.sin(newlon / 2.0) ** 2

    dist = 2 * np.arcsin(np.sqrt(haver_formula))
    m = (6367 * dist) * 1000  # 6367 for distance in m for miles use 3958
    return m