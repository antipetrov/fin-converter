# fin-converter

Converter utility

## Installation

Tested on Python 3.7. No installation actually required to use conversion utility. 
To run tests `pytest` is needed, it can be installed with 
```
pip install -r requirements.txt
```


## Usage

To run conversion from bank format to unified transaction format you need to specify `source`, `source-format` and the name of the resulting csv-file (`target-file`).

In the `source`-parameter you can specify a single path or a list of paths. Each path can be a file or a directory. If directory is passed - all the containing files will be processed (but only on the first level). 

Currently 3 types of source file formats are supported :
- bank1
- bank2
- bank3

```
usage: convert.py [-h] --source SOURCE [SOURCE ...] --source-format
                  {bank1,bank2,bank3} [--target-file TARGET_FILE] [--append]
                  [--csv-dialect {excel,excel_tab,unix}]

Convert bank transactions from multi-format csv

optional arguments:
  -h, --help            show this help message and exit
  --source SOURCE [SOURCE ...]
                        list of source-files or dirs containing files with the
                        same format
  --source-format {bank1,bank2,bank3}
                        source file format
  --target-file TARGET_FILE
                        target csv-file where unified records will be stored
  --append              append new records to the existing target-file
  --csv-dialect {excel,excel_tab,unix}
                        csv format for target-file
```

### Examples

```
convert.py --source=data/bank1.csv --source-format=bank1 --target-file=output.csv
convert.py --source=data/bank2 --source-format=bank2 --target-file=output.csv --append
convert.py --source=data/bank31.csv data/bank32.csv --source-format=bank3 --target-file=output.csv --append
```

## Tests
```
pytest tests.py
```


