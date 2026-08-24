"""Log comma-separated CAN frames received over serial to a CSV file.

Expected input from the acquisition board:
    arduino_ms,can_id,data

The original acquisition firmware is not included in this project archive.
"""

import csv
import time
from datetime import datetime
from typing import Optional, Tuple

import serial


SERIAL_PORT = "COM3"
BAUD_RATE = 115200
SERIAL_TIMEOUT_SECONDS = 1
BOARD_STARTUP_DELAY_SECONDS = 2
CSV_HEADER = ("pc_time", "arduino_ms", "can_id", "data")


def parse_serial_record(line: str) -> Optional[Tuple[str, str, str]]:
    """Return the expected fields, or None when a line is unusable."""
    if not line or line.startswith("CAN"):
        return None

    fields = line.split(",")
    if len(fields) != 3:
        return None

    arduino_ms, can_id, data = fields
    return arduino_ms, can_id, data


def build_output_filename() -> str:
    """Build the timestamped filename used by the original logger."""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    return f"can_log_{timestamp}.csv"


def run_logger() -> None:
    """Read serial CAN records until the user presses Ctrl+C."""
    output_filename = build_output_filename()
    serial_connection = serial.Serial(
        SERIAL_PORT,
        BAUD_RATE,
        timeout=SERIAL_TIMEOUT_SECONDS,
    )

    try:
        time.sleep(BOARD_STARTUP_DELAY_SECONDS)
        print(f"Logging CAN data to: {output_filename}")
        print("Press CTRL+C to stop.\n")

        with open(output_filename, "w", newline="") as csv_file:
            writer = csv.writer(csv_file)
            writer.writerow(CSV_HEADER)

            try:
                while True:
                    line = serial_connection.readline().decode(errors="ignore").strip()
                    record = parse_serial_record(line)
                    if record is None:
                        continue

                    arduino_ms, can_id, data = record
                    pc_time = datetime.now().strftime("%H:%M:%S.%f")[:-3]
                    writer.writerow((pc_time, arduino_ms, can_id, data))
                    print(pc_time, arduino_ms, can_id, data)
            except KeyboardInterrupt:
                print("\nLogging stopped.")
    finally:
        serial_connection.close()


if __name__ == "__main__":
    run_logger()
