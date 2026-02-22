#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import json, os, subprocess

CONFIG_PATH = "/home/pi/X8_Companion/config/X8_config.json"

def load_config():
    with open(CONFIG_PATH, 'r', encoding='utf-8') as f: return json.load(f)

def save_config(config):
    with open(CONFIG_PATH, 'w', encoding='utf-8') as f: json.dump(config, f, indent=4)

def get_service_status(service):
    res = os.system(f"systemctl is-active --quiet {service}")
    return "RUNNING" if res == 0 else "STOPPED"

def get_cpu_temp():
    try:
        with open("/sys/class/thermal/thermal_zone0/temp", "r") as f:
            return f"{float(f.read()) / 1000:.1f}C"
    except: return "N/A"

def menu(title, options):
    cmd = ["whiptail", "--title", title, "--menu", "Wybierz:", "22", "78", "14"]
    for k, v in options.items(): cmd.extend([k, v])
    proc = subprocess.Popen(cmd, stderr=subprocess.PIPE)
    return proc.communicate()[1].decode('utf-8', 'ignore').strip()

def input_box(title, prompt, default):
    cmd = ["whiptail", "--title", title, "--inputbox", prompt, "10", "65", str(default)]
    proc = subprocess.Popen(cmd, stderr=subprocess.PIPE)
    return proc.communicate()[1].decode('utf-8', 'ignore').strip()

def edit_ntrip():
    cfg = load_config()
    while True:
        opt = {
            "1": f"Server: {cfg['ntrip']['server']}",
            "2": f"Port:   {cfg['ntrip']['port']}",
            "3": f"Mount:  {cfg['ntrip']['mount']}",
            "4": f"User:   {cfg['ntrip']['user']}",
            "5": f"Pass:   {cfg['ntrip']['pass']}",
            "6": f"Pos:    {cfg['ntrip']['base_lat']}/{cfg['ntrip']['base_lon']} ({cfg['ntrip']['base_alt']}m)",
            "B": "POWROT"
        }
        c = menu("NTRIP Settings", opt)
        if c == "1":
            nv = input_box("NTRIP", "Host:", cfg['ntrip']['server'])
            if nv: cfg['ntrip']['server'] = nv
        elif c == "2":
            nv = input_box("NTRIP", "Port:", cfg['ntrip']['port'])
            if nv: cfg['ntrip']['port'] = int(nv)
        elif c == "3":
            nv = input_box("NTRIP", "Mountpoint:", cfg['ntrip']['mount'])
            if nv: cfg['ntrip']['mount'] = nv
        elif c == "4":
            nv = input_box("NTRIP", "User:", cfg['ntrip']['user'])
            if nv: cfg['ntrip']['user'] = nv
        elif c == "5":
            nv = input_box("NTRIP", "Pass:", cfg['ntrip']['pass'])
            if nv: cfg['ntrip']['pass'] = nv
        elif c == "6": 
            lat = input_box("NTRIP", "Lat:", cfg['ntrip']['base_lat'])
            lon = input_box("NTRIP", "Lon:", cfg['ntrip']['base_lon'])
            alt = input_box("NTRIP", "Alt:", cfg['ntrip']['base_alt'])
            if lat: cfg['ntrip']['base_lat'] = float(lat)
            if lon: cfg['ntrip']['base_lon'] = float(lon)
            if alt: cfg['ntrip']['base_alt'] = float(alt)
        elif c == "B" or not c: break
        save_config(cfg)

