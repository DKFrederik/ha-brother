"""Support for the Brother service."""
import logging

from homeassistant.helpers.entity import Entity

from .const import *

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(hass, config_entry, async_add_entities):
    """Add Brother entities from a config_entry."""
    brother = hass.data[DOMAIN][config_entry.entry_id]
    await brother.async_update()

    name = brother.model

    _LOGGER.debug("Brother printer model: %s", brother.model)

    sensors = []
    for sensor in SENSOR_TYPES:
        if sensor in brother.data:
            sensors.append(BrotherPrinterSensor(brother, name, sensor))
    async_add_entities(sensors, True)


class BrotherPrinterSensor(Entity):
    """Define an Brother Printer sensor."""

    def __init__(self, data, name, kind):
        """Initialize."""
        self.brother = data
        self._name = name
        self.kind = kind
        self._state = None
        self._unit_of_measurement = None
        self._attrs = {}

    @property
    def name(self):
        """Return the name."""
        return f"{self._name} {SENSOR_TYPES[self.kind][ATTR_LABEL]}"

    @property
    def state(self):
        """Return the state."""
        self._state = self.brother.data[self.kind]
        return self._state

    @property
    def device_state_attributes(self):
        """Return the state attributes."""
        if self.kind == ATTR_DRUM_REMAINING_LIFE:
            self._attrs["remaining_pages"] = self.brother.data.get(
                ATTR_DRUM_REMAINING_PAGES
            )
            self._attrs["counter"] = self.brother.data.get(ATTR_DRUM_COUNTER)
        return self._attrs

    @property
    def icon(self):
        """Return the icon."""
        return SENSOR_TYPES[self.kind][ATTR_ICON]

    @property
    def unique_id(self):
        """Return a unique_id for this entity."""
        return f"{self.brother.serial}_{self.kind}".lower()

    @property
    def unit_of_measurement(self):
        """Return the unit the value is expressed in."""
        return SENSOR_TYPES[self.kind][ATTR_UNIT]

    @property
    def available(self):
        """Return True if entity is available."""
        return self.brother.available

    @property
    def device_info(self):
        """Return the device info."""
        return {
            "identifiers": {(DOMAIN, self.brother.serial.lower())},
            "name": self.brother.model,
            "manufacturer": "Brother",
            "model": self.brother.model,
            "sw_version": self.brother.firmware,
        }

    async def async_update(self):
        """Update the data from printer."""
        await self.brother.async_update()
