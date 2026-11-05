import pytest

from project import parse_queries, match_sites
from taipei_sports_occupancy.sites import SITES


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
