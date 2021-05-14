import csv
from typing import TextIO
from collections import namedtuple

UnifiedTransactionRecord = namedtuple("UnifiedTransactionRecord",
                                      ["source", "timestamp", "type", "amount", "transfer_from", "transfer_to"])


class UnifiedTransactionStorage:
    """
    Stores UnifiedTransactionRecords and does the csv-saving.
    Can be easily extended to load previously saved files and then perform operations on the overall data like sorting.

    UnifiedTransactionRecord contains also source - the initial source-file - might be useful to combine
    data from different sources in append mode.
    """

    def __init__(self):
        self.records = []

    def add(self, record):
        self.records.append(record)

    def clear(self):
        self.records = []

    def get(self, index: int) -> UnifiedTransactionRecord:
        return self.records[index]

    def export_to_csv(self, target_file: TextIO, write_header: bool = True, dialect: str = csv.unix_dialect) -> int:
        """
        Dumps UnifiedTransactionRecords from storage to csv-file

        :param target_file: file or anything with .write()
        :param write_header: add first row of headers
        :return: number of records exported
        """

        if not self.records:
            return 0

        writer = csv.writer(target_file, dialect=dialect)

        # header
        if write_header:
            writer.writerow(self.records[0]._fields)

        # data
        export_count = 0
        for rec in self.records:
            rec_export = self.export_record(rec)
            writer.writerow(rec_export)
            export_count += 1

        return export_count

    @staticmethod
    def export_record(record: UnifiedTransactionRecord) -> tuple:
        """
        Performs pre-export formatting for each record in storage. Order of fields is preserved.
        A place to change something about the date-format or any pother field format in the export file.

        :param record: unified-record
        :return: tuple of formatted fields
        """
        data_dict = record._asdict()
        data_dict['timestamp'] = data_dict['timestamp'].date().isoformat()
        data_dict['amount'] = "{:.2f}".format(data_dict['amount'])
        return tuple(UnifiedTransactionRecord(**data_dict))



