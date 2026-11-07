import csv

from taipei_sports_occupancy.csv_storage import FIELDNAMES, to_rows, save_to_csv
from taipei_sports_occupancy.models import OccupancyRecord, FacilityReading


# --------------------  test to_rows() ----------------------
RECORD = OccupancyRecord(
    timestamp = "2026-08-21 10:00:00",
    city = "NTPC",
    name_zh = "中和",
    name_en = "Zhonghe",
    facilities = {"gym": FacilityReading(current= 44, capacity= 100), 
                  "pool": FacilityReading(current= 3, capacity= 150),
                  "rink": FacilityReading(current= None, capacity= None)
                },
    website = "https://example.tw"
)


def test_to_rows_yields_one_row_per_facility():
    base = {
        "timestamp": RECORD.timestamp,
        "city": RECORD.city,
        "name_zh": RECORD.name_zh, 
        "name_en": RECORD.name_en
    }
    assert list(to_rows(RECORD)) == [
        {**base, "facility": "gym", "current": 44, "capacity": 100},
        {**base, "facility": "pool", "current": 3, "capacity": 150},
        {**base, "facility": "rink", "current": None, "capacity": None},
    ]


def test_to_rows_keys_match_fieldnames():
    assert set(next(to_rows(RECORD))) == set(FIELDNAMES)


#  -------------------  test save_to_csv() ------------------
def make_record(timestamp, city, name_zh, name_en, gym, pool, rink):
    return OccupancyRecord(
        timestamp= timestamp,
        city= city,
        name_zh= name_zh,
        name_en= name_en,
        facilities= {"gym": gym, "pool": pool, "rink": rink},
        website= "https://example.tw"
    )

# 同一個月，資料類別不同
# 2 rows
TWO_FACILITIES = make_record(
    "2026-08-21 10:00:00", "NTPC", "中和", "Zhonghe", 
    FacilityReading(44, 100), FacilityReading(3, 150), FacilityReading(None, None)
)
# 3 rows
THREE_FACILITIES = make_record(
    "2026-08-22 19:58:43", "NTPC", "土城", "Tucheng", 
    FacilityReading(33, 120), FacilityReading(159, 280), FacilityReading(36, 250)
)
# 2 rows
NONE_CAP = make_record(
    "2026-08-01 05:16:28", "TPE", "大同", "Datong", 
    FacilityReading(55, None), FacilityReading(116, None), FacilityReading(None, None)
)
# 0 rows
NONE_CUR = make_record(
    "2026-08-15 01:47:15", "Nantou", "集集", "Jiji", 
    FacilityReading(None, 120), FacilityReading(None, 250), FacilityReading(None, None)
)
# 2 rows
ZERO_CUR = make_record(
    "2026-08-08 10:30:00", "NTPC", "蘆洲", "Luzhou", 
    FacilityReading(0, 120), FacilityReading(0, 250), FacilityReading(None, None)
)
# 隔一天但跨月
THIS_MONTH = make_record(
    "2026-08-31 23:59:59", "NTPC", "新莊", "Xinzhuang", 
    FacilityReading(10, 100), FacilityReading(20, 200), FacilityReading(None, None)
)
NEXT_MONTH  = make_record(
    "2026-09-01 00:00:01", "NTPC", "新莊", "Xinzhuang", 
    FacilityReading(11, 100), FacilityReading(21, 200), FacilityReading(None, None)
)


