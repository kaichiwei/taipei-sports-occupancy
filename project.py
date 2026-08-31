import truststore  # pyright: ignore[reportMissingImports]

truststore.inject_into_ssl()  # 放在 import requests 之前的最開頭，加了這個之後不用手動匯出憑證

# the stander import order: standard library -> third party library -> local library
import csv
import json
import re
from sys import stderr
import time
from typing import Any, Iterator
from pathlib import Path
from collections import defaultdict

import requests
from rich.console import Console
from rich.progress_bar import ProgressBar
from rich.table import Table

import sites


METRIC_BY_CATEGORY = {
    "健身房": "gym", "體適能中心": "gym", "游泳池": "pool", "冰宮": "rink",
    "gym": "gym", "swim": "pool", "ice": "rink"
}

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
}

ALL_SITES = sites.SITES

SUFFIXES_ZH = ["", "運動中心", "國民運動中心"]
SUFFIXES_EN = ["", " Sport Center", " Civil Sport Center"]

FIELDNAMES = ["timestamp", "city", "name_zh", "name_en", "metric", "current", "capacity"]


def main():
    records = []    
    queries = input("選擇場館： ").strip()
    tokens = parse_queries(queries)
    selected_sites, unknown_terms = match_sites(tokens, ALL_SITES)    
    

    for site in selected_sites:
        current_time = time.strftime("%Y-%m-%d %H:%M:%S")
        try:
            data = fetch(site)
            match site["mode"], data:
                case "json", dict():
                    metrics = parse_json(site, data)
                case "html", str():
                    metrics = parse_html(site, data)
                case "text", str():
                    metrics = parse_text(site, data)
                case _:
                    raise NotImplementedError(f"mode {site['mode']!r} 與回應型別 {type(data).__name__} 不相符")
        except NotImplementedError as e:
            print(f"{site['name_zh']} 設定不完整: {e}", file=stderr)
            continue
        except requests.RequestException as e:
            print(f"{site['name_zh']} 連線失敗: {e}", file=stderr)
            continue
        except (ValueError, KeyError, AttributeError) as e:
            print(f"{site['name_zh']} 解析失敗: {e}", file=stderr)
            continue
        record = {
            "timestamp": current_time,  "city": site["city"], 
            "name_zh": site["name_zh"], "name_en": site["name_en"], 
            "metrics": metrics,
            "website": site["web"],
        }
        records.append(record)
    
    print_to_cla(unknown_terms, records)
    save_to_csv(records)


# 若需要同時用多種符號（例如逗號與分號）來切字串，內建的 split() 做不到，必須改用正規表達式模組 re.split()
def parse_queries(queries) -> list[str]:
    return [query.strip() for query in re.split(r'[、，；,;]', queries) if query.strip()]
    

def match_sites(queries: list[str], all_sites: list[dict]) -> tuple[list[dict], list[str]]:
    matched_sites = []
    unknown_terms = []
    sites_by_alias = {}
    for site in all_sites:
        for name, suffixes in [(site["name_zh"], SUFFIXES_ZH), (site["name_en"], SUFFIXES_EN)]:
            for suffix in suffixes:
                sites_by_alias[name + suffix] = site
    for query in queries:
        if site := sites_by_alias.get(query):
            if site not in matched_sites:
                matched_sites.append(site)
        else:
            unknown_terms.append(query)    
    return matched_sites, unknown_terms


# 分辨是哪個獲取方式並回傳資料
def fetch(site: dict) -> str | dict[str, Any]:
    match site["mode"]:
        case "json":
            match site["name_zh"]:
                case "中和":
                    data = {}
                    # response = {"value":48}
                    for court in site["endpoint"]:
                        response = requests.get(site["endpoint"][court], headers=HEADERS, timeout=10)
                        response.raise_for_status()    
                        r = response.json()
                        data[court] = [r["value"], site["CAPACITY"][court]]
                case "新生":
                    data = {}
                    # 新生: API endpoint:
                    # xinsheng-gym: https://tmp.ezstore.com.tw/ezrwd/xccs/poolcount.php?site=xinsheng-gym
                    # response = {"ok":true,"count":17,"limit":70,"raw":"17,70,0"}
                    # xinsheng-pool: https://tmp.ezstore.com.tw/ezrwd/xccs/poolcount.php?site=xinsheng-pool
                    # response = {"ok":true,"count":15,"limit":120,"raw":"15,120,0"}
                    for court in site["endpoint"]:
                        response = requests.get(site["endpoint"][court], headers=HEADERS, timeout=10)
                        response.raise_for_status()    
                        r = response.json()
                        data[court] = [r["count"], r["limit"]]
                case _:
                    response = requests.get(site["endpoint"], headers=HEADERS, timeout=10)
                    response.raise_for_status()
                    data = response.json()
            return data
        case "html":
            response = requests.get(site["web"], headers=HEADERS, timeout=10)
            response.raise_for_status()
            response.encoding = "utf-8"
            return response.text
        case "text":
            response = requests.get(site["endpoint"], headers=HEADERS, timeout=10)
            response.raise_for_status()
            response.encoding = "utf-8"
            return response.text  # html 和 text 都回字串
        case _:
            raise NotImplementedError(f"未實作的 mode: {site['mode']!r}")


# 將字串數字轉成 int，轉不動就回 None,不讓整支 scraper 掛掉。
def to_int(value) -> int | None:
    try:
        return int(str(value).strip())
    except (ValueError, TypeError):
        return None


