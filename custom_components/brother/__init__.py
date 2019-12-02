"""The Brother component."""
import asyncio
import logging
from datetime import timedelta

from brother import Brother, SnmpError, UnsupportedModel
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import CONF_HOST, CONF_NAME
from homeassistant.core import HomeAssistant
from homeassistant.util import Throttle

from .const import DEFAULT_NAME, DOMAIN

PLATFORMS = ["sensor"]

DEFAULT_SCAN_INTERVAL = timedelta(seconds=30)

_LOGGER = logging.getLogger(__name__)


async def async_setup(hass: HomeAssistant, config: dict):
    """Set up the Brother component."""
    hass.data[DOMAIN] = {}
    return True


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry):
    """Set up Brother from a config entry."""
    host = entry.data[CONF_HOST]

    brother = BrotherData(host)

    hass.data[DOMAIN][entry.entry_id] = brother

    for component in PLATFORMS:
        hass.async_create_task(
            hass.config_entries.async_forward_entry_setup(entry, component)
        )

    return True


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry):
    """Unload a config entry."""
    unload_ok = all(
        await asyncio.gather(
            *[
                hass.config_entries.async_forward_entry_unload(entry, component)
                for component in PLATFORMS
            ]
        )
    )
    if unload_ok:
        hass.data[DOMAIN].pop(entry.entry_id)

    return unload_ok


class BrotherData:
    """Define an object to hold sensor data."""

    def __init__(self, host):
        """Initialize."""
        self._brother = Brother(host)
        self.host = host
        self.model = None
        self.serial = None
        self.firmware = None
        self.available = False
        self.data = {}

    @Throttle(DEFAULT_SCAN_INTERVAL)
    async def async_update(self):
        """Update data via library."""
        try:
            await self._brother.async_update()
        except (SnmpError, UnsupportedModel) as error:
            _LOGGER.error("Could not fetch data from %s, error: %s", self.host, error)
            self.data = {}
            return

        self.model = self._brother.model
        self.serial = self._brother.serial
        self.firmware = self._brother.firmware
        self.available = self._brother.available
        self.data = self._brother.data
