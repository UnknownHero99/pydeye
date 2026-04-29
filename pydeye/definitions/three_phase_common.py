"""Sensor definitions shared by all Deye three-phase hybrid inverters."""
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
    Sensor16,
    SensorDefinitions,
    TempSensor,
)

# ── Device info (read-only) ──────────────────────────────────────────────────
rated_power = Sensor((20, 21), "Rated Power", WATT, 0.1)

# ── Date / Time (read-write, 3 packed registers) ─────────────────────────────
date_time = SystemTimeRWSensor((62, 63, 64), "Date Time")

# ── Inverter enable ──────────────────────────────────────────────────────────
inverter_enabled = SwitchRWSensor(80, "Inverter Enabled")

# ── Battery configuration (R/W) ───────────────────────────────────────────────
battery_equalization_voltage = NumberRWSensor(99, "Battery Equalization Voltage", VOLT, 0.01, min=40.0, max=64.0)
battery_absorption_voltage = NumberRWSensor(100, "Battery Absorption Voltage", VOLT, 0.01, min=40.0, max=64.0)
battery_float_voltage = NumberRWSensor(101, "Battery Float Voltage", VOLT, 0.01, min=40.0, max=64.0)
battery_capacity_current = NumberRWSensor(102, "Battery Capacity Current", AMPS, min=0, max=250)
battery_low_voltage = NumberRWSensor(103, "Battery Low Voltage", VOLT, 0.01, min=40.0, max=60.0)
system_zero_export_power = NumberRWSensor(104, "System Zero Export Power", WATT, -1, min=0, max=20000)
battery_equalization_days = NumberRWSensor(105, "Battery Equalization Days", "days", -1, min=0, max=365)
battery_equalization_hours = NumberRWSensor(106, "Battery Equalization Hours", "h", -1, min=0, max=24)
battery_max_charge_current = NumberRWSensor(108, "Battery Max Charge Current", AMPS, min=0, max=250)
battery_max_discharge_current = NumberRWSensor(109, "Battery Max Discharge Current", AMPS, min=0, max=250)
battery_type = SelectRWSensor(111, "Battery Type", options={0: "Lithium", 1: "Lead-acid", 2: "Other"})
battery_wake_up = SelectRWSensor(112, "Battery Wake Up", options={0: "Disabled", 1: "Enabled"})
battery_resistance = NumberRWSensor(113, "Battery Resistance", "mΩ", min=0, max=6000)
battery_charge_efficiency = Sensor(114, "Battery Charge Efficiency", "%", 0.1)
battery_shutdown_capacity = NumberRWSensor(115, "Battery Shutdown Capacity", "%", min=0, max=100)
battery_restart_capacity = NumberRWSensor(116, "Battery Restart Capacity", "%", min=0, max=100)
battery_low_capacity = NumberRWSensor(117, "Battery Low Capacity", "%", min=0, max=100)
battery_shutdown_voltage = NumberRWSensor(118, "Battery Shutdown Voltage", VOLT, 0.01, min=40.0, max=60.0)
battery_restart_voltage = NumberRWSensor(119, "Battery Restart Voltage", VOLT, 0.01, min=40.0, max=60.0)
battery_low_voltage_setting = NumberRWSensor(120, "Battery Low Voltage Setting", VOLT, 0.01, min=40.0, max=60.0)

# ── Generator configuration (R/W) ────────────────────────────────────────────
generator_max_operating_time = NumberRWSensor(121, "Generator Max Operating Time", "h", 0.1, min=0, max=24)
generator_cooling_time = NumberRWSensor(122, "Generator Cooling Time", "h", 0.1, min=0, max=12)
generator_charge_start_voltage = NumberRWSensor(123, "Generator Charge Start Battery Voltage", VOLT, 0.01, min=40.0, max=60.0)
generator_charge_start_soc = NumberRWSensor(124, "Generator Charge Start Battery SOC", "%", min=0, max=100)
generator_charge_current = NumberRWSensor(125, "Generator Charge Battery Current", AMPS, min=0, max=250)

