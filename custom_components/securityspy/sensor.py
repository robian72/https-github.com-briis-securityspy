""" This component provides Sensors for SecuritySpy."""
from dataclasses import dataclass
import logging

from homeassistant.config_entries import ConfigEntry
from homeassistant.const import ENTITY_CATEGORY_DIAGNOSTIC
from homeassistant.components.sensor import (
    SensorEntity,
    SensorEntityDescription,
)
from homeassistant.core import HomeAssistant
from .entity import SecuritySpyEntity

from .const import (
    DOMAIN,
    RECORDING_TYPE_ACTION,
    RECORDING_TYPE_CONTINUOUS,
    RECORDING_TYPE_MOTION,
)
from .models import SecSpyRequiredKeysMixin


@dataclass
class SecuritySpyEntityDescription(SecSpyRequiredKeysMixin, SensorEntityDescription):
    """Describes SecuritySpy Sensor entity."""


SENSOR_ENTITIES: tuple[SecuritySpyEntityDescription, ...] = (
    SecuritySpyEntityDescription(
        key="motion_recording",
        name="Motion Recording",
        icon="mdi:video-outline",
        device_type=RECORDING_TYPE_MOTION,
    ),
    SecuritySpyEntityDescription(
        key="continuous_recording",
        name="Continuous Recording",
        icon="mdi:video-outline",
        device_type=RECORDING_TYPE_CONTINUOUS,
    ),
    SecuritySpyEntityDescription(
        key="actions",
        name="Actions Enabled",
        icon="mdi:script-text-play",
        device_type=RECORDING_TYPE_ACTION,
    ),
)
_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(
    hass: HomeAssistant, entry: ConfigEntry, async_add_entities
) -> None:
    """A SecsuritySpy Sensor."""
    entry_data = hass.data[DOMAIN][entry.entry_id]
    secspy_object = entry_data["nvr"]
    secspy_data = entry_data["secspy_data"]
    server_info = entry_data["server_info"]
    if not secspy_data.data:
        return

    sensors = []
    for description in SENSOR_ENTITIES:
        for device_id in secspy_data.data:
            device_data = secspy_data.data[device_id]
            sensors.append(
                SecuritySpySensor(
                    secspy_object,
                    secspy_data,
                    server_info,
                    device_id,
                    description,
                )
            )
            _LOGGER.debug(
                "Adding sensor entity %s for Camera %s",
                description.name,
                device_data["name"],
            )

    async_add_entities(sensors)


class SecuritySpySensor(SecuritySpyEntity, SensorEntity):
    """A SecuritySpy Sensor."""

    def __init__(
        self,
        secspy_object,
        secspy_data,
        server_info,
        device_id,
        description: SecuritySpyEntityDescription,
    ):
        """Initialize an Unifi Protect sensor."""
        super().__init__(
            secspy_object, secspy_data, server_info, device_id, description.key
        )
        self._description = description
        self._attr_name = f"{self._device_data['name']} {self._description.name}"
        self._attr_icon = self._description.icon
        self._attr_entity_category = ENTITY_CATEGORY_DIAGNOSTIC

    @property
    def state(self):
        """Return the state of the sensor."""
        if self._description.device_type == RECORDING_TYPE_ACTION:
            return self._device_data["recording_mode_a"]
        if self._description.device_type == RECORDING_TYPE_CONTINUOUS:
            return self._device_data["recording_mode_c"]
        if self._description.device_type == RECORDING_TYPE_MOTION:
            return self._device_data["recording_mode_m"]
        return None
