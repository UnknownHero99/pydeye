from __future__ import annotations

from typing import Sequence

from pymodbus.client import AsyncModbusSerialClient

from pydeye.interfaces.base import ModbusInterface


class ModbusSerial(ModbusInterface):
    """Async Modbus RTU adapter for RS-485 serial connections."""

    def __init__(
        self,
        port: str,
        baudrate: int = 9600,
        stopbits: int = 1,
        bytesize: int = 8,
        parity: str = "N",
        unit: int = 1,
        timeout: int = 3,
    ) -> None:
        self.client = AsyncModbusSerialClient(
            port=port,
            baudrate=baudrate,
            stopbits=stopbits,
            bytesize=bytesize,
            parity=parity,
            timeout=timeout,
        )
        self.unit = unit

    async def connect(self) -> None:
        await self.client.connect()

    async def close(self) -> None:
        self.client.close()

    def connected(self) -> bool:
        return self.client.connected

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
