import pytest

from taipei_sports_occupancy.parsers import to_int, parse_json, parse_html, parse_text
from taipei_sports_occupancy.models import FacilityReading


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
                "gym": FacilityReading(16, 60),
                "pool": FacilityReading(107, 300),
                "rink": FacilityReading(None, None)
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
                "gym": FacilityReading(44, 100),
                "pool": FacilityReading(3, 150),
                "rink": FacilityReading(217, 250)
            }
            data = {"gym":["44","100","0"],"swim":["3","150","0"]}
            assert parse_json(SITE_CYC, data) == {
                "gym": FacilityReading(44, 100),
                "pool": FacilityReading(3, 150),
                "rink": FacilityReading(None, None)
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
                "gym": FacilityReading(27, 100),
                "pool": FacilityReading(132, 400),
                "rink": FacilityReading(None, None)
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
                "gym": FacilityReading(25, 80),
                "pool": FacilityReading(67, 250),
                "rink": FacilityReading(None, None)
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
                "gym": FacilityReading(47, 80),
                "pool": FacilityReading(173, 250),
                "rink": FacilityReading(None, None)
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
                "gym": FacilityReading(99, 100),
                "pool": FacilityReading(199, 200),
                "rink": FacilityReading(None, None)
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
                "gym": FacilityReading(99, 100),
                "pool": FacilityReading(199, 200),
                "rink": FacilityReading(None, None)
            }