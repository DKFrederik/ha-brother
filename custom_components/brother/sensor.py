"""Support for the Brother service."""
import logging

from homeassistant.helpers.entity import Entity

from .const import DOMAIN

ATTR_STATUS = "status"
ATTR_UNIT = "unit"
ATTR_LABEL = "label"
ATTR_ICON = "icon"

SENSOR_TYPES = {
    ATTR_STATUS: {ATTR_ICON: "icon:mdi:printer", ATTR_LABEL: "Status", ATTR_UNIT: None},
    "printer_count": {
        ATTR_ICON: "mdi:file-document",
        ATTR_LABEL: "Printer Count",
        ATTR_UNIT: "p",
    },
    "drum_remaining_life": {
        ATTR_ICON: "mdi:chart-donut",
        ATTR_LABEL: "Drum Remaining Life",
        ATTR_UNIT: "%",
    },
    "belt_unit_remaining_life": {
        ATTR_ICON: "mdi:chart-donut",
        ATTR_LABEL: "Belt Unit Remaining Life",
        ATTR_UNIT: "%",
    },
    "fuser_remaining_life": {
        ATTR_ICON: "mdi:chart-donut",
        ATTR_LABEL: "Fuser Remaining Life",
        ATTR_UNIT: "%",
    },
    "laser_remaining_life": {
        ATTR_ICON: "mdi:chart-donut",
        ATTR_LABEL: "Laser Remaining Life",
        ATTR_UNIT: "%",
    },
    "pf_kit_1_remaining_life": {
        ATTR_ICON: "mdi:chart-donut",
        ATTR_LABEL: "PF Kit 1 Remaining Life",
        ATTR_UNIT: "%",
    },
    "pf_kit_mp_remaining_life": {
        ATTR_ICON: "mdi:chart-donut",
        ATTR_LABEL: "PF Kit MP Remaining Life",
        ATTR_UNIT: "%",
    },
    "black_toner": {
        ATTR_ICON: "mdi:flask-outline",
        ATTR_LABEL: "Black Toner",
        ATTR_UNIT: "%",
    },
    "black_toner_remaining": {
        ATTR_ICON: "mdi:flask-outline",
        ATTR_LABEL: "Black Toner Remaining",
        ATTR_UNIT: "%",
    },
    "cyan_toner": {
        ATTR_ICON: "mdi:flask-outline",
        ATTR_LABEL: "Cyan Toner",
        ATTR_UNIT: "%",
    },
    "cyan_toner_remaining": {
        ATTR_ICON: "mdi:flask-outline",
        ATTR_LABEL: "Cyan Toner Remaining",
        ATTR_UNIT: "%",
    },
    "magenta_toner": {
        ATTR_ICON: "mdi:flask-outline",
        ATTR_LABEL: "Magenta Toner",
        ATTR_UNIT: "%",
    },
    "magenta_toner_remaining": {
        ATTR_ICON: "mdi:flask-outline",
        ATTR_LABEL: "Magenta Toner Remaining",
        ATTR_UNIT: "%",
    },
    "yellow_toner": {
        ATTR_ICON: "mdi:flask-outline",
        ATTR_LABEL: "Yellow Toner",
        ATTR_UNIT: "%",
    },
    "yellow_toner_remaining": {
        ATTR_ICON: "mdi:flask-outline",
        ATTR_LABEL: "Yellow Toner Remaining",
        ATTR_UNIT: "%",
    },
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
        if self.kind == "drum_remaining_life":
            self._attrs["drum_remaining_pages"] = self.brother.data.get(
                "drum_remaining_pages"
            )
            self._attrs["drum_counter"] = self.brother.data.get("drum_count")
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
