from datetime import datetime
import json

import numpy as np
import pandas as pd

from src.parser.mast.utilities.iea_json.iea_models import (
    LoggerMainConfig,
    IEAMain,
    MeasurementLocation,
    MeasurementPoint,
    LoggerMeasurementConfig,
    ColumnName,
    Sensor,
)


def create_iea_json(
    logger_config_dict_list,
    sensor_config_dict_list,
    json_path,
    logger_oem_id,
    project_name="Test Project",
):
    # configuration dataframes
    main_df = pd.DataFrame(logger_config_dict_list)
    main_df["date_from"] = pd.to_datetime(main_df["date_from"])
    main_df["date_to"] = pd.to_datetime(main_df["date_to"])
    main_df.sort_values(["date_from"], ascending=[True], inplace=True)

    sensor_df = pd.DataFrame(sensor_config_dict_list)
    sensor_df["date_from"] = pd.to_datetime(sensor_df["date_from"])
    sensor_df["date_to"] = pd.to_datetime(sensor_df["date_to"])
    sensor_df.sort_values(["date_from"], ascending=[True], inplace=True)

    # set default common settings
    now = datetime.now().isoformat("T")
    notes = "Auto"

    # 01 create iea json
    iea_main = IEAMain()
    iea_main.author = "IEA Json Generator"
    iea_main.organisation = "NRG"
    iea_main.version = "0.1.1-2021.04"
    iea_main.plant_name = project_name
    iea_main.date = datetime.now().strftime("%Y-%m-%d")
    iea_main.measurement_location = []

    # 02 get measurement locations by detecting location change
    meas_loc_dict_list = get_measurement_locations(main_df)
    ctr = 0
    for meas_loc in meas_loc_dict_list:
        ctr += 1

        print(
            f'Detected measurement location {ctr} from {meas_loc["date_from"]} to {meas_loc["date_to"]} ..'
        )

        # 03 get measurement locations logger main config by date configuration, create logger main config list
        meas_loc_lmc_df = main_df[
            (main_df["date_from"] >= meas_loc["date_from"])
            & (main_df["date_to"] <= meas_loc["date_to"])
        ]
        lmc_list = create_logger_main_config(meas_loc_lmc_df, logger_oem_id, notes, now)

        # 04 get measurement locations sensor config by date configuration
        meas_loc_sensor_df = sensor_df[
            (sensor_df["date_from"] >= meas_loc["date_from"])
            & (sensor_df["date_to"] <= meas_loc["date_to"])
        ]
        mp_list = create_measurement_config(meas_loc_sensor_df, notes, now)

        # 05 create measurement location and assign settings accordingly
        measurement_location = MeasurementLocation()
        measurement_location.name = meas_loc["logger_name"]
        measurement_location.latitude_ddeg = meas_loc_lmc_df["latitude_ddeg"].iloc[0]
        measurement_location.longitude_ddeg = meas_loc_lmc_df["longitude_ddeg"].iloc[0]
        measurement_location.measurement_station_type_id = "mast"
        measurement_location.notes = notes
        measurement_location.update_at = now
        measurement_location.logger_main_config = lmc_list
        measurement_location.measurement_point = mp_list
        iea_main.measurement_location.append(measurement_location)

    # create json file
    iea_main_json = json.dumps(iea_main, cls=ComplexEncoder, indent=4)
    json_file = open(json_path + "/iea_task43.json", "w")
    json_file.write(iea_main_json)
    json_file.close()


def get_measurement_locations(df):
    mdf = df.copy()
    mdf = mdf.fillna("")

    # 01 detect location change
    mdf["loc_change_in_m"] = calculate_distance_m(
        mdf.latitude_ddeg,
        mdf.longitude_ddeg,
        mdf.latitude_ddeg.shift(1),
        mdf.longitude_ddeg.shift(1),
    )

    mdf["moved_beyond_12m"] = np.where(
        mdf["loc_change_in_m"] > 12, True, False
    ).cumsum()

    # group by location change every change - get date_from and date_to
    ml_grp = mdf.groupby(
        ["logger_name", "measurement_station_type_id", "moved_beyond_12m"],
        as_index=False,
        sort=False,
    ).agg({"date_from": ["min"], "date_to": ["max"]})

    # drop index (min, max)
    ml_grp = ml_grp.droplevel(1, axis=1)

    return ml_grp.to_dict("records")


def create_logger_main_config(df, logger_oem_id, notes, now):
    if df is None:
        return []  # empty list
    else:
        df = df.fillna("")
        df = df.sort_values(by="date_from")
        # shift data to detect change
        session = (
            (df.logger_id != df.logger_id.shift())
            | (df.logger_name != df.logger_name.shift())
            | (df.offset_from_utc_hrs != df.offset_from_utc_hrs.shift())
            | (df.firmware_version != df.firmware_version.shift())
        ).cumsum()

        # group by every change - get date_from and date_to
        lmc_grp = df.groupby(
            [
                "logger_serial_number",
                "logger_model_name",
                "logger_id",
                "logger_name",
                "offset_from_utc_hrs",
                "firmware_version",
                session,
            ],
            as_index=False,
            sort=False,
        ).agg({"date_from": ["min"], "date_to": ["max"]})

        # drop index (min, max)
        lmc_grp = lmc_grp.droplevel(1, axis=1)

        # convert to iea object
        lmc_list = list(
            map(
                lambda x: LoggerMainConfig(
                    logger_serial_number=x["logger_serial_number"],
                    logger_firmware_version=x["firmware_version"],
                    logger_model_name=x["logger_model_name"],
                    logger_oem_id=logger_oem_id,
                    logger_id=x["logger_id"],
                    logger_name=x["logger_name"],
                    date_from=x["date_from"].isoformat("T"),
                    date_to=x["date_to"].isoformat("T"),
                    offset_from_utc_hrs=x["offset_from_utc_hrs"],
                    notes=notes,
                    update_at=now,
                ),
                lmc_grp.to_dict("records"),
            )
        )

        return lmc_list


