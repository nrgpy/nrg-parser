import time
import logging
import os
import sys
import concurrent
import nrgpy
from concurrent.futures.thread import ThreadPoolExecutor

import src.common.utilities.function_helper as util_func
import src.logger.mast.utilities.iea_json.nrg_config as nrg_config
from src.logger.mast.logger_model.nrg.reader.symphoniepro_txt_reader import SymphonieProTxtReader
from src.logger.mast.utilities.iea_json.convert_to_iea_json import create_iea_json


def main():
    """ Creates IEA-task43 json from NRG Symphonie Pro logger data files
        SymPRO Desktop PRO must be installed. Please specify installation location in nrg_config.py
        Args:
            project_name(str): ex: Morgan-County
            local_path(str): local path directory where logger data files(.rld) are located

        Output: iea_task43.json file under local path
    """

    logging.info('IN execute - NRG Systems')
    project_name = sys.argv[1]
    local_path = sys.argv[2]

    # check if path exists

    if not os.path.isdir(local_path):
        logging.error(f'Local path {local_path} does not exists. Please confirm rld path directory.')
        return

    local_path_dir_converted = os.path.join(local_path, 'converted')

    # converted folder doesn't exist, create
    if not os.path.isdir(local_path_dir_converted):
        os.mkdir(local_path_dir_converted)
    else:
        util_func.remove_files_in_dir(local_path_dir_converted)

    process_start = time.perf_counter()

    # convert rld binary - txt conversion
    convert_start = time.perf_counter()

    # get symphonie pro desktop app locations
    if nrg_config.SYMPHONIE_APP is not None:
        symphro_path = nrg_config.SYMPHONIE_APP
    else:
        symphro_path = "C:/Program Files (x86)/Renewable NRG Systems/SymPRO Desktop/SymPRODesktop.exe"

    # # convert .rld file to txt
    converter = nrgpy.local_rld(rld_dir=local_path, out_dir=local_path_dir_converted, sympro_path=symphro_path)
    converter.convert()

    convert_end = time.perf_counter()
    logging.warning(f'PERF: Conversion {round(convert_end - convert_start, 2)} second(s)')

    # read and parse
    logger_config_dict_list, sensor_config_dict_list = read_and_parse(local_path_dir_converted)
    if len(logger_config_dict_list) > 0 and len(sensor_config_dict_list) > 0:
        create_iea_json(logger_config_dict_list, sensor_config_dict_list, local_path, 'NRG SymphoniePro', project_name)

    # remove all converted files after the run
    util_func.remove_files_in_dir(local_path_dir_converted)

    process_end = time.perf_counter()
    logging.warning(f'PERF: PROCESS EXEC OVERALL: {round(process_end - process_start, 2)} second(s)')
    logging.info(f'Please find the output file in {local_path}/iea_task43.json')
    logging.info('OUT execute - NRG Systems')


def read_and_parse(local_path):
    # initialize data
    logger_config_dict_list = []
    sensor_config_dict_list = []

    files = os.listdir(local_path)
    # Filtering only txt files.
    filename_list = [f for f in files if os.path.isfile(local_path + '/' + f) and f.endswith('.txt')]

    # use a with statement to ensure threads are cleaned up promptly
    with concurrent.futures.ThreadPoolExecutor(max_workers=100) as executor:
        # Start the load operations and mark each future with its filename
        future_to_file = {executor.submit(read, local_path, filename): filename for
                          filename in
                          filename_list}

        for future in concurrent.futures.as_completed(future_to_file):
            filename = future_to_file[future]
            try:
                data = future.result()
            except Exception as exc:
                print('%r generated an exception: %s' % (filename, exc))
            else:
                if data is not None and len(data.timeseries_data) > 0:
                    lmc_list = data.get_iea_logger_main_config()
                    if lmc_list is not None:
                        logger_config_dict_list.append(lmc_list)
                        sensor_config_dict_list.extend(data.get_iea_sensor_config())
                #     else:
                #         print(f'invalid file: {filename}')
                else:
                     print(f'Data file has empty dataset: {filename}. Skip!')

    return logger_config_dict_list, sensor_config_dict_list


def read(local_path, filename):
    txt_filepath = os.path.join(local_path, filename)
    parsed_data = SymphonieProTxtReader(txt_filepath)
    return parsed_data


if __name__ == '__main__':
    main()