# ── Grid charge configuration (R/W) ──────────────────────────────────────────
grid_charge_start_voltage = NumberRWSensor(126, "Grid Charge Start Battery Voltage", VOLT, 0.01, min=40.0, max=60.0)
grid_charge_start_soc = NumberRWSensor(127, "Grid Charge Start Battery SOC", "%", min=0, max=100)
grid_charge_battery_current = NumberRWSensor(128, "Grid Charge Battery Current", AMPS, min=0, max=250)

# ── Generator / Grid charge switches (R/W) ───────────────────────────────────
generator_charge_enabled = SwitchRWSensor(129, "Generator Charge Enabled")
grid_charge_enabled = SwitchRWSensor(130, "Grid Charge Enabled")
generator_ac_couple_frz_high = NumberRWSensor(131, "Generator AC Couple Frz High", HZ, 0.01, min=50.0, max=65.0)
force_generator_as_load = SwitchRWSensor(132, "Force Generator as Load Function")
generator_port_usage = SelectRWSensor(133, "Generator Port Usage", options={0: "Generator", 1: "Micro Inverter", 2: "Load"})
generator_off_soc = NumberRWSensor(135, "Generator Off SOC", "%", min=0, max=100)
generator_on_soc = NumberRWSensor(137, "Generator On SOC", "%", min=0, max=100)
min_pv_power_for_gen_start = NumberRWSensor(139, "Min PV Power for Gen Start", WATT, min=0, max=20000)

# Register 140 – bitmask-shared between Grid Signal On and Gen Signal On
grid_signal_on = SwitchRWSensor(140, "Grid Signal On", bitmask=0x0001)
gen_signal_on = SwitchRWSensor(140, "Gen Signal On", bitmask=0x0002)

priority_load = SwitchRWSensor(141, "Priority Load")
load_limit = SelectRWSensor(142, "Load Limit", options={0: "Limited", 1: "Unlimited"})
export_limit_power = NumberRWSensor(143, "Export Limit Power", WATT, min=0, max=20000)
solar_export = SwitchRWSensor(145, "Solar Export")

# Register 146 – timer enable flags (bitmask)
use_timer = SwitchRWSensor(146, "Use Timer", bitmask=0x0001)
prog_time_of_use_enabled = SwitchRWSensor(146, "Prog Time Of Use Enabled", bitmask=0x0010)
prog_monday_enabled = SwitchRWSensor(146, "Prog Monday Enabled", bitmask=0x0002)
prog_tuesday_enabled = SwitchRWSensor(146, "Prog Tuesday Enabled", bitmask=0x0004)
prog_wednesday_enabled = SwitchRWSensor(146, "Prog Wednesday Enabled", bitmask=0x0008)
prog_thursday_enabled = SwitchRWSensor(146, "Prog Thursday Enabled", bitmask=0x0020)
prog_friday_enabled = SwitchRWSensor(146, "Prog Friday Enabled", bitmask=0x0040)
prog_saturday_enabled = SwitchRWSensor(146, "Prog Saturday Enabled", bitmask=0x0080)
prog_sunday_enabled = SwitchRWSensor(146, "Prog Sunday Enabled", bitmask=0x0100)

# ── Six programmable time-of-use slots ────────────────────────────────────────
prog1_time = TimeRWSensor(148, "Prog1 Time")
prog2_time = TimeRWSensor(149, "Prog2 Time", min=prog1_time)
prog3_time = TimeRWSensor(150, "Prog3 Time", min=prog2_time)
prog4_time = TimeRWSensor(151, "Prog4 Time", min=prog3_time)
prog5_time = TimeRWSensor(152, "Prog5 Time", min=prog4_time)
prog6_time = TimeRWSensor(153, "Prog6 Time", min=prog5_time)

