"""Platform for sensor integration."""
import logging
from datetime import timedelta
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed
from homeassistant.const import TEMP_CELSIUS
from homeassistant.helpers.entity import Entity
from pymodbus.client.sync import ModbusTcpClient

_LOGGER = logging.getLogger(__name__)

PERCENT = "%"


async def async_setup_platform(hass, config, add_entities, discovery_info=None):
    """Set up the sensor platform."""

    client = ModbusTcpClient("192.168.1.18")

    async def async_update_data():
        """Fetch date from thessla device"""
        client.connect()
        temperatures = client.read_input_registers(16, 3, unit=10)
        fan_speed = client.read_holding_registers(4210, 1, unit=10)
        client.close()
        data = list(map(get_data_from_register, temperatures.registers))
        data.append(fan_speed.registers[0])
        return data

    def get_data_from_register(register):
        return round(register * 0.1, 1)

    coordinator = DataUpdateCoordinator(
        hass,
        _LOGGER,
        # Name of the data. For logging purposes.
        name="sensor",
        update_method=async_update_data,
        # Polling interval. Will only be polled if there are subscribers.
        update_interval=timedelta(seconds=30),
    )

    sensors = [
        ["Temperatura czerpni", TEMP_CELSIUS, 0, None],
        ["Temperatura nawiewu", TEMP_CELSIUS, 1, None],
        ["Temperatura wywiewu", TEMP_CELSIUS, 2, None],
        ["Wydajność wentylacji", PERCENT, 3, "mdi:fan"],
    ]

    entities = []
    for sensor in sensors:
        entities.append(
            ThesslaSensor(sensor[0], sensor[1], sensor[2], sensor[3], coordinator)
        )

    await coordinator.async_refresh()

    add_entities(entities)


class ThesslaSensor(Entity):
    """Representation of a Sensor."""

    def __init__(self, name, unit, registerNumber, icon, coordinator):
        """Initialize the sensor."""
        self._state = None
        self._name = name
        self._unit = unit
        self._register_number = registerNumber
        self.coordinator = coordinator
        self._icon = icon

    @property
    def should_poll(self):
        """No need to poll. Coordinator notifies entity of updates."""
        return False

    async def async_added_to_hass(self):
        """When entity is added to hass."""
        self.coordinator.async_add_listener(self.async_write_ha_state)

    async def async_will_remove_from_hass(self):
        """When entity will be removed from hass."""
        self.coordinator.async_remove_listener(self.async_write_ha_state)

    @property
    def name(self):
        """Return the name of the sensor."""
        return self._name

    @property
    def state(self):
        """Return the state of the sensor."""
        return self.coordinator.data[self._register_number]

    @property
    def unit_of_measurement(self):
        """Return the unit of measurement."""
        return self._unit

    @property
    def icon(self):
        # return "mdi:home"
        return self._icon
