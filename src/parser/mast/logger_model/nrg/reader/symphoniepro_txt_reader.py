import logging
import pandas as pd
import src.common.utilities.function_helper as util_func
from src.parser.mast.constants import iea_mapping_config


class SymphonieProSiteInfo:
    """
    Symphonie Text File format header object.
    This class contains site basic information on the data log file.
    """

    site_number = None
    site_description = None
    project = None
    tower = None
    location = None
    coordinate_system = None
    latitude = None
    longitude = None
    elevation = None
    timezone = None
    site_units = None
    logger_date = None
    logger_model = None
    logger_sn = None
    logger_firmware = None
    ipack_model = None
    ipack_sn = None
    ipack_firmware = None


class SymphonieProTxtReader:
    """
    Symphonie Text File Reader
    This class takes Symphonie Desktop Pro rld -> txt converted file.
    """

    def __init__(self, txt_filepath):
        """
        Initializes SymphonieProTxt by reading/parsing its file content,
        both headers and timeseries data.

        Args:
            txt_filepath: symphonie pro txt data file path
        """
        # initialize
        self.header_sections_dict = {}
        self.sensor_history_list = []
        self.header_line_ctr = 0
        self.timeseries_data = pd.DataFrame()
        self.first_timestamp = None
        self.last_timestamp = None

        # do parameter check here, if file exist, file not empty

        try:
            # read headers start
            line_ctr = 0

            with open(txt_filepath, "rt") as file_data:
                for line in file_data:
                    line_ctr += 1
                    line = line.strip()

                    if line == "Data":
                        break
                    if line == "Sensor History":
                        continue

                    # initialize section settings:
                    section_name = line
                    section = {}

                    # sensor history -- channel definition
                    if line.startswith("Channel:"):
                        split_arr = line.split(":", 1)
                        section[split_arr[0].strip()] = split_arr[1].strip()
                        section_name = "Ch_" + split_arr[1].strip()

                    # header section loop
                    for line in file_data:
                        line_ctr += 1
                        str_line = line.strip()
                        if (
                            str_line == "Data"
                        ):  # means timeseries section, break from section loop
                            break
                        elif (
                            str_line == ""
                        ):  # if empty, it means new section break from section loop
                            break
                        elif str_line.find(":") != -1:  # normal header data
                            split_arr = str_line.split(":", 1)
                            section[split_arr[0].strip()] = util_func.try_string(
                                split_arr[1].strip()
                            )

                    if section_name.startswith("Ch_"):
                        self.sensor_history_list.append(section)
                    else:
                        self.header_sections_dict[section_name] = section

            self.header_line_ctr = line_ctr

            # read headers end

            # read timeseries data
            try:
                self.timeseries_data = pd.read_csv(
                    txt_filepath,
                    skiprows=self.header_line_ctr,
                    sep="\t",
                    encoding="utf-8",
                )
            except:
                pass  # file has no data

            # get first and last timestamp if timeseries data is available
            if len(self.timeseries_data) > 0:
                self.timeseries_data["Timestamp"] = pd.to_datetime(
                    self.timeseries_data["Timestamp"], errors="coerce"
                )
                self.first_timestamp = self.timeseries_data["Timestamp"].min()
                self.last_timestamp = self.timeseries_data["Timestamp"].max()

        except Exception as e:
            # handle any possible exception
            logging.error(f"Failed to load file {txt_filepath} error: str{e}")

    def get_header(self, header_section_name=None, header=None):
        """
        Helper method that returns symphonie pro txt file in dictionary format if
        header is not given, else return header value.

        Args:
            header_section_name: section headers name in symphonie pro txt file
            header: headers name in symphonie pro txt file
        """

        if header_section_name is None:
            return self.header_sections_dict  # return all headers in dict

        if header_section_name in self.header_sections_dict:
            section = self.header_sections_dict[header_section_name]
            if header is not None:
                if header in section:
                    return section[header]
                else:
                    logging.debug(f"{header} header does not exists.")
                    return None
            else:
                return section

        else:
            logging.debug(f"{header_section_name} section does not exists")
            return None

        return self.header_sections_dict

    def get_site_info(self):
        """
        Helper method that returns SymphonieProSiteInfo
        SymphoniePRO basic site information from the headers

        Returns:
            site_info - Symphonie Pro site information
        """
        site_info = SymphonieProSiteInfo()

        # Export Parameters
        exp_params = "Export Parameters"
        site_info.site_number = self.get_header(
            header_section_name=exp_params, header="Site Number"
        )

        # site properties
        site_properties = "Site Properties"
        site_info.site_description = self.get_header(
            header_section_name=site_properties, header="Site Description"
        )
        site_info.project = self.get_header(
            header_section_name=site_properties, header="Project"
        )
        site_info.tower = self.get_header(
            header_section_name=site_properties, header="Tower"
        )
        site_info.location = self.get_header(
            header_section_name=site_properties, header="Location"
        )
        site_info.coordinate_system = self.get_header(
            header_section_name=site_properties, header="Coordinate System"
        )
        site_info.latitude = util_func.try_float(
            self.get_header(header_section_name=site_properties, header="Latitude")
        )
        site_info.longitude = util_func.try_float(
            self.get_header(header_section_name=site_properties, header="Longitude")
        )
        site_info.elevation = util_func.try_int(
            self.get_header(header_section_name=site_properties, header="Elevation")
        )
        site_info.timezone = self.get_header(
            header_section_name=site_properties, header="Time Zone"
        )
        site_info.site_units = self.get_header(
            header_section_name=site_properties, header="Site Units"
        )

        # logger history
        logger_history = "Logger History"
        site_info.logger_date = self.get_header(
            header_section_name=logger_history, header="Date"
        )
        site_info.logger_model = self.get_header(
            header_section_name=logger_history, header="Model"
        )
        site_info.logger_sn = self.get_header(
            header_section_name=logger_history, header="Serial Number"
        )
        site_info.logger_firmware = self.get_header(
            header_section_name=logger_history, header="Firmware"
        )

        # iPack History
        ipack_history = "iPack History"
        site_info.ipack_model = self.get_header(
            header_section_name=ipack_history, header="Model"
        )
        site_info.ipack_sn = self.get_header(
            header_section_name=ipack_history, header="Serial Number"
        )
        site_info.ipack_firmware = self.get_header(
            header_section_name=ipack_history, header="Firmware"
        )

        return site_info

    def get_iea_logger_main_config(self):
        """
        Helper method that returns the logger main configuration in IEATask43 format
        Returns:
            logger_main_config_dict: logger main configuration in dictionary format
        """

        logger_main_config_dict = {}

        # header sections
        logger_history = "Logger History"
        exp_params = "Export Parameters"
        site_properties = "Site Properties"

        logger_main_config_dict["logger_serial_number"] = self.get_header(
            header_section_name=logger_history, header="Serial Number"
        )
        logger_main_config_dict["logger_model_name"] = self.get_header(
            header_section_name=logger_history, header="Model"
        )
        logger_main_config_dict["logger_id"] = self.get_header(
            header_section_name=exp_params, header="Site Number"
        )
        logger_main_config_dict["logger_name"] = self.get_header(
            header_section_name=site_properties, header="Project"
        )

        logger_main_config_dict["date_from"] = self.first_timestamp
        logger_main_config_dict["date_to"] = self.last_timestamp

        logger_main_config_dict["latitude_ddeg"] = util_func.try_float(
            self.get_header(header_section_name=site_properties, header="Latitude")
        )
        logger_main_config_dict["longitude_ddeg"] = util_func.try_float(
            self.get_header(header_section_name=site_properties, header="Longitude")
        )
        logger_main_config_dict["measurement_station_type_id"] = "mast"
        logger_main_config_dict["offset_from_utc_hrs"] = util_func.try_float(
            self.get_header(header_section_name=site_properties, header="Time Zone")
            .replace("UTC", "")
            .replace(":", ".")
        )
        logger_main_config_dict["firmware_version"] = self.get_header(
            header_section_name=logger_history, header="Firmware"
        )

        return logger_main_config_dict

    def get_iea_sensor_config(self):
        """
        Helper method that returns the measurement point and sensor configuration in IEATask43 format
        Returns:
            sensor_config_dict_list: list of measurement points and sensor configurations (dict)
        """
        sensor_config_dict_list = []
        column_headers = list(self.timeseries_data.columns.values)

        # mast sensor configuration
        for ch_info in self.sensor_history_list:
            sensor_config_dict = {
                "connection_channel": util_func.try_int(ch_info["Channel"]),
                "sensor_serial_number": ch_info["Serial Number"],
            }

            if ch_info["Units"] is not None:
                if ch_info["Units"].lower() in iea_mapping_config.IEA_UNIT_DICT:
                    # map unit to iea task43
                    sensor_config_dict[
                        "measurement_unit_id"
                    ] = iea_mapping_config.IEA_UNIT_DICT[ch_info["Units"].lower()]
                else:
                    sensor_config_dict["measurement_unit_id"] = "-"
            else:
                sensor_config_dict["measurement_unit_id"] = None

            sensor_config_dict["logger_height"] = util_func.try_float(ch_info["Height"])
            sensor_config_dict["logger_slope"] = util_func.try_float(
                ch_info["Scale Factor"]
            )
            sensor_config_dict["logger_offset"] = util_func.try_float(ch_info["Offset"])
            sensor_config_dict["boom_orientation_deg"] = util_func.try_float(
                ch_info["Bearing"]
            )
            sensor_config_dict["boom_orientation_deg"] = util_func.try_float(
                ch_info["Bearing"]
            )
            if ch_info["Type"] == "Vane":
                sensor_config_dict[
                    "vane_dead_band_orientation_deg"
                ] = util_func.try_float(ch_info["Vane Mounting Angle"])

            match sensor_config_dict["measurement_unit_id"]:
                case "m/s":
                    sensor_config_dict["measurement_type"] = "wind_speed"
                    sensor_config_dict["sensor_type"] = "anemometer"
                case "deg":
                    sensor_config_dict["measurement_type"] = "wind_direction"
                    sensor_config_dict["sensor_type"] = "wind_vane"
                case "deg_C":
                    sensor_config_dict["measurement_type"] = "air_temperature"
                    sensor_config_dict["sensor_type"] = "thermometer"
                case "deg_F":
                    sensor_config_dict["measurement_type"] = "air_temperature"
                    sensor_config_dict["sensor_type"] = "thermometer"
                case "K":
                    sensor_config_dict["measurement_type"] = "air_temperature"
                    sensor_config_dict["sensor_type"] = "thermometer"
                case "%":
                    sensor_config_dict["measurement_type"] = "relative_humidity"
                    sensor_config_dict["sensor_type"] = "hygrometer"
                case "mbar":
                    sensor_config_dict["measurement_type"] = "air_pressure"
                    sensor_config_dict["sensor_type"] = "barometer"
                case "hPa":
                    sensor_config_dict["measurement_type"] = "air_pressure"
                    sensor_config_dict["sensor_type"] = "barometer"
                case "atm":
                    sensor_config_dict["measurement_type"] = "air_pressure"
                    sensor_config_dict["sensor_type"] = "barometer"
                case "mmHg":
                    sensor_config_dict["measurement_type"] = "air_pressure"
                    sensor_config_dict["sensor_type"] = "barometer"
                case "inHg":
                    sensor_config_dict["measurement_type"] = "air_pressure"
                    sensor_config_dict["sensor_type"] = "barometer"
                case "kg/m^2":
                    sensor_config_dict["measurement_type"] = "air_pressure"
                    sensor_config_dict["sensor_type"] = "barometer"
                case "kg/m^3":
                    sensor_config_dict["measurement_type"] = "air_density"
                    sensor_config_dict["sensor_type"] = "thermometer"
                case "V":
                    sensor_config_dict["measurement_type"] = "voltage"
                    sensor_config_dict["sensor_type"] = "voltmeter"
                case "mA":
                    sensor_config_dict["measurement_type"] = "current"
                    sensor_config_dict["sensor_type"] = "ammeter"
                case "A":
                    sensor_config_dict["measurement_type"] = "current"
                    sensor_config_dict["sensor_type"] = "ammeter"
                case "ohm":
                    sensor_config_dict["measurement_type"] = "resistance"
                    sensor_config_dict["sensor_type"] = "ice_detection_sensor"
                case "mm":
                    sensor_config_dict["measurement_type"] = "precipitation"
                    sensor_config_dict["sensor_type"] = "rain_gauge"
                case "W/m^2":
                    sensor_config_dict[
                        "measurement_type"
                    ] = "global_horizontal_irradiance"
                    sensor_config_dict["sensor_type"] = "pyranometer"
                case _:
                    sensor_config_dict["sensor_type"] = "other"
                    sensor_config_dict["measurement_type"] = "other"

            sensor_config_dict["date_from"] = self.first_timestamp
            sensor_config_dict["date_to"] = self.last_timestamp

            column_name_list = []
            ch_header = [
                columns
                for columns in column_headers
                if columns.startswith("Ch" + ch_info["Channel"] + "_")
            ]

            for column in ch_header:
                # parse statistic type
                chunks = column.split("_")
                statistic_type = chunks[len(chunks) - 2].lower()

                if statistic_type == "gustdir":
                    statistic_type = "gust"

                if statistic_type in iea_mapping_config.IEA_STATISTIC_TYPE:
                    statistic_type = statistic_type
                else:
                    statistic_type = "avg"

                column_name = column + "#" + statistic_type
                column_name_list.append(column_name)

            sensor_config_dict["column_name_list"] = ";".join(column_name_list)
            sensor_config_dict_list.append(sensor_config_dict)

        return sensor_config_dict_list
