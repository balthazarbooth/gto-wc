#!/usr/bin/env python3
"""WC2026 GTO prediction engine. Outputs predictions.json for the HTML frontend."""

import json, math, urllib.request

# ============ DATA ============

TEAMS = {
    "MEX": {"name": "Mexico",         "flag": "🇲🇽", "r": 1685},
    "KOR": {"name": "S. Korea",       "flag": "🇰🇷", "r": 1620},
    "CZE": {"name": "Czechia",        "flag": "🇨🇿", "r": 1635},
    "RSA": {"name": "S. Africa",      "flag": "🇿🇦", "r": 1545},
    "SUI": {"name": "Switzerland",    "flag": "🇨🇭", "r": 1700},
    "CAN": {"name": "Canada",         "flag": "🇨🇦", "r": 1675},
    "BIH": {"name": "Bosnia",         "flag": "🇧🇦", "r": 1585},
    "QAT": {"name": "Qatar",          "flag": "🇶🇦", "r": 1490},
    "BRA": {"name": "Brazil",         "flag": "🇧🇷", "r": 1955},
    "MAR": {"name": "Morocco",        "flag": "🇲🇦", "r": 1820},
    "SCO": {"name": "Scotland",       "flag": "🏴\U000e0067\U000e0062\U000e0073\U000e0063\U000e0074\U000e007f", "r": 1635},
    "HAI": {"name": "Haiti",          "flag": "🇭🇹", "r": 1470},
    "USA": {"name": "USA",            "flag": "🇺🇸", "r": 1715},
    "AUS": {"name": "Australia",      "flag": "🇦🇺", "r": 1645},
    "TUR": {"name": "Turkey",         "flag": "🇹🇷", "r": 1695},
    "PAR": {"name": "Paraguay",       "flag": "🇵🇾", "r": 1635},
    "GER": {"name": "Germany",        "flag": "🇩🇪", "r": 1915},
    "ECU": {"name": "Ecuador",        "flag": "🇪🇨", "r": 1745},
    "CIV": {"name": "Côte d'Ivoire",  "flag": "🇨🇮", "r": 1700},
    "CUW": {"name": "Curaçao",        "flag": "🇨🇼", "r": 1440},
    "NED": {"name": "Netherlands",    "flag": "🇳🇱", "r": 1860},
    "JPN": {"name": "Japan",          "flag": "🇯🇵", "r": 1785},
    "SWE": {"name": "Sweden",         "flag": "🇸🇪", "r": 1735},
    "TUN": {"name": "Tunisia",        "flag": "🇹🇳", "r": 1640},
    "BEL": {"name": "Belgium",        "flag": "🇧🇪", "r": 1815},
    "EGY": {"name": "Egypt",          "flag": "🇪🇬", "r": 1660},
    "IRN": {"name": "Iran",           "flag": "🇮🇷", "r": 1685},
    "NZL": {"name": "New Zealand",    "flag": "🇳🇿", "r": 1505},
    "ESP": {"name": "Spain",          "flag": "🇪🇸", "r": 2000},
    "URU": {"name": "Uruguay",        "flag": "🇺🇾", "r": 1875},
    "KSA": {"name": "Saudi Arabia",   "flag": "🇸🇦", "r": 1580},
    "CPV": {"name": "Cabo Verde",     "flag": "🇨🇻", "r": 1545},
    "FRA": {"name": "France",         "flag": "🇫🇷", "r": 1975},
    "NOR": {"name": "Norway",         "flag": "🇳🇴", "r": 1830},
    "SEN": {"name": "Senegal",        "flag": "🇸🇳", "r": 1795},
    "IRQ": {"name": "Iraq",           "flag": "🇮🇶", "r": 1545},
    "ARG": {"name": "Argentina",      "flag": "🇦🇷", "r": 1985},
    "AUT": {"name": "Austria",        "flag": "🇦🇹", "r": 1745},
    "ALG": {"name": "Algeria",        "flag": "🇩🇿", "r": 1700},
    "JOR": {"name": "Jordan",         "flag": "🇯🇴", "r": 1560},
    "POR": {"name": "Portugal",       "flag": "🇵🇹", "r": 1925},
    "COL": {"name": "Colombia",       "flag": "🇨🇴", "r": 1855},
    "COD": {"name": "DR Congo",       "flag": "🇨🇩", "r": 1665},
    "UZB": {"name": "Uzbekistan",     "flag": "🇺🇿", "r": 1620},
    "ENG": {"name": "England",        "flag": "🏴\U000e0067\U000e0062\U000e0065\U000e006e\U000e0067\U000e007f", "r": 1935},
    "CRO": {"name": "Croatia",        "flag": "🇭🇷", "r": 1820},
    "GHA": {"name": "Ghana",          "flag": "🇬🇭", "r": 1665},
    "PAN": {"name": "Panama",         "flag": "🇵🇦", "r": 1575},
}

