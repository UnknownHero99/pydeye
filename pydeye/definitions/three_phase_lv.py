"""Sensor definitions specific to Deye low-voltage three-phase hybrid inverters.

Extends THREE_PHASE with the LV battery register block (586-592) and the
battery manufacturer selection (register 229).
"""
from __future__ import annotations

from pydeye.definitions.three_phase_common import THREE_PHASE
from pydeye.helper import AMPS, CELSIUS, VOLT, WATT
from pydeye.rwsensors import SelectRWSensor
from pydeye.sensor import Sensor, TempSensor

# ── LV Battery measurements (registers 586-592) ───────────────────────────────
battery_temperature = TempSensor(586, "Battery Temperature")
battery_voltage = Sensor(587, "Battery Voltage", VOLT, 0.01)
battery_soc = Sensor(588, "Battery SOC", "%")
battery_power = Sensor(590, "Battery Power", WATT, -1)
battery_current = Sensor(591, "Battery Current", AMPS, -0.01)
battery_corrected_ah = Sensor(592, "Battery Corrected AH", "AH")

# ── Battery manufacturer selection (register 229) ─────────────────────────────
_BATTERY_MANUFACTURERS: dict[int, str] = {
    0: "HereYin",
    1: "PYLON",
    2: "SOLAX",
    3: "DYNESS_L",
    4: "CCGX",
    5: "Alpha_ESS",
    6: "SUNGO_CAN",
    7: "VISION_CAN",
    8: "WATTSONIC_CAN",
    9: "KUNLAN",
    10: "GSEnergy",
    11: "GS_HUB",
    12: "BYD_LV",
    13: "AOBO",
    14: "DEYE",
    15: "CFE",
    16: "DMEGC",
    17: "UZENERGY",
    18: "GROWATT",
}
battery_manufacturer = SelectRWSensor(229, "Battery Manufacturer", options=_BATTERY_MANUFACTURERS)

# ── SensorDefinitions ─────────────────────────────────────────────────────────
THREE_PHASE_LV = THREE_PHASE.copy()

for _s in [
    battery_temperature, battery_voltage, battery_soc,
    battery_power, battery_current, battery_corrected_ah,
    battery_manufacturer,
]:
    THREE_PHASE_LV += _s