def parse_json(site: dict, data: dict) -> dict:
    metrics: dict[str, list[str | int | None]] = {
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
                if key := METRIC_BY_CATEGORY.get(k):
                    metrics[key] = data[k][:2]
    
        case "xports":
            # data = {
            #   "returnCode":"200", "returnMsg":"成功", "data":[
            #       {"courtCatTitle":"游泳池","upperBound":300,"currCapacity":107,"capacityControl":1},
            #       {"courtCatTitle":"體適能中心","upperBound":60,"currCapacity":16,"capacityControl":1}]}
            for court in data["data"]:
                if key := METRIC_BY_CATEGORY.get(court["courtCatTitle"]):
                    metrics[key] = [court["currCapacity"], court["upperBound"]]

    metrics = {k: [to_int(x) for x in v] for k, v in metrics.items()}
    return metrics


def parse_html(site: dict, html: str) -> dict:
    metrics: dict[str, list[str | int | None]] = {
        "gym": [None, None], "pool": [None, None], "rink": [None, None]
    }

    if site["operator"] == "Fullhouse": 
        if not (m := re.search(site["pattern"], html)):
            return metrics
        venues = json.loads(json.loads(m.group(1)))
        # data = [{"MachineName": "游泳池", "MaxQty": 400, "UseQty": 132}, 
        #         {"MachineName": "健身房", "MaxQty": 100, "UseQty": 27}]
        for venue in venues:
            if key := METRIC_BY_CATEGORY.get(venue["MachineName"]):
                metrics[key] = [venue.get("UseQty"), venue.get("MaxQty")]
    else:
        # PATTERN_CJME = r'(?P<cat>[\u4e00-\u9fa5]+)<span class="stadium-info_number">(?P<cur>\d+)</span>人/ 容留<span>(?P<cap>\d+)人'
        for m in re.finditer(site["pattern"], html):
            field = m.groupdict()
            if key := METRIC_BY_CATEGORY.get(field["cat"]):
                metrics[key] = [field.get("cur"), field.get("cap")]
    
    metrics = {k: [to_int(x) for x in v] for k, v in metrics.items()}
    return metrics


def parse_text(site: dict, text: str) -> dict:
    metrics: dict[str, list[str | int | None]] = {
        "gym": [None, None], "pool": [None, None], "rink": [None, None]
    }
    
    match site["name_zh"]:
        case "新莊":
            gym_current, pool_current = text.split(",")
        case "樹林":
            pool_current, gym_current = text.split(",")
        
    metrics["gym"] = [gym_current, site["CAPACITY"]["gym"]]
    metrics["pool"] = [pool_current, site["CAPACITY"]["swim"]]

    metrics = {k: [to_int(x) for x in v] for k, v in metrics.items()}
    return metrics


def build_table(record: dict) -> Table:
    table = Table(box=None, title=f"{record["name_zh"]} {record["name_en"]}", 
                  title_style="bold white on gray23", show_footer=True)
    table.add_column("設施 Facility", justify="center")
    table.add_column("現在人數 Current", justify="right")
    table.add_column("容留人數 Capacity", justify="right")
    table.add_column("擁擠程度 Occupancy", justify="right")
    table.add_column("", justify="right")
    return table
    

def print_to_cla(unknown_terms, records) -> None:
    if unknown_terms:
        print(f'\n找不到場館：{"、".join(unknown_terms)}\n')
        print(f'Cannot find sites: {", ".join(unknown_terms)}\n')
        print(f'可選場館：\n{"、".join(s["name_zh"] for s in ALL_SITES)}\n')
        print(f'Available sites:\n{", ".join(s["name_en"] for s in ALL_SITES)}\n')

    key = {"gym": "健身房", "pool": "游泳池", "rink": "冰宮"}
    console = Console()
    for record in records:
        table = build_table(record)
        for metric in record["metrics"]:
            cur, cap = record["metrics"][metric][:2]
            if cur is not None:
                if cap is None:
                    table.add_row(f"{key.get(metric)} {metric}", f"{cur:>4}", "-", "-",)
                else:
                    ratio = cur / cap
                    style = "green3" if ratio < 0.2 else "yellow" if ratio < 0.5 else "red" if ratio < 1 else "dark_magenta"
                    table.add_row(
                        f"{key.get(metric)} {metric}", 
                        f"{cur:>4}",
                        f"{cap:>4}", 
                        ProgressBar(total=cap, completed=cur, width=30, complete_style=style, finished_style="dark_magenta", style="grey42"),
                        f"[bold {style}]{ratio:.0%}[/]"
                    )

        table.caption = f"[dim italic gray23]time: {record['timestamp']}\nwebsite: {record['website']}[/]"
        table.caption_justify = "right"
        console.print(table)
        print()


def to_rows(record: dict) -> Iterator[dict]:
    base = {k: record[k] for k in ("timestamp", "city", "name_zh", "name_en")}
    for metric, (cur, cap) in record["metrics"].items():
        yield {**base, "metric": metric, "current": cur, "capacity": cap}


def save_to_csv(records: list[dict]) -> None:
    rows_by_path = defaultdict(list)
    for record in records:
        csv_path = Path("data") / f"log_{record["timestamp"][:7]}.csv"
        for row in to_rows(record):
            if row["current"] is not None:
                rows_by_path[csv_path].append(row)

    Path("data").mkdir(parents=True, exist_ok=True)
    for csv_path, rows in rows_by_path.items():
        new_csv = not csv_path.exists() or csv_path.stat().st_size == 0
        with open(csv_path, "a", newline="", encoding="utf-8") as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames=FIELDNAMES)
            if new_csv:
                writer.writeheader()
            writer.writerows(rows)


if __name__ == "__main__":
    main()