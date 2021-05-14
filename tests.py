import datetime
from decimal import Decimal, getcontext

import pytest
from convert_lib.processors import InputConverterBank1, InputConverterBank2, InputConverterBank3
from convert_lib.storage import UnifiedTransactionStorage, UnifiedTransactionRecord

# decimal precision for money
getcontext().prec = 2


@pytest.fixture
def row_bank1_fixture():
    return ['Oct 1 2019', 'remove', '99.20', '198', '182']

@pytest.fixture
def row_bank2_fixture():
    return ['03-10-2019', 'remove', '99.40', '182', '198']

@pytest.fixture
def row_bank3_fixture():
    return ['6 Oct 2019', 'add', '1060', '8', '198', '188']

@pytest.fixture
def storage_filled():
    storage = UnifiedTransactionStorage()
    storage.add(UnifiedTransactionRecord(
        timestamp=datetime.datetime(year=2019, month=10, day=5),
        type='add',
        amount=Decimal('100.10'),
        transfer_to='test1',
        transfer_from='test2',
        source='test'
    ))

    return storage


def test_read_bank1(row_bank1_fixture):
    processor = InputConverterBank1(storage=list(), source='test')
    parsed = processor.parse_row(row_bank1_fixture)
    assert parsed.timestamp.date() == datetime.datetime(year=2019, month=10, day=1).date()
    assert parsed.amount == Decimal('99.20')
    assert parsed.transfer_from == '198'
    assert parsed.transfer_to == '182'


def test_read_bank2(row_bank2_fixture):
    processor = InputConverterBank2(storage=list(), source='test')
    parsed = processor.parse_row(row_bank2_fixture)
    assert parsed.timestamp.date() == datetime.datetime(year=2019, month=10, day=3).date()
    assert parsed.amount == Decimal('99.40')
    assert parsed.transfer_from == '198'
    assert parsed.transfer_to  == '182'


def test_read_bank3(row_bank3_fixture):
    processor = InputConverterBank3(storage=list(), source='test')
    parsed = processor.parse_row(row_bank3_fixture)
    assert parsed.timestamp.date() == datetime.datetime(year=2019, month=10, day=6).date()
    assert parsed.amount == Decimal('1060.8')
    assert parsed.transfer_from == '188'
    assert parsed.transfer_to  == '198'


def test_export_dateformat(storage_filled):
    exported = storage_filled.export_record(storage_filled.get(0))

    assert exported[1] == '2019-10-05'