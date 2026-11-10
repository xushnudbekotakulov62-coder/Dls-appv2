import json, os
from kivy.app import App
from kivy.lang import Builder
from kivy.clock import Clock
from kivy.core.window import Window
from kivy.graphics.texture import Texture
from kivy.uix.screenmanager import ScreenManager, Screen, FadeTransition
import bot

def gradient(c1, c2, horizontal=True):
    t = Texture.create(size=(2, 1) if horizontal else (1, 2), colorfmt="rgba")
    t.blit_buffer(bytes(c1 + c2), colorfmt="rgba", bufferfmt="ubyte")
    t.mag_filter = "linear"; t.min_filter = "linear"
    return t

KV = """
#:import dp kivy.metrics.dp
#:set SILVER (0.86, 0.89, 0.93, 1)
#:set MUTED (0.70, 0.76, 0.86, 1)
#:set CYAN (0.15, 0.88, 1, 1)
#:set NEON (0.22, 1, 0.55, 1)

<Glass@BoxLayout>:
    canvas.before:
        Color:
            rgba: 1, 1, 1, 0.09
        RoundedRectangle:
            pos: self.pos
            size: self.size
            radius: [dp(22)]
        Color:
            rgba: 0.15, 0.85, 1, 0.5
        Line:
            rounded_rectangle: self.x, self.y, self.width, self.height, dp(22)
            width: 1.2

<GradButton@ButtonBehavior+Label>:
    bold: True
    font_size: '18sp'
    size_hint_y: None
    height: dp(54)
    canvas.before:
        Color:
            rgba: 1, 1, 1, 1
        RoundedRectangle:
            pos: self.pos
            size: self.size
            radius: [dp(18)]
            texture: app.grad_btn

<StartBtn@ButtonBehavior+Label>:
    bold: True
    font_size: '20sp'
    color: 0.02, 0.1, 0.05, 1
    canvas.before:
        Color:
            rgba: 1, 1, 1, 1 if self.state == 'normal' else .7
        RoundedRectangle:
            pos: self.pos
            size: self.size
            radius: [dp(20)]
            texture: app.grad_green

<StopBtn@ButtonBehavior+Label>:
    bold: True
    font_size: '20sp'
    canvas.before:
        Color:
            rgba: 1, 1, 1, 1 if self.state == 'normal' else .7
        RoundedRectangle:
            pos: self.pos
            size: self.size
            radius: [dp(20)]
            texture: app.grad_red

<Field@TextInput>:
    multiline: False
    size_hint_y: None
    height: dp(46)
    padding: dp(14), dp(12)
    foreground_color: 1, 1, 1, 1
    hint_text_color: 0.75, 0.8, 0.88, 1
    cursor_color: 1, 1, 1, 1
    background_color: 0, 0, 0, 0
    canvas.before:
        Color:
            rgba: 0.15, 0.85, 1, 0.55
        Line:
            rounded_rectangle: self.x, self.y, self.width, self.height, dp(16)
            width: 1.05

<Cap@Label>:
    color: MUTED
    font_size: '12sp'
    size_hint_y: None
    height: dp(18)
    text_size: self.size
    halign: 'left'

<NavBtn@ButtonBehavior+Label>:
    color: SILVER
    font_size: '14sp'

<Root>:
    canvas.before:
        Color:
            rgba: 1, 1, 1, 1
        Rectangle:
            pos: self.pos
            size: self.size
            texture: app.grad_bg

<SplashScreen>:
    name: 'splash'
    Label:
        text: "FLEX // DLS BOT"
        font_size: '34sp'
        bold: True
        color: CYAN
        pos_hint: {'center_y': .62}
    Label:
        text: "Flex & DLS"
        color: MUTED
        font_size: '14sp'
        pos_hint: {'center_y': .06}

<LoginScreen>:
    name: 'login'
    BoxLayout:
        padding: dp(26)
        orientation: 'vertical'
        Widget:
        Glass:
            orientation: 'vertical'
            padding: dp(22)
            spacing: dp(12)
            size_hint_y: None
            height: dp(430)
            Label:
                text: "Kirish"
                font_size: '30sp'
                bold: True
                color: CYAN
                size_hint_y: None
                height: dp(44)
                text_size: self.size
                halign: 'left'
            Label:
                id: hint
                text: "Akkauntga kiring"
                color: SILVER
                size_hint_y: None
                height: dp(24)
                text_size: self.size
                halign: 'left'
            Field:
                id: user
                hint_text: 'Foydalanuvchi nomi'
            Field:
                id: pw
                hint_text: 'Parol'
                password: True
            GradButton:
                text: "Kirish"
                on_release: root.submit()
            Label:
                id: msg
                text: ""
                color: 1, .7, .7, 1
                size_hint_y: None
                height: dp(24)
            Label:
                text: "Faqat shu telefon uchun"
                color: MUTED
                font_size: '12sp'
                size_hint_y: None
                height: dp(20)
        Widget:

<HomeScreen>:
    name: 'home'
    BoxLayout:
        orientation: 'vertical'
        padding: dp(18), dp(40), dp(18), dp(8)
        spacing: dp(12)
        Label:
            text: "FLEX // DLS BOT"
            font_size: '24sp'
            bold: True
            color: CYAN
            size_hint_y: None
            height: dp(34)
            text_size: self.size
            halign: 'left'
        Glass:
            orientation: 'vertical'
            padding: dp(14)
            spacing: dp(4)
            size_hint_y: None
            height: dp(128)
            Cap:
                text: "SOZLAMALAR"
                color: CYAN
            BoxLayout:
                spacing: dp(10)
                size_hint_y: None
                height: dp(46)
                Field:
                    id: in_coins
                    hint_text: 'Maqsad tanga'
                    input_filter: 'int'
                    on_focus: if not self.focus: root.save_targets()
                Field:
                    id: in_dp
                    hint_text: 'DP limiti'
                    input_filter: 'int'
                    on_focus: if not self.focus: root.save_targets()
            Cap:
                text: "Qolgan limitlar: Sozlama bo'limida"
        Glass:
            orientation: 'vertical'
            padding: dp(14)
            spacing: dp(4)
            Label:
                text: root.state
                font_size: '20sp'
                bold: True
                color: NEON if root.running else SILVER
                size_hint_y: None
                height: dp(30)
                text_size: self.size
                halign: 'left'
            Label:
                text: root.chain
                markup: True
                font_size: '13sp'
                size_hint_y: None
                height: dp(24)
                text_size: self.size
                halign: 'left'
            Label:
                text: 'Match: %d    Tanga: %d / %d    DP: %d / %d' % (root.matches, root.coins, root.tcoins, root.dp, root.tdp)
                font_size: '12sp'
                color: MUTED
                size_hint_y: None
                height: dp(22)
                text_size: self.size
                halign: 'left'
            ScrollView:
                Label:
                    text: root.tail
                    font_size: '11sp'
                    color: 0.75, 0.95, 1, 1
                    size_hint_y: None
                    height: self.texture_size[1]
                    text_size: self.width, None
                    halign: 'left'
                    valign: 'top'
        BoxLayout:
            size_hint_y: None
            height: dp(64)
            spacing: dp(12)
            StartBtn:
                text: "START"
                on_release: root.start()
            StopBtn:
                text: "STOP"
                on_release: root.stop()

<LogScreen>:
    name: 'log'
    BoxLayout:
        orientation: 'vertical'
        padding: dp(18), dp(40), dp(18), dp(8)
        spacing: dp(10)
        Label:
            text: "Jurnal"
            font_size: '24sp'
            bold: True
            size_hint_y: None
            height: dp(36)
            text_size: self.size
            halign: 'left'
        Glass:
            padding: dp(12)
            ScrollView:
                Label:
                    id: txt
                    text: root.text
                    size_hint_y: None
                    height: self.texture_size[1]
                    text_size: self.width, None
                    font_size: '12sp'
                    halign: 'left'
                    valign: 'top'

<SettingsScreen>:
    name: 'settings'
    ScrollView:
        BoxLayout:
            orientation: 'vertical'
            size_hint_y: None
            height: self.minimum_height
            padding: dp(18), dp(40), dp(18), dp(12)
            spacing: dp(6)
            Label:
                text: "Sozlamalar"
                font_size: '24sp'
                bold: True
                size_hint_y: None
                height: dp(40)
                text_size: self.size
                halign: 'left'
            Cap:
                text: "Bosqichlar (yoqish / o'chirish)"
            GridLayout:
                cols: 4
                size_hint_y: None
                height: dp(70)
                Label:
                    text: "Match"
                    font_size: '12sp'
                Label:
                    text: "Claim"
                    font_size: '12sp'
                Label:
                    text: "Ads"
                    font_size: '12sp'
                Label:
                    text: "Best"
                    font_size: '12sp'
                Switch:
                    id: do_play
                Switch:
                    id: do_claim
                Switch:
                    id: do_ads
                Switch:
                    id: do_best
            Cap:
                text: "Maqsad: tanga"
            Field:
                id: target_coins
            Cap:
                text: "Maqsad: DP"
            Field:
                id: target_dp
            Cap:
                text: "Eng ko'p match"
            Field:
                id: max_matches
            Cap:
                text: "Vaqt limiti (daqiqa)"
            Field:
                id: max_minutes
            Cap:
                text: "Bitta match davomi (soniya)"
            Field:
                id: match_seconds
            Cap:
                text: "Reklama kutish (soniya)"
            Field:
                id: ad_wait
            Cap:
                text: "Sikl uchun taxminiy tanga / DP"
            BoxLayout:
                size_hint_y: None
                height: dp(46)
                spacing: dp(10)
                Field:
                    id: est_coins
                Field:
                    id: est_dp
            Cap:
                text: "ADB manzil va port (shu telefon)"
            BoxLayout:
                size_hint_y: None
                height: dp(46)
                spacing: dp(10)
                Field:
                    id: adb_host
                Field:
                    id: adb_port
            Cap:
                text: "Ekran o'lchami (eni / bo'yi, gorizontal)"
            BoxLayout:
                size_hint_y: None
                height: dp(46)
                spacing: dp(10)
                Field:
                    id: screen_w
                Field:
                    id: screen_h
            Cap:
                text: "Telegram bot tokeni"
            Field:
                id: tg_token
            Cap:
                text: "Telegram chat ID"
            Field:
                id: tg_chat
            Cap:
                text: "Anthropic API kaliti (AI uchun, bo'sh = AI o'chiq)"
            Field:
                id: api_key
            Widget:
                size_hint_y: None
                height: dp(8)
            GradButton:
                text: "Saqlash"
                on_release: root.save()
            NavBtn:
                text: "Ma'lumotlar kiritish oynasi"
                size_hint_y: None
                height: dp(40)
                on_release: app.root_w.go('setup')

<SetupScreen>:
    name: 'setup'
    ScrollView:
        BoxLayout:
            orientation: 'vertical'
            size_hint_y: None
            height: self.minimum_height
            padding: dp(26), dp(50), dp(26), dp(20)
            spacing: dp(8)
            Label:
                text: "Ma'lumotlar kiritish"
                font_size: '26sp'
                bold: True
                size_hint_y: None
                height: dp(44)
                text_size: self.size
                halign: 'left'
            Label:
                text: "Bular faqat shu telefonda saqlanadi. Keyin Sozlama'dan o'zgartirasiz."
                color: MUTED
                size_hint_y: None
                height: dp(40)
                text_size: self.size
                halign: 'left'
            Cap:
                text: "Telegram bot tokeni (@BotFather)"
            Field:
                id: tg_token
            Cap:
                text: "Telegram chat ID (@userinfobot)"
            Field:
                id: tg_chat
            Cap:
                text: "AI uchun API kalit (ixtiyoriy)"
            Field:
                id: api_key
            Cap:
                text: "ADB IP va port (odatda 127.0.0.1 / 5555)"
            BoxLayout:
                size_hint_y: None
                height: dp(46)
                spacing: dp(10)
                Field:
                    id: adb_host
                    text: "127.0.0.1"
                Field:
                    id: adb_port
                    text: "5555"
            Widget:
                size_hint_y: None
                height: dp(10)
            GradButton:
                text: "Saqlash va davom etish"
                on_release: root.save()
            NavBtn:
                text: "Keyinroq"
                size_hint_y: None
                height: dp(40)
                on_release: root.skip()

<Root>:
    ScreenManager:
        id: sm
    Glass:
        id: nav
        size_hint: 1, None
        height: 0
        opacity: 0
        pos_hint: {'x': 0, 'y': 0}
        padding: dp(6)
        NavBtn:
            text: "Bosh"
            on_release: root.go('home')
        NavBtn:
            text: "Jurnal"
            on_release: root.go('log')
        NavBtn:
            text: "Sozlama"
            on_release: root.go('settings')
"""

