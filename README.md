# X8 Drone Companion - Pi Zero 2 W

System komputera pokładowego dla drona X8, odpowiedzialny za telemetrię LTE, wstrzykiwanie poprawek RTK oraz monitoring linków komunikacyjnych.

## Architektura Sprzetowa
- **Komputer:** Raspberry Pi Zero 2 W
- **Flight Controller:** Kakute H7 (ArduPilot)
- **Polaczenie:** UART (@ttyAMA0) - Baud: 921600
- **Link zapasowy:** SiK Radio 433MHz (bezposrednio do FC)

## Konfiguracja Systemowa (OS)
Pakiety zainstalowane systemowo:
- git, usb-modeswitch, modemmanager, network-manager

## Struktura Uslug (systemd)
1. **x8_mavproxy.service**: Telemetria i routing MAVLink.
2. **x8_rtk.service**: Wstrzykiwanie poprawek RTK.
3. **x8_monitors.service**: Monitoring dostepnosci LTE i SiK.

## Konfiguracja MAVLink (MAVProxy)
- Master: `/dev/ttyAMA0` (921600 baud)
- GCS LTE: `10.148.178.3:14550`
- GCS Local: `192.168.1.115:14550`

## Srodowisko Python
Wymagane biblioteki znajduja sie w pliku `requirements.txt`.
Instalacja: `pip install -r requirements.txt`

---
*Aktualizacja: 2026-02-21*
