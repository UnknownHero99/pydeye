from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Sequence


class ModbusInterface(ABC):
    """Abstract base class for all Modbus transport adapters."""

    @abstractmethod
    async def connect(self) -> None:
        """Establish the connection."""

    @abstractmethod
    async def close(self) -> None:
        """Close the connection."""

    @abstractmethod
    def connected(self) -> bool:
        """Return True when the connection is active."""

    @abstractmethod
    async def read_holding_registers(self, start: int, length: int) -> Sequence[int]:
        """Read *length* holding registers beginning at *start*."""

    @abstractmethod
    async def write_register(self, address: int, value: int) -> bool:
        """Write a single holding register; return True on success."""

    async def get_basic_info(self):
        """Read device identification registers and return a BasicInfo object."""
        from pydeye.helper import BasicInfo, InverterType, ModbusMapper
        data = await self.read_holding_registers(0, 24)
        mapper = ModbusMapper(list(data), 0)

        protocol_version = f"{mapper.get_value(2):04X}"
        serial_number = "".join(mapper.get_string(r) for r in range(3, 8))
        inv_type = InverterType.UNDEFINED
        for t in InverterType:
            if t.value[0] == mapper.get_value(0):
                inv_type = t
                break

        rated_power = mapper.get_uint32(20) / 10
        main_version = (
            f"{mapper.get_value(14):04X}-{mapper.get_value(15):04X}-{mapper.get_value(11):04X}"
        )
        hmi_version = f"{mapper.get_value(17):04X}-{mapper.get_value(18):04X}"

        return BasicInfo(inv_type, serial_number, main_version, hmi_version, protocol_version, rated_power)