from kivy.uix.floatlayout import FloatLayout
from kivy.properties import StringProperty, NumericProperty, BooleanProperty

class Root(FloatLayout):
    def go(self, name):
        self.ids.sm.current = name
    def show_nav(self):
        self.ids.nav.height = 62; self.ids.nav.opacity = 1

class SplashScreen(Screen): pass

class LoginScreen(Screen):
    def on_pre_enter(self):
        c = bot.load_cfg()
        self.first = not c["user"]
        self.ids.hint.text = "Yangi akkaunt yarating" if self.first else "Xush kelibsiz, kiring"
    def submit(self):
        c = bot.load_cfg()
        u, p = self.ids.user.text.strip(), self.ids.pw.text
        if not u or not p:
            self.ids.msg.text = "Nom va parolni kiriting"; return
        if self.first:
            c["user"], c["password"] = u, p; bot.save_cfg(c)
        elif (u, p) != (c["user"], c["password"]):
            self.ids.msg.text = "Nom yoki parol noto'g'ri"; return
        App.get_running_app().enter()

class HomeScreen(Screen):
    state = StringProperty("Tayyor")
    chain = StringProperty("")
    tail = StringProperty("")
    matches = NumericProperty(0)
    coins = NumericProperty(0)
    dp = NumericProperty(0)
    tcoins = NumericProperty(0)
    tdp = NumericProperty(0)
    running = BooleanProperty(False)
    STEPS = ("Play Match", "Claim", "Ads", "Best Team")
    def on_pre_enter(self):
        c = bot.load_cfg()
        self.tcoins, self.tdp = c["target_coins"], c["target_dp"]
        self.ids.in_coins.text, self.ids.in_dp.text = str(c["target_coins"]), str(c["target_dp"])
        self.set_chain("")
        Clock.schedule_interval(self.poll, 1)
    def set_chain(self, cur):
        parts = []
        for s in self.STEPS:
            parts.append("[color=38ff8c][b]%s[/b][/color]" % s if s == cur else "[color=7fa0c0]%s[/color]" % s)
        self.chain = " > ".join(parts)
    def save_targets(self):
        c = bot.load_cfg()
        try:
            c["target_coins"] = int(self.ids.in_coins.text); c["target_dp"] = int(self.ids.in_dp.text)
        except ValueError:
            return
        bot.save_cfg(c); self.tcoins, self.tdp = c["target_coins"], c["target_dp"]
    def poll(self, dt):
        try:
            s = json.load(open(bot.STATUS))
            self.state = s.get("state", "Tayyor"); self.matches = s.get("matches", 0)
            self.coins = s.get("coins", 0); self.dp = s.get("dp", 0)
            self.running = s.get("running", False)
            self.set_chain(s.get("step", "") if self.running else "")
        except Exception:
            pass
        try:
            self.tail = "".join(open(bot.LOGF).readlines()[-8:])
        except Exception:
            self.tail = "Jurnal bo'sh"
    def start(self):
        if self.running:
            return
        self.save_targets()
        try:
            from android import AndroidService
            AndroidService("FLEX DLS Bot", "Bot ishlayapti").start("go")
        except Exception as e:
            self.state = "Faqat Android'da ishlaydi"; return
        bot.set_status(running=True, state="Ishga tushmoqda", matches=0, coins=0, dp=0, step="")
        self.running = True
    def stop(self):
        if self.running:
            open(bot.STOP, "w").write("1")

