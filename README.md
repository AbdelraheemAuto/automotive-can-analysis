# Automotive CAN Bus Logger and Signal Analysis

A personal automotive electronics project for capturing CAN frames through an Uno-compatible board, recording them with Python, isolating selected arbitration IDs, and displaying observed vehicle states.

![Bench hardware setup](images/hardware_setup.jpg)

## Project overview

The project follows this data path:

```text
Vehicle CAN
    ↓
OBD-II connection
    ↓
CAN controller/transceiver module
    ↓
ELEGOO Uno R3-compatible board
    ↓ USB serial
Python tools
    ├── Timestamped CSV logging
    ├── CAN-ID filtering
    ├── RPM display
    └── RPM / brake / lights dashboard
```

The Python programs expect the acquisition board to send one record per line in this format:

```text
arduino_ms,can_id,data
```

Example:

```text
61,1F9,20 00 16 C1 00 00 00 00
```

## What this project demonstrates

- Serial ingestion of CAN records produced by an embedded acquisition interface
- Computer and board timestamps stored in CSV format
- Filtering traffic by CAN arbitration ID
- Byte-level payload inspection during controlled vehicle conditions
- Interpretation of an observed multi-byte engine-speed field
- Terminal display of interpreted RPM, brake, and exterior-light states
- Preservation of real test captures for comparison and validation

## Repository contents

```text
automotive-can-analysis/
├── README.md
├── LICENSE
├── requirements.txt
├── python/
│   ├── can_csv_logger.py
│   ├── can_id_monitor.py
│   ├── specific_action_monitor.py
│   ├── live_rpm.py
│   └── live_dashboard.py
├── sample_data/
│   ├── maxima_dashboard_excerpt.csv
│   └── README.md
└── images/
    └── hardware_setup.jpg
```

## Python tools

| Program | Purpose |
| --- | --- |
| `can_csv_logger.py` | Adds a computer timestamp and records incoming serial CAN data to a timestamped CSV file. |
| `can_id_monitor.py` | Prints payloads for one selected CAN ID for focused observation. |
| `specific_action_monitor.py` | Prints the board timestamp, CAN ID, and payload for a selected ID. |
| `live_rpm.py` | Displays the RPM value observed at CAN ID `0x1F9`, using payload bytes 2–3 and the saved `raw / 8` rule. |
| `live_dashboard.py` | Displays the latest RPM, brake, and exterior-light interpretations encoded during the project. |

## Setup

Requirements:

- Python 3.8 or newer
- A serial-connected acquisition board producing the expected record format
- The `pyserial` package

Create a virtual environment and install the dependency:

```shell
python -m venv .venv
```

On Windows:

```shell
.venv\Scripts\activate
pip install -r requirements.txt
```

Before running a program, update `SERIAL_PORT` near the top of the file if the board is not connected as `COM3`.

Run the CSV logger:

```shell
python python/can_csv_logger.py
```

Run the live dashboard:

```shell
python python/live_dashboard.py
```

Press Ctrl+C to stop either program.

## Observed signal interpretations

The surviving dashboard code contains the following project observations for a 2010 Nissan Maxima capture:

| CAN ID | Payload field | Interpretation used by the program |
| --- | --- | --- |
| `0x1F9` | Bytes 2–3, big-endian | `RPM = raw / 8` |
| `0x354` | Byte 6 | `0x14` = brake on; `0x04` = brake off |
| `0x625` | Byte 1 | `0x00` = off; `0x40` = DRL; `0x60` = low beam; `0x70` = high beam |

These mappings are experimental observations encoded in the surviving programs. They are not manufacturer documentation, a complete DBC, or a claim that the same definitions apply to another model or year.

## Sample data

`sample_data/maxima_dashboard_excerpt.csv` contains a small excerpt from the saved engine-on/revving capture. It includes only the three IDs used by the dashboard so reviewers can understand the input format without publishing the complete capture.

For example, the first RPM frame contains bytes `16 C1` at payload positions 2–3:

```text
raw = 0x16C1 = 5825
RPM = 5825 / 8 = 728.125
displayed RPM = 728
```

## Project history and limitations

The embedded acquisition sketch originally uploaded to the board is no longer available. This repository therefore documents and publishes the surviving Python logging and analysis tools only. It does not recreate the missing sketch or claim authorship of firmware that cannot be verified.

The photographs confirm the physical bench assembly, but the surviving artifacts do not independently establish the acquisition firmware's CAN bitrate, oscillator setting, library, or operating mode. Those details are intentionally left unspecified.

The included Python programs consume serial data; they do not transmit CAN frames.

## Safety and responsible use

Work on vehicle networks can affect vehicle operation. Use appropriate isolation and protection, prefer passive observation, and do not experiment on public roads. Do not publish employer, customer, proprietary, security-sensitive, or personally identifying vehicle data.

## Future improvements

- Accept the serial port and target CAN ID as command-line options
- Validate malformed hexadecimal payloads without interrupting a session
- Add automated tests using recorded or simulated serial input
- Plot changing signals over time
- Record confirmed observations in a small DBC or signal-definition file
- Rebuild and document an independently authored acquisition firmware component

## License

Released under the MIT License. See `LICENSE`.
