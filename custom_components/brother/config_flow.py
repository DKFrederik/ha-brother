"""Adds config flow for Brother Printer."""
import logging

import voluptuous as vol
from brother import Brother, SnmpError, UnsupportedModel
from homeassistant import config_entries
from homeassistant.const import CONF_HOST

from .const import DOMAIN  # pylint:disable=unused-import

_LOGGER = logging.getLogger(__name__)

DATA_SCHEMA = vol.Schema({vol.Required(CONF_HOST, default=""): str})


class BrotherConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle a config flow for Brother Printer."""

    VERSION = 1
    CONNECTION_CLASS = config_entries.CONN_CLASS_LOCAL_POLL

    async def async_step_user(self, user_input=None):
        """Handle the initial step."""
        errors = {}

        if user_input is not None:
            brother = Brother(user_input[CONF_HOST])

            try:
                await brother.update()

                return self.async_create_entry(title=brother.model, data=user_input)
            except SnmpError:
                errors["base"] = "wrong_address"
            except UnsupportedModel:
                errors["base"] = "unsupported_model"
            except Exception:  # pylint: disable=broad-except
                _LOGGER.exception("Unexpected exception")
                errors["base"] = "unknown"

        return self.async_show_form(
            step_id="user", data_schema=DATA_SCHEMA, errors=errors
        )
