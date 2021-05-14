
from datetime import datetime
from decimal import Decimal, getcontext
from typing import List, Iterable
from convert_lib.storage import UnifiedTransactionRecord

getcontext().prec = 2



class InputConverterError(Exception):
    pass


class InputConverter:
    skip_first_row = True

    def __init__(self, storage, source, skip_first_row=None):
        self.storage = storage
        self.source = source
        if not skip_first_row is None:
            self.skip_first_row = skip_first_row

    def process_rows(self, row_source: Iterable) -> int:
        """
        Converts rows from row-source (e.g. csv file) to unified format and adds processed data to storage

        :param row_source: Iterable source of input rows. Can be tuples from csv.reader
        :return: number of records parsed
        """

        row_count = 0
        for row in row_source:
            row_count += 1
            if row_count == 1 and self.skip_first_row:
                continue

            try:
                new_record = self.parse_row(row)
            except Exception as ex:
                raise InputConverterError("Parser error in row {}: {}".format(row_count, ex))

            self.storage.add(new_record)

        return row_count

    def parse_row(self, row: List) -> UnifiedTransactionRecord:
        """
        Parses single input row from into unified record.
        Needs to be implemented in subclasses

        :param row: list\tuple array of strings
        :return: UnifiedTransactionRecord
        """

        raise NotImplementedError('')


class InputConverterBank1(InputConverter):
    """
    Converts records with bank1 format

    timestamp,type,amount,from,to
    Oct 1 2019,remove,99.20,198,182
    """
    def parse_row(self, row: List) -> UnifiedTransactionRecord:

        record = UnifiedTransactionRecord(
            source=self.source,
            timestamp=datetime.strptime(row[0], "%b %d %Y"),
            type=row[1],
            amount=Decimal(row[2]),
            transfer_from=row[3],
            transfer_to=row[4],
        )

        return record


class InputConverterBank2(InputConverter):
    """
    Converts records with bank1 format

    date,transaction,amounts,to,from
    03-10-2019,remove,99.40,182,198
    """

    def parse_row(self, row: List) -> UnifiedTransactionRecord:
        record = UnifiedTransactionRecord(
            source=self.source,
            timestamp=datetime.strptime(row[0], "%d-%m-%Y"),
            type=row[1],
            amount=Decimal(row[2]),
            transfer_from=row[4],
            transfer_to=row[3],
        )

        return record


class InputConverterBank3(InputConverter):
    """
    date_readable,type,euro,cents,to,from
    5 Oct 2019,remove,5,7,182,198
    """

    def parse_row(self, row):
        record = UnifiedTransactionRecord(
            source=self.source,
            timestamp=datetime.strptime(row[0], "%d %b %Y"),
            type=row[1],
            amount=Decimal("{}.{}".format(row[2], row[3]), ),
            transfer_from=row[5],
            transfer_to=row[4],
        )

        return record

