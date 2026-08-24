"""Show observed RPM, brake, and exterior-light states from live CAN data."""

import time
from typing import List

import serial


SERIAL_PORT = "COM3"
BAUD_RATE = 115200
SERIAL_TIMEOUT_SECONDS = 1
BOARD_STARTUP_DELAY_SECONDS = 2

RPM_CAN_ID = "1F9"
BRAKE_CAN_ID = "354"
LIGHTS_CAN_ID = "625"


def decode_rpm(data_bytes: List[str]) -> int:
    """Decode the observed big-endian RPM field from bytes 2-3."""
    raw_value = int(data_bytes[2] + data_bytes[3], 16)
    return int(raw_value / 8)


def decode_brake(data_bytes: List[str]) -> str:
    """Map observed byte-6 values to brake states."""
    brake_value = data_bytes[6]
    if brake_value == "14":
        return "ON"
    if brake_value == "04":
        return "OFF"
    return "UNKNOWN"


def decode_lights(data_bytes: List[str]) -> str:
    """Map observed byte-1 values to exterior-light states."""
    light_value = data_bytes[1]
    light_states = {
        "00": "OFF",
        "40": "DRL",
        "60": "LOW BEAM",
        "70": "HIGH BEAM",
    }
    return light_states.get(light_value, "UNKNOWN")


def print_dashboard(rpm: int, brake: str, lights: str) -> None:
    """Clear the terminal and print the latest interpreted values."""
    print("\033[2J\033[H", end="")
    print("========== MAXIMA 2010 LIVE CAN DASHBOARD ==========")
    print(f"RPM      : {rpm}")
    print(f"Brake    : {brake}")
    print(f"Lights   : {lights}")
    print("====================================================")


def run_dashboard() -> None:
    """Update the live dashboard until the user presses Ctrl+C."""
    serial_connection = serial.Serial(
        SERIAL_PORT,
        BAUD_RATE,
        timeout=SERIAL_TIMEOUT_SECONDS,
    )
    rpm = 0
    brake = "UNKNOWN"
    lights = "UNKNOWN"

    try:
        time.sleep(BOARD_STARTUP_DELAY_SECONDS)
        print("Maxima 2010 Live CAN Dashboard Started")
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
                can_id = can_id.upper()
                data_bytes = data.split()

                if can_id == RPM_CAN_ID and len(data_bytes) >= 4:
                    rpm = decode_rpm(data_bytes)
                elif can_id == BRAKE_CAN_ID and len(data_bytes) >= 7:
                    brake = decode_brake(data_bytes)
                elif can_id == LIGHTS_CAN_ID and len(data_bytes) >= 2:
                    lights = decode_lights(data_bytes)

                print_dashboard(rpm, brake, lights)
        except KeyboardInterrupt:
            print("\nStopped.")
    finally:
        serial_connection.close()


if __name__ == "__main__":
    run_dashboard()
