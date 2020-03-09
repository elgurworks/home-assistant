"""Demo fan platform that has a fake fan."""
from homeassistant.components.fan import (
    SUPPORT_SET_SPEED,
    FanEntity,
)
from homeassistant.const import STATE_OFF

from pymodbus.client.sync import ModbusTcpClient

import logging

LIMITED_SUPPORT = SUPPORT_SET_SPEED

_LOGGER = logging.getLogger(__name__)


SPEED_40 = "40%"
SPEED_50 = "50%"
SPEED_60 = "60%"
SPEED_70 = "70%"
SPEED_80 = "80%"
SPEED_90 = "90%"
SPEED_100 = "100%"

SPPED_VALUE = {
    40: SPEED_40,
    50: SPEED_50,
    60: SPEED_60,
    70: SPEED_70,
    80: SPEED_80,
    90: SPEED_90,
    100: SPEED_100,
}


async def async_setup_platform(hass, config, async_add_entities, discovery_info=None):
    """Set up the demo fan platform."""
    async_add_entities(
        [ThesslaFan(hass, "Moc wentylatora", LIMITED_SUPPORT),]
    )


async def async_setup_entry(hass, config_entry, async_add_entities):
    """Set up the Demo config entry."""
    await async_setup_platform(hass, {}, async_add_entities)


class ThesslaFan(FanEntity):
    """A demonstration fan component."""

    def __init__(self, hass, name: str, supported_features: int) -> None:
        """Initialize the entity."""
        self.hass = hass
        self._supported_features = supported_features
        self._speed = None
        self._name = name
        self._modbus_client = ModbusTcpClient("192.168.1.18")

    @property
    def name(self) -> str:
        """Get entity name."""
        return self._name

    @property
    def speed(self) -> str:
        """Return the current speed."""
        return self._speed

    @property
    def speed_list(self) -> list:
        """Get the list of available speeds."""
        return [SPEED_40, SPEED_50, SPEED_60, SPEED_70, SPEED_80, SPEED_90, SPEED_100]

    def turn_on(self, speed: str = None, **kwargs) -> None:
        """Turn on the entity."""
        if speed is None:
            speed = SPEED_50
        self.set_speed(speed)

    def turn_off(self, **kwargs) -> None:
        """Turn off the entity."""
        self.set_speed(STATE_OFF)

    def set_speed(self, speed: str) -> None:
        """Set the speed of the fan."""
        _LOGGER.error("set speed")
        self._speed = speed
        value = list(SPPED_VALUE.keys())[list(SPPED_VALUE.values()).index(speed)]
        self._modbus_client.connect()
        self._modbus_client.write_register(4210, value, unit=10)
        self._modbus_client.close()
        self.schedule_update_ha_state()

    @property
    def supported_features(self) -> int:
        """Flag supported features."""
        return self._supported_features

    def update(self):
        """Fetch new state data for the sensor.

        This is the only method that should fetch new data for Home Assistant.
        """
        _LOGGER.error("update ")
        self._modbus_client.connect()
        result = self._modbus_client.read_holding_registers(4210, 1, unit=10)
        self._modbus_client.close()
        self._speed = SPPED_VALUE.get(result.registers[0], SPEED_50)
