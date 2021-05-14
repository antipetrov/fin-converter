import os.path
import sys
import argparse
import csv
from typing import TextIO, Iterable

from convert_lib.processors import InputConverterBank1, InputConverterBank2, InputConverterBank3
from convert_lib.storage import UnifiedTransactionStorage


def actual_source_files(path_list):
    """
    Walks through list of strings which (hopefully) represent files or directories
    returns file if string represents file
    or all files from directory (1-st level), if string represents directory

    :param path_list: list of paths
    :return: file
    """

    for path in path_list:
        if os.path.isdir(path):
            for root, dirs, files in os.walk(path, topdown=False):
                for file in files:
                    yield os.path.join(root, file)
        elif os.path.isfile(path) or os.path.islink(path):
            yield path


def csv_reader(csvfile: TextIO) -> Iterable:
    """
    Small wrapper-generator over file to feed rows from file into the converter

    :param csvfile: cvs-file
    :return:
    """
    reader = csv.reader(csvfile)
    for row in reader:
        yield row


def convert_csv(source_filename: str, format_name: str, output_filename: str, append_mode: bool = False,
                target_dialect: str = 'unix') -> tuple:
    """
    Main conversion function. Chooses the right converter for the specified format-name,
    processes input data and fills unified-record-storage and writes unified data into csv-file.

    :param source_filename: source filename
    :param format_name: explicit name of the data format pattern
    :param output_filename: filename for unified records
    :param append_mode: append data to output file or rewrite output file each time
    :return: tuple (loaded records count, processed records count)
    """

    # choose appropriate processor
    if format_name == 'bank1':
        processor_class = InputConverterBank1
    elif format_name == 'bank2':
        processor_class = InputConverterBank2
    elif format_name == 'bank3':
        processor_class = InputConverterBank3
    else:
        raise ValueError('Unknown format {}'.format(format_name))

    # initialize unified storage
    storage_unified = UnifiedTransactionStorage()
    storage_unified.clear()

    processor = processor_class(storage=storage_unified, source=source_filename)

    # convert rows and store them
    try:
        with open(source_filename, 'r') as source_file:
            load_count = processor.process_rows(csv_reader(source_file))
    except OSError as ex:
        raise ValueError('Unable to open {} for reading: {}'.format(source_filename, ex))

    # export unified data to target-file
    # TODO: need better logic about headers here - first append-mode write will generate headerless file
    try:
        with open(output_filename, 'a' if append_mode else 'w') as output_file:
            export_count = storage_unified.export_to_csv(output_file, write_header=not append_mode,
                                                         dialect=target_dialect)
    except OSError as ex:
        raise ValueError('Unable to open {} for writing: {}'.format(output_filename, ex))

    return load_count, export_count


if __name__ == '__main__':

    # arguments parsing
    arg_parser = argparse.ArgumentParser(description='Convert bank transactions from multi-format csv')
    arg_parser.add_argument('--source', nargs='+', type=str,
                            help='list of source-files or dirs containing files with the same format', required=True)
    arg_parser.add_argument('--source-format', type=str, action='store', choices=('bank1', 'bank2', 'bank3'),
                            help='source file format', required=True)
    arg_parser.add_argument('--target-file', type=str, action='store',
                            help='target csv-file where unified records will be stored', default='output.csv')
    arg_parser.add_argument('--append', action='store_true',
                            help='append new records to the existing target-file')
    arg_parser.add_argument('--csv-dialect', action='store', type=str, choices=('excel', 'excel_tab', 'unix'),
                            required=False, default='unix', help='csv format for target-file')

    args = arg_parser.parse_args()

    # retrieve actual list of source files
    source_files = actual_source_files(args.source)

    # where the job is done
    for file in source_files:
        try:
            load_count, export_count = convert_csv(
                file,
                args.source_format,
                args.target_file,
                args.append,
                args.csv_dialect
            )

        except Exception as ex:
            sys.stderr.write("Error converting file {} (format: {}): {}\n".format(file, args.source_format, ex))
            continue
        sys.stdout.write("Processing completed for file {}. Records processed: {}\n".format(file, export_count))
