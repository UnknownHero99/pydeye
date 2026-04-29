"""Sensor definitions for Deye single-phase hybrid inverters."""
from __future__ import annotations

from pydeye.definitions import COMMON, PROG_CHARGE_OPTIONS, PROG_MODE_OPTIONS
from pydeye.helper import AMPS, CELSIUS, HZ, KWH, VOLT, WATT
from pydeye.rwsensors import (
    NumberRWSensor,
    SelectRWSensor,
    SwitchRWSensor,
    SystemTimeRWSensor,
    TimeRWSensor,
)
from pydeye.sensor import (
    BinarySensor,
    FaultSensor,
    InverterStateSensor,
    MathSensor,
    Sensor,
    SensorDefinitions,
    TempSensor,
)

# ── Battery (registers 182-191) ───────────────────────────────────────────────
battery_temperature = TempSensor(182, "Battery Temperature")
battery_voltage = Sensor(183, "Battery Voltage", VOLT, 0.01)
battery_soc = Sensor(184, "Battery SOC", "%")
battery_power = Sensor(190, "Battery Power", WATT, -1)
battery_current = Sensor(191, "Battery Current", AMPS, -0.01)

# ── Inverter output (registers 154-193) ───────────────────────────────────────
inverter_voltage = Sensor(154, "Inverter Voltage", VOLT, 0.1)
inverter_current = Sensor(164, "Inverter Current", AMPS, 0.01)
inverter_power = Sensor(175, "Inverter Power", WATT, -1)
inverter_frequency = Sensor(193, "Inverter Frequency", HZ, 0.01)

# ── Grid (registers 79-178) ───────────────────────────────────────────────────
grid_frequency = Sensor(79, "Grid Frequency", HZ, 0.01)
grid_voltage = Sensor(150, "Grid Voltage", VOLT, 0.1)
grid_l1_power = Sensor(167, "Grid L1 Power", WATT, -1)
grid_l2_power = Sensor(168, "Grid L2 Power", WATT, -1)
grid_power = Sensor(169, "Grid Power", WATT, -1)
grid_ct_power = Sensor(172, "Grid CT Power", WATT, -1)

# ── Load (registers 176-178) ─────────────────────────────────────────────────
load_l1_power = Sensor(176, "Load L1 Power", WATT, -1)
load_l2_power = Sensor(177, "Load L2 Power", WATT, -1)
load_power = Sensor(178, "Load Power", WATT, -1)

# ── PV arrays ─────────────────────────────────────────────────────────────────
pv1_power = Sensor(186, "PV1 Power", WATT, -1)
pv1_voltage = Sensor(109, "PV1 Voltage", VOLT, 0.1)
pv1_current = Sensor(110, "PV1 Current", AMPS, 0.1)
pv2_power = Sensor(187, "PV2 Power", WATT, -1)
pv2_voltage = Sensor(111, "PV2 Voltage", VOLT, 0.1)
pv2_current = Sensor(112, "PV2 Current", AMPS, 0.1)
pv3_power = Sensor(188, "PV3 Power", WATT, -1)
pv3_voltage = Sensor(113, "PV3 Voltage", VOLT, 0.1)
pv3_current = Sensor(114, "PV3 Current", AMPS, 0.1)
pv_power = MathSensor((186, 187, 188), "PV Power", WATT, (1, 1, 1))

# ── Temperatures ──────────────────────────────────────────────────────────────
dc_transformer_temperature = TempSensor(90, "DC Transformer Temperature")
radiator_temperature = TempSensor(91, "Radiator Temperature")

# ── Status ────────────────────────────────────────────────────────────────────
overall_state = InverterStateSensor(59, "Overall State")

# ── Energy counters ───────────────────────────────────────────────────────────
day_battery_charge = Sensor(70, "Day Battery Charge", KWH, 0.1)
day_battery_discharge = Sensor(71, "Day Battery Discharge", KWH, 0.1)
total_battery_charge = Sensor((72, 73), "Total Battery Charge", KWH, 0.1)
total_battery_discharge = Sensor((74, 75), "Total Battery Discharge", KWH, 0.1)
day_grid_import = Sensor(76, "Day Grid Import", KWH, 0.1)
day_grid_export = Sensor(77, "Day Grid Export", KWH, 0.1)
total_grid_import = Sensor((78, 79), "Total Grid Import", KWH, 0.1)
total_grid_export = Sensor((80, 81), "Total Grid Export", KWH, 0.1)
day_load_energy = Sensor(84, "Day Load Energy", KWH, 0.1)
total_load_energy = Sensor((85, 86), "Total Load Energy", KWH, 0.1)
day_pv_energy = Sensor(93, "Day PV Energy", KWH, 0.1)
total_pv_energy = Sensor((94, 95), "Total PV Energy", KWH, 0.1)

# ── Relay status ──────────────────────────────────────────────────────────────
grid_relay_status = BinarySensor(194, "Grid Relay Status", bitmask=0x0001)
load_relay_status = BinarySensor(194, "Load Relay Status", bitmask=0x0002)

# ── Fault registers ───────────────────────────────────────────────────────────
fault = FaultSensor((103, 104, 105, 106), "Fault")

