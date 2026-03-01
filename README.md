# X8 Drone Companion - Pi Zero 2 W

System komputera pokładowego dla drona X8, odpowiedzialny za telemetrię LTE, wstrzykiwanie poprawek RTK oraz monitoring linków komunikacyjnych.

## Architektura Sprzętowa
* **Komputer:** Raspberry Pi Zero 2 W
* **Flight Controller:** Kakute H7 (ArduPilot)
* **GNSS:** Unicore UM982 (NebulasIV) + 2x Antena HA-901
* **Połączenie FC-RPI:** UART (@ttyAMA0) - Baud: 921600
* **Połączenie RPI-GNSS:** Adapter USB-TTL - Baud: 115200
* **Link zapasowy:** SiK Radio 433MHz (bezpośrednio do FC)

## Konfiguracja Systemowa (OS)
Pakiety zainstalowane systemowo: `git`, `usb-modeswitch`, `modemmanager`, `network-manager`.

## Struktura Usług (systemd)
* `x8_mavproxy.service`: Telemetria i routing MAVLink.
* `x8_rtk.service`: Wstrzykiwanie poprawek RTK (NTRIP -> UM982).
* `x8_monitors.service`: Monitoring dostępności LTE i SiK.

## Moduł RTK (UM982)
Kluczowe komendy konfiguracji (zgodnie z manualem N4 R1.13):
* `CONFIG COM2 115200 8 N 1`
* `CONFIG HEADING LENGTH 0.53 0.01`
* `CONFIG RTK ANYSTATION ENABLE`
* `SAVECONFIG`

## Środowisko Python
Instalacja wszystkich zależności (MavProxy + RTK):
`pip install -r requirements.txt`
