import os
import src.logger.mast.collection_config as collection_config
import src.common.utilities.function_helper as util_func


def remove_files_in_dir(local_dir_path):
    if local_dir_path:
        for path in os.listdir(local_dir_path):
            file_path = local_dir_path + collection_config.DL_PATH_SEP + path

            if os.path.isfile(file_path):
                os.remove(file_path)


def get_timeseries_raw_path(measurement_location_uuid):
    return util_func.adl_path_join(get_timeseries_path(measurement_location_uuid), 'Raw')


def get_timeseries_raw_logger_path(measurement_location_uuid, logger_serial_number):
    return util_func.adl_path_join(get_timeseries_path(measurement_location_uuid),
                                   'Raw logger files',
                                   logger_serial_number)


def get_timeseries_path(measurement_location_uuid):
    return util_func.adl_path_join(collection_config.DL_DEVELOPMENT_MEASUREMENT_LOCATION,
                                   str(measurement_location_uuid).upper(),
                                   'Time series')
