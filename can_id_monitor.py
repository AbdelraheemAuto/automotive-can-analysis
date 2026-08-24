"""Display payloads received for one CAN arbitration ID."""

import time

import serial


SERIAL_PORT = "COM3"
BAUD_RATE = 115200
SERIAL_TIMEOUT_SECONDS = 1
BOARD_STARTUP_DELAY_SECONDS = 2
TARGET_CAN_ID = "164"


def run_monitor() -> None:
    """Print payloads matching TARGET_CAN_ID until the user presses Ctrl+C."""
    serial_connection = serial.Serial(
        SERIAL_PORT,
        BAUD_RATE,
        timeout=SERIAL_TIMEOUT_SECONDS,
    )

    try:
        time.sleep(BOARD_STARTUP_DELAY_SECONDS)
        print(f"Watching CAN ID 0x{TARGET_CAN_ID}")
        print("Press/release brake and watch data.\n")

        try:
            while True:
                line = serial_connection.readline().decode(errors="ignore").strip()
                if not line or line.startswith("CAN"):
                    continue

                fields = line.split(",")
                if len(fields) != 3:
                    continue

                _arduino_ms, can_id, data = fields
                if can_id.upper() == TARGET_CAN_ID:
                    print(data)
        except KeyboardInterrupt:
            print("\nStopped.")
    finally:
        serial_connection.close()


if __name__ == "__main__":
    run_monitor()