OPP = {
    "SRB": 1730, "SLV": 1440, "TTO": 1380, "KOS": 1550, "GUA": 1430, "JAM": 1540,
    "IRL": 1640, "MAD": 1350, "BOL": 1450, "PER": 1610, "VEN": 1560, "FIN": 1560,
    "ARU": 1200, "ICE": 1560, "RUS": 1650, "CRC": 1540, "GAM": 1440, "MLI": 1520,
    "HON": 1460, "WAL": 1570, "DEN": 1730, "BER": 1200, "NIR": 1490, "CHI": 1650,
    "NGA": 1690, "NCA": 1300,
}

HOST = {"USA", "MEX", "CAN"}

PRE = [
    ("POR","USA",2,0),("AUT","KOR",1,0),("CIV","KOR",4,0),
    ("RSA","PAN",1,1),("PAN","RSA",2,1),("TUN","QAT",3,0),
    ("MEX","GHA",2,0),("MEX","AUS",1,0),("GER","FIN",4,0),
    ("USA","SEN",3,2),("BRA","PAN",6,2),("CZE","KOS",2,1),("EGY","RUS",1,0),
    ("MEX","SRB",5,1),("CIV","FRA",2,1),("ESP","IRQ",1,1),("CZE","GUA",3,1),
    ("GER","USA",2,1),("BRA","EGY",2,1),("MAR","MAD",4,0),("MAR","NOR",1,1),
    ("SCO","BOL",4,0),("HAI","NZL",4,0),("PER","HAI",2,1),("TUR","VEN",2,1),
    ("PAR","NCA",4,0),("ECU","GUA",3,0),("ECU","KSA",2,1),("CUW","ARU",4,0),
    ("ALG","NED",1,0),("NED","UZB",2,1),("JPN","ICE",1,0),("NOR","SWE",3,1),
    ("AUT","TUN",1,0),("BEL","TUN",5,0),("BEL","CRO",2,0),("BEL","MEX",1,1),
    ("IRN","CRC",5,0),("IRN","GAM",3,1),("IRN","MLI",2,0),("ESP","PER",3,1),
    ("SEN","KSA",0,0),("CPV","BER",3,0),("FRA","NIR",3,1),("IRQ","VEN",0,2),
    ("ARG","HON",2,0),("ARG","ICE",3,0),("AUT","GUA",0,0),("POR","CHI",2,1),
    ("POR","NGA",2,1),("COL","CRC",3,1),("COL","JOR",2,0),("COD","DEN",0,0),
    ("ENG","NZL",1,0),("ENG","CRC",3,0),("GHA","WAL",1,1),("KOR","SLV",1,0),
    ("KOR","TTO",5,0),("SUI","JOR",4,1),("AUS","SUI",1,1),("CAN","UZB",2,0),
    ("CAN","IRL",1,1),("BIH","PAN",1,1),("IRL","QAT",1,0),("QAT","SLV",0,0),
    ("RSA","JAM",1,1),
]

