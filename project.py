import truststore  # pyright: ignore[reportMissingImports]

truststore.inject_into_ssl()  # 放在 import requests 之前的最開頭，加了這個之後不用手動匯出憑證

# the stander import order: standard library -> third party library -> local library

import re
from sys import stderr
import time

import requests

from sites import SITES
from occupancy import get_occupancy
from terminal import print_to_cla
from csv_storage import save_to_csv


SUFFIXES_ZH = ["", "運動中心", "國民運動中心"]
SUFFIXES_EN = ["", " Sport Center", " Civil Sport Center"]


def main():
    records = []    
    queries = input("選擇場館： ").strip()
    tokens = parse_queries(queries)
    selected_sites, unknown_terms = match_sites(tokens, SITES)    
    
    for site in selected_sites:
        current_time = time.strftime("%Y-%m-%d %H:%M:%S")
        try:
            facilities = get_occupancy(site)
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
            "facilities": facilities,
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


if __name__ == "__main__":
    main()