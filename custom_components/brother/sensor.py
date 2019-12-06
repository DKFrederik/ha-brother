"""Support for the Brother service."""
import logging

from homeassistant.const import CONF_NAME
from homeassistant.helpers import device_registry, entity_registry
from homeassistant.helpers.entity import Entity

from .const import (
    ATTR_DRUM_COUNTER,
    ATTR_DRUM_REMAINING_LIFE,
    ATTR_DRUM_REMAINING_PAGES,
    ATTR_ICON,
    ATTR_LABEL,
    ATTR_UNIT,
    DOMAIN,
    SENSOR_TYPES,
)

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(hass, config_entry, async_add_entities):
    """Add Brother entities from a config_entry."""
    brother = hass.data[DOMAIN][config_entry.entry_id]
    await brother.async_update()

    name = config_entry.data[CONF_NAME]

    sensors = []

    if not brother.available:
        dev_reg = await device_registry.async_get_registry(hass)
        for device in dev_reg.devices.values():
            if config_entry.entry_id in device.config_entries:
                _device_info = {
                    "name": device.name,
                    "model": device.model,
                    "identifiers": device.identifiers,
                    "manufacturer": device.manufacturer,
                    "sw_version": device.sw_version,
                }
                break
        reg_serial = next(iter(_device_info["identifiers"]))[1]
        reg_sensors = []
        ent_reg = await entity_registry.async_get_registry(hass)
        for entry in ent_reg.entities.items():
            if entry[1].config_entry_id == config_entry.entry_id:
                reg_sensors.append(entry[1].unique_id.replace(reg_serial + "_", ""))
        for sensor in reg_sensors:
            sensors.append(BrotherPrinterSensor(brother, name, sensor, _device_info))
    else:
        for sensor in SENSOR_TYPES:
            if sensor in brother.data:
                sensors.append(BrotherPrinterSensor(brother, name, sensor))
    async_add_entities(sensors, True)


class BrotherPrinterSensor(Entity):
    """Define an Brother Printer sensor."""

    def __init__(self, data, name, kind, device_info=None):
        """Initialize."""
        self.printer = data
        self._name = name
        self.kind = kind
        self._state = None
        self._unit_of_measurement = None
        if device_info:
            self._device_info = device_info
            serial = next(iter(device_info["identifiers"]))[1]
            self._unique_id = f"{serial}_{self.kind}"
        else:
            self._device_info = {
                "identifiers": {(DOMAIN, self.printer.serial.lower())},
                "name": self.printer.model,
                "manufacturer": "Brother",
                "model": self.printer.model,
                "sw_version": self.printer.firmware,
            }
            self._unique_id = f"{self.printer.serial}_{self.kind}".lower()

        self._attrs = {}

    @property
    def name(self):
        """Return the name."""
        return f"{self._name} {SENSOR_TYPES[self.kind][ATTR_LABEL]}"

    @property
    def state(self):
        """Return the state."""
        self._state = self.printer.data[self.kind]
        return self._state

    @property
    def device_state_attributes(self):
        """Return the state attributes."""
        if self.kind == ATTR_DRUM_REMAINING_LIFE:
            self._attrs["remaining_pages"] = self.printer.data.get(
                ATTR_DRUM_REMAINING_PAGES
            )
            self._attrs["counter"] = self.printer.data.get(ATTR_DRUM_COUNTER)
        return self._attrs

    @property
    def icon(self):
        """Return the icon."""
        return SENSOR_TYPES[self.kind][ATTR_ICON]

    @property
    def unique_id(self):
        """Return a unique_id for this entity."""
        return

    @property
    def unit_of_measurement(self):
        """Return the unit the value is expressed in."""
        return SENSOR_TYPES[self.kind][ATTR_UNIT]

    @property
    def available(self):
        """Return True if entity is available."""
        return self.printer.available

    @property
    def device_info(self):
        """Return the device info."""
        return self._device_info

    async def async_update(self):
        """Update the data from printer."""
        await self.printer.async_update()
