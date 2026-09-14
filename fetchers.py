from typing import Any

import requests


HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
}


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