prog1_power = NumberRWSensor(154, "Prog1 Power", WATT, min=0, max=30000)
prog2_power = NumberRWSensor(155, "Prog2 Power", WATT, min=0, max=30000)
prog3_power = NumberRWSensor(156, "Prog3 Power", WATT, min=0, max=30000)
prog4_power = NumberRWSensor(157, "Prog4 Power", WATT, min=0, max=30000)
prog5_power = NumberRWSensor(158, "Prog5 Power", WATT, min=0, max=30000)
prog6_power = NumberRWSensor(159, "Prog6 Power", WATT, min=0, max=30000)

prog1_voltage = NumberRWSensor(160, "Prog1 Voltage", VOLT, 0.01, min=40.0, max=60.0)
prog2_voltage = NumberRWSensor(161, "Prog2 Voltage", VOLT, 0.01, min=40.0, max=60.0)
prog3_voltage = NumberRWSensor(162, "Prog3 Voltage", VOLT, 0.01, min=40.0, max=60.0)
prog4_voltage = NumberRWSensor(163, "Prog4 Voltage", VOLT, 0.01, min=40.0, max=60.0)
prog5_voltage = NumberRWSensor(164, "Prog5 Voltage", VOLT, 0.01, min=40.0, max=60.0)
prog6_voltage = NumberRWSensor(165, "Prog6 Voltage", VOLT, 0.01, min=40.0, max=60.0)

prog1_capacity = NumberRWSensor(166, "Prog1 Capacity", "%", min=0, max=100)
prog2_capacity = NumberRWSensor(167, "Prog2 Capacity", "%", min=0, max=100)
prog3_capacity = NumberRWSensor(168, "Prog3 Capacity", "%", min=0, max=100)
prog4_capacity = NumberRWSensor(169, "Prog4 Capacity", "%", min=0, max=100)
prog5_capacity = NumberRWSensor(170, "Prog5 Capacity", "%", min=0, max=100)
prog6_capacity = NumberRWSensor(171, "Prog6 Capacity", "%", min=0, max=100)

# Program charge and mode share one register per slot via bitmasks
prog1_charge = SelectRWSensor(172, "Prog1 Charge", bitmask=0x03, options=PROG_CHARGE_OPTIONS)
prog1_mode = SelectRWSensor(172, "Prog1 Mode", bitmask=0x0C, options=PROG_MODE_OPTIONS)
prog2_charge = SelectRWSensor(173, "Prog2 Charge", bitmask=0x03, options=PROG_CHARGE_OPTIONS)
prog2_mode = SelectRWSensor(173, "Prog2 Mode", bitmask=0x0C, options=PROG_MODE_OPTIONS)
prog3_charge = SelectRWSensor(174, "Prog3 Charge", bitmask=0x03, options=PROG_CHARGE_OPTIONS)
prog3_mode = SelectRWSensor(174, "Prog3 Mode", bitmask=0x0C, options=PROG_MODE_OPTIONS)
prog4_charge = SelectRWSensor(175, "Prog4 Charge", bitmask=0x03, options=PROG_CHARGE_OPTIONS)
prog4_mode = SelectRWSensor(175, "Prog4 Mode", bitmask=0x0C, options=PROG_MODE_OPTIONS)
prog5_charge = SelectRWSensor(176, "Prog5 Charge", bitmask=0x03, options=PROG_CHARGE_OPTIONS)
prog5_mode = SelectRWSensor(176, "Prog5 Mode", bitmask=0x0C, options=PROG_MODE_OPTIONS)
prog6_charge = SelectRWSensor(177, "Prog6 Charge", bitmask=0x03, options=PROG_CHARGE_OPTIONS)
prog6_mode = SelectRWSensor(177, "Prog6 Mode", bitmask=0x0C, options=PROG_MODE_OPTIONS)

