"""Support for the Airly service."""
import homeassistant.helpers.config_validation as cv
import voluptuous as vol
from homeassistant import config_entries
from homeassistant.components.sensor import PLATFORM_SCHEMA
from homeassistant.const import (
    ATTR_ATTRIBUTION,
    ATTR_DEVICE_CLASS,
    CONF_API_KEY,
    CONF_LATITUDE,
    CONF_LONGITUDE,
    CONF_NAME,
    CONF_SCAN_INTERVAL,
    DEVICE_CLASS_HUMIDITY,
    DEVICE_CLASS_PRESSURE,
    DEVICE_CLASS_TEMPERATURE,
    PRESSURE_HPA,
    TEMP_CELSIUS,
)
from homeassistant.helpers.entity import Entity

from .const import (
    ATTR_CAQI,
    ATTR_CAQI_ADVICE,
    ATTR_CAQI_DESCRIPTION,
    ATTR_CAQI_LEVEL,
    CONF_LANGUAGE,
    DATA_CLIENT,
    DEFAULT_LANGUAGE,
    DEFAULT_NAME,
    DEFAULT_SCAN_INTERVAL,
    DOMAIN,
    LANGUAGE_CODES,
)

ATTR_ICON = "icon"
ATTR_LABEL = "label"
ATTR_LIMIT = "limit"
ATTR_PERCENT = "percent"
ATTR_PM1 = "PM1"
ATTR_PM10 = "PM10"
ATTR_PM10_LIMIT = "PM10_LIMIT"
ATTR_PM10_PERCENT = "PM10_PERCENT"
ATTR_PM25 = "PM25"
ATTR_PM25_LIMIT = "PM25_LIMIT"
ATTR_PM25_PERCENT = "PM25_PERCENT"
ATTR_HUMIDITY = "HUMIDITY"
ATTR_PRESSURE = "PRESSURE"
ATTR_TEMPERATURE = "TEMPERATURE"
ATTR_UNIT = "unit"

HUMI_PERCENT = "%"
VOLUME_MICROGRAMS_PER_CUBIC_METER = "µg/m³"

ATTRIBUTION = {"en": "Data provided by Airly", "pl": "Dane dostarczone przez Airly"}

SENSOR_TYPES = {
    ATTR_CAQI: {
        ATTR_DEVICE_CLASS: None,
        ATTR_ICON: None,
        ATTR_LABEL: ATTR_CAQI,
        ATTR_UNIT: None,
    },
    ATTR_CAQI_DESCRIPTION: {
        ATTR_DEVICE_CLASS: None,
        ATTR_ICON: "mdi:card-text-outline",
        ATTR_LABEL: ATTR_CAQI_DESCRIPTION.capitalize(),
        ATTR_UNIT: None,
    },
    ATTR_PM1: {
        ATTR_DEVICE_CLASS: None,
        ATTR_ICON: "mdi:blur",
        ATTR_LABEL: ATTR_PM1,
        ATTR_UNIT: VOLUME_MICROGRAMS_PER_CUBIC_METER,
    },
    ATTR_PM10: {
        ATTR_DEVICE_CLASS: None,
        ATTR_ICON: "mdi:blur",
        ATTR_LABEL: ATTR_PM10,
        ATTR_UNIT: VOLUME_MICROGRAMS_PER_CUBIC_METER,
    },
    ATTR_PM25: {
        ATTR_DEVICE_CLASS: None,
        ATTR_ICON: "mdi:blur",
        ATTR_LABEL: "PM2.5",
        ATTR_UNIT: VOLUME_MICROGRAMS_PER_CUBIC_METER,
    },
    ATTR_HUMIDITY: {
        ATTR_DEVICE_CLASS: DEVICE_CLASS_HUMIDITY,
        ATTR_ICON: None,
        ATTR_LABEL: ATTR_HUMIDITY.capitalize(),
        ATTR_UNIT: HUMI_PERCENT,
    },
    ATTR_PRESSURE: {
        ATTR_DEVICE_CLASS: DEVICE_CLASS_PRESSURE,
        ATTR_ICON: None,
        ATTR_LABEL: ATTR_PRESSURE.capitalize(),
        ATTR_UNIT: PRESSURE_HPA,
    },
    ATTR_TEMPERATURE: {
        ATTR_DEVICE_CLASS: DEVICE_CLASS_TEMPERATURE,
        ATTR_ICON: None,
        ATTR_LABEL: ATTR_TEMPERATURE.capitalize(),
        ATTR_UNIT: TEMP_CELSIUS,
    },
}

