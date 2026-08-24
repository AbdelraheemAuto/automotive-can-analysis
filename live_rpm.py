"""Display the observed engine-speed signal from live CAN traffic."""

import time
from typing import List

import serial


SERIAL_PORT = "COM3"
BAUD_RATE = 115200
SERIAL_TIMEOUT_SECONDS = 1
BOARD_STARTUP_DELAY_SECONDS = 2
RPM_CAN_ID = "1F9"


def decode_rpm(data_bytes: List[str]) -> float:
    """Decode bytes 2-3 as a big-endian value using the observed /8 scale."""
    raw_value = int(data_bytes[2] + data_bytes[3], 16)
    return raw_value / 8


def run_display() -> None:
    """Display RPM values until the user presses Ctrl+C."""
    serial_connection = serial.Serial(
        SERIAL_PORT,
        BAUD_RATE,
        timeout=SERIAL_TIMEOUT_SECONDS,
    )

    try:
        time.sleep(BOARD_STARTUP_DELAY_SECONDS)
        print("Live RPM Display Started")
        print("Using CAN ID 0x1F9, bytes 2-3, RPM = raw / 8")
        print("Press CTRL+C to stop.\n")

        try:
            while True:
                line = serial_connection.readline().decode(errors="ignore").strip()
                if not line or line.startswith("CAN"):
                    continue

                fields = line.split(",")
                if len(fields) != 3:
                    continue

                _arduino_ms, can_id, data = fields
                if can_id.upper() != RPM_CAN_ID:
                    continue

                data_bytes = data.split()
                if len(data_bytes) < 4:
                    continue

                rpm = decode_rpm(data_bytes)
                print(f"RPM: {rpm:.0f}")
        except KeyboardInterrupt:
            print("\nStopped.")
    finally:
        serial_connection.close()


if __name__ == "__main__":
    run_display()
