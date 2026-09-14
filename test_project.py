import csv

import pytest

from project import (
    parse_queries,
    match_sites,
    save_to_csv,
)

from sites import SITES
from parsers import to_int, parse_json, parse_html, parse_text
from csv_storage import FIELDNAMES, to_rows


#  -------------------  test parse_queries() -----------------
@pytest.mark.parametrize("queries,expected", [
    # 基本
    ("中和", ["中和"]), 
    ("中和、新莊", ["中和", "新莊"]), 
    ("中和，新莊", ["中和", "新莊"]), 
    ("中和；新莊", ["中和", "新莊"]), 
    ("中和,新莊", ["中和", "新莊"]), 
    ("中和;新莊", ["中和", "新莊"]),
    ("中和、新莊,板橋;三重，樹林；蘆洲", ["中和", "新莊", "板橋", "三重", "樹林", "蘆洲"]),
    # 空白處理
    ("  中和  ", ["中和"]),
    (" 中和 , 新莊 ", ["中和", "新莊"]),
    ("中和\t、\n新莊", ["中和", "新莊"]),
    ("　中和　", ["中和"]),
    ("中和、、新莊", ["中和", "新莊"]),
    ("、中和", ["中和"]),
    ("中和、", ["中和"]),
    ("中和、 、新莊", ["中和", "新莊"]),
    ("", []),
    ("   ", []),
    ("、，；,;", []),
    ("、 ; ，", []),
    # 英文名（內部空白必須保留）
    ("Zhonghe", ["Zhonghe"]),
    ("Xinzhuang Sport Center", ["Xinzhuang Sport Center"]),
    ("Zhonghe, Xinzhuang Civil Sport Center", ["Zhonghe", "Xinzhuang Civil Sport Center"]),
    # 不切分、不去重、不驗證（交給 match_sites
    ("中和 新莊", ["中和 新莊"]),
    ("中和/新莊", ["中和/新莊"]),
])
def test_parse_queries(queries, expected):
    assert parse_queries(queries) == expected


#  -------------------  test match_sites() ------------------
def reveal(names: list[str]) -> list[dict]:
    sites_by_name = {s["name_zh"]: s for s in SITES}
    return [sites_by_name[name] for name in names]

class TestMatchSites:
    class TestValidCases:
        @pytest.mark.parametrize("queries,expected", [
        (["中和"], (reveal(["中和"]), [])), 
        (["中和", "新莊", "桃園", "板橋"], (reveal(["中和", "新莊", "桃園", "板橋"]), [])),
        ])
        def test_match_sites_matched_order(self, queries, expected):
            assert match_sites(queries, SITES) == expected

        @pytest.mark.parametrize("queries,expected", [
            (["Zhonghe"], (reveal(["中和"]), [])),
            (["Zhonghe", "Xinzhuang", "Taoyuan", "Banqiao"], (reveal(["中和", "新莊", "桃園", "板橋"]), []))
        ])
        def test_match_sites_matched_english_alias(self, queries, expected):
            assert match_sites(queries, SITES) == expected

    class TestNotFoundCases:
        @pytest.mark.parametrize("queries,expected", [
            (["不存在"], ([], ["不存在"])), 
            (["彰化", "嘉義", "雲林"], ([], ["彰化", "嘉義", "雲林"])),
        ])
        def test_match_sites_not_found_order(self, queries, expected):
            assert match_sites(queries, SITES) == expected

        @pytest.mark.parametrize("queries,expected", [
            (["unknown"], ([], ["unknown"])), 
            (["Changhua", "Chiayi", "Yunlin"], ([], ["Changhua", "Chiayi", "Yunlin"]))
        ])
        def test_match_sites_not_found_english_alias(self, queries, expected):
            assert match_sites(queries, SITES) == expected

        def test_match_sites_empty_input(self):
            assert match_sites([], SITES) == ([], [])

        def test_match_sites_empty_registry(self):
            assert match_sites(["中和"], []) == ([], ["中和"])

    class TestMixedCases:
        @pytest.mark.parametrize("queries,expected", [
            # valid
            (["中和運動中心"], (reveal(["中和"]), [])), 
            (["中和國民運動中心"], (reveal(["中和"]), [])), 
            (["Xinzhuang Sport Center"], (reveal(["新莊"]), [])),
            (["Xinzhuang Civil Sport Center"], (reveal(["新莊"]), [])),
            # test_concatenated_names
            (["中和新莊"], ([], ["中和新莊"])),
            # test_prefix_too_short
            (["中"], ([], ["中"]))
        ])
        def test_match_sites_suffix(self, queries, expected):
            assert match_sites(queries, SITES) == expected

        def test_match_sites_mixed_found_and_unknown(self):
            queries = ["中正", "abc", "Xinzhuang", "Chiayi", "大安", "基隆"]
            assert match_sites(queries, SITES) == (reveal(["中正", "新莊", "大安"]), ["abc", "Chiayi", "基隆"])
    
        def test_match_sites_deduplicates(self):
            assert match_sites(["Daan", "大安", "大安運動中心"], SITES) == (reveal(["大安"]), [])