class SetupScreen(Screen):
    def save(self):
        c = bot.load_cfg()
        for k in ("tg_token", "tg_chat", "api_key", "adb_host"):
            c[k] = self.ids[k].text.strip()
        try: c["adb_port"] = int(self.ids.adb_port.text)
        except ValueError: pass
        c["setup_done"] = True; bot.save_cfg(c)
        App.get_running_app().enter()
    def skip(self):
        c = bot.load_cfg(); c["setup_done"] = True; bot.save_cfg(c)
        App.get_running_app().enter()

class LogScreen(Screen):
    text = StringProperty("")
    def on_pre_enter(self):
        Clock.schedule_interval(self.refresh, 2); self.refresh(0)
    def refresh(self, dt):
        try:
            self.text = "".join(open(bot.LOGF).readlines()[-80:])
        except Exception:
            self.text = "Hali yozuv yo'q"

NUM = ("target_coins", "target_dp", "max_matches", "max_minutes", "match_seconds",
       "ad_wait", "est_coins", "est_dp", "adb_port", "screen_w", "screen_h")
TXT = ("adb_host", "tg_token", "tg_chat", "api_key")

class SettingsScreen(Screen):
    def on_pre_enter(self):
        c = bot.load_cfg()
        for k in NUM + TXT:
            self.ids[k].text = str(c[k])
        for k in ("do_play", "do_claim", "do_ads", "do_best"):
            self.ids[k].active = c[k]
    def save(self):
        c = bot.load_cfg()
        for k in NUM:
            try: c[k] = int(self.ids[k].text)
            except ValueError: pass
        for k in TXT:
            c[k] = self.ids[k].text.strip()
        for k in ("do_play", "do_claim", "do_ads", "do_best"):
            c[k] = self.ids[k].active
        bot.save_cfg(c)

