#!/bin/bash
sleep 2
cd /home/pi/X8_Companion/

# Zabijamy stare procesy, ¿eby porty by³y wolne
killall -9 mavproxy.py python3 2>/dev/null

/home/pi/X8_Companion/venv/bin/python3 /home/pi/X8_Companion/venv/bin/mavproxy.py \
--master=/dev/ttyAMA0 --baud=921600 \
--master=udpin:127.0.0.1:14551 \
--out=udp:192.168.1.115:14550 \
--out=udp:10.148.178.3:14550 \
--out=udp:10.148.178.64:14552 \
--aircraft="logs" --daemon --non-interactive