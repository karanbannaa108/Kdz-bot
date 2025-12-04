import streamlit as st
import subprocess
import os
import psutil
import signal
import time
from datetime import datetime

st.set_page_config(page_title("My Bots Dashboard")
st.set_page_config(layout="wide")

# ── Bots List (yahan apne bots add karte jao) ─────────────────────
BOTS = {
    "Trading Bot": "python trading_bot.py",
    "Telegram Bot": "python telegram_bot.py",
    "Discord Bot": "python discord_bot.py",
    "Instagram Scraper": "python scraper.py",
    "Auto Poster": "python poster.py"
}

# PID folder
if not os.path.exists("pids"):
    os.makedirs("pids")

def get_pid(name):
    try:
        with open(f"pids/{name}.pid") as f:
            pid = int(f.read())
        return pid if psutil.pid_exists(pid) else None
    except:
        return None

def save_pid(name, pid):
    with open(f"pids/{name}.pid", "w") as f:
        f.write(str(pid))

def start_bot(name, cmd):
    if get_pid(name):
        return
    proc = subprocess.Popen(
        cmd.split(),
        cwd=os.getcwd(),
        stdout=open(f"logs/{name.replace(' ', '_')}.log", "a"),
        stderr=subprocess.STDOUT
    )
    save_pid(name, proc.pid)

def stop_bot(name):
    pid = get_pid(name)
    if pid:
        try:
            os.kill(pid, signal.SIGTERM)
            time.sleep(1)
            if psutil.pid_exists(pid):
                os.kill(pid, signal.SIGKILL)
        except:
            pass
        if os.path.exists(f"pids/{name}.pid"):
            os.remove(f"pids/{name}.pid")

# Logs folder
os.makedirs("logs", exist_ok=True)
os.makedirs("pids", exist_ok=True)

st.title("Python Bots Control Panel")
st.markdown("---")

# Auto refresh every 5 seconds
st.autorefresh(interval=5000, key="refresh")

col1, col2, col3 = st.columns([3,1,1])
with col2:
    if st.button("Stop All", type="primary"):
        for n in BOTS:
            stop_bot(n)
        st.success("All bots stopped!")
with col3:
    if st.button("Restart All"):
        for n,c in BOTS.items():
            stop_bot(n)
            time.sleep(0.5)
            start_bot(n, c)
        st.success("All restarted!")

st.markdown("---")

for bot_name, command in BOTS.items():
    col1, col2, col3, col4 = st.columns([3,1,1,2])
    pid = get_pid(bot_name)
    is_running = pid is not None

    with col1:
        st.subheader(f"{bot_name}")
    with col2:
        if is_running:
            st.success(f"Running (PID: {pid})")
        else:
            st.error("Stopped")
    with col3:
        if is_running:
            if st.button("Stop", key=f"stop_{bot_name}"):
                stop_bot(bot_name)
                st.rerun()
        else:
            if st.button("Start", key=f"start_{bot_name}", type="primary"):
                start_bot(bot_name, command)
                st.rerun()
    with col4:
        if is_running and st.button("Restart", key=f"restart_{bot_name}"):
            stop_bot(bot_name)
            time.sleep(0.5)
            start_bot(bot_name, command)
            st.rerun()

st.markdown("---")
st.header("Live Logs")

selected = st.selectbox("Bot select karo", ["None"] + list(BOTS.keys()))
if selected != "None":
    log_file = f"logs/{selected.replace(' ', '_')}.log"
    if os.path.exists(log_file):
        with open(log_file, "r", encoding="utf-8") as f:
            lines = f.readlines()[-100:]
        for line in lines:
            st.text(line.rstrip())
    else:
        st.info("Log abhi tak nahi bana")
