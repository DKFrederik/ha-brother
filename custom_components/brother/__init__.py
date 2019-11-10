"""The Brother component."""
import logging
from aiohttp import ClientSession
from asyncio import TimeoutError
from datetime import timedelta

from aiohttp.client_exceptions import ClientConnectorError
from async_timeout import timeout
from homeassistant.const import CONF_HOST, CONF_NAME, CONF_SCAN_INTERVAL
from homeassistant.core import Config, HomeAssistant
from homeassistant.exceptions import ConfigEntryNotReady
from homeassistant.helpers.aiohttp_client import async_get_clientsession
from homeassistant.util import Throttle

from .const import (
    DATA_CLIENT,
    DEFAULT_NAME,
    DEFAULT_SCAN_INTERVAL,
    DOMAIN,
)

_LOGGER = logging.getLogger(__name__)

URL_INFO = "http://{}/general/information.html"
URL_STATUS = "http://{}/general/status.html"

CONF_MODEL = "model"
MODEL_HL_L2340DW = "HL-L2340DW"

async def async_setup(hass: HomeAssistant, config: Config) -> bool:
    """Set up configured Brother."""
    hass.data[DOMAIN] = {}
    hass.data[DOMAIN][DATA_CLIENT] = {}
    return True


async def async_setup_entry(hass, config_entry):
    """Set up Brother as config entry."""
    host = config_entry.data[CONF_HOST]
    try:
        scan_interval = config_entry.options[CONF_SCAN_INTERVAL]
    except KeyError:
        scan_interval = DEFAULT_SCAN_INTERVAL

    websession = async_get_clientsession(hass)

    brother = BrotherData(websession, host, scan_interval=timedelta(seconds=scan_interval))

    await brother.async_update()

    hass.data[DOMAIN][DATA_CLIENT][config_entry.entry_id] = brother

    config_entry.add_update_listener(update_listener)
    hass.async_create_task(
        hass.config_entries.async_forward_entry_setup(config_entry, "sensor")
    )
    return True


async def async_unload_entry(hass, config_entry):
    """Unload a config entry."""
    await hass.config_entries.async_forward_entry_unload(config_entry, "sensor")
    return True


async def update_listener(hass, entry):
    """Update listener."""
    await hass.config_entries.async_forward_entry_unload(entry, "sensor")
    hass.async_add_job(hass.config_entries.async_forward_entry_setup(entry, "sensor"))


class BrotherData:
    """Define an object to hold sensor data."""

    def __init__(self, session, host, **kwargs):
        """Initialize."""
        self.host = host
        self.model = None
        self.serial = None
        self.data = {}

        self.async_update = Throttle(kwargs[CONF_SCAN_INTERVAL])(self._async_update)

    async def _async_update(self):
        """Update Brother data."""
        url = URL_INFO.format(self.host)
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(url) as resp:
                    data = await resp.text()
        except aiohttp.ClientError as error:
            _LOGGER.error("Could not fetch data from %s, error: %s", url, error)
            return

            values = measurements.current["values"]
            standards = measurements.current["standards"]
            index = measurements.current["indexes"][0]

            if index["description"] == NO_AIRLY_SENSORS[self.language]:
                _LOGGER.error("Can't retrieve data: no Airly sensors in this area")
                return
            for value in values:
                self.data[value["name"]] = value["value"]
            for standard in standards:
                self.data[f"{standard['pollutant']}_LIMIT"] = standard["limit"]
                self.data[f"{standard['pollutant']}_PERCENT"] = standard["percent"]
            self.data[ATTR_CAQI] = index["value"]
            self.data[ATTR_CAQI_LEVEL] = index["level"].lower().replace("_", " ")
            self.data[ATTR_CAQI_DESCRIPTION] = index["description"]
            self.data[ATTR_CAQI_ADVICE] = index["advice"]
            _LOGGER.debug("Data retrieved from Airly")
        except TimeoutError:
            _LOGGER.error("Asyncio Timeout Error")
        except (ValueError, AirlyError, ClientConnectorError) as error:
            _LOGGER.error(error)
            self.data = {}