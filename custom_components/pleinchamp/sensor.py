from homeassistant.components.sensor import SensorEntity
from .const import DOMAIN

async def async_setup_entry(hass, entry, async_add_entities):
    """Configuration des entités sensor à partir d'une entrée de configuration."""
    coordinator = hass.data[DOMAIN][entry.entry_id]

    # On passe entry.entry_id à chaque capteur pour le unique_id et le device_info
    entities = [
        PleinchampSensor(coordinator, "Condition", "condition", None, "mdi:weather-cloudy", entry.entry_id),
        PleinchampSensor(coordinator, "Température", "temp", "°C", "mdi:thermometer", entry.entry_id),
        PleinchampSensor(coordinator, "Précipitations", "precip", "mm", "mdi:weather-pour", entry.entry_id),
        PleinchampSensor(coordinator, "Température Min", "temp_min", "°C", "mdi:thermometer-chevron-down", entry.entry_id),
        PleinchampSensor(coordinator, "Température Max", "temp_max", "°C", "mdi:thermometer-chevron-up", entry.entry_id),
        PleinchampSensor(coordinator, "Vitesse du vent", "wind_speed", "km/h", "mdi:weather-windy", entry.entry_id),
        PleinchampSensor(coordinator, "Humidité", "humidity", "%", "mdi:water-percent", entry.entry_id),
        PleinchampSensor(coordinator, "Direction du vent", "wind_dir", None, "mdi:compass-outline", entry.entry_id),
    ]
    
    async_add_entities(entities)

class PleinchampSensor(SensorEntity):
    """Représentation d'un capteur Pleinchamp."""

    def __init__(self, coordinator, name, data_key, unit, icon, entry_id):
        """Initialisation du capteur."""
        self.coordinator = coordinator
        self._name = f"Pleinchamp {name}"
        self._data_key = data_key
        self._unit = unit
        self._icon = icon
        self._entry_id = entry_id

    @property
    def unique_id(self):
        """Identifiant unique pour que HA puisse gérer l'entité via l'UI."""
        # Cet ID permet de ne plus avoir le message d'erreur jaune
        return f"{self._entry_id}_{self._data_key}"

    @property
    def name(self):
        """Retourne le nom du capteur."""
        return self._name

    @property
    def native_value(self):
        """Retourne la valeur actuelle du capteur depuis le coordinator."""
        return self.coordinator.data.get(self._data_key)

    @property
    def native_unit_of_measurement(self):
        """Retourne l'unité de mesure."""
        return self._unit

    @property
    def icon(self):
        """Retourne l'icône mdi."""
        return self._icon

    @property
    def device_info(self):
        """Lie tous les capteurs à un seul 'appareil' Pleinchamp dans l'UI."""
        return {
            "identifiers": {("pleinchamp", self._entry_id)},
            "name": "Météo Pleinchamp",
            "manufacturer": "Pleinchamp",
            "entry_type": "service",
        }

    @property
    def should_poll(self):
        """Pas besoin de poll, le coordinator s'en charge."""
        return False

    async def async_added_to_hass(self):
        """S'abonne aux mises à jour du coordinator."""
        self.async_on_remove(
            self.coordinator.async_add_listener(self.async_write_ha_state)
        )
