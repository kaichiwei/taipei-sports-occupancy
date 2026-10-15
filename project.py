import truststore  # pyright: ignore[reportMissingImports]
truststore.inject_into_ssl()  # 放在 import requests 之前的最開頭，加了這個之後不用手動匯出憑證

# the standard import order: standard library -> third party library -> local library
from sys import stderr
import time

import requests

from taipei_sports_occupancy.sites import SITES
from taipei_sports_occupancy.occupancy import get_occupancy
from taipei_sports_occupancy.terminal import print_to_cli
from taipei_sports_occupancy.csv_storage import save_to_csv
from taipei_sports_occupancy.site_lookup import parse_queries, match_sites
from taipei_sports_occupancy.models import OccupancyRecord
from taipei_sports_occupancy.db_storage import init_db, save_to_db

def main():   
    init_db()
    queries = input("選擇場館： ").strip()
    tokens = parse_queries(queries)
    selected_sites, unknown_terms = match_sites(tokens, SITES)    
    
    records = make_records(selected_sites)
    
    print_to_cli(unknown_terms, records)
    save_to_csv(records)
    save_to_db(records)


def make_records(selected_sites: list[dict]) -> list[OccupancyRecord]:
    records = [] 
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

        record = OccupancyRecord(
            timestamp = current_time,
            city = site["city"], 
            name_zh = site["name_zh"], 
            name_en = site["name_en"], 
            facilities = facilities,
            website = site["web"],
        )
        records.append(record)

    return records


if __name__ == "__main__":
    main()