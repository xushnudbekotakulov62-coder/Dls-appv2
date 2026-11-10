"""FLEX DLS Auto Bot - engine (UI'siz). Xizmat (service) ichida ishlaydi."""
import json, os, time, random

try:
    from android.storage import app_storage_path
    BASE = app_storage_path()
except Exception:
    BASE = os.path.join(os.path.expanduser("~"), ".flexbot")
os.makedirs(BASE, exist_ok=True)
CFG = os.path.join(BASE, "config.json")
STATUS = os.path.join(BASE, "status.json")
LOGF = os.path.join(BASE, "log.txt")
STOP = os.path.join(BASE, "stop.flag")

DEFAULT = dict(
    user="", password="",
    adb_host="127.0.0.1", adb_port=5555,
    target_coins=100000, target_dp=6000, max_matches=500, max_minutes=480,
    est_coins=207, est_dp=146,          # bitta sikldan taxminiy daromad (skrinshotdan)
    match_seconds=420, ad_wait=35,
    do_best=True, do_play=True, do_claim=True, do_ads=True,
    setup_done=False, tg_token="", tg_chat="", api_key="", ai_model="claude-haiku-5-5",
    screen_w=2340, screen_h=1080,
)

def load_cfg():
    c = dict(DEFAULT)
    try:
        c.update(json.load(open(CFG)))
    except Exception:
        pass
    return c

def save_cfg(c):
    json.dump(c, open(CFG, "w"))

def log(msg):
    line = time.strftime("%H:%M:%S ") + msg
    with open(LOGF, "a") as f:
        f.write(line + "\n")

def set_status(**kw):
    s = {}
    try:
        s = json.load(open(STATUS))
    except Exception:
        pass
    s.update(kw)
    json.dump(s, open(STATUS, "w"))

def telegram(cfg, text):
    if not (cfg["tg_token"] and cfg["tg_chat"]):
        return
    try:
        import requests
        requests.post("https://api.telegram.org/bot%s/sendMessage" % cfg["tg_token"],
                      data={"chat_id": cfg["tg_chat"], "text": text}, timeout=15)
    except Exception as e:
        log("Telegram xato: %s" % e)

# DLS skrinshotlaridagi koordinatalar (2340x1080, gorizontal)
P = dict(
    play_now=(640, 183), team=(340, 1020), best_team=(1697, 190), back=(170, 48),
    play=(2040, 1020), cont=(2075, 1020),
    claims=[(836, 890), (1198, 890), (1560, 890), (1922, 890)],
    joy=(435, 755), shoot_b=(1820, 925), pass_a=(2100, 925),
)