# Register 178 – advanced feature flags (bitmask)
microinverter_export_cutoff = SwitchRWSensor(178, "Microinverter Export to Grid Cutoff", bitmask=0x0001)
gen_peak_shaving = SwitchRWSensor(178, "Gen Peak Shaving", bitmask=0x0002)
grid_peak_shaving = SwitchRWSensor(178, "Grid Peak Shaving", bitmask=0x0004)
on_grid_always_on = SwitchRWSensor(178, "On Grid Always On", bitmask=0x0008)
external_relay = SwitchRWSensor(178, "External Relay", bitmask=0x0010)
loss_of_lithium_battery_fault = SwitchRWSensor(178, "Loss of Lithium Battery Report Fault", bitmask=0x0020)
drm_switch = SwitchRWSensor(178, "DRM", bitmask=0x0040)
us_grounding_fault = SwitchRWSensor(178, "US Version Grounding Fault", bitmask=0x0080)

off_grid_mode = SwitchRWSensor(179, "Off Grid Mode", on=1, off=0)

_GRID_STANDARD_OPTIONS: dict[int, str] = {
    0: "Generic",
    1: "IEEE 1547",
    2: "AS 4777",
    3: "EN 50549",
    4: "VDE 4105",
    5: "Chile",
    6: "Philippines",
    7: "Slovakia",
    8: "Lithuania",
    9: "Latvia",
    10: "Estonia",
    11: "Singapore",
    12: "Hungary",
}
grid_standard = SelectRWSensor(182, "Grid Standard", options=_GRID_STANDARD_OPTIONS)
configured_grid_frequency = SelectRWSensor(183, "Configured Grid Frequency", options={0: "50Hz", 1: "60Hz"})
grid_phases = SelectRWSensor(184, "Configured Grid Phases", options={0: "3 Phase", 1: "L1", 2: "L2", 3: "L3"})

generator_connected_to_grid = SwitchRWSensor(189, "Generator Connected to Grid Input")
grid_peak_shaving_power = NumberRWSensor(191, "Grid Peak Shaving Power", WATT, min=0, max=30000)
ups_delay_time = NumberRWSensor(209, "UPS Delay Time", "s", min=0, max=3000)

# ── BMS interface (read-only) ─────────────────────────────────────────────────
bms_charging_voltage = Sensor(210, "Battery 1 BMS Charging Voltage", VOLT, 0.01)
bms_discharging_voltage = Sensor(211, "Battery 1 BMS Discharging Voltage", VOLT, 0.01)
bms_charging_current_limit = Sensor(212, "Battery 1 BMS Charging Current Limit", AMPS)
bms_discharging_current_limit = Sensor(213, "Battery 1 BMS Discharging Current Limit", AMPS)
bms_soc = Sensor(214, "Battery 1 BMS SOC", "%")
bms_voltage = Sensor(215, "Battery 1 BMS Voltage", VOLT, 0.01)
bms_current = Sensor(216, "Battery 1 BMS Current", AMPS, 0.01)
bms_temperature = TempSensor(217, "Battery 1 BMS Temperature")
bms_max_charge_current = Sensor(218, "Battery 1 BMS Max Charge Current Limit", AMPS)
bms_max_discharge_current = Sensor(219, "Battery 1 BMS Max Discharge Current Limit", AMPS)
bms_alarm_flag = Sensor(220, "Battery 1 BMS Alarm Flag")

# Register 228 – software feature flags (bitmask)
time_sync = SwitchRWSensor(228, "Time Synchronization", bitmask=0x0001)
beep = SwitchRWSensor(228, "Beep", bitmask=0x0002)
am_pm = SwitchRWSensor(228, "AM PM", bitmask=0x0004)
auto_dim = SwitchRWSensor(228, "Auto Dim", bitmask=0x0008)
allow_remote = SwitchRWSensor(228, "Allow Remote", bitmask=0x0010)

track_grid_phase = SwitchRWSensor(235, "Track Grid Phase")

