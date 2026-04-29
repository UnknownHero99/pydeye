from __future__ import annotations

from pydeye.sensor import EnumSensor, ProtocolVersionSensor, SerialSensor, SensorDefinitions

PROG_CHARGE_OPTIONS: dict[int, str] = {
    0: "No Grid or Gen",
    1: "Allow Grid",
    2: "Allow Gen",
    3: "Allow Grid & Gen",
}

PROG_MODE_OPTIONS: dict[int, str] = {
    0: "None",
    4: "General",
    8: "Backup",
    12: "Charge",
}

DEVICE_TYPES: dict[int, str] = {
    0: "Undefined",
    1: "String Inverter",
    2: "Single Phase Hybrid (2 MPPT)",
    3: "Single Phase Hybrid",
    4: "Micro Inverter",
    5: "LV Three Phase Hybrid",
    6: "HV Three Phase Hybrid",
    7: "HV Three Phase 6-12kW",
    8: "Three Phase PCS",
    9: "Balcony ESS",
    262: "HV Three Phase 20-50kW",
}

# Sensors present on every Deye inverter (registers 0-7)
COMMON = SensorDefinitions()
COMMON += EnumSensor(0, "Device Type", options=DEVICE_TYPES)
COMMON += ProtocolVersionSensor(2, "Protocol")
COMMON += SerialSensor((3, 4, 5, 6, 7), "Serial")
