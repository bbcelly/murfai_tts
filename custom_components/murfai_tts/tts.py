"""
Setting up TTS entity.
"""
import logging
from homeassistant.components.tts import TextToSpeechEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.entity import generate_entity_id
from .const import CONF_MODEL, CONF_STYLE, CONF_URL, DOMAIN, UNIQUE_ID
from .murfaitts_engine import MurfAITTSEngine
from homeassistant.exceptions import MaxLengthExceeded

_LOGGER = logging.getLogger(__name__)

async def async_setup_entry(
    hass: HomeAssistant,
    config_entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up MurfAI Text-to-speech platform via config entry."""

    engine = MurfAITTSEngine(
        config_entry.data[CONF_STYLE],
        config_entry.data[CONF_MODEL],
        config_entry.data[CONF_URL]
    )
    async_add_entities([MurfAITTSEntity(hass, config_entry, engine)])


class MurfAITTSEntity(TextToSpeechEntity):
    """The MurfAI TTS entity."""
    _attr_has_entity_name = True
    _attr_should_poll = False

    def __init__(self, hass, config, engine):
        """Initialize TTS entity."""
        self.hass = hass
        self._engine = engine
        self._config = config

        self._attr_unique_id = config.data.get(UNIQUE_ID)
        if self._attr_unique_id is None:
            # generate a legacy unique_id
            self._attr_unique_id = f"{config.data[CONF_STYLE]}_{config.data[CONF_MODEL]}"
        self.entity_id = generate_entity_id("tts.murfai_tts_{}", config.data[CONF_STYLE], hass=hass)

    @property
    def default_language(self):
        """Return the default language."""
        return "en"

    @property
    def supported_languages(self):
        """Return the list of supported languages."""
        return self._engine.get_supported_langs()

    @property
    def device_info(self):
        return {
            "identifiers": {(DOMAIN, self._attr_unique_id)},
            "model": f"{self._config.data[CONF_STYLE]}",
            "manufacturer": "MurfAI"
        }

    @property
    def name(self):
        """Return name of entity"""
        return f"{self._config.data[CONF_STYLE]}"

    def get_tts_audio(self, message, language, options=None):
        """Convert a given text to speech and return it as bytes."""
        try:
            if len(message) > 4096:
                raise MaxLengthExceeded

            speech = self._engine.get_tts(message)

            # The response should contain the audio file content
            return "mp3", speech
        except MaxLengthExceeded:
            _LOGGER.error("Maximum length of the message exceeded")
        except Exception as e:
            _LOGGER.error("Unknown Error: %s", e)

        return None, None