MATCHES = [
    {"g":"A","md":1,"d":"Jun 11","h":"MEX","a":"RSA","p":1,"hg":2,"ag":0},
    {"g":"A","md":1,"d":"Jun 11","h":"KOR","a":"CZE","p":1,"hg":2,"ag":1},
    {"g":"A","md":2,"d":"Jun 18","h":"CZE","a":"RSA","p":1,"hg":1,"ag":1},
    {"g":"A","md":2,"d":"Jun 18","h":"MEX","a":"KOR","p":1,"hg":1,"ag":0},
    {"g":"A","md":3,"d":"Jun 24","h":"CZE","a":"MEX","p":0},{"g":"A","md":3,"d":"Jun 24","h":"RSA","a":"KOR","p":0},
    {"g":"B","md":1,"d":"Jun 12","h":"CAN","a":"BIH","p":1,"hg":1,"ag":1},
    {"g":"B","md":1,"d":"Jun 13","h":"QAT","a":"SUI","p":1,"hg":1,"ag":1},
    {"g":"B","md":2,"d":"Jun 18","h":"SUI","a":"BIH","p":1,"hg":4,"ag":1},
    {"g":"B","md":2,"d":"Jun 18","h":"CAN","a":"QAT","p":1,"hg":6,"ag":0},
    {"g":"B","md":3,"d":"Jun 24","h":"SUI","a":"CAN","p":0},{"g":"B","md":3,"d":"Jun 24","h":"BIH","a":"QAT","p":0},
    {"g":"C","md":1,"d":"Jun 13","h":"BRA","a":"MAR","p":1,"hg":1,"ag":1},
    {"g":"C","md":1,"d":"Jun 13","h":"SCO","a":"HAI","p":1,"hg":1,"ag":0},
    {"g":"C","md":2,"d":"Jun 19","h":"SCO","a":"MAR","p":1,"hg":0,"ag":1},
    {"g":"C","md":2,"d":"Jun 19","h":"BRA","a":"HAI","p":1,"hg":3,"ag":0},
    {"g":"C","md":3,"d":"Jun 24","h":"SCO","a":"BRA","p":0},{"g":"C","md":3,"d":"Jun 24","h":"MAR","a":"HAI","p":0},
    {"g":"D","md":1,"d":"Jun 12","h":"USA","a":"PAR","p":1,"hg":4,"ag":1},
    {"g":"D","md":1,"d":"Jun 13","h":"AUS","a":"TUR","p":1,"hg":2,"ag":0},
    {"g":"D","md":2,"d":"Jun 19","h":"USA","a":"AUS","p":1,"hg":2,"ag":0},
    {"g":"D","md":2,"d":"Jun 19","h":"TUR","a":"PAR","p":1,"hg":0,"ag":1},
    {"g":"D","md":3,"d":"Jun 25","h":"TUR","a":"USA","p":0},{"g":"D","md":3,"d":"Jun 25","h":"PAR","a":"AUS","p":0},
    {"g":"E","md":1,"d":"Jun 14","h":"GER","a":"CUW","p":1,"hg":7,"ag":1},
    {"g":"E","md":1,"d":"Jun 14","h":"CIV","a":"ECU","p":1,"hg":1,"ag":0},
    {"g":"E","md":2,"d":"Jun 20","h":"GER","a":"CIV","p":1,"hg":2,"ag":1},
    {"g":"E","md":2,"d":"Jun 20","h":"ECU","a":"CUW","p":1,"hg":0,"ag":0},
    {"g":"E","md":3,"d":"Jun 25","h":"ECU","a":"GER","p":0},{"g":"E","md":3,"d":"Jun 25","h":"CUW","a":"CIV","p":0},
    {"g":"F","md":1,"d":"Jun 14","h":"NED","a":"JPN","p":1,"hg":2,"ag":2},
    {"g":"F","md":1,"d":"Jun 14","h":"SWE","a":"TUN","p":1,"hg":5,"ag":1},
    {"g":"F","md":2,"d":"Jun 20","h":"NED","a":"SWE","p":1,"hg":5,"ag":1},
    {"g":"F","md":2,"d":"Jun 20","h":"TUN","a":"JPN","p":1,"hg":0,"ag":4},
    {"g":"F","md":3,"d":"Jun 25","h":"JPN","a":"SWE","p":0},{"g":"F","md":3,"d":"Jun 25","h":"TUN","a":"NED","p":0},
    {"g":"G","md":1,"d":"Jun 15","h":"BEL","a":"EGY","p":1,"hg":1,"ag":1},
    {"g":"G","md":1,"d":"Jun 15","h":"IRN","a":"NZL","p":1,"hg":2,"ag":2},
    {"g":"G","md":2,"d":"Jun 21","h":"BEL","a":"IRN","p":1,"hg":0,"ag":0},
    {"g":"G","md":2,"d":"Jun 21","h":"NZL","a":"EGY","p":1,"hg":1,"ag":3},
    {"g":"G","md":3,"d":"Jun 26","h":"EGY","a":"IRN","p":0},{"g":"G","md":3,"d":"Jun 26","h":"NZL","a":"BEL","p":0},
    {"g":"H","md":1,"d":"Jun 15","h":"ESP","a":"CPV","p":1,"hg":0,"ag":0},
    {"g":"H","md":1,"d":"Jun 15","h":"KSA","a":"URU","p":1,"hg":1,"ag":1},
    {"g":"H","md":2,"d":"Jun 21","h":"ESP","a":"KSA","p":1,"hg":4,"ag":0},
    {"g":"H","md":2,"d":"Jun 21","h":"URU","a":"CPV","p":1,"hg":2,"ag":2},
    {"g":"H","md":3,"d":"Jun 26","h":"CPV","a":"KSA","p":0},{"g":"H","md":3,"d":"Jun 26","h":"URU","a":"ESP","p":0},
    {"g":"I","md":1,"d":"Jun 16","h":"FRA","a":"SEN","p":1,"hg":3,"ag":1},
    {"g":"I","md":1,"d":"Jun 16","h":"NOR","a":"IRQ","p":1,"hg":4,"ag":1},
    {"g":"I","md":2,"d":"Jun 22","h":"FRA","a":"IRQ","p":0},{"g":"I","md":2,"d":"Jun 22","h":"NOR","a":"SEN","p":0},
    {"g":"I","md":3,"d":"Jun 26","h":"NOR","a":"FRA","p":0},{"g":"I","md":3,"d":"Jun 26","h":"SEN","a":"IRQ","p":0},
    {"g":"J","md":1,"d":"Jun 16","h":"ARG","a":"ALG","p":1,"hg":3,"ag":0},
    {"g":"J","md":1,"d":"Jun 17","h":"AUT","a":"JOR","p":1,"hg":3,"ag":1},
    {"g":"J","md":2,"d":"Jun 22","h":"ARG","a":"AUT","p":0},{"g":"J","md":2,"d":"Jun 22","h":"JOR","a":"ALG","p":0},
    {"g":"J","md":3,"d":"Jun 27","h":"ALG","a":"AUT","p":0},{"g":"J","md":3,"d":"Jun 27","h":"JOR","a":"ARG","p":0},
    {"g":"K","md":1,"d":"Jun 17","h":"POR","a":"COD","p":1,"hg":1,"ag":1},
    {"g":"K","md":1,"d":"Jun 17","h":"COL","a":"UZB","p":1,"hg":3,"ag":1},
    {"g":"K","md":2,"d":"Jun 23","h":"POR","a":"UZB","p":0},{"g":"K","md":2,"d":"Jun 23","h":"COL","a":"COD","p":0},
    {"g":"K","md":3,"d":"Jun 27","h":"COL","a":"POR","p":0},{"g":"K","md":3,"d":"Jun 27","h":"COD","a":"UZB","p":0},
    {"g":"L","md":1,"d":"Jun 17","h":"ENG","a":"CRO","p":1,"hg":4,"ag":2},
    {"g":"L","md":1,"d":"Jun 17","h":"GHA","a":"PAN","p":1,"hg":1,"ag":0},
    {"g":"L","md":2,"d":"Jun 23","h":"ENG","a":"GHA","p":0},{"g":"L","md":2,"d":"Jun 23","h":"PAN","a":"CRO","p":0},
    {"g":"L","md":3,"d":"Jun 27","h":"PAN","a":"ENG","p":0},{"g":"L","md":3,"d":"Jun 27","h":"CRO","a":"GHA","p":0},
]