def edit_network():
    cfg = load_config()
    while True:
        wifi_ip = subprocess.getoutput("ip -4 addr show wlan0 2>/dev/null | grep -oP '(?<=inet\\s)\\d+(\\.\\d+){3}'").strip()
        lte_ip = subprocess.getoutput("ip -4 addr show usb0 2>/dev/null | grep -oP '(?<=inet\\s)\\d+(\\.\\d+){3}'").strip()
        link_status = "LTE" if lte_ip else ("WIFI" if wifi_ip else "NONE")

        opt = {
            "1": f"UAV ZT IP (Local):  {cfg['mavlink'].get('uav_zt_ip', '')}",
            "2": f"GCS ZT IP (Target): {cfg['mavlink'].get('gcs_zt_ip', '')}",
            "3": f"GCS WiFi IP (PC):   {cfg['mavlink'].get('gcs_local_ip', '')}",
            "4": f"INFO: UAV WiFi IP:   {wifi_ip if wifi_ip else 'OFFLINE'}",
            "5": f"INFO: LINK STATUS:   {link_status}",
            "6": "TEST: Ping GCS (ZeroTier)",
            "7": "TEST: Ping GCS (WiFi)",
            "8": "ACTION: DISABLE WIFI",
            "B": "POWROT"
        }
        c = menu("Network & ZeroTier Settings", opt)
        
        if c == "1":
            nv = input_box("Net", "UAV ZT IP:", cfg['mavlink'].get('uav_zt_ip', ''))
            if nv: cfg['mavlink']['uav_zt_ip'] = nv
        elif c == "2":
            nv = input_box("Net", "GCS ZT IP:", cfg['mavlink'].get('gcs_zt_ip', ''))
            if nv: cfg['mavlink']['gcs_zt_ip'] = nv
        elif c == "3":
            nv = input_box("Net", "GCS WiFi IP:", cfg['mavlink'].get('gcs_local_ip', ''))
            if nv: cfg['mavlink']['gcs_local_ip'] = nv
        elif c == "6": 
            os.system(f"ping -c 3 {cfg['mavlink'].get('gcs_zt_ip', '')}; read -p 'Enter...'")
        elif c == "7": 
            os.system(f"ping -c 3 {cfg['mavlink'].get('gcs_local_ip', '')}; read -p 'Enter...'")
        elif c == "8":
            if os.system("whiptail --title 'POTWIERDZ' --yesno 'Wylaczyc WiFi? Zostanie tylko LTE/ZT.' 8 45") == 0:
                os.system("sudo ifconfig wlan0 down")
                break
        elif c == "B" or not c: break
        save_config(cfg)

def edit_system():
    cfg = load_config()
    while True:
        opt = {
            "1": f"Drone Name:   {cfg['system']['drone_name']}",
            "2": f"Companion ID: {cfg['system']['sysid_companion']}",
            "3": f"Target ID:    {cfg['system']['sysid_target']}",
            "4": f"UART FC:      {cfg['mavlink']['fc_uart']} ({cfg['mavlink']['fc_baud']})",
            "5": f"UART SiK:     {cfg['mavlink']['sik_uart']} ({cfg['mavlink']['sik_baud']})",
            "B": "POWROT"
        }
        c = menu("MAVLink & Hardware Settings", opt)
        if c == "1":
            nv = input_box("Sys", "Name:", cfg['system']['drone_name'])
            if nv: cfg['system']['drone_name'] = nv
        elif c == "2":
            nv = input_box("MAV", "CompID:", cfg['system']['sysid_companion'])
            if nv: cfg['system']['sysid_companion'] = int(nv)
        elif c == "3":
            nv = input_box("MAV", "TargetID:", cfg['system']['sysid_target'])
            if nv: cfg['system']['sysid_target'] = int(nv)
        elif c == "4": 
            u = input_box("Ser", "Port FC:", cfg['mavlink']['fc_uart'])
            b = input_box("Ser", "Baud FC:", cfg['mavlink']['fc_baud'])
            if u: cfg['mavlink']['fc_uart'] = u
            if b: cfg['mavlink']['fc_baud'] = int(b)
        elif c == "5": 
            u = input_box("Ser", "Port SiK:", cfg['mavlink']['sik_uart'])
            b = input_box("Ser", "Baud SiK:", cfg['mavlink']['sik_baud'])
            if u: cfg['mavlink']['sik_uart'] = u
            if b: cfg['mavlink']['sik_baud'] = int(b)
        elif c == "B" or not c: break
        save_config(cfg)

if __name__ == "__main__":
    while True:
        rtk_s = get_service_status("x8_rtk.service")
        mav_s = get_service_status("x8_mavproxy.service")
        temp = get_cpu_temp()
        m = {
            "1": "NTRIP Settings (RTK)",
            "2": "Network & LTE (BVLOS)",
            "3": "MAVLink & Hardware",
            "4": f"RESTART: RTK[{rtk_s}] MAV[{mav_s}]",
            "5": f"SYSTEM POWER (CPU: {temp})",
            "Q": "WYJSCIE"
        }
        choice = menu("X8 BVLOS PRO CONTROL PANEL", m)
        if choice == "1": edit_ntrip()
        elif choice == "2": edit_network()
        elif choice == "3": edit_system()
        elif choice == "4": 
            os.system("sudo systemctl restart x8_mavproxy.service x8_rtk.service")
        elif choice == "5":
            p_opt = {"1": "SHUTDOWN", "2": "REBOOT", "B": "POWROT"}
            p_choice = menu(f"ZASILANIE (CPU: {temp})", p_opt)
            if p_choice == "1": os.system("sudo shutdown -h now")
            elif p_choice == "2": os.system("sudo reboot")
        elif choice == "Q" or not choice: break
