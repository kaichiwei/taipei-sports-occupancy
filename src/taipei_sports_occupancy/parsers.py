import re
import json
from .models import FacilityReading

FACILITY_BY_CATEGORY = {
    "健身房": "gym", "體適能中心": "gym", "游泳池": "pool", "冰宮": "rink",
    "gym": "gym", "swim": "pool", "ice": "rink"
}


# 將字串數字轉成 int，轉不動就回 None,不讓整支 scraper 掛掉。
def to_int(value) -> int | None:
    try:
        return int(str(value).strip())
    except (ValueError, TypeError):
        return None


def parse_json(site: dict, data: dict) -> dict:
    facilities: dict[str, list[str | int | None]] = {
        "gym": [None, None], "pool": [None, None], "rink": [None, None]
    }

    match site["operator"]:
        case "cce" | "ymca" | "far_east_steel" | "cyc":
            # cce: 只有中和，本來是 gym 、 pool 分別獲取資料，經由 fetch 轉成與 cyc 相同格式
            # ymca: 只有新生，本來是 gym 、 pool 分別獲取資料，經由 fetch 轉成與 cyc 相同格式
            # far_east_steel: 資料格式與 cyc 相同，data = {"gym":["18","110","0"],"swim":["64","200","0"],"ice":["26","120","0"]}
            # cyc: data = {"gym":["44","100","0"],"swim":["3","150","0"],"ice":["217","250","0"]}
            # key_map = {"gym": "gym", "swim": "pool", "ice": "rink"}
            for k in data:
                if key := FACILITY_BY_CATEGORY.get(k):
                    facilities[key] = data[k][:2]
    
        case "xports":
            # data = {
            #   "returnCode":"200", "returnMsg":"成功", "data":[
            #       {"courtCatTitle":"游泳池","upperBound":300,"currCapacity":107,"capacityControl":1},
            #       {"courtCatTitle":"體適能中心","upperBound":60,"currCapacity":16,"capacityControl":1}]}
            for court in data["data"]:
                if key := FACILITY_BY_CATEGORY.get(court["courtCatTitle"]):
                    facilities[key] = [court["currCapacity"], court["upperBound"]]

    return {
        k: FacilityReading(
            current= to_int(v[0]), 
            capacity= to_int(v[1])
            )
        for k, v in facilities.items()
    }


def parse_html(site: dict, html: str) -> dict:
    facilities: dict[str, list[str | int | None]] = {
        "gym": [None, None], "pool": [None, None], "rink": [None, None]
    }

    if site["operator"] == "Fullhouse": 
        if not (m := re.search(site["pattern"], html)):
            return facilities
        venues = json.loads(json.loads(m.group(1)))
        # data = [{"MachineName": "游泳池", "MaxQty": 400, "UseQty": 132}, 
        #         {"MachineName": "健身房", "MaxQty": 100, "UseQty": 27}]
        for venue in venues:
            if key := FACILITY_BY_CATEGORY.get(venue["MachineName"]):
                facilities[key] = [venue.get("UseQty"), venue.get("MaxQty")]
    else:
        # PATTERN_CJME = r'(?P<cat>[\u4e00-\u9fa5]+)<span class="stadium-info_number">(?P<cur>\d+)</span>人/ 容留<span>(?P<cap>\d+)人'
        for m in re.finditer(site["pattern"], html):
            field = m.groupdict()
            if key := FACILITY_BY_CATEGORY.get(field["cat"]):
                facilities[key] = [field.get("cur"), field.get("cap")]
    
    return {
        k: FacilityReading(
            current= to_int(v[0]), 
            capacity= to_int(v[1])
            )
        for k, v in facilities.items()
    }


def parse_text(site: dict, text: str) -> dict:
    facilities: dict[str, list[str | int | None]] = {
        "gym": [None, None], "pool": [None, None], "rink": [None, None]
    }
    
    match site["name_zh"]:
        case "新莊":
            gym_current, pool_current = text.split(",")
        case "樹林":
            pool_current, gym_current = text.split(",")
        
    facilities["gym"] = [gym_current, site["CAPACITY"]["gym"]]
    facilities["pool"] = [pool_current, site["CAPACITY"]["swim"]]

    return {
        k: FacilityReading(
            current= to_int(v[0]), 
            capacity= to_int(v[1])
            )
        for k, v in facilities.items()
    }