class FlexApp(App):
    def build(self):
        self.title = "FLEX"
        Window.clearcolor = (0.01, 0.03, 0.08, 1)
        self.grad_bg = gradient((2, 5, 18, 255), (5, 26, 54, 255), horizontal=False)
        self.grad_btn = gradient((20, 120, 255, 255), (20, 220, 255, 255))
        self.grad_green = gradient((40, 255, 120, 255), (20, 200, 90, 255))
        self.grad_red = gradient((220, 30, 50, 255), (140, 10, 30, 255))
        Builder.load_string(KV)
        self.root_w = Root()
        sm = self.root_w.ids.sm
        sm.transition = FadeTransition(duration=0.25)
        for s in (SplashScreen(), LoginScreen(), HomeScreen(), SetupScreen(), LogScreen(), SettingsScreen()):
            sm.add_widget(s)
        sm.current = "splash"
        Clock.schedule_once(lambda dt: setattr(sm, "current", "login"), 1.6)
        return self.root_w
    def enter(self):
        if not bot.load_cfg()["setup_done"]:
            self.root_w.go("setup"); return
        self.root_w.show_nav(); self.root_w.go("home")
        try:
            from jnius import autoclass
            a = autoclass("org.kivy.android.PythonActivity").mActivity
            a.getWindow().addFlags(128)  # ekran o'chmasin
        except Exception:
            pass

if __name__ == "__main__":
    FlexApp().run()
