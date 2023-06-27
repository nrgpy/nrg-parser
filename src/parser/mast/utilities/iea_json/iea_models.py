class IEAMain:
    author = None
    organisation = None
    date = None
    version = None
    plant_name = None
    plant_type = None
    measurement_location = None


class MeasurementLocation:
    name = None
    latitude_ddeg = None
    longitude_ddeg = None
    measurement_station_type_id = 'mast'
    notes = None
    update_at = None
    logger_main_config = None
    measurement_point = None


class LoggerMainConfig:
    logger_serial_number = None
    logger_firmware_version = None
    logger_model_name = None
    logger_id = None
    logger_oem_id = None
    logger_name = None
    date_from = None
    date_to = None
    encryption_pin_or_key = None
    enclosure_lock_details = None
    data_transfer_details = None
    offset_from_utc_hrs = None
    sampling_rate_sec = None
    averaging_period_minutes = None
    timestamp_is_end_of_period = None
    clock_is_auto_synced = None
    logger_acquisition_uncertainty = None
    notes = None
    update_at = None

    def __init__(self,
                 logger_serial_number,
                 logger_firmware_version,
                 logger_model_name,
                 logger_oem_id,
                 logger_id,
                 logger_name,
                 date_from,
                 date_to,
                 offset_from_utc_hrs,
                 notes,
                 update_at
                 ):
        self.logger_serial_number = logger_serial_number
        self.logger_firmware_version = logger_firmware_version
        self.logger_model_name = logger_model_name
        self.logger_oem_id = logger_oem_id
        self.logger_id = logger_id
        self.logger_name = logger_name
        self.date_from = date_from
        self.date_to = date_to
        self.offset_from_utc_hrs = offset_from_utc_hrs
        self.notes = notes
        self.update_at = update_at


class MeasurementPoint:
    name = None
    measurement_type_id = None
    height_m = None
    height_reference_id = None
    logger_measurement_config = None
    sensor = None
    notes = None
    update_at = None


class LoggerMeasurementConfig:
    slope = None
    offset = None
    sensitivity = None
    measurement_units_id = None
    height_m = None
    serial_number = None
    connection_channel = None
    logger_stated_boom_orientation_deg = None
    date_from = None
    date_to = None
    column_name = None
    notes = None
    update_at = None


class ColumnName:
    column_name = None
    statistic_type_id = None
    is_ignored = None
    notes = None
    update_at = None


class Sensor:
    oem = None
    model = None
    serial_number = None
    sensor_type_id = None
    classification = None
    instrument_poi_height_mm = None
    is_heated = None
    sensor_body_size_mm = None
    date_from = None
    date_to = None
    update_at = None
    notes = None


class MountingArrangement:
    mast_section_geometry_uuid = None
    mounting_type_id = None
    boom_orientation_deg = None
    vane_dead_band_orientation_deg = None
    orientation_reference_id = None
    tilt_angle_deg = None
    boom_oem = None
    boom_model = None
    upstand_height_mm = None
    upstand_diameter_mm = None
    boom_diameter_mm = None
    boom_length_mm = None
    distance_from_mast_to_sensor_mm = None
    date_from = None
    date_to = None
    update_at = None
    notes = None
