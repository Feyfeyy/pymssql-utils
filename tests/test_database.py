import os
from datetime import date, time, datetime, timezone, timedelta

import pytest

import pymssqlutils as sql
from pymssqlutils import model_to_values

SKIP_FILE = not os.environ.get("TEST_ON_DATABASE")
SKIP_REASON = "TEST_ON_DATABASE is not set in environment"


@pytest.mark.skipif(SKIP_FILE, reason=SKIP_REASON)
def test_can_connect():
    sql.query("SELECT sysdatetimeoffset() now")


@pytest.mark.skipif(SKIP_FILE, reason=SKIP_REASON)
def test_type_parsing():
    data = sql.query(
        """
            SELECT
                CAST(GETDATE() AS DATE) Col_Date,
                CONVERT(VARBINARY(MAX), 'BinaryText') Col_Binary,
                CAST(SYSDATETIMEOFFSET() AS time(1)) Col_Time1,
                CAST(SYSDATETIMEOFFSET() AS time(2)) Col_Time2,
                CAST(SYSDATETIMEOFFSET() AS time(3)) Col_Time3,
                CAST(SYSDATETIMEOFFSET() AS time(4)) Col_Time4,
                CAST(SYSDATETIMEOFFSET() AS time(5)) Col_Time5,
                CAST(SYSDATETIMEOFFSET() AS time(6)) Col_Time6,
                CAST(SYSDATETIMEOFFSET() AS time(7)) Col_Time7,
                CAST(SYSDATETIMEOFFSET() AS Smalldatetime) Col_Smalldatetime,
                CAST(SYSDATETIMEOFFSET() AS Datetime) Col_Datetime,
                CAST(SYSDATETIMEOFFSET() AS Datetime2) Col_Datetime2,
                CAST(SYSDATETIMEOFFSET() AS Datetimeoffset(0)) Col_Datetimeoffset0,
                CAST(SYSDATETIMEOFFSET() AS Datetimeoffset(1)) Col_Datetimeoffset1,
                CAST(SYSDATETIMEOFFSET() AS Datetimeoffset(2)) Col_Datetimeoffset2,
                CAST(SYSDATETIMEOFFSET() AS Datetimeoffset(3)) Col_Datetimeoffset3,
                CAST(SYSDATETIMEOFFSET() AS Datetimeoffset(4)) Col_Datetimeoffset4,
                CAST(SYSDATETIMEOFFSET() AS Datetimeoffset(5)) Col_Datetimeoffset5,
                CAST(SYSDATETIMEOFFSET() AS Datetimeoffset(6)) Col_Datetimeoffset6,
                CAST(SYSDATETIMEOFFSET() AS Datetimeoffset(7)) Col_Datetimeoffset7,
                CAST(1.2344566 AS NUMERIC) Col_Numeric
        """
    ).data[0]

    assert isinstance(data["Col_Binary"], bytes)
    assert data["Col_Binary"].decode("UTF8") == "BinaryText"
    assert isinstance(data["Col_Date"], date)
    assert isinstance(data["Col_Time1"], time)
    assert isinstance(data["Col_Time2"], time)
    assert isinstance(data["Col_Time3"], time)
    assert isinstance(data["Col_Time4"], time)
    assert isinstance(data["Col_Time5"], time)
    assert isinstance(data["Col_Time6"], time)
    assert isinstance(data["Col_Time7"], time)
    assert isinstance(data["Col_Smalldatetime"], datetime)
    assert isinstance(data["Col_Datetime"], datetime)
    assert isinstance(data["Col_Datetime2"], datetime)
    assert isinstance(data["Col_Datetimeoffset0"], datetime)
    assert isinstance(data["Col_Datetimeoffset1"], datetime)
    assert isinstance(data["Col_Datetimeoffset2"], datetime)
    assert isinstance(data["Col_Datetimeoffset3"], datetime)
    assert isinstance(data["Col_Datetimeoffset4"], datetime)
    assert isinstance(data["Col_Datetimeoffset5"], datetime)
    assert isinstance(data["Col_Datetimeoffset6"], datetime)
    assert isinstance(data["Col_Datetimeoffset7"], datetime)
    assert isinstance(data["Col_Numeric"], float)


@pytest.mark.skipif(SKIP_FILE, reason=SKIP_REASON)
def test_execute():
    sql.execute("CREATE TABLE #temp (val int)")


@pytest.mark.skipif(SKIP_FILE, reason=SKIP_REASON)
def test_execute_with_fetch():
    result = sql.execute("SELECT 'hello' col", fetch=True)
    assert result.data[0]["col"] == "hello"


@pytest.mark.skipif(SKIP_FILE, reason=SKIP_REASON)
def test_execute_many():
    sql.execute("SELECT %s val", [(1,), (2,), (3,)])


@pytest.mark.skipif(SKIP_FILE, reason=SKIP_REASON)
def test_execute_batched():
    sql.execute(
        "SELECT %s a, %s b, %s c",
        [(val, val + 1, val + 2) for val in range(1000)],
        batch_size=500,
    )


@pytest.mark.skipif(SKIP_FILE, reason=SKIP_REASON)
def test_execute_many_operations():
    result = sql.execute([f"SELECT {val} val" for val in range(1000)], fetch=True)
    assert result.data[0]["val"] == 999


@pytest.mark.skipif(SKIP_FILE, reason=SKIP_REASON)
def test_datetime_offset_handling():
    model = {
        "col1": "hello",
        "col2": 1.23,
        "col3": datetime(2020, 6, 1, 12, 30, tzinfo=timezone(timedelta(hours=-1))),
        "col4": True,
    }
    result = sql.execute(
        [
            "CREATE TABLE #temp (col1 VARCHAR(100), col2 DECIMAL(6,2), col3 DATETIMEOFFSET, col4 TINYINT)",
            f"INSERT INTO #temp {model_to_values(model)}",
            "SELECT * FROM #temp",
        ],
        fetch=True,
    )
    assert result.data[0]["col1"] == "hello"
    assert result.data[0]["col2"] == 1.23
    assert result.data[0]["col3"] == datetime(
        2020, 6, 1, 12, 30, tzinfo=timezone(timedelta(hours=-1))
    )
    assert result.data[0]["col4"] == 1