# Register 336 – parallel operation flags (bitmask)
parallel_enable = SwitchRWSensor(336, "Parallel Enable", bitmask=0x0001)
parallel_mode = SelectRWSensor(336, "Parallel Mode", bitmask=0x0006, options={0: "Single", 2: "Master", 4: "Slave"})
parallel_phase = SelectRWSensor(336, "Parallel Phase", bitmask=0x0018, options={0: "L1", 8: "L2", 16: "L3"})
parallel_modbus_sn = NumberRWSensor(336, "Parallel Modbus SN", bitmask=0x01E0, min=0, max=15)

max_solar_power = NumberRWSensor(340, "Max Solar Power", WATT, min=0, max=32000)

# ── Inverter status (read-only) ───────────────────────────────────────────────
overall_state = InverterStateSensor(500, "Overall State")
day_active_energy = Sensor(502, "Day Active Energy", KWH, -0.1)
total_active_energy = Sensor((506, 507), "Total Active Energy", KWH, 0.1)

# ── Energy counters (read-only) ───────────────────────────────────────────────
day_battery_charge = Sensor(514, "Day Battery Charge", KWH, 0.1)
day_battery_discharge = Sensor(515, "Day Battery Discharge", KWH, 0.1)
total_battery_charge = Sensor((516, 517), "Total Battery Charge", KWH, 0.1)
total_battery_discharge = Sensor((518, 519), "Total Battery Discharge", KWH, 0.1)
day_grid_import = Sensor(520, "Day Grid Import", KWH, 0.1)
day_grid_export = Sensor(521, "Day Grid Export", KWH, 0.1)
total_grid_import = Sensor((522, 523), "Total Grid Import", KWH, 0.1)
total_grid_export = Sensor((524, 525), "Total Grid Export", KWH, 0.1)
day_load_energy = Sensor(526, "Day Load Energy", KWH, 0.1)
total_load_energy = Sensor((527, 528), "Total Load Energy", KWH, 0.1)
day_pv_energy = Sensor(529, "Day PV Energy", KWH, 0.1)
total_pv_energy = Sensor((534, 535), "Total PV Energy", KWH, 0.1)
day_gen_energy = Sensor(536, "Day Gen Energy", KWH, 0.1)

# ── Inverter temperatures ─────────────────────────────────────────────────────
dc_transformer_temperature = TempSensor(540, "DC Transformer Temperature")
radiator_temperature = TempSensor(541, "Radiator Temperature")

# ── DRM codes (register 544, bitmask-per-bit) ────────────────────────────────
drm0 = BinarySensor(544, "DRM0", bitmask=0x0001)
drm1 = BinarySensor(544, "DRM1", bitmask=0x0002)
drm2 = BinarySensor(544, "DRM2", bitmask=0x0004)
drm3 = BinarySensor(544, "DRM3", bitmask=0x0008)
drm4 = BinarySensor(544, "DRM4", bitmask=0x0010)
drm5 = BinarySensor(544, "DRM5", bitmask=0x0020)
drm6 = BinarySensor(544, "DRM6", bitmask=0x0040)
drm7 = BinarySensor(544, "DRM7", bitmask=0x0080)
drm8 = BinarySensor(544, "DRM8", bitmask=0x0100)

# ── Relay / connection status (register 552, bitmask-per-bit) ────────────────
grid_connected = BinarySensor(552, "Grid Connected", bitmask=0x0001)
inv_relay_status = BinarySensor(552, "INV Relay Status", bitmask=0x0002)
load_relay_status = BinarySensor(552, "Undefined Load Relay Status", bitmask=0x0004)
grid_relay_status = BinarySensor(552, "Grid Relay Status", bitmask=0x0008)
generator_relay_status = BinarySensor(552, "Generator Relay Status", bitmask=0x0010)
grid_give_power_relay = BinarySensor(552, "Grid Give Power to Relay Status", bitmask=0x0020)
dry_contact1 = BinarySensor(552, "Dry Contact1 Status", bitmask=0x0040)
dry_contact2 = BinarySensor(552, "Dry Contact2 Status", bitmask=0x0080)

# ── Fault register bank (555-558) ────────────────────────────────────────────
fault = FaultSensor((555, 556, 557, 558), "Fault")

