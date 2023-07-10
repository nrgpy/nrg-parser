# nrg-parser Documentation

IEA task 43 parsers for NRG Systems, Inc. SymphoniePRO loggers.

## Installation

Install with pip

`pip install nrg-parser`

## Usage

This package takes the TXT exports of SymphoniePRO data files, and converts the metadata there into IEA Task 43 format.

__NOTE:__ For converting binary SymphoniePRO/Symphonie Classic data files into TXT, see the [nrgpy](https://github.com/nrgpy/nrgpy) repository.

## Example Notebook

### IEA Task43 Metadata Parser

This notebook includes some examples for extracting IEA Task43 metadata from NRG Systems Symphonie-series data logger data files.

See README.md, docs, and the Task43 Github page for more information:

-  [README.md](https://github.com/nrgpy/nrg-parser/blob/main/README.md)
-  [docs](https://github.com/nrgpy/nrg-parser/blob/main/README.md)
-  [Task43 Github](https://github.com/IEA-Task-43/digital_wra_data_standard)



```python
import nrg_parser
```

#### Instantiate the nrg_parser object


```python
metadata = nrg_parser.SymphonieProTxtReader(
    txt_filepath="tests/files/004310_2022-03-17_00.00_000835_meas.txt"
)
```

#### Run the `get_all_metadata` method, or run through the metadata methods individually:

- `get_header`
- `get_site_info`
- `get_iea_logger_main_config`
- `get_iea_sensor_config`


```python
metadata.get_all_metadata()
```

#### IEA metadata objects end in `_dict`

- `header_sections_dict`
- `logger_main_config_dict`
- `sensor_config_dict_list`


```python
metadata.header_sections_dict
```


```python
metadata.logger_main_config_dict
```


```python
metadata.sensor_config_dict_list
```
