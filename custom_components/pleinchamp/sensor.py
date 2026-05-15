from homeassistant.components.sensor import SensorEntity
from .const import DOMAIN

async def async_setup_entry(hass, entry, async_add_entities):
    coordinator = hass.data[DOMAIN][entry.entry_id]

    entities = [
        PleinchampSensor(coordinator, "Condition", "condition", None, "mdi:weather-cloudy"),
        PleinchampSensor(coordinator, "Température", "temp", "°C", "mdi:thermometer"),
        PleinchampSensor(coordinator, "Précipitations", "precip", "mm", "mdi:weather-pour"),
        PleinchampSensor(coordinator, "Température Min", "temp_min", "°C", "mdi:thermometer-chevron-down"),
        PleinchampSensor(coordinator, "Température Max", "temp_max", "°C", "mdi:thermometer-chevron-up"),
        PleinchampSensor(coordinator, "Vitesse du vent", "wind_speed", "km/h", "mdi:weather-windy"),
        PleinchampSensor(coordinator, "Humidité", "humidity", "%", "mdi:water-percent"),
        PleinchampSensor(coordinator, "Direction du vent", "wind_dir", None, "mdi:compass-outline"),
    ]
    async_add_entities(entities)

class PleinchampSensor(SensorEntity):
    def __init__(self, coordinator, name, data_key, unit, icon, entry_id):
        self.coordinator = coordinator
        self._name = f"Pleinchamp {name}"
        self._data_key = data_key
        self._unit = unit
        self._icon = icon
        # On stocke l'ID de l'entrée pour créer un ID unique
        self._entry_id = entry_id

    @property
    def unique_id(self):
        """Identifiant unique pour que HA puisse gérer l'entité via l'UI."""
        return f"{self._entry_id}_{self._data_key}"

    @property
    def name(self):
        return self._name

    @property
    def native_value(self):
        return self.coordinator.data.get(self._data_key)

    @property
    def native_unit_of_measurement(self):
        return self._unit

    @property
    def icon(self):
        return self._icon
    
    @property
    def device_info(self):
        """Optionnel : lie tous les capteurs à un seul 'appareil' Pleinchamp."""
        return {
            "identifiers": {("pleinchamp", self._entry_id)},
            "name": "Météo Pleinchamp",
            "manufacturer": "Pleinchamp",
        }

    @property
    def should_poll(self):
        return False

    async def async_added_to_hass(self):
        self.async_on_remove(self.coordinator.async_add_listener(self.async_write_ha_state))
