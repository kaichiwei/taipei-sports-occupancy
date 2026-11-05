from taipei_sports_occupancy.fetchers import fetch
import requests
import pytest


site_json = {
    "mode": "json",
    "name_zh": "測試",
    "endpoint": "https://example.com/api"
}

site_html = {
    "mode": "html",
    "name_zh": "測試",
    "web": "https://example.com"
}

site_text = {
    "mode": "text",
    "name_zh": "測試",
    "endpoint": "https://example.com.text"
}


# JSON ，正常回應，自訂 FakeResponse

def test_fetch_json(monkeypatch):

    class FakeResponse:
        def json(self):
            return {"gym":["12","65","0"],"swim":["48","300","0"]}
        def raise_for_status(self):
            pass
        
    def fake_get(url, headers, timeout):
        return FakeResponse()
    
    monkeypatch.setattr(requests, "get", fake_get)
    
    assert fetch(site_json) == {"gym":["12","65","0"],"swim":["48","300","0"]}


# JSON, HTML, Text ，HTTP 錯誤，使用真實 requests.Response

sites = [
    pytest.param(site_json, id="json"),
    pytest.param(site_html, id="html"),
    pytest.param(site_text, id="text"),
]


@pytest.mark.parametrize("site", sites)
def test_fetch_http_error(monkeypatch, site):
    def fake_get(url, headers, timeout):
        response = requests.Response()
        response.status_code = 404
        return response

    monkeypatch.setattr(requests, "get", fake_get)

    with pytest.raises(requests.exceptions.HTTPError):
        fetch(site)


# JSON, HTML, Text ，網路逾時，使用真實 requests.Response

@pytest.mark.parametrize("site", sites)
def test_fetch_json_timeout(monkeypatch, site):

    def fake_get(url, headers, timeout):
        raise requests.exceptions.Timeout()
    
    monkeypatch.setattr(requests, "get", fake_get)

    with pytest.raises(requests.exceptions.Timeout):
        fetch(site)


# JSON 多個 API 端點，中和 & 新生，正常回應，使用真實 requests.Response

GYM_URL = "https://example.com/gym"
SWIM_URL = "https://example.com/swim"

site_zhonghe = {
    "name_zh": "中和",
    "mode": "json",
    "endpoint": {"gym": GYM_URL, "swim": SWIM_URL},
    "CAPACITY": {"gym": 120, "swim": 300},
}

data_zhonghe = {
    GYM_URL: b'{"value": 30}',
    SWIM_URL: b'{"value": 48}',
}

expected_zhonghe = {"gym": [30, 120], "swim": [48, 300]}

site_xinsheng = {
    "name_zh": "新生",
    "mode": "json",
    "endpoint": {"gym": GYM_URL, "swim": SWIM_URL},
}

data_xinsheng = {
    GYM_URL: b'{"ok":true,"count":17,"limit":70,"raw":"17,70,0"}',
    SWIM_URL: b'{"ok":true,"count":15,"limit":120,"raw":"15,120,0"}',
}

expected_xinsheng = {"gym": [17, 70], "swim": [15, 120]}

case_zhonghe = pytest.param(site_zhonghe, data_zhonghe, expected_zhonghe, id="zhonghe")
case_xinsheng = pytest.param(site_xinsheng, data_xinsheng, expected_xinsheng, id="xinsheng")


@pytest.mark.parametrize("site, data_by_url, expected", [case_zhonghe, case_xinsheng])
def test_fetch_json_multi_endpoint(monkeypatch, site, data_by_url, expected):

    def fake_get(url, headers, timeout):
        response = requests.Response()
        response.status_code = 200
        response._content = data_by_url[url]
        return response

    monkeypatch.setattr(requests, "get", fake_get)

    assert fetch(site) == expected


# HTML & Text ，正常回應，使用真實 requests.Response

expected_html = '健身房<div class="notice">47</div>人  <span>容留80人</span>'
expected_text = '64, 79'

case_html = pytest.param(site_html, expected_html, id="html")
case_text = pytest.param(site_text, expected_text, id="text")


@pytest.mark.parametrize("site, expected", [case_html, case_text])
def test_fetch_html_text(monkeypatch, site, expected):

    def fake_get(url, headers, timeout):
        response = requests.Response()
        response.status_code = 200
        response._content = expected.encode("utf-8")
        return response

    monkeypatch.setattr(requests, "get", fake_get)

    assert fetch(site) == expected

