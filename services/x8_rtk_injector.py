#!/usr/bin/env python3
import json, socket, time, base64
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
    for char in msg: checksum ^= ord(char)
    return f"${msg}*{checksum:02X}\r\n"

def run_injector():
    with open(CONFIG_PATH, 'r') as f: cfg = json.load(f)['ntrip']
    
    # Inicjalizacja polaczenia MAVLink do MAVProxy (port 14551)
    print("Inicjalizacja MAVLink Connection...")
    mav = mavutil.mavlink_connection('udpout:127.0.0.1:14551', source_system=255, source_component=250)
    
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
                # Wysylaj pozycje GGA co 5 sekund do serwera NTRIP
                if time.time() - last_nmea > 5:
                    nmea = get_nmea_gga(cfg['base_lat'], cfg['base_lon'], cfg['base_alt'])
                    sock.sendall(nmea.encode())
                    last_nmea = time.time()
                
                data = sock.recv(2048)
                if not data: break
                
                # Pakowanie surowego RTCM w ramki MAVLink (GPS_RTCM_DATA)
                # Max rozmiar danych w jednej ramce to 180 bajtow
                length = len(data)
                for i in range(0, length, 180):
                    chunk = data[i:i+180]
                    chunk_len = len(chunk)
                    # Uzupelnienie zerami do 180 bajtow (wymog Mavlink)
                    padding = b'\x00' * (180 - chunk_len)
                    
                    mav.mav.gps_rtcm_data_send(
                        0, # flags: 0 = brak fragmentacji lub prosta paczka
                        chunk_len,
                        chunk + padding
                    )
                
                # Opcjonalnie: Wysylaj Heartbeat, aby MAVProxy widzialo Injector jako komponent 250
                mav.mav.heartbeat_send(mavutil.mavlink.MAV_TYPE_GCS, mavutil.mavlink.MAV_AUTOPILOT_INVALID, 0, 0, 0)
                
                print(f"Przeslano do FC: {len(data)} bajtow (jako MAVLink)")
                
        except Exception as e:
            print(f"Blad: {e}. Reconnect za 5s...")
            time.sleep(5)

if __name__ == "__main__":
    run_injector()