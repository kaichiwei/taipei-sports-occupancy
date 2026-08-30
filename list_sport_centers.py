PATTERN_CJME = r'(?P<cat>[\u4e00-\u9fa5]+)<span class="stadium-info_number">(?P<cur>\d+)</span>人/ 容留<span>(?P<cap>\d+)人'
PATTERN_WS = r'(?P<cat>[\u4e00-\u9fa5]+)<div class="notice">(?P<cur>\d+)</div>人\s*<span>容留(?P<cap>\d+)人'
PATTERN_FULLHOUSE = r'this\.venueInfo\s*=\s*JSON\.parse\((.+?)\)'

SITES = [
    # 長佳機電 cjme: html-regex:
    # https://www.{name}.tw/zh_TW/onsitenum
    # Sourse:
    # 健身房<span class="stadium-info_number">25</span>人/ 容留<span>80人
    # 游泳池<span class="stadium-info_number">67</span>人/ 容留<span>250人
    # pattern = r'([\u4e00-\u9fa5]+)<span class="stadium-info_number">(\d+)</span>人/ 容留<span>(\d+)人'
    {
        "city": "TPE",
        "name_zh": "大安",
        "name_en": "Daan",
        "operator": "cjme",
        "mode": "html",
        "web": "https://www.daansports.com.tw/zh_TW/onsitenum",
        "pattern": PATTERN_CJME,
    },
    {
        "city": "NTPC",
        "name_zh": "板橋",
        "name_en": "Banqiao",
        "operator": "cjme",
        "mode": "html",
        "web": "https://www.bqsports.com.tw/zh_TW/onsitenum",
        "pattern": PATTERN_CJME,
    },
    {
        "city": "NTPC",
        "name_zh": "新店",
        "name_en": "Xindian",
        "operator": "cjme",
        "mode": "html",
        "web": "https://www.xdsports.com.tw/zh_TW/onsitenum",
        "pattern": PATTERN_CJME,
    },
    {
        "city": "Taoyuan",
        "name_zh": "蘆竹",
        "name_en": "Luzhu",
        "operator": "cjme",
        "mode": "html",
        "web": "https://www.lzsports.com.tw/zh_TW/onsitenum",
        "pattern": PATTERN_CJME,
    },
    
    # 舞動陽光 ws: html-regex:
    # https://{name}.com.tw
    # Sourse:
    # 健身房<div class="notice">47</div>人  <span>容留80人</span>
    # 游泳池<div class="notice">173</div>人 <span>容留250人</span>
    # pattern = r'([\u4e00-\u9fa5]+)<div class="notice">(\d+)</div>人\s*<span>容留(\d+)人'
    {
        "city": "TPE",
        "name_zh": "大同",
        "name_en": "Datong",
        "operator": "ws",
        "mode": "html",
        "web": "https://www.dtsc-wdyg.com.tw",
        "pattern": PATTERN_WS,
    },
    {
        "city": "TPE",
        "name_zh": "中正",
        "name_en": "Zhongzheng",
        "operator": "ws",
        "mode": "html",
        "web": "https://wsjjsc.com.tw",
        "pattern": PATTERN_WS,
    },
    {
        "city": "NTPC",
        "name_zh": "淡水",
        "name_en": "Tamsui",
        "operator": "ws",
        "mode": "html",
        "web": "https://wstssc.com.tw",
        "pattern": PATTERN_WS,
    },
    {
        "city": "NTPC",
        "name_zh": "泰山",
        "name_en": "Taishan",
        "operator": "ws",
        "mode": "html",
        "web": "https://wstscsc.com.tw",
        "pattern": PATTERN_WS,
    },
    {
        "city": "Taoyuan",
        "name_zh": "楊梅",
        "name_en": "Yangmei",
        "operator": "ws",
        "mode": "html",
        "web": "https://ymscwdyg.com.tw",
        "pattern": PATTERN_WS,
    },
    
    # 匯陽百貨 Fullhouse Corporation: html-regex
    # 內嵌在 HTML 裡的 JSON
    # Sourses:
    # this.venueInfo = JSON.parse("[
    #       \r\n  {\r\n    \"MachineName\": \"游泳池\",\r\n    \"MaxQty\": 400,\r\n    \"UseQty\": 132\r\n  },
    #       \r\n  {\r\n    \"MachineName\": \"健身房\",\r\n    \"MaxQty\": 100,\r\n    \"UseQty\": 27\r\n  }
    # \r\n]")
    # pattern = r'this.venueInfo\s*=\s*JSON\.parse\((.+?)\)'
    {
        "city": "TPE",
        "name_zh": "松山",
        "name_en": "Songshan",
        "operator": "Fullhouse",
        "mode": "html",
        "web": "https://sssc.com.tw",
        "pattern": PATTERN_FULLHOUSE,
    },
    {
        "city": "TPE",
        "name_zh": "萬華",
        "name_en": "Wanhua",
        "operator": "Fullhouse",
        "mode": "html",
        "web": "https://whsc.com.tw",
        "pattern": PATTERN_FULLHOUSE,
    },
    
    # 展昭國際 chanchao: html-regex
    # 沒有容留人數，只有現在人數
    # 蘆洲 Sources:
    # <span>游泳池</span> <span id="show_number_of_people1" data-unit="人">78</span>
    # <span>體適能中心</span> <span id="show_number_of_people2" data-unit="人">44</span>
    # pattern = r'([\u4e00-\u9fa5]+)</span>\s*<span id="show_number_of_people[12]" data-unit="人">(\d+)</span>'
    {
        "city": "NTPC",
        "name_zh": "蘆洲",
        "name_en": "Luzhou",
        "operator": "chanchao",
        "mode": "html",
        "web": "https://lzsc.chanchao.com.tw/",
        "pattern": r'(?P<cat>[\u4e00-\u9fa5]+)</span>\s*<span id="show_number_of_people[12]" data-unit="人">(?P<cur>\d+)</span>',
    },
    # 五股 Sources:
    # 體適能中心</span> <span class="num_1center" id="total_num_534" data-to="27" style="text-align: center">27</span><span class="mun_2">人
    # 游泳池</span> <span class="num_1center" id="total_num_535" data-to="129" style="text-align: center">129</span><span class="mun_2">人
    # pattern = r'([\u4e00-\u9fa5]+)\s*</span>\s*<span class="num_1center" id="total_num_53[45]" data-to="\d+" style="text-align: center">(\d+)</span><span class="mun_2">人'
    {
        "city": "NTPC",
        "name_zh": "五股",
        "name_en": "Wugu",
        "operator": "chanchao",
        "mode": "html",
        "web": "https://wgsc.chanchao.com.tw/",
        "pattern": r'(?P<cat>[\u4e00-\u9fa5]+)\s*</span>\s*<span class="num_1center" id="total_num_53[45]" data-to="\d+" style="text-align: center">(?P<cur>\d+)</span><span class="mun_2">人',
    },
    
    # 救國團 cyc (China Youth Corps): API end-point:
    # https://{name}.cyc.org.tw/api
    # response = {"gym":["18","110","0"],"swim":["64","200","0"],"ice":["26","120","0"]}
    {
        "city": "TPE",
        "name_zh": "南港",
        "name_en": "Nangang",
        "operator": "cyc",
        "mode": "json",
        "web": "https://ngsc.cyc.org.tw",
        "endpoint": "https://ngsc.cyc.org.tw/api",
    },
    {
        "city": "TPE",
        "name_zh": "中山",
        "name_en": "Zhongshan",
        "operator": "cyc",
        "mode": "json",
        "web": "https://cssc.cyc.org.tw",
        "endpoint": "https://cssc.cyc.org.tw/api",
    },
    {
        "city": "TPE",
        "name_zh": "內湖",
        "name_en": "Neihu",
        "operator": "cyc",
        "mode": "json",
        "web": "https://nhsc.cyc.org.tw",
        "endpoint": "https://nhsc.cyc.org.tw/api",
    },
    # 景美游泳池跟文山運動中心共用一個 API endpoint，景美游泳池人數資料在冰宮 "ice":["26","120","0"]
    {
        "city": "TPE",
        "name_zh": "文山",
        "name_en": "Wenshan",
        "operator": "cyc",
        "mode": "json",
        "web": "https://wssc.cyc.org.tw",
        "endpoint": "https://wssc.cyc.org.tw/api",
    },
    {
        "city": "NTPC",
        "name_zh": "汐止",
        "name_en": "Xizhi",
        "operator": "cyc",
        "mode": "json",
        "web": "https://xzcsc.cyc.org.tw",
        "endpoint": "https://xzcsc.cyc.org.tw/api",
    },
    {
        "city": "NTPC",
        "name_zh": "永和",
        "name_en": "Yonghe",
        "operator": "cyc",
        "mode": "json",
        "web": "https://yhcsc.cyc.org.tw",
        "endpoint": "https://yhcsc.cyc.org.tw/api",
    },
    {
        "city": "NTPC",
        "name_zh": "林口",
        "name_en": "Linkou",
        "operator": "cyc",
        "mode": "json",
        "web": "https://lkcsc.cyc.org.tw",
        "endpoint": "https://lkcsc.cyc.org.tw/api",
    },
    {
        "city": "Taoyuan",
        "name_zh": "桃園",
        "name_en": "Taoyuan",
        "operator": "cyc",
        "mode": "json",
        "web": "https://tycsc.cyc.org.tw",
        "endpoint": "https://tycsc.cyc.org.tw/api",
    },
    {
        "city": "Taoyuan",
        "name_zh": "中壢",
        "name_en": "Zhongli",
        "operator": "cyc",
        "mode": "json",
        "web": "https://zlcsc.cyc.org.tw",
        "endpoint": "https://zlcsc.cyc.org.tw/api",
    },
    {
        "city": "Taoyuan",
        "name_zh": "八德",
        "name_en": "Bade",
        "operator": "cyc",
        "mode": "json",
        "web": "https://bdcsc.cyc.org.tw",
        "endpoint": "https://bdcsc.cyc.org.tw/api",
    },
    {
        "city": "Hsinchu",
        "name_zh": "竹光",
        "name_en": "Zhuguang",
        "operator": "cyc",
        "mode": "json",
        "web": "https://zgcsc.cyc.org.tw",
        "endpoint": "https://zgcsc.cyc.org.tw/api",
    },
    {
        "city": "Taichung",
        "name_zh": "朝馬",
        "name_en": "Chaoma",
        "operator": "cyc",
        "mode": "json",
        "web": "https://cmcsc.cyc.org.tw",
        "endpoint": "https://cmcsc.cyc.org.tw/api",
    },
    # 北屯有冰宮
    {
        "city": "Taichung",
        "name_zh": "北屯",
        "name_en": "Beitun",
        "operator": "cyc",
        "mode": "json",
        "web": "https://btcsc.cyc.org.tw",
        "endpoint": "https://btcsc.cyc.org.tw/api",
    },
    
    # 全越運動 xports: API end-point:
    # https://webapi.teamxports.com/api/web/carosel/get-court-cat-people-flow?siteId={site_index}
    # site_index = {"信義": 4, "三峽": 7, "鶯歌": 6, "台北大學": 1}
    # response = {"returnCode":"200","returnMsg":"成功","data":[
    #               {"courtCatTitle":"游泳池","upperBound":300,"currCapacity":107,"capacityControl":1},
    #               {"courtCatTitle":"體適能中心","upperBound":60,"currCapacity":16,"capacityControl":1}]}
    {
        "city": "TPE",
        "name_zh": "信義",
        "name_en": "Xinyi",
        "operator": "xports",
        "mode": "json",
        "web": "https://xysc.teamxports.com",
        "endpoint": "https://webapi.teamxports.com/api/web/carosel/get-court-cat-people-flow?siteId=4",
    },
    {
        "city": "NTPC",
        "name_zh": "三峽",
        "name_en": "Sanxia",
        "operator": "xports",
        "mode": "json",
        "web": "https://sxsc.teamxports.com",
        "endpoint": "https://webapi.teamxports.com/api/web/carosel/get-court-cat-people-flow?siteId=7",
    },
    {
        "city": "NTPC",
        "name_zh": "鶯歌",
        "name_en": "Yingge",
        "operator": "xports",
        "mode": "json",
        "web": "https://ygsc.teamxports.com",
        "endpoint": "https://webapi.teamxports.com/api/web/carosel/get-court-cat-people-flow?siteId=6",
    },
    {
        "city": "NTPC",
        "name_zh": "台北大學",
        "name_en": "NTPU",
        "operator": "xports",
        "mode": "json",
        "web": "https://www.tusc.tw",
        "endpoint": "https://webapi.teamxports.com/api/web/carosel/get-court-cat-people-flow?siteId=1",
    },
    
    # 建中工程 cce: 不統一的網站建製
    # 北投: html-regex
    # Sources:
    # 健身房<span class="flow_number">20<small>人</small></span><small>容流</small><span>60人
    # 游泳池<span class="flow_number">286<small>人</small></span><small>容流</small><span>200人
    # pattern = r'([\u4e00-\u9fa5]+)<span class="flow_number">(\d+)<small>人</small></span><small>容流</small><span>(\d+)人'
    {
        "city": "TPE",
        "name_zh": "北投",
        "name_en": "Beitou",
        "operator": "cce",
        "mode": "html",
        "web": "https://www.btsport.org.tw/zh-TW/onsitenum",
        "pattern": r'(?P<cat>[\u4e00-\u9fa5]+)<span class="flow_number">(?P<cur>\d+)<small>人</small></span><small>容流</small><span>(?P<cap>\d+)人',
    },
    # 中和: API endpoint:
    # gym: https://zhs.mraytec.com/state/fitness
    # response = {"value":30}
    # pool: https://zhs.mraytec.com/state/pool
    # response = {"value":48}
    # mraytec 只回 {"value": N}，無容留人數需自行查官網後填入
    {
        "city": "NTPC",
        "name_zh": "中和",
        "name_en": "Zhonghe",
        "operator": "cce",
        "mode": "json",
        "web": "https://www.zhsc.com.tw",
        "endpoint": {"gym": "https://zhs.mraytec.com/state/fitness", "swim": "https://zhs.mraytec.com/state/pool"},
        "CAPACITY": {"gym": 120, "swim": 300},
    },
    
    # 頂尖運動: plain-text
    # 新莊 API end-point:
    # https://cmc.idv.tw/17fit/data/counter_296.txt
    # response = 健身房人數, 游泳池人數 text
    # 新莊官網健身房人數寫死為 API 人數 + 30 人
    {
        "city": "NTPC",
        "name_zh": "新莊",
        "name_en": "Xinzhuang",
        "operator": "elite",
        "mode": "text",  # 回傳的是 text ， 分到 json 的話 response.json() 會報錯：回傳的資料無法解析為 JSON，分到 html 的話會因為沒有 pattern 報錯 KeyError: 'pattern'
        "web": "https://www.xzsports.com.tw",
        "endpoint": "https://cmc.idv.tw/17fit/data/counter_296.txt",
        "CAPACITY": {"gym": 150, "swim": 250},
        "offset": {"gym": 30}
    },
    # 樹林 API end-point:
    # https://www.ntcslsports.com.tw/parser.php
    # response = 游泳池人數, 健身房人數 text
    {
        "city": "NTPC",
        "name_zh": "樹林",
        "name_en": "Shulin",
        "operator": "elite",
        "mode": "text",
        "web": "https://www.ntcslsports.com.tw",
        "endpoint": "https://www.ntcslsports.com.tw/parser.php",
        "CAPACITY": {"gym": 90, "swim": 250}
    },
    
    # 遠東鐵櫃 Far-East_Steel: API endpoint:
    # http://www.scsports.com.tw/proxy1.php
    # response = {"swim":["0","280","0"],"gym":["0","120","0"],"ice":["0","250","0"]}
    {
        "city": "NTPC",
        "name_zh": "三重",
        "name_en": "Sanchong",
        "operator": "far_east_steel",
        "mode": "json",
        "web": "https://www.scsports.com.tw",
        "endpoint": "http://www.scsports.com.tw/proxy1.php",
    },
    # 土城原救國團，已換約遠東鐵櫃; 另有冰宮人數
    {
        "city": "NTPC",
        "name_zh": "土城",
        "name_en": "Tucheng",
        "operator": "far_east_steel",
        "mode": "json",
        "web": "https://www.tcsports.com.tw",
        "endpoint": "http://www.tcsports.com.tw/proxy1.php",
    },
    
    # ymca
    # 士林: html-regex
    # Sources:
    # 健身房<span class="number">34</span> 人 / 容納100人
    # 游泳池<span class="number">75</span> 人 / 容納200人
    # pattern = r'([中文+])<span\s*class="number">(\d+)</span>\s*人\s*/\s*容納(\d+)人'
    {
        "city": "TPE",
        "name_zh": "士林",
        "name_en": "Shilin",
        "operator": "ymca",
        "mode": "html",
        "web": "https://www.slsc-taipei.org",
        "pattern": r'(?P<cat>[\u4e00-\u9fa5]+)<span\s*class="number">(?P<cur>\d+)</span>\s*人\s*/\s*容納(?P<cap>\d+)人',
    },
    # 新生: API endpoint:
    # xinsheng-gym: https://tmp.ezstore.com.tw/ezrwd/xccs/poolcount.php?site=xinsheng-gym
    # response = {"ok":true,"count":17,"limit":70,"raw":"17,70,0"}
    # xinsheng-pool: https://tmp.ezstore.com.tw/ezrwd/xccs/poolcount.php?site=xinsheng-pool
    # response = {"ok":true,"count":15,"limit":120,"raw":"15,120,0"}
    # bihu-pool: https://tmp.ezstore.com.tw/ezrwd/xccs/poolcount.php?site=bihu-pool
    # response = {"ok":true,"count":0,"limit":80,"raw":"0,80,0"}
    {
        "city": "TPE",
        "name_zh": "新生",
        "name_en": "Xinsheng",
        "operator": "ymca",
        "mode": "json",
        "web": "https://www.ymca-xssc.org/?lang=tw",
        "endpoint": {"gym": "https://tmp.ezstore.com.tw/ezrwd/xccs/poolcount.php?site=xinsheng-gym", "swim": "https://tmp.ezstore.com.tw/ezrwd/xccs/poolcount.php?site=xinsheng-pool"}
    },
]


print("，".join(s["name_zh"] for s in SITES))
print(len(SITES))