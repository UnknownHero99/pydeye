from __future__ import annotations

from typing import Sequence

from pymodbus.client import AsyncModbusTcpClient

from pydeye.interfaces.base import ModbusInterface


class ModbusTCP(ModbusInterface):
    """Async Modbus TCP adapter (also used as a Modbus TCP-over-serial gateway)."""

    def __init__(self, host: str, port: int = 502, unit: int = 1, timeout: int = 3) -> None:
        self.client = AsyncModbusTcpClient(host=host, port=port, timeout=timeout)
        self.unit = unit

    async def connect(self) -> None:
        await self.client.connect()

    async def close(self) -> None:
        self.client.close()

    def connected(self) -> bool:
        return self.client.connected

    # ── New standardised API ─────────────────────────────────────────────────

    async def read_holding_registers(self, start: int, length: int) -> Sequence[int]:
        if not self.connected():
            await self.connect()
        result = await self.client.read_holding_registers(start, count=length, device_id=self.unit)
        return result.registers

    async def write_register(self, address: int, value: int) -> bool:
        if not self.connected():
            await self.connect()
        result = await self.client.write_registers(address, values=[value], device_id=self.unit)
        return not result.isError()

    # ── Legacy API kept for backward compatibility ───────────────────────────

    async def read_registers(self, register_address: int, count: int) -> Sequence[int]:
        return await self.read_holding_registers(register_address, count)

    async def write_registers(self, register_address: int, values: list[int]):
        if not self.connected():
            await self.connect()
        return await self.client.write_registers(
            register_address, values=values, device_id=self.unit
        )
