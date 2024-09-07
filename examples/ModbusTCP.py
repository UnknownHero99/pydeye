import asyncio
from pydeye import BaseInverter
from pydeye.interfaces import ModbusTCP
from pydeye.inverters.base_inverter import BaseInverter

async def main():
	adapter = ModbusTCP("192.168.1.21", port=10001, unit=1)
	inverter = await  BaseInverter.create_device(adapter)
	await inverter.init()
	await inverter.update_status()
	

asyncio.run(main())