"""
╔══════════════════════════════════════════════════════════════╗
║   ARIA — AI Response & Interaction Assistant                 ║
║   Personal AI-Based Command Automation System                ║
║   Version 2.0 — All-in-One File                              ║
║                                                              ║
║   HOW TO RUN:                                                ║
║     python ARIA.py                                           ║
║                                                              ║
║   INSTALL DEPENDENCIES:                                      ║
║     pip install SpeechRecognition pyttsx3 pyaudio psutil     ║
║     pip install Pillow pyperclip                             ║
╚══════════════════════════════════════════════════════════════╝
"""

# ══════════════════════════════════════════════════════════════
#  STANDARD LIBRARY IMPORTS
# ══════════════════════════════════════════════════════════════

import tkinter as tk
import threading
import datetime
import sys
import os
import re
import math
import time
import random
import platform
import socket
import subprocess
import webbrowser
import urllib.request


# ══════════════════════════════════════════════════════════════
#  SECTION 1 ── INTENT ENGINE (Offline NLP)
# ══════════════════════════════════════════════════════════════

class IntentEngine:
    """Keyword-based intent recognizer — 100% offline, no API needed."""

    INTENTS = {
        "greeting":    ["hello", "hi", "hey", "good morning", "good evening",
                         "good afternoon", "howdy", "what's up", "greetings"],
        "farewell":    ["bye", "goodbye", "see you", "exit", "quit", "close",
                         "shut down assistant", "stop", "farewell"],
        "time":        ["time", "what time", "current time", "clock"],
        "date":        ["date", "what date", "today", "what day", "which day"],
        "joke":        ["joke", "funny", "laugh", "humor", "tell me a joke",
                         "make me laugh"],
        "quote":       ["quote", "inspire", "motivate", "motivation", "wisdom"],
        "search_web":  ["search", "google", "look up", "find online", "browse",
                         "bing", "internet search"],
        "youtube":     ["youtube", "watch video", "play video", "video"],
        "open_app":    ["open", "launch", "start", "run", "execute"],
        "shutdown":    ["shutdown", "power off", "turn off computer"],
        "restart":     ["restart", "reboot", "reset computer"],
        "sleep":       ["sleep", "hibernate", "suspend"],
        "screenshot":  ["screenshot", "capture screen", "take screenshot",
                         "screen capture", "snap screen"],
        "system_info": ["system info", "cpu", "ram", "memory", "disk",
                         "battery", "pc info", "hardware"],
        "ip_address":  ["ip address", "my ip", "what is my ip"],
        "calculator":  ["calculate", "compute", "math", "solve", "what is",
                         "how much is"],
        "weather":     ["weather", "temperature", "forecast", "rain", "sunny",
                         "climate"],
        "file_open":   ["open folder", "open directory", "file explorer",
                         "open desktop", "open downloads", "open documents"],
        "volume":      ["volume", "louder", "quieter", "mute", "unmute",
                         "sound up", "sound down"],
        "wifi":        ["wifi", "wi-fi", "internet connection", "network status"],
        "help":        ["help", "what can you do", "commands", "features",
                         "capabilities", "list commands"],
    }

    APP_MAP = {
        "chrome":       ["chrome", "google chrome"],
        "firefox":      ["firefox", "mozilla"],
        "edge":         ["edge", "microsoft edge"],
        "notepad":      ["notepad", "text editor"],
        "calculator":   ["calculator app", "calc app"],
        "explorer":     ["file explorer", "explorer", "my computer"],
        "terminal":     ["terminal", "cmd", "command prompt", "powershell"],
        "vlc":          ["vlc", "media player"],
        "spotify":      ["spotify", "music player"],
        "word":         ["word", "ms word", "microsoft word"],
        "excel":        ["excel", "spreadsheet"],
        "powerpoint":   ["powerpoint", "presentation"],
        "paint":        ["paint", "ms paint"],
        "vscode":       ["vs code", "vscode", "visual studio code"],
        "task_manager": ["task manager"],
        "settings":     ["settings", "control panel"],
        "zoom":         ["zoom"],
        "discord":      ["discord"],
        "telegram":     ["telegram"],
        "whatsapp":     ["whatsapp"],
    }

    def recognize(self, text: str):
        t = text.lower().strip()

        # Fast-path: math expression
        if re.search(r'\d+\s*[\+\-\*\/\^%]\s*\d+', t):
            return "calculator", {"query": text}

        # App launch detection
        for trigger in ["open", "launch", "start", "run"]:
            if trigger in t:
                for app_key, aliases in self.APP_MAP.items():
                    for alias in aliases:
                        if alias in t:
                            return "open_app", {"app": app_key, "query": text}
                return "open_app", {"app": None, "query": text}

        # Score intents
        scores = {}
        for intent, keywords in self.INTENTS.items():
            score = sum(1 for kw in keywords if kw in t)
            if score > 0:
                scores[intent] = score

        if scores:
            return max(scores, key=scores.get), {"query": text}

        return "unknown", {"query": text}


# ══════════════════════════════════════════════════════════════
#  SECTION 2 ── ACTION EXECUTOR
# ══════════════════════════════════════════════════════════════

JOKES = [
    "Why do programmers prefer dark mode? Because light attracts bugs! 🐛",
    "Why did the computer go to the doctor? It had a virus! 🦠",
    "How do you comfort a JavaScript developer? You console them.",
    "A SQL query walks into a bar and asks two tables: 'Can I join you?'",
    "Why did the programmer quit? Because he didn't get arrays.",
    "What do you call 8 bits? A byte! And what do you call that? Delicious.",
    "I have a joke about UDP... but you might not get it.",
    "Why do Java developers wear glasses? Because they don't C#!",
    "Why was the math book sad? Too many problems.",
    "What is a computer's favorite snack? Microchips! 🍪",
]

QUOTES = [
    '"The only way to do great work is to love what you do." — Steve Jobs',
    '"Talk is cheap. Show me the code." — Linus Torvalds',
    '"First, solve the problem. Then, write the code." — John Johnson',
    '"Code is like humor. When you have to explain it, it\'s bad." — Cory House',
    '"Simplicity is the soul of efficiency." — Austin Freeman',
    '"Any fool can write code a computer understands. Good programmers write code humans understand." — Martin Fowler',
    '"The best error message is the one that never shows up." — Thomas Fuchs',
    '"Programs must be written for people to read." — Harold Abelson',
]