# ── Battery configuration (R/W) ───────────────────────────────────────────────
battery_max_charge_current = NumberRWSensor(210, "Battery Max Charge Current", AMPS, min=0, max=250)
battery_max_discharge_current = NumberRWSensor(211, "Battery Max Discharge Current", AMPS, min=0, max=250)
battery_shutdown_capacity = NumberRWSensor(232, "Battery Shutdown Capacity", "%", min=0, max=100)
battery_restart_capacity = NumberRWSensor(233, "Battery Restart Capacity", "%", min=0, max=100)
battery_low_capacity = NumberRWSensor(234, "Battery Low Capacity", "%", min=0, max=100)

grid_charge_current = NumberRWSensor(230, "Grid Charge Current", AMPS, min=0, max=250)
grid_charge_enabled = SwitchRWSensor(243, "Grid Charge Enabled")

# ── Six programmable time-of-use slots ────────────────────────────────────────
prog1_time = TimeRWSensor(250, "Prog1 Time")
prog2_time = TimeRWSensor(251, "Prog2 Time", min=prog1_time)
prog3_time = TimeRWSensor(252, "Prog3 Time", min=prog2_time)
prog4_time = TimeRWSensor(253, "Prog4 Time", min=prog3_time)
prog5_time = TimeRWSensor(254, "Prog5 Time", min=prog4_time)
prog6_time = TimeRWSensor(255, "Prog6 Time", min=prog5_time)

prog1_capacity = NumberRWSensor(268, "Prog1 Capacity", "%", min=0, max=100)
prog2_capacity = NumberRWSensor(269, "Prog2 Capacity", "%", min=0, max=100)
prog3_capacity = NumberRWSensor(270, "Prog3 Capacity", "%", min=0, max=100)
prog4_capacity = NumberRWSensor(271, "Prog4 Capacity", "%", min=0, max=100)
prog5_capacity = NumberRWSensor(272, "Prog5 Capacity", "%", min=0, max=100)
prog6_capacity = NumberRWSensor(273, "Prog6 Capacity", "%", min=0, max=100)

prog1_charge = SelectRWSensor(274, "Prog1 Charge", bitmask=0x03, options=PROG_CHARGE_OPTIONS)
prog1_mode = SelectRWSensor(274, "Prog1 Mode", bitmask=0x0C, options=PROG_MODE_OPTIONS)
prog2_charge = SelectRWSensor(275, "Prog2 Charge", bitmask=0x03, options=PROG_CHARGE_OPTIONS)
prog2_mode = SelectRWSensor(275, "Prog2 Mode", bitmask=0x0C, options=PROG_MODE_OPTIONS)
prog3_charge = SelectRWSensor(276, "Prog3 Charge", bitmask=0x03, options=PROG_CHARGE_OPTIONS)
prog3_mode = SelectRWSensor(276, "Prog3 Mode", bitmask=0x0C, options=PROG_MODE_OPTIONS)
prog4_charge = SelectRWSensor(277, "Prog4 Charge", bitmask=0x03, options=PROG_CHARGE_OPTIONS)
prog4_mode = SelectRWSensor(277, "Prog4 Mode", bitmask=0x0C, options=PROG_MODE_OPTIONS)
prog5_charge = SelectRWSensor(278, "Prog5 Charge", bitmask=0x03, options=PROG_CHARGE_OPTIONS)
prog5_mode = SelectRWSensor(278, "Prog5 Mode", bitmask=0x0C, options=PROG_MODE_OPTIONS)
prog6_charge = SelectRWSensor(279, "Prog6 Charge", bitmask=0x03, options=PROG_CHARGE_OPTIONS)
prog6_mode = SelectRWSensor(279, "Prog6 Mode", bitmask=0x0C, options=PROG_MODE_OPTIONS)

# ── SensorDefinitions ─────────────────────────────────────────────────────────
SINGLE_PHASE = COMMON.copy()

for _s in [
    battery_temperature, battery_voltage, battery_soc, battery_power, battery_current,
    inverter_voltage, inverter_current, inverter_power, inverter_frequency,
    grid_frequency, grid_voltage, grid_l1_power, grid_l2_power, grid_power, grid_ct_power,
    load_l1_power, load_l2_power, load_power,
    pv1_power, pv1_voltage, pv1_current,
    pv2_power, pv2_voltage, pv2_current,
    pv3_power, pv3_voltage, pv3_current,
    pv_power,
    dc_transformer_temperature, radiator_temperature,
    overall_state,
    day_battery_charge, day_battery_discharge, total_battery_charge, total_battery_discharge,
    day_grid_import, day_grid_export, total_grid_import, total_grid_export,
    day_load_energy, total_load_energy, day_pv_energy, total_pv_energy,
    grid_relay_status, load_relay_status, fault,
    battery_max_charge_current, battery_max_discharge_current,
    battery_shutdown_capacity, battery_restart_capacity, battery_low_capacity,
    grid_charge_current, grid_charge_enabled,
    prog1_time, prog2_time, prog3_time, prog4_time, prog5_time, prog6_time,
    prog1_capacity, prog2_capacity, prog3_capacity, prog4_capacity, prog5_capacity, prog6_capacity,
    prog1_charge, prog1_mode, prog2_charge, prog2_mode,
    prog3_charge, prog3_mode, prog4_charge, prog4_mode,
    prog5_charge, prog5_mode, prog6_charge, prog6_mode,
]:
    SINGLE_PHASE += _s
