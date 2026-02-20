#!/usr/bin/env python3
import socket, base64, time, json
from pymavlink import mavutil

CONFIG_PATH = "/home/pi/X8_Companion/config/X8_config.json"

class RTKInjector:
    def __init__(self):
        with open(CONFIG_PATH, 'r') as f: self.cfg = json.load(f)
        self.mav = mavutil.mavlink_connection('udpin:127.0.0.1:14551')
        self.lat = self.cfg['ntrip']['base_lat']
        self.lon = self.cfg['ntrip']['base_lon']
        self.alt = self.cfg['ntrip']['base_alt']

    def get_gga(self):
        msg = self.mav.recv_match(type='GLOBAL_POSITION_INT', blocking=False)
        if msg:
            self.lat, self.lon, self.alt = msg.lat/1e7, msg.lon/1e7, msg.alt/1000
        
        now = time.gmtime()
        ts = time.strftime("%H%M%S.00", now)
        msg_str = f"GPGGA,{ts},{abs(int(self.lat))}{abs(self.lat-int(self.lat))*60:07.4f},{'N' if self.lat>0 else 'S'},{abs(int(self.lon)):03}{abs(self.lon-int(self.lon))*60:07.4f},{'E' if self.lon>0 else 'W'},1,12,1.0,{self.alt},M,0.0,M,,"
        ck = 0
        for c in msg_str: ck ^= ord(c)
        return f"${msg_str}*{format(ck, '02X')}\r\n"

    def run(self):
        print(f"Start RTK Injector: {self.cfg['ntrip']['server']}")
        while True:
            try:
                s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                s.settimeout(10)
                s.connect((self.cfg['ntrip']['server'], self.cfg['ntrip']['port']))
                
                auth_str = f"{self.cfg['ntrip']['user']}:{self.cfg['ntrip']['pass']}"
                auth = base64.b64encode(auth_str.encode()).decode()
                
                headers = (
                    f"GET /{self.cfg['ntrip']['mount']} HTTP/1.0\r\n"
                    f"User-Agent: NTRIP X8\r\n"
                    f"Authorization: Basic {auth}\r\n"
                    f"Connection: close\r\n\r\n"
                )
                s.sendall(headers.encode())
                
                last_gga = 0
                while True:
                    if time.time() - last_gga > 10:
                        s.sendall(self.get_gga().encode())
                        last_gga = time.time()
                    
                    data = s.recv(2048)
                    if not data: break
                    
                    for i in range(0, len(data), 180):
                        chunk = data[i:i+180]
                        self.mav.mav.gps_rtcm_data_send(0, len(chunk), chunk.ljust(180, b'\0'))
            except Exception as e:
                print(f"Błąd: {e}"); time.sleep(5)

if __name__ == "__main__":
    RTKInjector().run()