#  ------------------- test to_int() -----------------------
@pytest.mark.parametrize("value,expected", [
    ("678", 678),
    ('123', 123),
    (0, 0),
    (45, 45),
    ("abc", None),
    (None, None),
])
def test_to_int(value, expected):
    assert to_int(value) == expected


class TestParse:
#  ------------------- test parse_json() -------------------
    class TestJSON:
        def test_parse_json_xports(self):
            SITE_XPORTS = {
                "name_zh": "測試館",
                "name_en": "test",
                "operator": "xports",
                "mode": "json",
            }
            data = {
                "returnCode":"200", "returnMsg":"成功", "data":[
                    {"courtCatTitle":"游泳池","upperBound":300,"currCapacity":107,"capacityControl":1},
                    {"courtCatTitle":"體適能中心","upperBound":60,"currCapacity":16,"capacityControl":1}]
            }
            assert parse_json(SITE_XPORTS, data) == {
                "gym": [16, 60],
                "pool": [107, 300],
                "rink": [None, None]
            }

        def test_parse_json_cyc(self):
            SITE_CYC = {
            "name_zh": "測試館", 
            "name_en": "test",
            "operator": "cyc",
            "mode": "json",
            }
            data = {"gym":["44","100","0"],"swim":["3","150","0"],"ice":["217","250","0"]}
            assert parse_json(SITE_CYC, data) == {
                "gym": [44, 100],
                "pool": [3, 150],
                "rink": [217, 250]
            }
            data = {"gym":["44","100","0"],"swim":["3","150","0"]}
            assert parse_json(SITE_CYC, data) == {
                "gym": [44, 100],
                "pool": [3, 150],
                "rink": [None, None]
            }

#  ------------------- test parse_html() -------------------
    class TestHTML:
        def test_parse_html_fullhouse(self):
            SITE_FULLHOUSE = {
                "name_zh": "測試館",
                "name_en": "test",
                "operator": "Fullhouse",
                "mode": "html",
                "pattern": r'this\.venueInfo\s*=\s*JSON\.parse\((.+?)\)'
            }
            # using raw string r''
            source = r'this.venueInfo = ' \
                    r'JSON.parse("[ \r\n  {\r\n    \"MachineName\": \"游泳池\",\r\n    \"MaxQty\": 400,\r\n    \"UseQty\": 132\r\n  }, ' \
                    r'\r\n  {\r\n    \"MachineName\": \"健身房\",\r\n    \"MaxQty\": 100,\r\n    \"UseQty\": 27\r\n  } \r\n]")'
            assert parse_html(SITE_FULLHOUSE, source) == {
                "gym": [27, 100],
                "pool": [132, 400],
                "rink": [None, None]
            }

        def test_parse_html_cjme(self):
            SITE_cjme = {
                "name_zh": "測試館",
                "name_en": "test",
                "operator": "cjme",
                "mode": "html",
                "pattern": r'(?P<cat>[\u4e00-\u9fa5]+)<span class="stadium-info_number">(?P<cur>\d+)</span>人/ 容留<span>(?P<cap>\d+)人'
            }
            source = '健身房<span class="stadium-info_number">25</span>人/ 容留<span>80人' \
                    '游泳池<span class="stadium-info_number">67</span>人/ 容留<span>250人'
            assert parse_html(SITE_cjme, source) == {
                "gym": [25, 80],
                "pool": [67, 250],
                "rink": [None, None]
            }

        def test_parse_html_ws(self):
            SITE_ws = {
                "name_zh": "測試館",
                "name_en": "test",
                "operator": "ws",
                "mode": "html",
                "pattern": r'(?P<cat>[\u4e00-\u9fa5]+)<div class="notice">(?P<cur>\d+)</div>人\s*<span>容留(?P<cap>\d+)人'
            }
            source = '健身房<div class="notice">47</div>人  <span>容留80人</span>' \
                    '游泳池<div class="notice">173</div>人 <span>容留250人</span>'
            assert parse_html(SITE_ws, source) == {
                "gym": [47, 80],
                "pool": [173, 250],
                "rink": [None, None]
            }