NAMES = {
    "Mexico":"MEX","South Korea":"KOR","Korea Republic":"KOR","Czechia":"CZE","Czech Republic":"CZE",
    "South Africa":"RSA","Switzerland":"SUI","Canada":"CAN",
    "Bosnia and Herzegovina":"BIH","Bosnia-Herzegovina":"BIH","Bosnia & Herzegovina":"BIH",
    "Qatar":"QAT","Brazil":"BRA","Morocco":"MAR","Scotland":"SCO","Haiti":"HAI",
    "United States":"USA","USA":"USA","United States of America":"USA",
    "Australia":"AUS","Turkey":"TUR","Türkiye":"TUR","Paraguay":"PAR","Germany":"GER","Ecuador":"ECU",
    "Côte d'Ivoire":"CIV","Cote d'Ivoire":"CIV","Côte D'Ivoire":"CIV","Ivory Coast":"CIV",
    "Curaçao":"CUW","Curacao":"CUW",
    "Netherlands":"NED","Japan":"JPN","Sweden":"SWE","Tunisia":"TUN",
    "Belgium":"BEL","Egypt":"EGY","Iran":"IRN","Iran (Islamic Republic of)":"IRN",
    "New Zealand":"NZL","Spain":"ESP","Uruguay":"URU",
    "Saudi Arabia":"KSA","Cabo Verde":"CPV","Cape Verde":"CPV","Cape Verde Islands":"CPV",
    "France":"FRA","Norway":"NOR","Senegal":"SEN","Iraq":"IRQ",
    "Argentina":"ARG","Austria":"AUT","Algeria":"ALG","Jordan":"JOR","Portugal":"POR","Colombia":"COL",
    "DR Congo":"COD","Congo DR":"COD","Democratic Republic of Congo":"COD","Congo, DR":"COD","Congo, Democratic Republic of":"COD",
    "Uzbekistan":"UZB","England":"ENG","Croatia":"CRO","Ghana":"GHA","Panama":"PAN",
}