PLATFORM_SCHEMA = PLATFORM_SCHEMA.extend(
    {
        vol.Required(CONF_API_KEY, None): cv.string,
        vol.Required(CONF_LATITUDE): cv.latitude,
        vol.Required(CONF_LONGITUDE): cv.longitude,
        vol.Optional(CONF_LANGUAGE, default=DEFAULT_LANGUAGE): vol.In(LANGUAGE_CODES),
        vol.Optional(CONF_NAME, default=DEFAULT_NAME): cv.string,
        vol.Optional(CONF_SCAN_INTERVAL, default=DEFAULT_SCAN_INTERVAL): cv.time_period,
    }
)


async def async_setup_entry(hass, config_entry, async_add_entities):
    """Add a Airly entities from a config_entry."""
    name = config_entry.data[CONF_NAME]

    data = hass.data[DOMAIN][DATA_CLIENT][config_entry.entry_id]

    sensors = []
    for sensor in SENSOR_TYPES:
        sensors.append(AirlySensor(data, name, sensor))
    async_add_entities(sensors, True)


class BrotherPrinterSensor(Entity):
    """Define an Brother Printer sensor."""

    def __init__(self, data, name, kind):
        """Initialize."""
        self._data = data
        self._name = name
        self._kind = kind
        self._device_class = None
        self._state = None
        self._icon = None
        self._unit_of_measurement = None

    @property
    def name(self):
        """Return the name."""
        return f"{self._name} {SENSOR_TYPES[self.kind][ATTR_LABEL]}"

    @property
    def state(self):
        """Return the state."""
        self._state = self.data[self.kind]
        if self.kind in [ATTR_PM1, ATTR_PM25, ATTR_PM10, ATTR_PRESSURE, ATTR_CAQI]:
            self._state = round(self._state)
        if self.kind in [ATTR_TEMPERATURE, ATTR_HUMIDITY]:
            self._state = round(self._state, 1)
        return self._state

    @property
    def device_state_attributes(self):
        """Return the state attributes."""
        if self.kind == ATTR_CAQI_DESCRIPTION:
            self._attrs[ATTR_CAQI_ADVICE] = self.data[ATTR_CAQI_ADVICE]
        if self.kind == ATTR_CAQI:
            self._attrs[ATTR_CAQI_LEVEL] = self.data[ATTR_CAQI_LEVEL]
        if self.kind == ATTR_PM25:
            self._attrs[ATTR_LIMIT] = self.data[ATTR_PM25_LIMIT]
            self._attrs[ATTR_PERCENT] = round(self.data[ATTR_PM25_PERCENT])
        if self.kind == ATTR_PM10:
            self._attrs[ATTR_LIMIT] = self.data[ATTR_PM10_LIMIT]
            self._attrs[ATTR_PERCENT] = round(self.data[ATTR_PM10_PERCENT])
        return self._attrs

    @property
    def icon(self):
        """Return the icon."""
        if self.kind == ATTR_CAQI:
            if isinstance(self._state, int):
                if self._state <= 25:
                    self._icon = "mdi:emoticon-excited"
                elif self._state <= 50:
                    self._icon = "mdi:emoticon-happy"
                elif self._state <= 75:
                    self._icon = "mdi:emoticon-neutral"
                elif self._state <= 100:
                    self._icon = "mdi:emoticon-sad"
                elif self._state > 100:
                    self._icon = "mdi:emoticon-dead"
        else:
            self._icon = SENSOR_TYPES[self.kind][ATTR_ICON]
        return self._icon

    @property
    def device_class(self):
        """Return the device_class."""
        return SENSOR_TYPES[self.kind][ATTR_DEVICE_CLASS]

    @property
    def unique_id(self):
        """Return a unique_id for this entity."""
        return f"{self.airly.latitude}-{self.airly.longitude}-{self.kind.lower()}"

    @property
    def unit_of_measurement(self):
        """Return the unit the value is expressed in."""
        return SENSOR_TYPES[self.kind][ATTR_UNIT]

    @property
    def available(self):
        """Return True if entity is available."""
        return bool(self.airly.data)

    async def async_update(self):
        """Get the data from Airly."""
        await self.airly.async_update()

        if self.airly.data:
            self.data = self.airly.data
