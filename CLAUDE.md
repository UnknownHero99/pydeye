# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

**pyDeye** is an async Python library for reading data from and writing settings to Deye solar inverters over Modbus TCP or RS-485 serial. It connects via a Modbus TCP gateway or direct RS-485 and exposes structured sensor objects and a state machine.

## Development Commands

```bash
# Install dependencies (requires Poetry)
poetry install

# Build the package
poetry build

# Run a script
poetry run python examples/ModbusTCP.py
```

No test suite or linter is currently configured.

## Architecture

```
ModbusTCP / ModbusSerial   (transport layer — interfaces/)
          ↓
    ModbusInterface        (abstract base — interfaces/base.py)
          ↓
BaseInverter               (sensor read/write engine — inverters/base_inverter.py)
          ↓
InverterState              (value + history store — state.py)
          ↑
SensorDefinitions          (named sensor registry — definitions/)
          ↑
Sensor / RWSensor objects  (sensor.py / rwsensors.py)
```

### Key modules

**`helper.py`** — unit constants (`WATT`, `VOLT`, …), type aliases (`RegType`, `ValType`, `NumType`), register pack/unpack helpers (`pack_value`, `unpack_value`), `SSTime` (time-of-day converter), `slug()`, `patch_bitmask()`. Also contains legacy `ModbusMapper`, `BasicInfo`, `InverterType` for backward compat.

**`sensor.py`** — All read-only sensor classes:
- `Sensor` — base; `reg_to_value(regs)` converts raw registers using `factor`
- `TempSensor` — uint16 × factor + offset (Deye temperature convention)
- `BinarySensor` — bitmask → ON/OFF
- `EnumSensor` — integer → string lookup
- `MathSensor` — weighted sum of multiple registers
- `SerialSensor` — registers → ASCII string
- `Sensor16` — picks primary vs alt address based on which has a non-zero value (firmware compatibility)
- `FaultSensor` / `HVFaultSensor` — bit-mapped fault code decoding
- `InverterStateSensor`, `SDStatusSensor`, `ProtocolVersionSensor`
- `SensorDefinitions` — ordered dict of sensors supporting `+=` and `.copy()`

**`rwsensors.py`** — Read/write sensor subclasses: `NumberRWSensor` (with min/max Sensor refs), `SelectRWSensor`, `SwitchRWSensor`, `SystemTimeRWSensor`, `TimeRWSensor`

**`state.py`** — `InverterState`: tracks `values`, `registers`, `history`, `onchange` callback. `group_sensors()` partitions sensor addresses into contiguous Modbus read blocks. `register_map()` converts a flat register list to an address dict.

**`interfaces/ModbusTCP.py`** — wraps `pymodbus.AsyncModbusTcpClient`. Implements `read_holding_registers(start, length)` and `write_register(address, value)`.

**`interfaces/ModbusSerial.py`** — wraps `pymodbus.AsyncModbusSerialClient` for RS-485 connections.

**`inverters/base_inverter.py`** — `BaseInverter`: `read_sensors(sensors)` uses `group_sensors()` for batched reads and updates `self.state`; `write_sensor(sensor, value)` handles bitmask-safe writes. `create_device(adapter)` is the public factory.

### Sensor definitions

```
definitions/
├── __init__.py            COMMON (device-type, protocol, serial)
├── three_phase_common.py  THREE_PHASE — all 3-phase sensors (config + measurements)
├── three_phase_lv.py      THREE_PHASE_LV = THREE_PHASE + LV battery (regs 586-592) + mfr
└── single_phase.py        SINGLE_PHASE — standalone single-phase definitions
```

### Sensor factor convention (Deye)

| factor sign | register interpretation | result |
|-------------|------------------------|--------|
| `factor > 0` | unsigned uint16/uint32 | `raw × factor` |
| `factor < 0` | signed int16/int32     | `int16 × abs(factor)` (sign preserved) |

**Temperature**: always `TempSensor(addr, name, factor=0.1, offset=-100)` — raw is uint16; formula: `raw × 0.1 − 100 = °C`.

**32-bit values** (energy counters): use address tuple `(low_reg, high_reg)` — Deye word-swap puts low word at first address.

## Usage Example

```python
import asyncio
from pydeye import BaseInverter
from pydeye.interfaces import ModbusTCP
from pydeye.definitions.three_phase_lv import THREE_PHASE_LV, battery_soc, battery_power, pv1_power

async def main():
    adapter = ModbusTCP("192.168.1.21", port=10001, unit=1)
    inverter = await BaseInverter.create_device(adapter)
    await inverter.init()

    # Track sensors you care about
    inverter.state.track(battery_soc, battery_power, pv1_power)

    # Read them in optimally batched Modbus requests
    await inverter.read_sensors([battery_soc, battery_power, pv1_power])

    print(inverter.state[battery_soc])    # e.g. 85
    print(inverter.state[battery_power])  # e.g. -2400 (W, negative = discharging)

    # Write a setting
    from pydeye.definitions.three_phase_common import grid_charge_enabled
    await inverter.write_sensor(grid_charge_enabled, "ON")

asyncio.run(main())
```

## Adding a New Inverter Model

1. Check whether the registers match `three_phase_common.py` or `single_phase.py`.
2. Create `definitions/<model>.py`, copy the nearest base `SensorDefinitions`, override/add model-specific sensors.
3. In `inverters/base_inverter.py` `create_device()`, add a branch for the new `InverterType` value.
4. Optionally create `inverters/<model>.py` if the legacy `update_status()` / `InverterMeasurements` API is needed for that model.

## Backward Compatibility

The original `measurements.py` dataclasses and `inverters/deye_SUN12KEU.py` (which uses `ModbusMapper` and returns `InverterMeasurements`) are preserved unchanged. `BaseInverter.create_device()` still returns a `DeyeSUN12KEU` for three-phase devices. The new sensor-based API (`read_sensors`, `write_sensor`, `InverterState`) is additive.