WORKER = "https://rapid-surf-b1b2.balthazarbooth01.workers.dev"


# ============ ELO ENGINE ============

ADJ = {}

def base_r(tid):
    if tid in TEAMS: return TEAMS[tid]["r"]
    return OPP.get(tid, 1500)

def form(tid):
    a = ADJ.get(tid, [])
    return sum(a[-5:])

def elo(tid):
    return TEAMS[tid]["r"] + form(tid) + (60 if tid in HOST else 0)

def init_elo():
    ADJ.clear()
    for tid in TEAMS:
        ADJ[tid] = []
    for a, b, ga, gb in PRE:
        r_a = base_r(a) + form(a)
        r_b = base_r(b) + form(b)
        e_a = 1 / (1 + 10 ** ((r_b - r_a) / 400))
        s_a = 1 if ga > gb else (0 if ga < gb else 0.5)
        if a in TEAMS: ADJ[a].append(10 * (s_a - e_a))
        if b in TEAMS: ADJ[b].append(10 * ((1 - s_a) - (1 - e_a)))

def update_elo(m):
    r_h, r_a = elo(m["h"]), elo(m["a"])
    e_h = 1 / (1 + 10 ** ((r_a - r_h) / 400))
    s_h = 1 if m["hg"] > m["ag"] else (0 if m["hg"] < m["ag"] else 0.5)
    ADJ[m["h"]].append(60 * (s_h - e_h))
    ADJ[m["a"]].append(60 * ((1 - s_h) - (1 - e_h)))


# ============ STRATEGY ============

def win_probs(h, a, suppress_draw):
    dr = elo(h) - elo(a)
    we = 1 / (1 + 10 ** (-dr / 400))
    p_d = 0.38 * math.exp(-(dr / 450) ** 2)
    if suppress_draw:
        p_d *= 0.65
    p_d = min(max(p_d, 0.05), 0.48)
    p_h = we - 0.5 * p_d
    p_a = (1 - we) - 0.5 * p_d
    p_h = max(p_h, 0.02)
    p_a = max(p_a, 0.02)
    s = p_h + p_a + p_d
    return {"h": p_h / s, "d": p_d / s, "a": p_a / s, "dr": dr}

def tier_score(gap):
    if gap > 230: return (3, 0)
    if gap > 110: return (3, 1)
    return (2, 1)

def core_pick(m):
    p = win_probs(m["h"], m["a"], True)
    fav_home = p["h"] >= p["a"]
    close = abs(p["h"] - p["a"]) < 0.15
    modal = "D" if (p["d"] >= p["h"] and p["d"] >= p["a"]) else ("H" if p["h"] > p["a"] else "A")
    res = modal
    upset = False
    if modal == "D":
        res = "H" if fav_home else "A"
    elif close and max(p["h"], p["a"]) < 0.66:
        res = "A" if fav_home else "H"
        upset = True
    win = res == "H"
    w, l = (2, 1) if upset else tier_score(abs(p["dr"]))
    return {"res": res, "hg": w if win else l, "ag": l if win else w, "tag": "upset" if upset else "elo"}

def draw_override(m):
    p = win_probs(m["h"], m["a"], False)
    return max(p["h"], p["a"]) < 0.52 and abs(p["dr"]) >= 130


def predict(m):
    if draw_override(m):
        return {"res": "D", "hg": 1, "ag": 1, "tag": "draw"}
    return core_pick(m)


# ============ LIVE DATA ============

def fetch_live():
    try:
        req = urllib.request.Request(WORKER, headers={"User-Agent": "GTO-WC/1.0"})
        with urllib.request.urlopen(req, timeout=10) as resp:
            return json.loads(resp.read())
    except Exception as e:
        print(f"Warning: could not fetch live data: {e}")
        return None

def apply_live(data):
    if not data:
        return []
    for am in data.get("matches", []):
        h_k = NAMES.get(am.get("home"))
        a_k = NAMES.get(am.get("away"))
        if not h_k or not a_k:
            continue
        e, flip = find_match(h_k, a_k)
        if not e or am.get("status") != "FINISHED" or am.get("hg") is None:
            continue
        e["p"] = 1
        e["hg"] = am["ag"] if flip else am["hg"]
        e["ag"] = am["hg"] if flip else am["ag"]
    return data.get("odds", [])

