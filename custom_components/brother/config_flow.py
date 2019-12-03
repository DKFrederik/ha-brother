"""Adds config flow for Brother Printer."""
import ipaddress
import logging
import re

import voluptuous as vol
from brother import Brother, SnmpError, UnsupportedModel
from homeassistant import config_entries, exceptions
from homeassistant.const import CONF_HOST

from .const import DOMAIN  # pylint:disable=unused-import

_LOGGER = logging.getLogger(__name__)

DATA_SCHEMA = vol.Schema({vol.Required(CONF_HOST, default=""): str})


def host_valid(host):
    try:
        if ipaddress.ip_address(host).version == (4 or 6):
            return True
    except ValueError:
        disallowed = re.compile(r"[^a-zA-Z\d\-]")
        if all(map(lambda x: len(x) and not disallowed.search(x), host.split("."))):
            return True
        return False


class BrotherConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle a config flow for Brother Printer."""

    VERSION = 1
    CONNECTION_CLASS = config_entries.CONN_CLASS_LOCAL_POLL

    async def async_step_user(self, user_input=None):
        """Handle the initial step."""
        errors = {}

        if user_input is not None:
            try:
                if not host_valid(user_input[CONF_HOST]):
                    raise InvalidHost()
                brother = Brother(user_input[CONF_HOST])
                await brother.async_update()

                return self.async_create_entry(title=brother.model, data=user_input)
            except InvalidHost:
                errors["base"] = "wrong_address"
            except SnmpError:
                errors["base"] = "snmp_error"
            except UnsupportedModel:
                errors["base"] = "unsupported_model"
            except Exception:  # pylint: disable=broad-except
                _LOGGER.exception("Unexpected exception")
                errors["base"] = "unknown"

        return self.async_show_form(
            step_id="user", data_schema=DATA_SCHEMA, errors=errors
        )


class InvalidHost(exceptions.HomeAssistantError):
    """Error to indicate that hostname/IP address is invalid."""