HELP_TEXT = """ARIA COMMAND REFERENCE
══════════════════════════════════════

INFORMATION
  "what time is it"       Current time
  "what is today's date"  Current date
  "system info"           CPU, RAM, disk, battery
  "what's my IP"          Local IP address

ENTERTAINMENT
  "tell me a joke"        Random programmer joke
  "give me a quote"       Inspirational quote

WEB & SEARCH
  "search python"         Google search
  "youtube lo-fi music"   YouTube search
  "weather London"        Live weather (online)

APP CONTROL
  "open chrome"           Launch Chrome
  "open notepad"          Launch Notepad
  "open terminal"         Launch terminal
  "open spotify"          Launch Spotify

SYSTEM
  "take a screenshot"     Capture & save screen
  "shutdown"              Power off (30s delay)
  "restart"               Reboot (30s delay)
  "sleep"                 Sleep/hibernate

MATH
  "calculate 25 * 4"      Evaluate expression
  "what is 100 / 5 + 8"   Chained math

NETWORK
  "wifi status"           Check internet
  "what is my ip"         Show local IP

TYPE 'bye' OR 'goodbye' TO EXIT
══════════════════════════════════════"""


class ActionExecutor:
    OS = platform.system()

    def execute(self, intent, params):
        query = params.get("query", "")
        handlers = {
            "greeting":    self._greeting,
            "farewell":    self._farewell,
            "time":        self._get_time,
            "date":        self._get_date,
            "joke":        self._joke,
            "quote":       self._quote,
            "search_web":  self._search_web,
            "youtube":     self._youtube,
            "open_app":    self._open_app,
            "shutdown":    self._shutdown,
            "restart":     self._restart,
            "sleep":       self._sleep,
            "screenshot":  self._screenshot,
            "system_info": self._system_info,
            "ip_address":  self._ip_address,
            "calculator":  self._calculate,
            "weather":     self._weather,
            "file_open":   self._file_open,
            "volume":      self._volume,
            "wifi":        self._wifi_status,
            "help":        self._help,
            "unknown":     self._unknown,
        }
        try:
            return handlers.get(intent, self._unknown)(query, params)
        except Exception as e:
            return f"⚠️ Action failed: {e}"

    def _greeting(self, q, p):
        h = datetime.datetime.now().hour
        period = "Good morning" if 5<=h<12 else "Good afternoon" if h<17 else "Good evening"
        return f"{period}! I'm ARIA, your personal AI assistant. How can I help you today? 😊"

    def _farewell(self, q, p):
        return "Goodbye! Have a great day. ARIA signing off. 👋"

    def _get_time(self, q, p):
        now = datetime.datetime.now()
        return f"🕐 Current time: {now.strftime('%I:%M:%S %p')}  ({now.strftime('%H:%M:%S')} 24h)"

    def _get_date(self, q, p):
        now = datetime.datetime.now()
        return (f"📅 Today is {now.strftime('%A, %B %d, %Y')}\n"
                f"   Week {now.strftime('%U')} of the year | Day {now.timetuple().tm_yday} of 365")

    def _joke(self, q, p):
        return f"😄 {random.choice(JOKES)}"

    def _quote(self, q, p):
        return f"✨ {random.choice(QUOTES)}"

    def _search_web(self, q, p):
        term = re.sub(r'\b(search|google|look up|find|browse|for|me|online)\b', '', q, flags=re.I).strip()
        if not term:
            return "🔍 What would you like to search? Try: 'search Python tutorials'"
        url = f"https://www.google.com/search?q={term.replace(' ','+')}"
        webbrowser.open(url)
        return f"🔍 Searching Google for: \"{term}\"\n   Browser opened!"

    def _youtube(self, q, p):
        term = re.sub(r'\b(youtube|watch|play|video|videos)\b', '', q, flags=re.I).strip()
        if not term:
            webbrowser.open("https://www.youtube.com")
            return "▶️ Opened YouTube!"
        url = f"https://www.youtube.com/results?search_query={term.replace(' ','+')}"
        webbrowser.open(url)
        return f"▶️ Searching YouTube for: \"{term}\""

    def _open_app(self, q, p):
        app = p.get("app")
        if not app:
            return "❓ Which app? Try: 'open chrome', 'open notepad', 'open terminal'"
        win = {"chrome":["start","chrome"],"firefox":["start","firefox"],
               "edge":["start","msedge"],"notepad":["notepad"],"calculator":["calc"],
               "explorer":["explorer"],"terminal":["start","cmd"],"vlc":["start","vlc"],
               "spotify":["start","spotify"],"word":["start","winword"],
               "excel":["start","excel"],"powerpoint":["start","powerpnt"],
               "paint":["mspaint"],"vscode":["code"],"task_manager":["taskmgr"],
               "settings":["start","ms-settings:"],"zoom":["start","zoom"],
               "discord":["start","discord"],"telegram":["start","telegram"],
               "whatsapp":["start","whatsapp"]}
        mac = {"chrome":["open","-a","Google Chrome"],"firefox":["open","-a","Firefox"],
               "notepad":["open","-a","TextEdit"],"calculator":["open","-a","Calculator"],
               "explorer":["open",os.path.expanduser("~")],"terminal":["open","-a","Terminal"],
               "vlc":["open","-a","VLC"],"spotify":["open","-a","Spotify"],
               "vscode":["open","-a","Visual Studio Code"],"settings":["open","-a","System Preferences"]}
        linux = {"chrome":["google-chrome"],"firefox":["firefox"],"notepad":["gedit"],
                 "calculator":["gnome-calculator"],"explorer":["nautilus"],
                 "terminal":["gnome-terminal"],"vlc":["vlc"],"spotify":["spotify"],
                 "vscode":["code"],"settings":["gnome-control-center"]}
        cmds = {"Windows":win,"Darwin":mac,"Linux":linux}.get(self.OS, linux)
        cmd = cmds.get(app)
        if not cmd:
            return f"❓ I don't know how to open '{app}' on {self.OS}."
        try:
            subprocess.Popen(cmd, shell=(self.OS=="Windows"),
                             stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            return f"🚀 Launching {app.replace('_',' ').title()}..."
        except FileNotFoundError:
            return f"⚠️ '{app}' not found. Make sure it's installed."
        except Exception as e:
            return f"⚠️ Error launching {app}: {e}"

    def _shutdown(self, q, p):
        if "cancel" in q.lower():
            if self.OS=="Windows": os.system("shutdown /a")
            return "✅ Shutdown cancelled."
        if self.OS=="Windows": os.system("shutdown /s /t 30")
        elif self.OS=="Darwin": os.system("sudo shutdown -h +1")
        else: os.system("shutdown -h +1")
        return "⚠️ SHUTDOWN in 30 seconds. Type 'cancel shutdown' to abort."

    def _restart(self, q, p):
        if self.OS=="Windows": os.system("shutdown /r /t 30")
        elif self.OS=="Darwin": os.system("sudo shutdown -r +1")
        else: os.system("shutdown -r +1")
        return "🔄 RESTART in 30 seconds."

    def _sleep(self, q, p):
        if self.OS=="Windows": os.system("rundll32.exe powrprof.dll,SetSuspendState 0,1,0")
        elif self.OS=="Darwin": os.system("pmset sleepnow")
        else: os.system("systemctl suspend")
        return "💤 Putting computer to sleep..."

    def _screenshot(self, q, p):
        try:
            from PIL import ImageGrab
            ts = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
            path = os.path.join(os.path.expanduser("~"), "Desktop", f"aria_shot_{ts}.png")
            ImageGrab.grab().save(path)
            return f"📷 Screenshot saved!\n   → {path}"
        except ImportError:
            return "⚠️ Pillow not installed. Run: pip install Pillow"

    def _system_info(self, q, p):
        try:
            import psutil
            cpu = psutil.cpu_percent(interval=1)
            ram = psutil.virtual_memory()
            disk = psutil.disk_usage('/')
            info = (f"💻 SYSTEM INFORMATION\n"
                    f"   OS:    {platform.system()} {platform.release()} ({platform.machine()})\n"
                    f"   CPU:   {cpu:.1f}% usage | {psutil.cpu_count()} cores\n"
                    f"   RAM:   {ram.used/1e9:.1f} GB / {ram.total/1e9:.1f} GB ({ram.percent:.0f}% used)\n"
                    f"   Disk:  {disk.used/1e9:.0f} GB / {disk.total/1e9:.0f} GB ({disk.percent:.0f}% used)")
            bat = psutil.sensors_battery()
            if bat:
                info += f"\n   🔋 Battery: {bat.percent:.0f}% ({'charging' if bat.power_plugged else 'on battery'})"
            return info
        except ImportError:
            return f"⚠️ psutil not installed. Run: pip install psutil\n   OS: {platform.system()} {platform.release()}"

    def _ip_address(self, q, p):
        try:
            hostname = socket.gethostname()
            ip = socket.gethostbyname(hostname)
            return f"🌐 Hostname: {hostname}\n   Local IP: {ip}"
        except Exception as e:
            return f"⚠️ Could not get IP: {e}"

    def _calculate(self, q, p):
        expr = re.sub(r'\b(calculate|compute|what is|solve|math|how much is)\b','',q,flags=re.I)
        expr = expr.strip().rstrip('?').replace('^','**')
        safe = re.sub(r'[^0-9\+\-\*\/\.\(\)\s\%\*]','',expr).strip()
        if not safe:
            return "❓ Provide an expression. E.g., 'calculate 25 * 4 + 10'"
        try:
            result = eval(safe, {"__builtins__": {}})
            return f"🧮 {safe} = {result}"
        except ZeroDivisionError:
            return "⚠️ Cannot divide by zero!"
        except Exception as e:
            return f"⚠️ Could not evaluate: {e}"

    def _weather(self, q, p):
        try:
            city = re.sub(r'\b(weather|forecast|temperature|in|for|at|of|the)\b','',q,flags=re.I).strip()
            city = city.replace(' ','+') or 'auto'
            with urllib.request.urlopen(f"http://wttr.in/{city}?format=3", timeout=5) as r:
                return f"🌤️ {r.read().decode().strip()}\n   (via wttr.in)"
        except Exception:
            return "⚠️ Weather unavailable. Check internet connection."

    def _file_open(self, q, p):
        folders = {k: os.path.join(os.path.expanduser("~"), k.title())
                   for k in ["desktop","downloads","documents","pictures","music","videos"]}
        folders["home"] = os.path.expanduser("~")
        for name, path in folders.items():
            if name in q.lower() and os.path.exists(path):
                if self.OS=="Windows": os.startfile(path)
                elif self.OS=="Darwin": subprocess.Popen(["open", path])
                else: subprocess.Popen(["xdg-open", path])
                return f"📁 Opening {name.title()}: {path}"
        home = os.path.expanduser("~")
        if self.OS=="Windows": os.startfile(home)
        elif self.OS=="Darwin": subprocess.Popen(["open", home])
        else: subprocess.Popen(["xdg-open", home])
        return f"📁 Opening home: {home}"

    def _volume(self, q, p):
        return "ℹ️ Volume control: Use your system keyboard media keys or taskbar."

    def _wifi_status(self, q, p):
        try:
            socket.create_connection(("8.8.8.8", 53), timeout=3)
            return "📶 Internet: ONLINE ✅"
        except OSError:
            return "📵 Internet: OFFLINE ❌"

    def _help(self, q, p):
        return HELP_TEXT

    def _unknown(self, q, p):
        return (f"❓ I didn't understand: \"{q}\"\n"
                f"   Type 'help' to see all available commands.")


# ══════════════════════════════════════════════════════════════
#  SECTION 3 ── SPEECH HANDLER (Offline TTS + Online/Offline STT)
# ══════════════════════════════════════════════════════════════

def _strip_for_tts(text: str) -> str:
    emoji_re = re.compile(
        "[" "\U0001F600-\U0001F64F" "\U0001F300-\U0001F5FF"
        "\U0001F680-\U0001F6FF" "\U0001F1E0-\U0001F1FF"
        "\U00002702-\U000027B0" "\U000024C2-\U0001F251" "]+",
        flags=re.UNICODE)
    text = emoji_re.sub('', text)
    text = re.sub(r'[│├└┌┐┘┤┬┴┼─═╔╗╚╝╠╣╦╩╬▶●■□]', '', text)
    return text.strip()


class SpeechHandler:
    def __init__(self):
        self._rec = None
        self._tts = None
        self._lock = threading.Lock()
        self._init_stt()
        self._init_tts()

    def _init_stt(self):
        try:
            import speech_recognition as sr
            self._rec = sr.Recognizer()
            self._rec.energy_threshold = 300
            self._rec.pause_threshold = 0.8
            self._rec.dynamic_energy_threshold = True
        except ImportError:
            pass

    def _init_tts(self):
        try:
            import pyttsx3
            self._tts = pyttsx3.init()
            self._tts.setProperty('rate', 175)
            self._tts.setProperty('volume', 0.9)
            voices = self._tts.getProperty('voices')
            if voices:
                for v in voices:
                    if 'female' in v.name.lower() or 'zira' in v.name.lower():
                        self._tts.setProperty('voice', v.id)
                        break
        except ImportError:
            pass

    @property
    def available(self):
        return self._rec is not None

    def listen(self, timeout=8, phrase_limit=10):
        if not self._rec:
            return ""
        try:
            import speech_recognition as sr
            with sr.Microphone() as src:
                self._rec.adjust_for_ambient_noise(src, duration=0.4)
                audio = self._rec.listen(src, timeout=timeout,
                                          phrase_time_limit=phrase_limit)
            try:
                return self._rec.recognize_google(audio)
            except sr.RequestError:
                pass
            except sr.UnknownValueError:
                return ""
            try:
                return self._rec.recognize_sphinx(audio)
            except Exception:
                pass
        except Exception:
            pass
        return ""

    def speak(self, text: str):
        if not self._tts:
            return
        t = threading.Thread(target=self._speak_sync,
                              args=(_strip_for_tts(text),), daemon=True)
        t.start()

    def _speak_sync(self, text: str):
        with self._lock:
            try:
                self._tts.say(text)
                self._tts.runAndWait()
            except Exception:
                pass

    def stop(self):
        if self._tts:
            try: self._tts.stop()
            except: pass


# ══════════════════════════════════════════════════════════════
#  SECTION 4 ── CORE ASSISTANT
# ══════════════════════════════════════════════════════════════

class AIAssistant:
    def __init__(self, ui=None):
        self.intent_engine   = IntentEngine()
        self.action_executor = ActionExecutor()
        self.ui = ui
        self.history = []

    def process(self, text: str) -> str:
        text = text.strip()
        if not text:
            return "❓ Please enter a command. Type 'help' to see all commands."
        intent, params = self.intent_engine.recognize(text)
        response = self.action_executor.execute(intent, params)
        self.history.append({
            "input": text, "intent": intent,
            "response": response,
            "time": datetime.datetime.now().isoformat()
        })
        return response


# ══════════════════════════════════════════════════════════════
#  SECTION 5 ── WAVEFORM ANIMATOR
# ══════════════════════════════════════════════════════════════

def _mix_color(c1, c2, t):
    t = max(0.0, min(1.0, t))
    def h(s):
        s = s.lstrip('#')
        return int(s[0:2],16), int(s[2:4],16), int(s[4:6],16)
    r1,g1,b1 = h(c1); r2,g2,b2 = h(c2)
    return f"#{int(r1+(r2-r1)*t):02x}{int(g1+(g2-g1)*t):02x}{int(b1+(b2-b1)*t):02x}"


class WaveformCanvas(tk.Canvas):
    STATES = {
        "idle":      ("#3a5060", "🎤", "say something"),
        "listening": ("#ff4466", "👂", "listening..."),
        "thinking":  ("#00c8ff", "⚡", "thinking..."),
        "speaking":  ("#00ff9d", "🔊", "speaking..."),
        "paused":    ("#ffd700", "⏸",  "paused"),
    }

    def __init__(self, parent, size=260, **kw):
        super().__init__(parent, width=size, height=size,
                         bg="#07090f", highlightthickness=0, **kw)
        self.size = size
        self.cx = self.cy = size // 2
        self.state = "idle"
        self._tick = 0.0
        self.create_oval(8,8,size-8,size-8, outline="#1e2d3d", width=1)
        self._animate()

    def set_state(self, s):
        self.state = s

    def _animate(self):
        self._tick += 0.08
        self.delete("dyn")
        cx, cy, r, t = self.cx, self.cy, 88, self._tick
        color, icon, sub = self.STATES.get(self.state, self.STATES["idle"])

        if self.state == "listening":
            for i in range(36):
                a = (i/36)*2*math.pi
                amp = (0.18*math.sin(t*6+i*1.3) +
                       0.12*math.sin(t*9.5+i*2.1) +
                       0.07*math.sin(t*13+i*0.7))
                x1 = cx + (r-4)*math.cos(a); y1 = cy + (r-4)*math.sin(a)
                x2 = cx + (r+8+amp*55)*math.cos(a); y2 = cy + (r+8+amp*55)*math.sin(a)
                self.create_line(x1,y1,x2,y2, fill=_mix_color("#330011",color,0.4+amp),
                                  width=2, tags="dyn")

        elif self.state == "thinking":
            for i in range(8):
                a = (i/8)*2*math.pi + t*2.5
                x = cx + r*math.cos(a); y = cy + r*math.sin(a)
                sz = 4 + 3*abs(math.sin(t*3+i))
                c = _mix_color("#07090f", color, (math.sin(t*2+i*0.8)+1)/2)
                self.create_oval(x-sz,y-sz,x+sz,y+sz, fill=c, outline="", tags="dyn")

        elif self.state == "speaking":
            for ring in range(3):
                pts = []
                for i in range(61):
                    a = (i/60)*2*math.pi
                    wave = math.sin(t*4 + a*5 + ring*1.2) * (14-ring*3)
                    rx = (r - ring*12) + wave
                    pts.extend([cx+rx*math.cos(a), cy+rx*math.sin(a)])
                if len(pts) >= 4:
                    self.create_line(*pts, fill=_mix_color("#07090f",color,1-ring*0.3),
                                      width=2, smooth=True, tags="dyn")

        else:  # idle / paused
            for i in range(12):
                a = (i/12)*2*math.pi + t*0.25
                p = 1 + 0.05*math.sin(t*1.5+i*0.8)
                x = cx + r*p*math.cos(a); y = cy + r*p*math.sin(a)
                self.create_oval(x-3,y-3,x+3,y+3,
                                  fill=color, outline="", tags="dyn")

        # Center circle
        self.create_oval(cx-50,cy-50,cx+50,cy+50,
                          fill="#0d1117", outline=color, width=2, tags="dyn")
        self.create_text(cx, cy-8, text=icon, font=("Segoe UI Emoji",22),
                          fill=color, tags="dyn")
        self.create_text(cx, cy+22, text=sub, font=("Courier New",8),
                          fill=color, tags="dyn")
        self.after(45, self._animate)


# ══════════════════════════════════════════════════════════════
#  SECTION 6 ── VOICE-ONLY WINDOW
# ══════════════════════════════════════════════════════════════

C = {
    "bg":       "#07090f", "bg2": "#0d1117", "bg3": "#0a0e16",
    "accent":   "#00c8ff", "accent2": "#00ff9d", "accent3": "#ff6b6b",
    "warn":     "#ffd700", "text": "#c9d8e8", "text_dim": "#3a5060",
    "text_ai":  "#86efac", "text_user": "#7dd3fc", "border": "#1e2d3d",
    "btn_hover":"#152030",
}


class VoiceOnlyWindow:
    def __init__(self, parent=None):
        self.win = tk.Toplevel(parent) if parent else tk.Tk()
        self.win.title("ARIA — Voice Mode")
        self.win.geometry("440x660")
        self.win.configure(bg=C["bg"])
        self.win.resizable(False, False)

        self.assistant = AIAssistant()
        self.speech    = None
        self._running  = False
        self._paused   = False

        self._build_ui()
        self.win.after(500, self._boot)
        self.win.protocol("WM_DELETE_WINDOW", self._close)

    def _build_ui(self):
        self.win.grid_rowconfigure(3, weight=1)
        self.win.grid_columnconfigure(0, weight=1)

        # Header
        hdr = tk.Frame(self.win, bg=C["bg2"], height=46)
        hdr.grid(row=0, column=0, sticky="ew"); hdr.grid_propagate(False)
        hdr.grid_columnconfigure(1, weight=1)
        tk.Label(hdr, text="ARIA", font=("Courier New",15,"bold"),
                 fg=C["accent"], bg=C["bg2"]).grid(row=0,column=0,padx=14,pady=8)
        tk.Label(hdr, text="VOICE MODE", font=("Courier New",8),
                 fg=C["text_dim"], bg=C["bg2"]).grid(row=0,column=1,sticky="w")
        x_btn = tk.Label(hdr, text=" ✕ ", font=("Courier New",11),
                          fg=C["text_dim"], bg=C["bg2"], cursor="hand2")
        x_btn.grid(row=0,column=2,padx=8)
        x_btn.bind("<Button-1>", lambda e: self._close())
        x_btn.bind("<Enter>", lambda e: x_btn.config(fg=C["accent3"]))
        x_btn.bind("<Leave>", lambda e: x_btn.config(fg=C["text_dim"]))
        tk.Frame(self.win, bg=C["border"], height=1).grid(row=0,column=0,sticky="sew")

        # Waveform
        wf = tk.Frame(self.win, bg=C["bg"])
        wf.grid(row=1, column=0, pady=(20,0))
        self.wave = WaveformCanvas(wf, size=260)
        self.wave.pack()

        # Status
        self._sv = tk.StringVar(value="Initializing...")
        tk.Label(self.win, textvariable=self._sv,
                 font=("Courier New",11,"bold"),
                 fg=C["accent"], bg=C["bg"]).grid(row=2,column=0,pady=(12,0))

        # Log
        lf = tk.Frame(self.win, bg=C["bg"])
        lf.grid(row=3,column=0,sticky="nsew",padx=18,pady=10)
        lf.grid_rowconfigure(0,weight=1); lf.grid_columnconfigure(0,weight=1)
        self.log = tk.Text(lf, bg=C["bg3"], fg=C["text"],
                            font=("Courier New",9), wrap=tk.WORD,
                            state="disabled", bd=0, relief="flat",
                            padx=10, pady=8, height=8)
        self.log.grid(row=0,column=0,sticky="nsew")
        sb = tk.Scrollbar(lf, orient="vertical", command=self.log.yview,
                           bg=C["bg2"], width=4, relief="flat")
        sb.grid(row=0,column=1,sticky="ns")
        self.log.config(yscrollcommand=sb.set)
        self.log.tag_configure("user", foreground=C["text_user"],
                                font=("Courier New",9,"bold"))
        self.log.tag_configure("ai",   foreground=C["text_ai"])
        self.log.tag_configure("sys",  foreground=C["text_dim"],
                                font=("Courier New",8))

        # Buttons
        br = tk.Frame(self.win, bg=C["bg"])
        br.grid(row=4,column=0,pady=(2,18))
        self._pb = self._btn(br, "⏸  PAUSE",  self._toggle_pause, C["accent"], 0)
        self._sb = self._btn(br, "⏹  STOP",   self._stop,         C["accent3"], 1)

    def _btn(self, p, text, cmd, color, col):
        b = tk.Label(p, text=text, font=("Courier New",10,"bold"),
                      fg=C["bg"], bg=color, cursor="hand2", padx=18, pady=7)
        b.grid(row=0,column=col,padx=8)
        b.bind("<Button-1>", lambda e: cmd())
        hover = _mix_color(color,"#ffffff",0.15)
        b.bind("<Enter>", lambda e,h=hover: b.config(bg=h))
        b.bind("<Leave>", lambda e,c=color: b.config(bg=c))
        return b

    def _boot(self):
        self._log("sys", "Loading speech engine...")
        threading.Thread(target=self._init_and_run, daemon=True).start()

    def _init_and_run(self):
        try:
            self.speech = SpeechHandler()
        except Exception as e:
            self._set("⚠️ Speech engine error","idle")
            self._log("sys", f"Error: {e}")
            return
        if not self.speech.available:
            self._set("⚠️ No microphone found","idle")
            self._log("sys","Install: pip install SpeechRecognition pyaudio")
            return
        self._log("sys","✓ Ready. Speak your command.")
        self._running = True
        self._voice_loop()

    def _voice_loop(self):
        self.speech._speak_sync("Hello! I am ARIA. I am listening. Speak your command.")
        while self._running:
            if self._paused:
                self._set("⏸ Paused — say resume or click ▶","paused")
                time.sleep(0.5); continue

            self._set("👂 Listening...","listening")
            text = self.speech.listen(timeout=8, phrase_limit=10)
            if not self._running: break
            if not text: continue

            self._log("user", f"You: {text}")
            tl = text.lower()
            if any(w in tl for w in ["pause","stop listening","be quiet"]):
                self._toggle_pause(); continue
            if any(w in tl for w in ["resume","continue","start listening"]):
                if self._paused: self._toggle_pause(); continue

            self._set("⚡ Processing...","thinking")
            response = self.assistant.process(text)
            self._log("ai", f"ARIA: {response}")

            self._set("🔊 Speaking...","speaking")
            self.speech._speak_sync(_strip_for_tts(response))

            intent, _ = self.assistant.intent_engine.recognize(text)
            if intent == "farewell":
                time.sleep(1.5)
                self.win.after(0, self._close); break

        self._set("Stopped","idle")

    def _toggle_pause(self):
        self._paused = not self._paused
        if self._paused:
            self._pb.config(text="▶  RESUME")
            self._log("sys","--- Paused ---")
        else:
            self._pb.config(text="⏸  PAUSE")
            self._log("sys","--- Resumed ---")

    def _stop(self):
        self._running = False
        if self.speech: self.speech.stop()
        self._set("⏹ Stopped","idle")
        self._log("sys","Stopped. Close window to exit.")

    def _close(self):
        self._running = False
        if self.speech:
            try: self.speech.stop()
            except: pass
        self.win.destroy()

    def _set(self, text, state):
        self.win.after(0, lambda: self._sv.set(text))
        self.win.after(0, lambda: self.wave.set_state(state))

    def _log(self, kind, text):
        def ins():
            self.log.config(state="normal")
            ts = datetime.datetime.now().strftime("%H:%M:%S")
            tag = {"user":"user","ai":"ai"}.get(kind,"sys")
            short = text[:180]+"..." if len(text)>180 else text
            self.log.insert("end", f"[{ts}] {short}\n\n" if kind!="sys" else f"{text}\n", tag)
            self.log.config(state="disabled")
            self.log.see("end")
        self.win.after(0, ins)

    def run(self):
        if not isinstance(self.win, tk.Toplevel):
            self.win.mainloop()


# ══════════════════════════════════════════════════════════════
#  SECTION 7 ── MAIN UI (Chat + Voice Combined)
# ══════════════════════════════════════════════════════════════

QUICK_CMDS = [
    ("⏰  What time is it",      "what time is it"),
    ("📅  Today's date",         "what is today's date"),
    ("💻  System information",   "system info"),
    ("🌐  Check internet",       "wifi status"),
    ("🔍  Search Google",        "search python tutorials"),
    ("▶️   Open YouTube",        "open youtube"),
    ("🖥️   Open Chrome",         "open chrome"),
    ("📁  Open Downloads",       "open downloads folder"),
    ("📷  Take screenshot",      "take a screenshot"),
    ("🧮  Calculate",            "calculate 25 * 4 + 10"),
    ("😄  Tell me a joke",       "tell me a joke"),
    ("✨  Inspirational quote",  "give me a quote"),
    ("❓  Show all commands",    "help"),
]


class ARIAApp:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("ARIA — AI Command Automation System  v2.0")
        self.root.geometry("1060x700")
        self.root.configure(bg=C["bg"])
        self.root.minsize(820, 560)

        self.assistant    = AIAssistant(self)
        self.speech       = None
        self.tts_on       = tk.BooleanVar(value=True)
        self.is_listening = False
        self._sidebar_vis = True
        self._placeholder = "Type a command or click 🎤 to speak..."

        self._build_ui()
        self._update_clock()
        self.root.after(400, self._boot_msg)

    # ── Build UI ────────────────────────────────────

    def _build_ui(self):
        self.root.grid_rowconfigure(1, weight=1)
        self.root.grid_columnconfigure(0, weight=1)
        self._build_header()
        self._build_body()
        self._build_input()
        self._build_statusbar()

    def _build_header(self):
        hdr = tk.Frame(self.root, bg=C["bg2"], height=58)
        hdr.grid(row=0, column=0, sticky="ew"); hdr.grid_propagate(False)
        hdr.grid_columnconfigure(1, weight=1)

        # Left
        left = tk.Frame(hdr, bg=C["bg2"])
        left.grid(row=0, column=0, padx=16, sticky="w")
        self._pulse_c = tk.Canvas(left, width=13, height=13,
                                   bg=C["bg2"], highlightthickness=0)
        self._pulse_c.pack(side="left", padx=(0,10))
        self._pdot = self._pulse_c.create_oval(1,1,12,12,
                                                fill=C["accent2"], outline="")
        self._pulse_tick = 0.0
        self._animate_pulse()
        tk.Label(left, text="ARIA", font=("Courier New",19,"bold"),
                 fg=C["accent"], bg=C["bg2"]).pack(side="left")
        tk.Label(left, text="  AI COMMAND SYSTEM",
                 font=("Courier New",8), fg=C["text_dim"],
                 bg=C["bg2"]).pack(side="left", pady=(5,0))

        # Center
        self._sv = tk.StringVar(value="● SYSTEM READY")
        tk.Label(hdr, textvariable=self._sv, font=("Courier New",9),
                 fg=C["accent2"], bg=C["bg2"]).grid(row=0,column=1)

        # Right
        right = tk.Frame(hdr, bg=C["bg2"])
        right.grid(row=0, column=2, padx=16, sticky="e")

        self._clk = tk.StringVar()
        tk.Label(right, textvariable=self._clk, font=("Courier New",10),
                 fg=C["accent"], bg=C["bg2"]).pack(side="right", padx=(8,0))

        # TTS toggle
        tk.Checkbutton(right, text="🔊 TTS", variable=self.tts_on,
                        font=("Courier New",9), fg=C["text_dim"],
                        bg=C["bg2"], selectcolor=C["bg3"],
                        activebackground=C["bg2"],
                        activeforeground=C["accent"],
                        cursor="hand2", bd=0).pack(side="right", padx=8)

        # Voice Mode button
        vb = tk.Label(right, text="  🎙 VOICE MODE  ",
                       font=("Courier New",9,"bold"),
                       fg=C["bg"], bg=C["accent2"],
                       cursor="hand2", padx=4, pady=3)
        vb.pack(side="right", padx=(0,10))
        vb.bind("<Button-1>", lambda e: self._open_voice_mode())
        vb.bind("<Enter>", lambda e: vb.config(bg="#00cc7a"))
        vb.bind("<Leave>", lambda e: vb.config(bg=C["accent2"]))

        # Sidebar toggle
        tb = tk.Label(right, text="☰", font=("Courier New",13),
                       fg=C["text_dim"], bg=C["bg2"], cursor="hand2", padx=8, pady=2)
        tb.pack(side="right")
        tb.bind("<Button-1>", lambda e: self._toggle_sidebar())

        tk.Frame(self.root, bg=C["border"], height=1).grid(row=0, column=0, sticky="sew")

    def _animate_pulse(self):
        self._pulse_tick += 0.15
        t = (math.sin(self._pulse_tick)+1)/2
        color = _mix_color(C["accent2"], "#ffffff", t*0.3)
        self._pulse_c.itemconfig(self._pdot, fill=color)
        self.root.after(50, self._animate_pulse)

    def _build_body(self):
        body = tk.Frame(self.root, bg=C["bg"])
        body.grid(row=1, column=0, sticky="nsew")
        body.grid_rowconfigure(0, weight=1)
        body.grid_columnconfigure(0, weight=1)
        self._body = body
        self._build_chat(body)
        self._build_sidebar(body)

    def _build_chat(self, parent):
        cf = tk.Frame(parent, bg=C["bg"])
        cf.grid(row=0, column=0, sticky="nsew")
        cf.grid_rowconfigure(0, weight=1); cf.grid_columnconfigure(0, weight=1)
        self.chat = tk.Text(cf, bg=C["bg"], fg=C["text"],
                             font=("Courier New",11), wrap=tk.WORD,
                             state="disabled", cursor="arrow", bd=0,
                             padx=22, pady=16, spacing1=3, spacing3=10,
                             selectbackground=C["border"],
                             insertbackground=C["accent"])
        self.chat.grid(row=0, column=0, sticky="nsew")
        sb = tk.Scrollbar(cf, orient="vertical", command=self.chat.yview,
                           bg=C["bg2"], troughcolor=C["bg"],
                           activebackground=C["accent"], width=6, relief="flat")
        sb.grid(row=0, column=1, sticky="ns")
        self.chat.config(yscrollcommand=sb.set)
        tags = {
            "ts":       {"foreground":C["text_dim"],  "font":("Courier New",8)},
            "you_lbl":  {"foreground":C["text_user"], "font":("Courier New",10,"bold")},
            "you_txt":  {"foreground":C["text"],      "lmargin1":16,"lmargin2":16},
            "ai_lbl":   {"foreground":C["accent2"],   "font":("Courier New",10,"bold")},
            "ai_txt":   {"foreground":C["text_ai"],   "lmargin1":16,"lmargin2":16},
            "err_txt":  {"foreground":C["accent3"],   "lmargin1":16,"lmargin2":16},
            "mono":     {"foreground":C["accent"],    "font":("Courier New",10),
                         "background":C["bg2"],       "lmargin1":16,"lmargin2":16},
        }
        for tag, cfg in tags.items():
            self.chat.tag_configure(tag, **cfg)

    def _build_sidebar(self, parent):
        self._sidebar = tk.Frame(parent, bg=C["bg2"], width=215)
        self._sidebar.grid(row=0, column=1, sticky="ns")
        self._sidebar.grid_propagate(False)
        tk.Label(self._sidebar, text="QUICK COMMANDS",
                  font=("Courier New",8,"bold"),
                  fg=C["text_dim"], bg=C["bg2"]).pack(pady=(14,4),padx=14,anchor="w")
        tk.Frame(self._sidebar, bg=C["border"], height=1).pack(fill="x",padx=14,pady=(0,4))
        for label, cmd in QUICK_CMDS:
            b = tk.Label(self._sidebar, text=label, font=("Courier New",9),
                          fg=C["text"], bg=C["bg2"], cursor="hand2",
                          padx=14, pady=5, anchor="w")
            b.pack(fill="x")
            b.bind("<Button-1>", lambda e, c=cmd: self._run_quick(c))
            b.bind("<Enter>", lambda e, w=b: w.config(fg=C["accent"], bg=C["btn_hover"]))
            b.bind("<Leave>", lambda e, w=b: w.config(fg=C["text"], bg=C["bg2"]))
        tk.Frame(self._sidebar, bg=C["border"], height=1).pack(fill="x",padx=14,pady=(8,4))
        clr = tk.Label(self._sidebar, text="🗑️  Clear chat",
                        font=("Courier New",9), fg=C["text_dim"],
                        bg=C["bg2"], cursor="hand2", padx=14, pady=5, anchor="w")
        clr.pack(fill="x")
        clr.bind("<Button-1>", lambda e: self._clear_chat())
        clr.bind("<Enter>", lambda e: clr.config(fg=C["accent3"], bg=C["btn_hover"]))
        clr.bind("<Leave>", lambda e: clr.config(fg=C["text_dim"], bg=C["bg2"]))

    def _build_input(self):
        tk.Frame(self.root, bg=C["border"], height=1).grid(row=2,column=0,sticky="ew")
        bar = tk.Frame(self.root, bg=C["bg2"], height=56)
        bar.grid(row=3, column=0, sticky="ew"); bar.grid_propagate(False)
        bar.grid_columnconfigure(1, weight=1)

        # Mic button
        self._mic = tk.Label(bar, text="🎤", font=("Segoe UI Emoji",16),
                              fg=C["text_dim"], bg=C["bg2"], cursor="hand2", padx=14)
        self._mic.grid(row=0, column=0, pady=8)
        self._mic.bind("<Button-1>", lambda e: self._toggle_mic())
        self._mic.bind("<Enter>", lambda e: self._mic.config(fg=C["accent"]))
        self._mic.bind("<Leave>", lambda e: self._mic.config(
            fg="#ff4466" if self.is_listening else C["text_dim"]))

        # Entry
        ef = tk.Frame(bar, bg=C["border"], padx=1, pady=1)
        ef.grid(row=0, column=1, padx=10, pady=10, sticky="ew")
        self._iv = tk.StringVar()
        self._entry = tk.Entry(ef, textvariable=self._iv,
                                font=("Courier New",12),
                                fg=C["text_dim"], bg=C["bg3"],
                                insertbackground=C["accent"],
                                relief="flat", bd=0)
        self._entry.pack(fill="x", ipady=7, padx=10)
        self._iv.set(self._placeholder)
        self._entry.bind("<Return>",   lambda e: self._send())
        self._entry.bind("<FocusIn>",  self._clr_ph)
        self._entry.bind("<FocusOut>", self._rst_ph)
        self._entry.bind("<FocusIn>",  lambda e: ef.config(bg=C["accent"]), add="+")
        self._entry.bind("<FocusOut>", lambda e: ef.config(bg=C["border"]), add="+")

        # Send
        sb = tk.Label(bar, text="  SEND ▶  ",
                       font=("Courier New",10,"bold"),
                       fg=C["bg"], bg=C["accent"],
                       cursor="hand2", pady=7)
        sb.grid(row=0, column=2, padx=(0,14), pady=10)
        sb.bind("<Button-1>", lambda e: self._send())
        sb.bind("<Enter>", lambda e: sb.config(bg="#009dbf"))
        sb.bind("<Leave>", lambda e: sb.config(bg=C["accent"]))

    def _build_statusbar(self):
        bar = tk.Frame(self.root, bg=C["bg2"], height=22)
        bar.grid(row=4, column=0, sticky="ew")
        bar.grid_columnconfigure(1, weight=1)
        tk.Label(bar, text=" ARIA v2.0  |",
                  font=("Courier New",7), fg=C["text_dim"],
                  bg=C["bg2"]).grid(row=0,column=0,padx=(8,0))
        tk.Label(bar, text="Personal AI Command Automation System",
                  font=("Courier New",7), fg=C["text_dim"],
                  bg=C["bg2"]).grid(row=0,column=1,sticky="w",padx=4)

    # ── Interaction ──────────────────────────────────

    def _clr_ph(self, e=None):
        if self._iv.get() == self._placeholder:
            self._iv.set(""); self._entry.config(fg=C["text"])

    def _rst_ph(self, e=None):
        if not self._iv.get().strip():
            self._iv.set(self._placeholder); self._entry.config(fg=C["text_dim"])

    def _send(self):
        text = self._iv.get().strip()
        if not text or text == self._placeholder: return
        self._iv.set(""); self._entry.config(fg=C["text"])
        self._insert("YOU", text, "user")
        self._set_status("● THINKING...", "thinking")
        threading.Thread(target=self._process, args=(text,), daemon=True).start()

    def _process(self, text):
        resp = self.assistant.process(text)
        self.root.after(0, lambda: self._insert("ARIA", resp, "ai"))
        self.root.after(0, lambda: self._set_status("● READY", "ready"))
        if self.tts_on.get():
            threading.Thread(target=self._tts_speak, args=(resp,), daemon=True).start()

    def _tts_speak(self, text):
        if self.speech is None: self._load_speech()
        if self.speech:
            self.speech._speak_sync(_strip_for_tts(text))

    def _run_quick(self, cmd):
        self._iv.set(cmd); self._entry.config(fg=C["text"]); self._send()

    # ── Microphone ───────────────────────────────────

    def _toggle_mic(self):
        if self.is_listening:
            self.is_listening = False
            self._mic.config(fg=C["text_dim"])
            self._set_status("● READY", "ready")
            return
        if self.speech is None: self._load_speech()
        if self.speech and self.speech.available:
            self.is_listening = True
            self._mic.config(fg="#ff4466")
            self._set_status("● LISTENING...", "listening")
            threading.Thread(target=self._do_listen, daemon=True).start()
        else:
            self._insert("ARIA",
                "⚠️ No speech engine found.\n"
                "   Install: pip install SpeechRecognition pyaudio", "ai")

    def _do_listen(self):
        text = self.speech.listen()
        self.is_listening = False
        self.root.after(0, lambda: self._mic.config(fg=C["text_dim"]))
        if text:
            self.root.after(0, lambda: self._insert("YOU", f"🎤 {text}", "user"))
            resp = self.assistant.process(text)
            self.root.after(0, lambda: self._insert("ARIA", resp, "ai"))
            self.root.after(0, lambda: self._set_status("● READY", "ready"))
            if self.tts_on.get():
                threading.Thread(target=self._tts_speak, args=(resp,), daemon=True).start()
        else:
            self.root.after(0, lambda: self._set_status("● READY", "ready"))
            self.root.after(0, lambda: self._insert("ARIA",
                "❓ Didn't catch that. Please try again.", "ai"))

    # ── Voice Mode ───────────────────────────────────

    def _open_voice_mode(self):
        VoiceOnlyWindow(self.root)

    # ── Chat Display ─────────────────────────────────

    def _insert(self, sender, text, kind):
        def do():
            self.chat.config(state="normal")
            ts = datetime.datetime.now().strftime("%H:%M:%S")
            if kind == "user":
                self.chat.insert("end", f" {ts}  ", "ts")
                self.chat.insert("end", "YOU\n", "you_lbl")
                self.chat.insert("end", f"{text}\n\n", "you_txt")
            else:
                self.chat.insert("end", f" {ts}  ", "ts")
                self.chat.insert("end", "ARIA\n", "ai_lbl")
                for line in text.split('\n'):
                    tag = "mono" if line.startswith(('│','├','└','┌','╔','═','║')) else "ai_txt"
                    self.chat.insert("end", line+'\n', tag)
                self.chat.insert("end", "\n")
            self.chat.config(state="disabled")
            self.chat.see("end")
        self.root.after(0, do)

    def _boot_msg(self):
        self._insert("ARIA",
            f"System online. Running on {platform.system()} {platform.release()}.\n"
            "I'm ARIA — your Personal AI Command Automation System.\n"
            "Chat mode: type below. Voice mode: click '🎙 VOICE MODE' or 🎤.\n"
            "Type 'help' to see all available commands.", "ai")

    def _set_status(self, text, state="ready"):
        self.root.after(0, lambda: self._sv.set(text))

    def _update_clock(self):
        self._clk.set(datetime.datetime.now().strftime("%a %d %b  %H:%M:%S"))
        self.root.after(1000, self._update_clock)

    def _toggle_sidebar(self):
        if self._sidebar_vis: self._sidebar.grid_remove()
        else: self._sidebar.grid()
        self._sidebar_vis = not self._sidebar_vis

    def _clear_chat(self):
        self.chat.config(state="normal")
        self.chat.delete("1.0","end")
        self.chat.config(state="disabled")
        self._insert("ARIA","Chat cleared. How can I help you?","ai")

    def _load_speech(self):
        try:
            self.speech = SpeechHandler()
        except Exception as e:
            self._insert("ARIA", f"⚠️ Speech module error: {e}", "ai")

    def run(self):
        self.root.mainloop()


# ══════════════════════════════════════════════════════════════
#  ENTRY POINT
# ══════════════════════════════════════════════════════════════

if __name__ == "__main__":
    print("""
╔════════════════════════════════════════════╗
║   ARIA — AI Command Automation System      ║
║   Version 2.0 | All-in-One                ║
║   Starting up...                           ║
╚════════════════════════════════════════════╝
    """)
    app = ARIAApp()
    app.run()