def find_match(h, a):
    for m in MATCHES:
        if m["h"] == h and m["a"] == a:
            return m, False
        if m["h"] == a and m["a"] == h:
            return m, True
    return None, False


# ============ DRAW ALARM ============

def amer_to_prob(v):
    return 100 / (v + 100) if v > 0 else -v / (-v + 100)

def amer_to_dec(v):
    return 1 + v / 100 if v > 0 else 1 + 100 / (-v)

def match_odds(live_odds, h, a):
    for o in live_odds:
        oh = NAMES.get(o.get("home"))
        oa = NAMES.get(o.get("away"))
        if (oh == h and oa == a) or (oh == a and oa == h):
            return o
    return None

def odds_draw_override(live_odds, h, a):
    o = match_odds(live_odds, h, a)
    if not o:
        return None
    h_dec = amer_to_dec(o["homeOdds"])
    a_dec = amer_to_dec(o["awayOdds"])
    d_dec = amer_to_dec(o["drawOdds"])
    u25 = o.get("u25Dec", 99)
    # ponytail: two independent draw signals from the slides
    evenly_matched = h_dec < 3.0 and a_dec < 3.0
    low_scoring = u25 <= 1.65
    draw_short = d_dec < 3.40
    if draw_short and (evenly_matched or low_scoring):
        return {"res": "D", "hg": 1, "ag": 1, "tag": "odds draw"}
    return None

def build_alarm(live_odds, predictions):
    alarm = []
    for entry in predictions:
        m, pick = entry["match"], entry["prediction"]
        if m["played"] or pick["res"] == "D":
            continue
        o = match_odds(live_odds, m["home"], m["away"])
        if not o:
            continue
        d_prob = amer_to_prob(o["drawOdds"])
        if d_prob < 0.33:
            continue
        alarm.append({
            "home": m["home"], "away": m["away"],
            "group": m["group"], "date": m["date"],
            "prediction": pick,
            "draw_prob": round(d_prob, 3),
            "draw_dec": round(amer_to_dec(o["drawOdds"]), 2),
        })
    return alarm


# ============ MAIN ============

def run():
    init_elo()

    sorted_matches = sorted(MATCHES, key=lambda m: (
        "2026-" + m["d"].replace("Jun ", "06-").zfill(5),
        m["g"]
    ))

    live_odds = apply_live(fetch_live())

    pts = res_count = exact = played = 0
    predictions = []

    for m in sorted_matches:
        pick = predict(m)
        if not m["p"] and pick["res"] != "D":
            odraw = odds_draw_override(live_odds, m["h"], m["a"])
            if odraw:
                pick = odraw
        entry = {
            "match": {
                "group": m["g"], "matchday": m["md"], "date": m["d"],
                "home": m["h"], "away": m["a"],
                "played": bool(m["p"]),
            },
            "prediction": pick,
            "points": None,
        }
        if m["p"]:
            entry["match"]["home_goals"] = m["hg"]
            entry["match"]["away_goals"] = m["ag"]
            played += 1
            actual = "H" if m["hg"] > m["ag"] else ("A" if m["hg"] < m["ag"] else "D")
            r_ok = pick["res"] == actual
            s_ok = pick["hg"] == m["hg"] and pick["ag"] == m["ag"]
            p = 6 if s_ok else (3 if r_ok else 0)
            entry["points"] = p
            pts += p
            if r_ok: res_count += 1
            if s_ok: exact += 1
            update_elo(m)

        predictions.append(entry)

    alarm = build_alarm(live_odds, predictions)

    teams_out = {k: {"name": v["name"], "flag": v["flag"]} for k, v in TEAMS.items()}

    output = {
        "teams": teams_out,
        "matches": predictions,
        "totals": {
            "points": pts,
            "played": played,
            "results": res_count,
            "exact": exact,
        },
        "alarm": alarm,
        "names": NAMES,
        "worker": WORKER,
    }

    with open("predictions.json", "w", encoding="utf-8") as f:
        json.dump(output, f, ensure_ascii=False, indent=2)

    pct = round(100 * res_count / played) if played else 0
    print(f"predictions.json written — {pts} pts, {res_count}/{played} results ({pct}%), {exact} exact")


if __name__ == "__main__":
    run()