class TestSaveCSV:
    def test_save_to_csv_all_none_cur_creates_no_file(self, tmp_path, monkeypatch):
        monkeypatch.chdir(tmp_path)
        save_to_csv([NONE_CUR])
        assert not (tmp_path / "data" / "log_2026-08.csv").exists()

    def test_save_to_csv(self, tmp_path, monkeypatch):
        monkeypatch.chdir(tmp_path)
        save_to_csv([TWO_FACILITIES, THREE_FACILITIES, NONE_CAP, NONE_CUR, ZERO_CUR])
        with open(tmp_path / "data" / "log_2026-08.csv", newline="", encoding="utf-8") as f:
            reader = list(csv.DictReader(f))
            assert len(reader) == 9
            assert reader[:2] == [
                {
                    "timestamp": "2026-08-21 10:00:00",
                    "city": "NTPC",
                    "name_zh": "中和",
                    "name_en": "Zhonghe",
                    "facility": "gym",
                    "current": "44",
                    "capacity": "100",
                },
                {
                    "timestamp": "2026-08-21 10:00:00",
                    "city": "NTPC",
                    "name_zh": "中和",
                    "name_en": "Zhonghe",
                    "facility": "pool",
                    "current": "3",
                    "capacity": "150",
                },
            ]
            assert reader[2:5] == [
                {
                    "timestamp": "2026-08-22 19:58:43",
                    "city": "NTPC",
                    "name_zh": "土城",
                    "name_en": "Tucheng",
                    "facility": "gym",
                    "current": "33",
                    "capacity": "120",
                },
                {
                    "timestamp": "2026-08-22 19:58:43",
                    "city": "NTPC",
                    "name_zh": "土城",
                    "name_en": "Tucheng",
                    "facility": "pool",
                    "current": "159", 
                    "capacity": "280",
                },
                {
                    "timestamp": "2026-08-22 19:58:43",
                    "city": "NTPC",
                    "name_zh": "土城",
                    "name_en": "Tucheng",
                    "facility": "rink",
                    "current": "36", 
                    "capacity": "250",
                },
            ]
            assert reader[5:7] == [
                {
                    "timestamp": "2026-08-01 05:16:28",
                    "city": "TPE",
                    "name_zh": "大同",
                    "name_en": "Datong",
                    "facility": "gym",
                    "current": "55",
                    "capacity": "",
                },
                {
                    "timestamp": "2026-08-01 05:16:28",
                    "city": "TPE",
                    "name_zh": "大同",
                    "name_en": "Datong",
                    "facility": "pool",
                    "current": "116",
                    "capacity": "",
                },
            ]
            assert reader[7:] == [
                {
                    "timestamp": "2026-08-08 10:30:00",
                    "city": "NTPC",
                    "name_zh": "蘆洲",
                    "name_en": "Luzhou",
                    "facility": "gym",
                    "current": "0",
                    "capacity": "120",
                },
                {
                    "timestamp": "2026-08-08 10:30:00",
                    "city": "NTPC",
                    "name_zh": "蘆洲",
                    "name_en": "Luzhou",
                    "facility": "pool",
                    "current": "0",
                    "capacity": "250",
                },
            ]

    def test_save_to_csv_splits_by_month(self, tmp_path, monkeypatch):
        monkeypatch.chdir(tmp_path)
        save_to_csv([THIS_MONTH, NEXT_MONTH])
        assert (tmp_path / "data" / "log_2026-08.csv").exists()
        assert (tmp_path / "data" / "log_2026-09.csv").exists()
        assert sorted(p.name for p in (tmp_path / "data").iterdir()) == [
            "log_2026-08.csv", "log_2026-09.csv"
        ]

        with open(tmp_path / "data" / "log_2026-08.csv", newline="", encoding="utf-8") as f:
                reader = list(csv.DictReader(f))
                assert reader == [
                    {
                        "timestamp": "2026-08-31 23:59:59",
                        "city": "NTPC", "name_zh": "新莊", "name_en": "Xinzhuang",
                        "facility": "gym",
                        "current": "10",
                        "capacity": "100"
                    },
                    {
                        "timestamp": "2026-08-31 23:59:59",
                        "city": "NTPC", "name_zh": "新莊", "name_en": "Xinzhuang",
                        "facility": "pool",
                        "current": "20",
                        "capacity": "200"
                    },
                ]

        with open(tmp_path / "data" / "log_2026-09.csv", newline="", encoding="utf-8") as f:
                reader = list(csv.DictReader(f))
                assert reader == [
                    {
                        "timestamp": "2026-09-01 00:00:01",
                        "city": "NTPC", "name_zh": "新莊", "name_en": "Xinzhuang",
                        "facility": "gym",
                        "current": "11",
                        "capacity": "100"
                    },
                    {
                        "timestamp": "2026-09-01 00:00:01",
                        "city": "NTPC", "name_zh": "新莊", "name_en": "Xinzhuang",
                        "facility": "pool",
                        "current": "21",
                        "capacity": "200"
                    },
                ]