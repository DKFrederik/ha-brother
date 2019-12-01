"""Support for the Brother service."""
import logging

from homeassistant import config_entries
from homeassistant.helpers.entity import Entity

from .const import DOMAIN

ATTR_STATUS = "status"
ATTR_UNIT = "unit"
ATTR_LABEL = "label"
ATTR_ICON = "icon"

SENSOR_TYPES = {
    ATTR_STATUS: {
        ATTR_ICON: "icon:mdi:printer",
        ATTR_LABEL: "Status",
        ATTR_UNIT: None,
    },
    "printer_count": {
        ATTR_ICON: "mdi:file-document",
        ATTR_LABEL: "Printer Count",
        ATTR_UNIT: "p"
    },
    "drum_remaining_life": {
        ATTR_ICON: "mdi:chart-donut",
        ATTR_LABEL: "Drum Remaining Life",
        ATTR_UNIT: "%"
    },
    "printer_count": {
        ATTR_ICON: "mdi:file-document",
        ATTR_LABEL: "Printer Count",
        ATTR_UNIT: "p"
    },
    "black_toner": {
        ATTR_ICON: "mdi:flask-outline",
        ATTR_LABEL: "Black Toner",
        ATTR_UNIT: "%"
    }
}

_LOGGER = logging.getLogger(__name__)

async def async_setup_entry(hass, config_entry, async_add_entities):
    """Add Brother entities from a config_entry."""
    brother = hass.data[DOMAIN][config_entry.entry_id]
    await brother.async_update()

    name = brother.model

    _LOGGER.debug(brother.model)
    _LOGGER.debug(brother.data)

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

    @property
    def name(self):
        """Return the name."""
        return f"{self._name} {SENSOR_TYPES[self.kind][ATTR_LABEL]}"

    @property
    def state(self):
        """Return the state."""
        self._state = self.brother.data[self.kind]
        return self._state

    # @property
    # def device_state_attributes(self):
    #     """Return the state attributes."""
    #     if self.kind == ATTR_CAQI_DESCRIPTION:
    #         self._attrs[ATTR_CAQI_ADVICE] = self.data[ATTR_CAQI_ADVICE]
    #     if self.kind == ATTR_CAQI:
    #         self._attrs[ATTR_CAQI_LEVEL] = self.data[ATTR_CAQI_LEVEL]
    #     if self.kind == ATTR_PM25:
    #         self._attrs[ATTR_LIMIT] = self.data[ATTR_PM25_LIMIT]
    #         self._attrs[ATTR_PERCENT] = round(self.data[ATTR_PM25_PERCENT])
    #     if self.kind == ATTR_PM10:
    #         self._attrs[ATTR_LIMIT] = self.data[ATTR_PM10_LIMIT]
    #         self._attrs[ATTR_PERCENT] = round(self.data[ATTR_PM10_PERCENT])
    #     return self._attrs

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
            "identifiers": {
                # Serial numbers are unique identifiers within a specific domain
                (DOMAIN, self.brother.serial.lower())
            },
            "name": self.brother.model,
            "manufacturer": "Brother",
            "model": self.brother.model,
            "sw_version": self.brother.firmware,
        }

    async def async_update(self):
        """Get the data from Airly."""
        await self.brother.async_update()
