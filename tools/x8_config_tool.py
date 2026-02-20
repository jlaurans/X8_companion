#!/usr/bin/env python3
import json, os, subprocess

CONFIG_PATH = "/home/pi/X8_Companion/config/X8_config.json"

def load_config():
    with open(CONFIG_PATH, 'r') as f: return json.load(f)

def save_config(config):
    with open(CONFIG_PATH, 'w') as f: json.dump(config, f, indent=4)

def menu(title, options):
    cmd = ["whiptail", "--title", title, "--menu", "Wybierz:", "22", "78", "14"]
    for k, v in options.items(): cmd.extend([k, v])
    proc = subprocess.Popen(cmd, stderr=subprocess.PIPE)
    return proc.communicate()[1].decode().strip()

def input_box(title, prompt, default):
    cmd = ["whiptail", "--title", title, "--inputbox", prompt, "10", "65", str(default)]
    proc = subprocess.Popen(cmd, stderr=subprocess.PIPE)
    return proc.communicate()[1].decode().strip()

def edit_ntrip():
    cfg = load_config()
    while True:
        opt = {
            "1": f"Server: {cfg['ntrip']['server']}",
            "2": f"Port:   {cfg['ntrip']['port']}",
            "3": f"Mount:  {cfg['ntrip']['mount']}",
            "4": f"User:   {cfg['ntrip']['user']}",
            "5": f"Pass:   {cfg['ntrip']['pass']}",
            "6": f"Lat/Lon: {cfg['ntrip']['base_lat']}/{cfg['ntrip']['base_lon']}",
            "B": "POWRÓT"
        }
        c = menu("NTRIP Settings", opt)
        if c == "1": cfg['ntrip']['server'] = input_box("NTRIP", "Host:", cfg['ntrip']['server'])
        elif c == "2": cfg['ntrip']['port'] = int(input_box("NTRIP", "Port:", cfg['ntrip']['port']))
        elif c == "3": cfg['ntrip']['mount'] = input_box("NTRIP", "Mountpoint:", cfg['ntrip']['mount'])
        elif c == "4": cfg['ntrip']['user'] = input_box("NTRIP", "User:", cfg['ntrip']['user'])
        elif c == "5": cfg['ntrip']['pass'] = input_box("NTRIP", "Pass:", cfg['ntrip']['pass'])
        elif c == "6": 
            cfg['ntrip']['base_lat'] = float(input_box("NTRIP", "Lat:", cfg['ntrip']['base_lat']))
            cfg['ntrip']['base_lon'] = float(input_box("NTRIP", "Lon:", cfg['ntrip']['base_lon']))
        elif c == "B" or not c: break
        save_config(cfg)

def edit_network():
    cfg = load_config()
    while True:
        opt = {
            "1": f"GCS WiFi IP: {cfg['mavlink']['gcs_local_ip']}",
            "2": f"GCS ZT IP:   {cfg['mavlink']['gcs_zt_ip']}",
            "3": f"UAV ZT IP:   {cfg['system']['uav_zt_ip']}",
            "4": f"GCS Port:    {cfg['mavlink']['gcs_port']}",
            "5": f"LTE APN:     {cfg['lte_modem']['apn']}",
            "6": f"LTE PIN:     {cfg['lte_modem']['pin']}",
            "B": "POWRÓT"
        }
        c = menu("Network & LTE Settings", opt)
        if c == "1": cfg['mavlink']['gcs_local_ip'] = input_box("Net", "GCS WiFi IP:", cfg['mavlink']['gcs_local_ip'])
        elif c == "2": cfg['mavlink']['gcs_zt_ip'] = input_box("Net", "GCS ZT IP:", cfg['mavlink']['gcs_zt_ip'])
        elif c == "3": cfg['system']['uav_zt_ip'] = input_box("Net", "UAV ZT IP:", cfg['system']['uav_zt_ip'])
        elif c == "4": cfg['mavlink']['gcs_port'] = int(input_box("Net", "GCS Port:", cfg['mavlink']['gcs_port']))
        elif c == "5": cfg['lte_modem']['apn'] = input_box("LTE", "APN:", cfg['lte_modem']['apn'])
        elif c == "6": cfg['lte_modem']['pin'] = input_box("LTE", "PIN:", cfg['lte_modem']['pin'])
        elif c == "B" or not c: break
        save_config(cfg)

def edit_system():
    cfg = load_config()
    while True:
        opt = {
            "1": f"Drone Name: {cfg['system']['drone_name']}",
            "2": f"Companion ID: {cfg['system']['sysid_companion']}",
            "3": f"Target ID:    {cfg['system']['sysid_target']}",
            "4": f"UART FC:      {cfg['mavlink']['fc_uart']} ({cfg['mavlink']['fc_baud']})",
            "5": f"UART SiK:     {cfg['mavlink']['sik_uart']} ({cfg['mavlink']['sik_baud']})",
            "B": "POWRÓT"
        }
        c = menu("MAVLink & Hardware Settings", opt)
        if c == "1": cfg['system']['drone_name'] = input_box("Sys", "Name:", cfg['system']['drone_name'])
        elif c == "2": cfg['system']['sysid_companion'] = int(input_box("MAV", "CompID:", cfg['system']['sysid_companion']))
        elif c == "3": cfg['system']['sysid_target'] = int(input_box("MAV", "TargetID:", cfg['system']['sysid_target']))
        elif c == "4":
            cfg['mavlink']['fc_uart'] = input_box("Ser", "Port FC:", cfg['mavlink']['fc_uart'])
            cfg['mavlink']['fc_baud'] = int(input_box("Ser", "Baud FC:", cfg['mavlink']['fc_baud']))
        elif c == "5":
            cfg['mavlink']['sik_uart'] = input_box("Ser", "Port SiK:", cfg['mavlink']['sik_uart'])
            cfg['mavlink']['sik_baud'] = int(input_box("Ser", "Baud SiK:", cfg['mavlink']['sik_baud']))
        elif c == "B" or not c: break
        save_config(cfg)

if __name__ == "__main__":
    while True:
        m = {"1": "NTRIP Settings", "2": "Network & LTE", "3": "MAVLink & Hardware", "4": "RESTART SERVICES", "Q": "WYJŚCIE"}
        choice = menu("X8 BVLOS PRO CONTROL PANEL", m)
        if choice == "1": edit_ntrip()
        elif choice == "2": edit_network()
        elif choice == "3": edit_system()
        elif choice == "4": os.system("sudo systemctl restart x8_mavproxy.service x8_rtk.service")
        elif choice == "Q" or not choice: break
