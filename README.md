# 🌦️ Pleinchamp Météo pour Home Assistant (Version API)

Une intégration personnalisée pour **Home Assistant** qui récupère les données météo ultra-locales et agricoles directement depuis l'API de production de **Pleinchamp**.

[![hacs_badge](https://img.shields.io/badge/HACS-Custom-orange.svg)](https://hacs.xyz/)
[![Maintenance](https://img.shields.io/badge/Maintained%3F-yes-green.svg)](https://github.com/votre_pseudo/votre_repo/graphs/commit-activity)

## ✨ Caractéristiques

* **Zéro Scraping** : Utilise l'API JSON officielle (`api.prod.pleinchamp.com`) pour une stabilité totale.
* **Localisation précise** : Configuration simplifiée par **Latitude** et **Longitude**.
* **Capteurs Agricoles** : Inclut la température au sol (mesure à 2m) pour la surveillance du gel.
* **Analyses Avancées** :
    * **Pluie sur 24h** : Calcul du cumul total prévu.
    * **Risque de pluie** : Probabilité maximale de précipitations sur la journée.
* **Prévisions Chronologiques** : Capteurs de prévisions dédiés stockant les séries de données (24h) dans leurs attributs.

## 📊 Capteurs disponibles

| Capteur | Unité | Description |
| :--- | :--- | :--- |
| **Température** | °C | Air à l'instant T |
| **Condition** | - | État du ciel actuel |
| **Pluie 24h** | mm | Cumul total prévu sur les prochaines 24h |
| **Risque de pluie** | % | Probabilité maximale sur la journée |
| **Temp au sol** | °C | Température proche du sol |
| **Vent** | km/h | Vitesse et direction (NO, SO, etc.) |
| **Prévisions Temp** | °C | Série de données pour graphique (24h) |
| **Prévisions Pluie** | mm | Série de données pour graphique (24h) |
| **Previsions Rafales** | km/h | maximale sur la journée |
| **Rafales Vent** | km/h | Rafale de vent à l'instant T |

## 🚀 Installation

### Option 1 : Installation via HACS (Recommandé)
1. Allez dans **HACS** > **Intégrations**.
2. Cliquez sur les trois points en haut à droite > **Dépôts personnalisés**.
3. Ajoutez l'URL de ce dépôt et sélectionnez la catégorie **Intégration**.
4. Cliquez sur **Installer**.

### Option 2 : Installation Manuelle
1. Copiez le dossier `pleinchamp` dans votre répertoire `/config/custom_components/`.
2. Redémarrez Home Assistant.

## ⚙️ Configuration
1. Allez dans **Paramètres** > **Appareils et services**.
2. Cliquez sur **Ajouter une intégration** et recherchez **Pleinchamp Météo API**.
3. Saisissez vos coordonnées GPS (ex: Pannes : `48.004732` / `2.675917`).

---

## 📈 Visualisation (ApexCharts Card)

Pour afficher les prévisions futures (et non l'historique de Home Assistant), utilisez l'extension **ApexCharts-Card** avec les codes suivants :

### 🌡️ Graphique de Température (24h)
```yaml
type: custom:apexcharts-card
graph_span: 24h
span:
  start: hour
header:
  show: true
  title: Prévisions Température (24h)
  show_states: true
series:
  - entity: sensor.meteo_pleinchamp_pleinchamp_previsions_temperature
    data_generator: |
      return entity.attributes.timestamps.map((t, index) => {
        return [new Date(t).getTime(), entity.attributes.data[index]];
      });
    stroke_width: 3
    curve: smooth
    color: "#e67e22"
```


### 🌧️ Histogramme de Pluie (24h)
```yaml
type: custom:apexcharts-card
graph_span: 24h
span:
  start: hour
header:
  show: true
  title: Précipitations (3h)
  show_states: true
series:
  - entity: sensor.meteo_pleinchamp_pleinchamp_previsions_pluie
    type: column
    data_generator: |
      return entity.attributes.timestamps.map((t, index) => {
        return [new Date(t).getTime(), entity.attributes.data[index]];
      });
    color: "#3498db"
```

## 📱 Interface Recommandée (Dashboard)

Pour obtenir un affichage complet, vous pouvez combiner les cartes natives et **ApexCharts-card**.

```yaml
type: vertical-stack
cards:
  - type: custom:button-card
    name: Météo Pleinchamp
    label: >
      [[[ return states['sensor.meteo_pleinchamp_pleinchamp_condition'].state +
      ' • ' + states['sensor.meteo_pleinchamp_pleinchamp_temperature'].state +
      '°C' ]]]
    show_label: true
    styles:
      card:
        - background: "linear-gradient(145deg, #2c3e50, #000000)"
        - color: white
        - padding: 10px
      name:
        - font-weight: bold
        - font-size: 18px
  - type: grid
    columns: 3
    square: false
    cards:
      - type: entity
        entity: sensor.meteo_pleinchamp_pleinchamp_temp_au_sol
        name: Temp Sol
      - type: entity
        entity: sensor.meteo_pleinchamp_pleinchamp_pluie_24h
        name: Pluie 24h
      - type: entity
        entity: sensor.meteo_pleinchamp_pleinchamp_risque_de_pluie
        name: Risque
  - type: custom:apexcharts-card
    graph_span: 24h
    span:
      start: hour
    header:
      show: true
      title: Température & Rafales (24h)
    all_series_config:
      stroke_width: 2
    series:
      - entity: sensor.meteo_pleinchamp_pleinchamp_previsions_temperature
        name: Temp
        type: area
        color: "#e67e22"
        opacity: 0.3
        data_generator: |
          return entity.attributes.timestamps.map((t, index) => {
            return [new Date(t).getTime(), entity.attributes.data[index]];
          });
      - entity: sensor.meteo_pleinchamp_pleinchamp_previsions_rafales
        name: Rafales
        type: line
        color: "#c0392b"
        data_generator: |
          return entity.attributes.timestamps.map((t, index) => {
            return [new Date(t).getTime(), entity.attributes.data[index]];
          });
  - type: custom:apexcharts-card
    graph_span: 24h
    span:
      start: hour
    header:
      show: true
      title: Précipitations prévues
    series:
      - entity: sensor.meteo_pleinchamp_pleinchamp_previsions_pluie
        type: column
        color: "#3498db"
        data_generator: |
          return entity.attributes.timestamps.map((t, index) => {
            return [new Date(t).getTime(), entity.attributes.data[index]];
          });
  - type: glance
    entities:
      - entity: sensor.meteo_pleinchamp_pleinchamp_vent_vitesse
        name: Vent
      - entity: sensor.meteo_pleinchamp_pleinchamp_vent_direction
        name: Dir.
      - entity: sensor.meteo_pleinchamp_pleinchamp_humidite
        name: Humidité

```
<img width="590" height="1392" alt="image" src="https://github.com/user-attachments/assets/bc7b95f1-0ebe-49a5-89e6-c148acaebdbf" />

Note : Cette intégration est un projet communautaire non-affilié officiellement à Pleinchamp.
