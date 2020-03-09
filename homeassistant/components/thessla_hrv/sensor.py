"""Platform for sensor integration."""
from homeassistant.const import TEMP_CELSIUS
from homeassistant.helpers.entity import Entity
from pymodbus.client.sync import ModbusTcpClient


def setup_platform(hass, config, add_entities, discovery_info=None):
    """Set up the sensor platform."""

    sensors = [
        ["Temperatura czerpni", TEMP_CELSIUS, 0],
        ["Temperatura nawiewu", TEMP_CELSIUS, 1],
        ["Temperatura wywiewu", TEMP_CELSIUS, 2],
    ]

    entities = []
    for sensor in sensors:
        entities.append(ThesslaSensor(sensor[0], sensor[1], sensor[2]))

    add_entities(entities)


class ThesslaSensor(Entity):
    """Representation of a Sensor."""

    def __init__(self, name, unit, registerNumber):
        """Initialize the sensor."""
        self._state = None
        self._name = name
        self._unit = unit
        self._register_number = registerNumber

    @property
    def name(self):
        """Return the name of the sensor."""
        return self._name

    @property
    def state(self):
        """Return the state of the sensor."""
        return self._state

    @property
    def unit_of_measurement(self):
        """Return the unit of measurement."""
        return self._unit

    def update(self):
        """Fetch new state data for the sensor.

        This is the only method that should fetch new data for Home Assistant.
        """
        client = ModbusTcpClient("192.168.1.18")
        client.connect()
        result = client.read_input_registers(16, 3, unit=10)
        client.close()
        value = round(result.registers[self._register_number] * 0.1, 1)
        self._state = value
