from .fetchers import fetch
from .parsers import parse_json, parse_html, parse_text


def get_occupancy(site: dict) -> dict:
    data = fetch(site)
    match site["mode"], data:
        case "json", dict():
            return parse_json(site, data)
        case "html", str():
            return parse_html(site, data)
        case "text", str():
            return parse_text(site, data)
        case _:
            raise NotImplementedError(f"mode {site['mode']!r} 與回應型別 {type(data).__name__} 不相符")