# ── Grid measurements ─────────────────────────────────────────────────────────
grid_l1_voltage = Sensor(598, "Grid L1 Voltage", VOLT, 0.1)
grid_l2_voltage = Sensor(599, "Grid L2 Voltage", VOLT, 0.1)
grid_l3_voltage = Sensor(600, "Grid L3 Voltage", VOLT, 0.1)

grid_l1_power = Sensor16(604, 701, "Grid L1 Inner Power", WATT, -1)
grid_l2_power = Sensor16(605, 702, "Grid L2 Inner Power", WATT, -1)
grid_l3_power = Sensor16(606, 703, "Grid L3 Inner Power", WATT, -1)
grid_inner_total_active_power = Sensor16(607, 704, "Grid Inner Total Active Power", WATT, -1)

grid_frequency = Sensor(609, "Grid Frequency", HZ, 0.01)

grid_l1_current = Sensor(610, "Grid L1 Current", AMPS, -0.01)
grid_l2_current = Sensor(611, "Grid L2 Current", AMPS, -0.01)
grid_l3_current = Sensor(612, "Grid L3 Current", AMPS, -0.01)
grid_current = MathSensor((610, 611, 612), "Grid Current", AMPS, (-0.01, -0.01, -0.01))

grid_ct_l1_current = Sensor(613, "Grid CT L1 Current", AMPS, -0.01)
grid_ct_l2_current = Sensor(614, "Grid CT L2 Current", AMPS, -0.01)
grid_ct_l3_current = Sensor(615, "Grid CT L3 Current", AMPS, -0.01)
grid_ct_current = MathSensor((613, 614, 615), "Grid CT Current", AMPS, (-0.01, -0.01, -0.01))

grid_ct_l1_power = Sensor16(616, 705, "Grid CT L1 Power", WATT, -1)
grid_ct_l2_power = Sensor16(617, 706, "Grid CT L2 Power", WATT, -1)
grid_ct_l3_power = Sensor16(618, 707, "Grid CT L3 Power", WATT, -1)
grid_ct_power = Sensor16(619, 708, "Grid CT Power", WATT, -1)

grid_l1_power_outer = Sensor16(622, 687, "Grid L1 Power", WATT, -1)
grid_l2_power_outer = Sensor16(623, 688, "Grid L2 Power", WATT, -1)
grid_l3_power_outer = Sensor16(624, 689, "Grid L3 Power", WATT, -1)
grid_power = Sensor16(625, 690, "Grid Power", WATT, -1)

# ── Inverter measurements ─────────────────────────────────────────────────────
inverter_l1_voltage = Sensor(627, "Inverter L1 Voltage", VOLT, 0.1)
inverter_l2_voltage = Sensor(628, "Inverter L2 Voltage", VOLT, 0.1)
inverter_l3_voltage = Sensor(629, "Inverter L3 Voltage", VOLT, 0.1)

inverter_l1_current = Sensor(630, "Inverter L1 Current", AMPS, -0.01)
inverter_l2_current = Sensor(631, "Inverter L2 Current", AMPS, -0.01)
inverter_l3_current = Sensor(632, "Inverter L3 Current", AMPS, -0.01)

inverter_l1_power = Sensor16(633, 691, "Inverter L1 Power", WATT, -1)
inverter_l2_power = Sensor16(634, 692, "Inverter L2 Power", WATT, -1)
inverter_l3_power = Sensor16(635, 693, "Inverter L3 Power", WATT, -1)
inverter_power = Sensor16(636, 694, "Inverter Power", WATT, -1)

inverter_frequency = Sensor(638, "Inverter Frequency", HZ, 0.01)

# ── UPS / backup load ─────────────────────────────────────────────────────────
ups_l1_power = Sensor16(640, 696, "UPS Load L1 Power", WATT, 1)
ups_l2_power = Sensor16(641, 697, "UPS Load L2 Power", WATT, 1)
ups_l3_power = Sensor16(642, 698, "UPS Load L3 Power", WATT, 1)
ups_power = Sensor16(643, 699, "UPS Load Power", WATT, 1)

