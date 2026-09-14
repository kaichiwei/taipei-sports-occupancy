
import re

SUFFIXES_ZH = ["", "運動中心", "國民運動中心"]
SUFFIXES_EN = ["", " Sport Center", " Civil Sport Center"]


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
