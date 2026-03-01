#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import json, socket, time, base64, threading, serial
from pymavlink import mavutil

CONFIG_PATH = "/home/pi/X8_Companion/config/X8_config.json"

def get_nmea_gga(lat, lon, alt):
    now = time.strftime("%H%M%S.00", time.gmtime())
    lat_d = f"{abs(lat)//1:02.0f}{abs(lat)%1*60:07.4f}"
    lat_n = 'N' if lat >= 0 else 'S'
    lon_d = f"{abs(lon)//1:03.0f}{abs(lon)%1*60:07.4f}"
    lon_e = 'E' if lon >= 0 else 'W'
    msg = f"GPGGA,{now},{lat_d},{lat_n},{lon_d},{lon_e},1,12,1.0,{alt},M,0.0,M,,"
    checksum = 0
    for char in msg:
        checksum ^= ord(char)
    return f"${msg}*{checksum:02X}\r\n"

def heartbeat_thread(mav):
    while True:
        mav.mav.heartbeat_send(
            mavutil.mavlink.MAV_TYPE_GCS,
            mavutil.mavlink.MAV_AUTOPILOT_INVALID,
            0, 0, 0
        )
        time.sleep(1)

def run_injector():
    with open(CONFIG_PATH, 'r') as f:
        cfg = json.load(f)['ntrip']

    print("Inicjalizacja MAVLink Connection...")

    # Wymuœ w³aœciwy dialect
    mavutil.set_dialect("ardupilotmega")

    mav = mavutil.mavlink_connection(

        'udpout:127.0.0.1:14551',
        source_system=255,
        source_component=190
    )


    # Wyœlij pierwszy heartbeat natychmiast
    mav.mav.heartbeat_send(
        mavutil.mavlink.MAV_TYPE_GCS,
        mavutil.mavlink.MAV_AUTOPILOT_INVALID,
        0, 0, 0
    )

    # Uruchom heartbeat w tle
    threading.Thread(target=heartbeat_thread, args=(mav,), daemon=True).start()

    auth = base64.b64encode(f"{cfg['user']}:{cfg['pass']}".encode()).decode()
    last_nmea = 0

    while True:
        try:
            print(f"Laczenie z serwerem NTRIP: {cfg['server']}...")
            sock = socket.socket(socket.getaddrinfo(cfg['server'], cfg['port'])[0][0], socket.SOCK_STREAM)
            sock.settimeout(10)
            sock.connect((cfg['server'], int(cfg['port'])))

            headers = (f"GET /{cfg['mount']} HTTP/1.0\r\n"
                       f"User-Agent: NTRIP PythonClient\r\n"
                       f"Authorization: Basic {auth}\r\n"
                       f"Connection: close\r\n\r\n")
            sock.sendall(headers.encode())

            while True:
                if time.time() - last_nmea > 5:
                    nmea = get_nmea_gga(cfg['base_lat'], cfg['base_lon'], cfg['base_alt'])
                    sock.sendall(nmea.encode())
                    last_nmea = time.time()

                data = sock.recv(2048)
                if not data:
                    break



                # WYSY£KA NA UART2 (piny 27/28)

                if ser and ser.is_open:
                    ser.write(data); ser.flush()





                # WYSY£KA MAVLINK (Oryginalna pêtla) 

                length = len(data)
                for i in range(0, length, 180):
                    chunk = data[i:i+180]
                    chunk_len = len(chunk)
                    padding = b'\x00' * (180 - chunk_len)

                    mav.mav.gps_rtcm_data_send(
                        0,
                        chunk_len,
                        chunk + padding
                    )

                print(f"Przeslano do FC: {len(data)} bajtow (jako MAVLink)")

        except Exception as e:
            print(f"Blad: {e}. Reconnect za 5s...")
            time.sleep(5)

if __name__ == "__main__":
    run_injector()