# ── Load measurements ─────────────────────────────────────────────────────────
load_l1_voltage = Sensor(644, "Load L1 Voltage", VOLT, 0.1)
load_l2_voltage = Sensor(645, "Load L2 Voltage", VOLT, 0.1)
load_l3_voltage = Sensor(646, "Load L3 Voltage", VOLT, 0.1)

load_l1_power = Sensor16(650, 656, "Load L1 Power", WATT, -1)
load_l2_power = Sensor16(651, 657, "Load L2 Power", WATT, -1)
load_l3_power = Sensor16(652, 658, "Load L3 Power", WATT, -1)
load_power = Sensor16(653, 659, "Load Power", WATT, -1)

load_frequency = Sensor(655, "Load Frequency", HZ, 0.01)

# ── Generator measurements ────────────────────────────────────────────────────
gen_l1_voltage = Sensor(661, "Gen L1 Voltage", VOLT, 0.1)
gen_l2_voltage = Sensor(662, "Gen L2 Voltage", VOLT, 0.1)
gen_l3_voltage = Sensor(663, "Gen L3 Voltage", VOLT, 0.1)

gen_l1_power = Sensor16(664, 668, "Gen L1 Power", WATT, -1)
gen_l2_power = Sensor16(665, 669, "Gen L2 Power", WATT, -1)
gen_l3_power = Sensor16(666, 670, "Gen L3 Power", WATT, -1)
gen_power = Sensor16(667, 671, "Gen Power", WATT, -1)

# ── PV string measurements ────────────────────────────────────────────────────
pv1_power = Sensor(672, "PV1 Power", WATT, -1)
pv2_power = Sensor(673, "PV2 Power", WATT, -1)
pv3_power = Sensor(674, "PV3 Power", WATT, -1)
pv4_power = Sensor(675, "PV4 Power", WATT, -1)
pv_power = MathSensor((672, 673, 674, 675), "PV Power", WATT, (1, 1, 1, 1))

pv1_voltage = Sensor(676, "PV1 Voltage", VOLT, 0.1)
pv1_current = Sensor(677, "PV1 Current", AMPS, 0.1)
pv2_voltage = Sensor(678, "PV2 Voltage", VOLT, 0.1)
pv2_current = Sensor(679, "PV2 Current", AMPS, 0.1)
pv3_voltage = Sensor(680, "PV3 Voltage", VOLT, 0.1)
pv3_current = Sensor(681, "PV3 Current", AMPS, 0.1)
pv4_voltage = Sensor(682, "PV4 Voltage", VOLT, 0.1)
pv4_current = Sensor(683, "PV4 Current", AMPS, 0.1)

# ── SensorDefinitions container ───────────────────────────────────────────────
THREE_PHASE = COMMON.copy()

