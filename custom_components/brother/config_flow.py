"""Adds config flow for Brother."""
import logging

import homeassistant.helpers.config_validation as cv
import voluptuous as vol
from async_timeout import timeout
from homeassistant import config_entries
from homeassistant.const import CONF_HOST, CONF_NAME, CONF_SCAN_INTERVAL
from homeassistant.core import callback
from homeassistant.helpers.aiohttp_client import async_get_clientsession

from .const import (DEFAULT_NAME, DEFAULT_SCAN_INTERVAL, DOMAIN)

_LOGGER = logging.getLogger(__name__)


@callback
def configured_instances(hass):
    """Return a set of configured Brother instances."""
    return set(
        entry.data[CONF_NAME] for entry in hass.config_entries.async_entries(DOMAIN)
    )


class BrotherFlowHandler(config_entries.ConfigFlow, domain=DOMAIN):
    """Config flow for Brother."""

    VERSION = 1
    CONNECTION_CLASS = config_entries.CONN_CLASS_CLOUD_POLL

    def __init__(self):
        """Initialize."""
        self._errors = {}

    async def async_step_user(self, user_input=None):
        """Handle a flow initialized by the user."""
        self._errors = {}

        websession = async_get_clientsession(self.hass)

        if user_input is not None:
            if user_input[CONF_NAME] in configured_instances(self.hass):
                self._errors[CONF_NAME] = "name_exists"
            host_valid = await self._test_host(websession, user_input[CONF_HOST])
            if not host_valid:
                self._errors[CONF_HOST] = "invalid_host"

            if not self._errors:
                return self.async_create_entry(
                    title=user_input[CONF_NAME], data=user_input
                )

        return self._show_config_form(name=DEFAULT_NAME, host="")

    def _show_config_form(self, name=None, host=None):
        """Show the configuration form to edit data."""
        return self.async_show_form(
            step_id="user",
            data_schema=vol.Schema(
                {
                    vol.Required(CONF_HOST, default=""): str,
                    vol.Optional(CONF_NAME, default=name): str,
                }
            ),
            errors=self._errors,
        )

    @staticmethod
    @callback
    def async_get_options_flow(config_entry):
        """Brother options callback."""
        return BrotherOptionsFlowHandler(config_entry)

    async def _test_host(self, client, host):
        """Return true if host is valid."""
        return True


class BrotherOptionsFlowHandler(config_entries.OptionsFlow):
    """Config flow options for Brother."""

    def __init__(self, config_entry):
        """Initialize Brother options flow."""
        self.config_entry = config_entry

    async def async_step_init(self, user_input=None):
        """Manage the options."""
        return await self.async_step_user()

    async def async_step_user(self, user_input=None):
        """Handle a flow initialized by the user."""
        if user_input is not None:
            return self.async_create_entry(title="", data=user_input)

        return self.async_show_form(
            step_id="user",
            data_schema=vol.Schema(
                {
                    vol.Optional(
                        CONF_SCAN_INTERVAL,
                        default=self.config_entry.options.get(
                            CONF_SCAN_INTERVAL, DEFAULT_SCAN_INTERVAL
                        ),
                    ): int
                }
            ),
        )