class Bot:
    def __init__(self, cfg):
        self.c = cfg
        self.dev = None
        self.sx = cfg["screen_w"] / 2340.0
        self.sy = cfg["screen_h"] / 1080.0

    def connect(self):
        from adb_shell.adb_device import AdbDeviceTcp
        from adb_shell.auth.keygen import keygen
        from adb_shell.auth.sign_pythonrsa import PythonRSASigner
        key = os.path.join(BASE, "adbkey")
        if not os.path.exists(key):
            keygen(key)
        signer = PythonRSASigner(open(key + ".pub").read(), open(key).read())
        self.dev = AdbDeviceTcp(self.c["adb_host"], int(self.c["adb_port"]),
                                default_transport_timeout_s=10.0)
        self.dev.connect(rsa_keys=[signer], auth_timeout_s=30)
        log("ADB ulandi")

    def sh(self, cmd):
        return self.dev.shell(cmd)

    def tap(self, p):
        x = int(p[0] * self.sx) + random.randint(-6, 6)
        y = int(p[1] * self.sy) + random.randint(-6, 6)
        self.sh("input tap %d %d" % (x, y))

    def key(self, code):
        self.sh("input keyevent %d" % code)

    def swipe(self, a, b, ms=400):
        self.sh("input swipe %d %d %d %d %d" % (a[0]*self.sx, a[1]*self.sy, b[0]*self.sx, b[1]*self.sy, ms))

    def wait(self, s):
        end = time.time() + s
        while time.time() < end:
            if os.path.exists(STOP):
                raise KeyboardInterrupt
            time.sleep(0.5)

    # --- AI (Claude ko'rish) ---
    def shot_b64(self):
        import io, base64
        from PIL import Image
        try:
            raw = self.dev.exec_out("screencap -p", decode=False)
        except Exception:
            raw = self.dev.shell("screencap -p", decode=False).replace(b"\r\n", b"\n")
        im = Image.open(io.BytesIO(raw)).convert("RGB").resize((1170, 540))
        buf = io.BytesIO(); im.save(buf, "JPEG", quality=70)
        return base64.b64encode(buf.getvalue()).decode()

    def ai(self, question):
        """Ekranni Claude'ga yuboradi, JSON qaytaradi. Koordinatalar 2340x1080 da."""
        if not self.c["api_key"]:
            return None
        import requests
        prompt = ("Bu Dream League Soccer ekrani. Faqat JSON qaytar: "
                  '{"screen":"home|division|lineup|team|match|rewards|ad|other",'
                  '"tap":[x,y] yoki null,"coins":son yoki null,"diamonds":son yoki null}. '
                  "Koordinatalar 2340x1080 ekran uchun. coins/diamonds yuqori panelda: "
                  "sariq tanga raqami = coins, ko'k kristall raqami = diamonds. " + question)
        try:
            r = requests.post("https://api.anthropic.com/v1/messages", timeout=60,
                headers={"x-api-key": self.c["api_key"], "anthropic-version": "2023-06-01",
                         "content-type": "application/json"},
                json={"model": self.c["ai_model"], "max_tokens": 200, "messages": [{"role": "user", "content": [
                    {"type": "image", "source": {"type": "base64", "media_type": "image/jpeg", "data": self.shot_b64()}},
                    {"type": "text", "text": prompt}]}]})
            t = r.json()["content"][0]["text"]
            return json.loads(t[t.index("{"):t.rindex("}") + 1])
        except Exception as e:
            log("AI xato: %s" % e)
            return None

    def ai_close_ad(self):
        d = self.ai("Agar reklama bo'lsa, uni yopish (X / Close / Skip) tugmasi koordinatasini 'tap' ga yoz. Reklama bo'lmasa tap=null.")
        if d and d.get("tap"):
            self.tap(d["tap"]); log("AI: reklama yopildi")
        else:
            self.key(4)
        self.wait(2.5)

    def ai_recover(self):
        d = self.ai("Meni Legendary Division ('PLAY NOW') ekraniga qaytaradigan keyingi bosish koordinatasini 'tap' ga yoz.")
        if d and d.get("tap"):
            self.tap(d["tap"]); self.wait(2.5)
        else:
            self.key(4); self.wait(2.5)

    def ai_balance(self):
        d = self.ai("Faqat coins va diamonds ni o'qi. Yuqori panel ko'rinmasa null.")
        return (d.get("coins"), d.get("diamonds")) if d else (None, None)

    # --- bosqichlar ---
    def best_team(self):
        log("Best Team"); set_status(step="Best Team")
        self.tap(P["play_now"]); self.wait(3)
        self.tap(P["team"]); self.wait(2.5)
        self.tap(P["best_team"]); self.wait(1.5)
        self.tap(P["back"]); self.wait(2.5)

    def play_match(self):
        log("Match boshlandi"); set_status(step="Play Match")
        self.tap(P["play"]); self.wait(10)
        end = time.time() + self.c["match_seconds"]
        joy = P["joy"]
        while time.time() < end:
            # oddiy skript: darvozaga qarab yurish + zarba/pas
            self.swipe(joy, (joy[0] + 120, joy[1] - 60), 900)
            self.tap(P["shoot_b"]); self.wait(0.6)
            self.tap(P["pass_a"]); self.wait(0.6)
        self.wait(3)

    def claim_and_ads(self):
        for i, p in enumerate(P["claims"]):
            log("Claim %d" % (i + 1)); set_status(step="Claim")
            self.tap(p)
            if self.c["do_ads"]:
                set_status(step="Ads")
                self.wait(self.c["ad_wait"])
                if self.c["api_key"]:
                    self.ai_close_ad()
                else:
                    self.key(4)       # BACK - reklamani yopish
                    self.wait(2.5)
            else:
                self.wait(1.5)

    def finish(self):
        for _ in range(3):
            self.tap(P["cont"]); self.wait(2.5)
        if self.c["api_key"]:
            self.ai_recover()

    def run(self):
        c = self.c
        t0 = time.time(); n = 0; coins = 0; dp = 0
        set_status(running=True, matches=0, coins=0, dp=0, state="Ulanmoqda")
        telegram(c, "FLEX: bot ishga tushdi")
        try:
            self.connect()
            while True:
                if os.path.exists(STOP):
                    raise KeyboardInterrupt
                if n >= c["max_matches"] or coins >= c["target_coins"] and dp >= c["target_dp"] \
                        or time.time() - t0 > c["max_minutes"] * 60:
                    break
                set_status(state="Sikl %d" % (n + 1))
                try:
                    if c["do_best"]: self.best_team()
                    if c["do_play"]: self.play_match()
                    if c["do_claim"]: self.claim_and_ads()
                    self.finish()
                except KeyboardInterrupt:
                    raise
                except Exception as e:
                    log("Xato: %s" % e)
                    self.key(4); self.wait(3)
                    continue
                n += 1; coins += c["est_coins"]; dp += c["est_dp"]
                if c["api_key"]:
                    rc, rd = self.ai_balance()       # haqiqiy qiymat AI orqali
                    if rc is not None: coins = int(rc)
                    if rd is not None: dp = int(rd)
                set_status(matches=n, coins=coins, dp=dp)
                if n % 5 == 0:
                    telegram(c, "FLEX: %d match, ~%d tanga, ~%d DP" % (n, coins, dp))
            telegram(c, "FLEX: MAQSADGA YETILDI! %d match, %d tanga, %d DP" % (n, coins, dp))
        except KeyboardInterrupt:
            telegram(c, "FLEX: to'xtatildi (%d match)" % n)
        except Exception as e:
            log("Fatal: %s" % e)
            telegram(c, "FLEX xato: %s" % e)
        finally:
            set_status(running=False, state="To'xtadi")
            try: os.remove(STOP)
            except Exception: pass