for _s in [
    rated_power, date_time, inverter_enabled,
    battery_equalization_voltage, battery_absorption_voltage, battery_float_voltage,
    battery_capacity_current, battery_low_voltage, system_zero_export_power,
    battery_equalization_days, battery_equalization_hours,
    battery_max_charge_current, battery_max_discharge_current,
    battery_type, battery_wake_up, battery_resistance, battery_charge_efficiency,
    battery_shutdown_capacity, battery_restart_capacity, battery_low_capacity,
    battery_shutdown_voltage, battery_restart_voltage, battery_low_voltage_setting,
    generator_max_operating_time, generator_cooling_time,
    generator_charge_start_voltage, generator_charge_start_soc, generator_charge_current,
    grid_charge_start_voltage, grid_charge_start_soc, grid_charge_battery_current,
    generator_charge_enabled, grid_charge_enabled,
    generator_ac_couple_frz_high, force_generator_as_load, generator_port_usage,
    generator_off_soc, generator_on_soc, min_pv_power_for_gen_start,
    grid_signal_on, gen_signal_on, priority_load, load_limit,
    export_limit_power, solar_export,
    use_timer, prog_time_of_use_enabled,
    prog_monday_enabled, prog_tuesday_enabled, prog_wednesday_enabled,
    prog_thursday_enabled, prog_friday_enabled, prog_saturday_enabled, prog_sunday_enabled,
    prog1_time, prog2_time, prog3_time, prog4_time, prog5_time, prog6_time,
    prog1_power, prog2_power, prog3_power, prog4_power, prog5_power, prog6_power,
    prog1_voltage, prog2_voltage, prog3_voltage, prog4_voltage, prog5_voltage, prog6_voltage,
    prog1_capacity, prog2_capacity, prog3_capacity, prog4_capacity, prog5_capacity, prog6_capacity,
    prog1_charge, prog1_mode, prog2_charge, prog2_mode,
    prog3_charge, prog3_mode, prog4_charge, prog4_mode,
    prog5_charge, prog5_mode, prog6_charge, prog6_mode,
    microinverter_export_cutoff, gen_peak_shaving, grid_peak_shaving,
    on_grid_always_on, external_relay, loss_of_lithium_battery_fault, drm_switch, us_grounding_fault,
    off_grid_mode, grid_standard, configured_grid_frequency, grid_phases,
    generator_connected_to_grid, grid_peak_shaving_power, ups_delay_time,
    bms_charging_voltage, bms_discharging_voltage, bms_charging_current_limit,
    bms_discharging_current_limit, bms_soc, bms_voltage, bms_current,
    bms_temperature, bms_max_charge_current, bms_max_discharge_current, bms_alarm_flag,
    time_sync, beep, am_pm, auto_dim, allow_remote, track_grid_phase,
    parallel_enable, parallel_mode, parallel_phase, parallel_modbus_sn, max_solar_power,
    overall_state, day_active_energy, total_active_energy,
    day_battery_charge, day_battery_discharge, total_battery_charge, total_battery_discharge,
    day_grid_import, day_grid_export, total_grid_import, total_grid_export,
    day_load_energy, total_load_energy, day_pv_energy, total_pv_energy, day_gen_energy,
    dc_transformer_temperature, radiator_temperature,
    drm0, drm1, drm2, drm3, drm4, drm5, drm6, drm7, drm8,
    grid_connected, inv_relay_status, load_relay_status, grid_relay_status,
    generator_relay_status, grid_give_power_relay, dry_contact1, dry_contact2,
    fault,
    grid_l1_voltage, grid_l2_voltage, grid_l3_voltage,
    grid_l1_power, grid_l2_power, grid_l3_power, grid_inner_total_active_power,
    grid_frequency, grid_l1_current, grid_l2_current, grid_l3_current, grid_current,
    grid_ct_l1_current, grid_ct_l2_current, grid_ct_l3_current, grid_ct_current,
    grid_ct_l1_power, grid_ct_l2_power, grid_ct_l3_power, grid_ct_power,
    grid_l1_power_outer, grid_l2_power_outer, grid_l3_power_outer, grid_power,
    inverter_l1_voltage, inverter_l2_voltage, inverter_l3_voltage,
    inverter_l1_current, inverter_l2_current, inverter_l3_current,
    inverter_l1_power, inverter_l2_power, inverter_l3_power, inverter_power,
    inverter_frequency,
    ups_l1_power, ups_l2_power, ups_l3_power, ups_power,
    load_l1_voltage, load_l2_voltage, load_l3_voltage,
    load_l1_power, load_l2_power, load_l3_power, load_power, load_frequency,
    gen_l1_voltage, gen_l2_voltage, gen_l3_voltage,
    gen_l1_power, gen_l2_power, gen_l3_power, gen_power,
    pv1_power, pv2_power, pv3_power, pv4_power, pv_power,
    pv1_voltage, pv1_current, pv2_voltage, pv2_current,
    pv3_voltage, pv3_current, pv4_voltage, pv4_current,
]:
    THREE_PHASE += _s