def create_measurement_config(df, notes, now):
    if df is None:
        return []  # empty list
    else:
        mp_list = []

        # processed by connection channel
        channel_list = df.connection_channel.unique().tolist()

        for channel_no in channel_list:
            channel_df = df[df["connection_channel"] == channel_no]
            ch_shift_session = (
                (
                    channel_df.measurement_unit_id
                    != channel_df.measurement_unit_id.shift()
                )
                | (channel_df.logger_height != channel_df.logger_height.shift())
                | (channel_df.logger_slope != channel_df.logger_slope.shift())
                | (channel_df.logger_offset != channel_df.logger_offset.shift())
                | (
                    channel_df.boom_orientation_deg
                    != channel_df.boom_orientation_deg.shift()
                )
            ).cumsum()

            ch_grp = channel_df.groupby(
                [
                    "connection_channel",
                    "measurement_unit_id",
                    "logger_height",
                    "logger_slope",
                    "logger_offset",
                    "boom_orientation_deg",
                    "sensor_serial_number",
                    "measurement_type",
                    "column_name_list",
                    "sensor_type",
                    ch_shift_session,
                ],
                as_index=False,
                sort=False,
            ).agg({"date_from": ["min"], "date_to": ["max"]})

            ch_grp = ch_grp.droplevel(1, axis=1)

            mp_list_dict = ch_grp.to_dict("records")

            for x in mp_list_dict:
                # measurement point mapping
                meas_point = MeasurementPoint()
                meas_point.name = (
                    x["measurement_type"]
                    + "_"
                    + str(x["logger_height"])
                    + "_"
                    + str(x["boom_orientation_deg"])
                )
                meas_point.measurement_type_id = x["measurement_type"]
                meas_point.height_m = x["logger_height"]
                meas_point.height_reference_id = "ground_level"
                meas_point.notes = notes
                meas_point.update_at = now

                # logger measurement config mapping
                measurement_config = LoggerMeasurementConfig()
                measurement_config.slope = x["logger_slope"]
                measurement_config.offset = x["logger_offset"]
                measurement_config.measurement_units_id = x["measurement_unit_id"]
                measurement_config.height_m = x["logger_height"]
                measurement_config.serial_number = x["sensor_serial_number"]
                measurement_config.connection_channel = str(x["connection_channel"])
                measurement_config.logger_stated_boom_orientation_deg = x[
                    "boom_orientation_deg"
                ]
                measurement_config.date_from = x["date_from"].isoformat("T")
                measurement_config.date_to = x["date_to"].isoformat("T")
                measurement_config.notes = notes
                measurement_config.update_at = now

                # column name mapping
                column_name_list = []
                column_name_data = x["column_name_list"].split(";")

                if column_name_data is not None:
                    for column in column_name_data:
                        cn = column.split("#")
                        column_name = ColumnName()

                        if cn[0] == "":
                            # print('column name is empty')
                            continue

                        column_name.column_name = cn[0]
                        column_name.statistic_type_id = "avg" if len(cn) < 2 else cn[1]
                        column_name.is_ignored = False
                        column_name.notes = notes
                        column_name.update_at = now
                        column_name_list.append(column_name)

                measurement_config.column_name = column_name_list
                meas_point.logger_measurement_config = [measurement_config]

                # sensor
                sensor = Sensor()
                sensor.serial_number = x["sensor_serial_number"]
                sensor.sensor_type_id = x["sensor_type"]
                sensor.date_from = x["date_from"].isoformat("T")
                sensor.date_to = x["date_to"].isoformat("T")
                sensor.notes = notes
                sensor.update_at = now
                meas_point.sensor = [sensor]

                mp_list.append(meas_point)

        return mp_list


class ComplexEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, IEAMain):
            return obj.__dict__
        if isinstance(obj, MeasurementLocation):
            return obj.__dict__
        if isinstance(obj, LoggerMainConfig):
            return obj.__dict__
        if isinstance(obj, MeasurementPoint):
            return obj.__dict__
        if isinstance(obj, LoggerMeasurementConfig):
            return obj.__dict__
        if isinstance(obj, ColumnName):
            return obj.__dict__
        if isinstance(obj, Sensor):
            return obj.__dict__
        return json.JSONEncoder.default(self, obj)


def calculate_distance_m(lat1, lon1, lat2, lon2):
    """Returns distance, in metere, between one set of longitude/latitude coordinates and another"""
    lon1, lat1, lon2, lat2 = map(np.radians, [lon1, lat1, lon2, lat2])

    newlon = lon2 - lon1
    newlat = lat2 - lat1

    haver_formula = (
        np.sin(newlat / 2.0) ** 2
        + np.cos(lat1) * np.cos(lat2) * np.sin(newlon / 2.0) ** 2
    )

    dist = 2 * np.arcsin(np.sqrt(haver_formula))
    m = (6367 * dist) * 1000  # 6367 for distance in m for miles use 3958

    return m
