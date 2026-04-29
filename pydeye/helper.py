from __future__ import annotations

import re
import struct
import logging
from enum import Enum
from typing import Optional, Union

_LOG = logging.getLogger(__name__)

# Type aliases
NumType = Union[float, int]
ValType = Union[str, float, int]
RegType = tuple[int, ...]

# Unit constants
AMPS = "A"
CELSIUS = "°C"
HZ = "Hz"
KWH = "kWh"
VOLT = "V"
WATT = "W"

BOOL_ON = "ON"
BOOL_OFF = "OFF"


def slug(name: str) -> str:
    """Convert a name to a lowercase underscore-separated identifier."""
    return re.sub(r"[^a-z0-9_]+", "_", name.lower()).strip("_")


def int_round(value: float) -> NumType:
    """Round to 2 decimal places; return int when the value is whole."""
    val = round(float(value), 2)
    return int(val) if val == int(val) else val


def as_num(value: ValType) -> NumType:
    """Safely convert any value to a number, defaulting to 0."""
    try:
        return float(value)
    except (ValueError, TypeError):
        return 0


def hex_str(regs: RegType, address: Optional[RegType] = None) -> str:
    """Format register values as a hex string, optionally with addresses."""
    if address is not None:
        return " ".join(f"{a}:{v:04X}" for a, v in zip(address, regs))
    return " ".join(f"{v:04X}" for v in regs)


def pack_value(value: int, bits: int = 16, signed: bool = False) -> RegType:
    """Pack an integer into register format (Deye word-swap: low word first)."""
    if bits == 16:
        if signed and value < 0:
            value += 65536
        return (value & 0xFFFF,)
    if bits == 32:
        if signed and value < 0:
            value += 4294967296
        lo = value & 0xFFFF
        hi = (value >> 16) & 0xFFFF
        return (lo, hi)
    raise ValueError(f"Unsupported bits: {bits}")


def unpack_value(regs: RegType, signed: bool = False) -> int:
    """Unpack one or two registers into an integer (Deye word-swap: regs[0]=low)."""
    if len(regs) == 1:
        val = regs[0] & 0xFFFF
        if signed and val > 32767:
            val -= 65536
        return val
    if len(regs) == 2:
        val = ((regs[1] & 0xFFFF) << 16) | (regs[0] & 0xFFFF)
        if signed and val > 2147483647:
            val -= 4294967296
        return val
    raise ValueError(f"Cannot unpack {len(regs)} registers")


def patch_bitmask(current: int, value: int, bitmask: int) -> int:
    """Apply value to current register using a bitmask, preserving unrelated bits."""
    return (current & ~bitmask) | (value & bitmask)


class SSTime:
    """Converts between time formats: HH:MM string, packed register (HHMM), and minutes."""

    def __init__(
        self,
        minutes: int = 0,
        regv: Optional[int] = None,
        strv: Optional[str] = None,
    ) -> None:
        if regv is not None:
            # Deye decimal encoding: register value = hours*100 + minutes
            h = regv // 100
            m = regv % 100
            self.minutes = h * 60 + m
        elif strv is not None:
            parts = str(strv).strip().split(":")
            h = int(parts[0]) if parts else 0
            m = int(parts[1]) if len(parts) > 1 else 0
            self.minutes = h * 60 + m
        else:
            self.minutes = minutes

    @property
    def reg_value(self) -> int:
        h, m = divmod(self.minutes % (24 * 60), 60)
        return h * 100 + m  # Deye decimal encoding: hours*100 + minutes

    @property
    def str_value(self) -> str:
        h, m = divmod(self.minutes % (24 * 60), 60)
        return f"{h}:{m:02d}"


# ── Legacy classes kept for backward compatibility ──────────────────────────

class InverterType(Enum):
    UNDEFINED = (0, "Undefined")
    SINGLE_PHASE_HYBRID_INVERTER = (3, "Single phase hybrid inverter")
    MICRO_INVERTER = (4, "Micro inverter")
    LOW_VOLTAGE_THREE_PHASE_HYBRID_INVERTER = (5, "Low voltage three phase hybrid inverter")
    HIGH_VOLTAGE_THREE_PHASE_HYBRID_INVERTER = (6, "High voltage three phase hybrid inverter")
    HIGH_VOLTAGE_THREE_PHASE_INVERTER_6_12KW = (7, "High voltage three phase inverter 6-12kW")
    HIGH_VOLTAGE_THREE_PHASE_INVERTER_20_50WK = (262, "High voltage three phase inverter 20-50kW")
    THREE_PHASE_POWER_CONVERSION_SYSTEM = (8, "Three phase power conversion system")
    BALCONY_ENERGY_STORAGE_SYSTEM = (9, "Balcony energy storage system")


class BasicInfo:
    def __init__(self, type: InverterType, serial_number, main_version, hmi_version, protocol_version, rated_power) -> None:
        self.type = type
        self.serial_number = serial_number
        self.main_version = main_version
        self.hmi_version = hmi_version
        self.protocol_version = protocol_version
        self.rated_power = rated_power


class ModbusMapper:
    """Maps a flat list of register values to absolute addresses."""

    def __init__(self, register_values, start_address):
        self.register_values = register_values
        self.start_address = start_address

    def get_value(self, desired_address):
        if desired_address < self.start_address or desired_address >= self.start_address + len(self.register_values):
            return None
        return self.register_values[desired_address - self.start_address]

    def get_uint16(self, desired_address):
        return self.get_value(desired_address)

    def get_int16(self, desired_address):
        value = self.get_value(desired_address)
        if value is None:
            return None
        if value > 32767:
            value -= 65536
        return value

    def get_uint32(self, desired_address, word_swap=True):
        high_word = self.get_value(desired_address)
        low_word = self.get_value(desired_address + 1)
        if word_swap:
            return (low_word << 16) + high_word
        return (high_word << 16) + low_word

    def get_string(self, desired_address):
        value = self.get_value(desired_address)
        high_byte = (value >> 8) & 0xFF
        low_byte = value & 0xFF
        return "".join([chr(high_byte), chr(low_byte)])

    def dump(self):
        for i, value in enumerate(self.register_values):
            print(f"Address {self.start_address + i}: {value} 0x{value:04X}")