#  ------------------- test parse_text() -------------------
    class TestTEXT:    
        def test_parse_text_elite_Xinzhuang(self):    
            SITE_elite = {
                "name_zh": "新莊",
                "name_en": "Xinzhuang",
                "operator": "elite",
                "mode": "text",
                "CAPACITY": {"gym": 100, "swim": 200}
            }
            text = '99, 199'
            assert parse_text(SITE_elite, text) == {
                "gym": [99, 100],
                "pool": [199, 200],
                "rink": [None, None]
            }
 
        def test_parse_text_elite_Shulin(self):    
            SITE_elite = {
                "name_zh": "樹林",
                "name_en": "Shulin",
                "operator": "elite",
                "mode": "text", 
                "CAPACITY": {"gym": 100, "swim": 200}
            }
            text = '199, 99'
            assert parse_text(SITE_elite, text) == {
                "gym": [99, 100],
                "pool": [199, 200],
                "rink": [None, None]
            }


# --------------------  test to_rows() ----------------------
RECORD = {
    "timestamp": "2026-08-21 10:00:00",
    "city": "NTPC",
    "name_zh": "中和",
    "name_en": "Zhonghe",
    "facilities": {"gym": [44, 100], "pool": [3, 150], "rink": [None, None]},
}


def test_to_rows_yields_one_row_per_facility():
    base = {"timestamp": "2026-08-21 10:00:00", "city": "NTPC", "name_zh": "中和", "name_en": "Zhonghe"}
    assert list(to_rows(RECORD)) == [
        {**base, "facility": "gym", "current": 44, "capacity": 100},
        {**base, "facility": "pool", "current": 3, "capacity": 150},
        {**base, "facility": "rink", "current": None, "capacity": None},
    ]


def test_to_rows_keys_match_fieldnames():
    assert set(next(to_rows(RECORD))) == set(FIELDNAMES)


#  -------------------  test save_to_csv() ------------------
def make_record(timestamp, city, name_zh, name_en, gym, pool, rink):
    return {
        "timestamp": timestamp, "city": city,
        "name_zh": name_zh, "name_en": name_en,
        "facilities": {"gym": gym, "pool": pool, "rink": rink},
    }

# 同一個月，資料類別不同
# 2 rows
TWO_FACILITIES = make_record("2026-08-21 10:00:00", "NTPC", "中和", "Zhonghe", [44, 100], [3, 150], [None, None])
# 3 rows
THREE_FACILITIES = make_record("2026-08-22 19:58:43", "NTPC", "土城", "Tucheng", [33, 120], [159, 280], [36, 250])
# 2 rows
NONE_CAP = make_record("2026-08-01 05:16:28", "TPE", "大同", "Datong", [55, None], [116, None], [None, None]
)
# 0 rows
NONE_CUR = make_record("2026-08-15 01:47:15", "Nantou", "集集", "Jiji", [None, 120], [None, 250], [None, None])
# 2 rows
ZERO_CUR = make_record("2026-08-08 10:30:00", "NTPC", "蘆洲", "Luzhou", [0, 120], [0, 250], [None, None])
# 隔一天但跨月
THIS_MONTH = make_record("2026-08-31 23:59:59", "NTPC", "新莊", "Xinzhuang", [10, 100], [20, 200], [None, None])
NEXT_MONTH  = make_record("2026-09-01 00:00:01", "NTPC", "新莊", "Xinzhuang", [11, 100], [21, 200], [None, None])

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

