# 🌦️ Pleinchamp Météo pour Home Assistant

Une intégration personnalisée pour **Home Assistant** qui récupère les données météo ultra-locales et agricoles directement depuis l'API de production de **Pleinchamp**.

Contrairement aux anciennes méthodes basées sur le web scraping, cette version utilise l'API native (JSON) pour une fiabilité maximale et des données précises.

## ✨ Caractéristiques

* **Zéro Scraping** : Utilise l'API de production officielle (`api.prod.pleinchamp.com`).
* **Localisation précise** : Configuration simplifiée par **Latitude** et **Longitude**.
* **Capteurs Agricoles** : Inclut la température au sol (idéal pour la surveillance du gel).
* **Prévisions Avancées** :
    * **Pluie sur 24h** : Calcul du cumul total prévu sur les prochaines 24 heures.
    * **Risque de pluie** : Probabilité maximale de précipitations sur la journée.
* **Identifiants uniques** : Toutes les entités sont gérables via l'interface utilisateur de Home Assistant (nom, icône, zone).

## 📊 Capteurs disponibles

| Capteur | Description | Unité |
| :--- | :--- | :--- |
| **Température** | Température actuelle de l'air | °C |
| **Condition** | État du ciel (Ensoleillé, Pluie, etc.) | - |
| **Précipitations** | Quantité de pluie immédiate (tranche actuelle) | mm |
| **Pluie 24h** | Cumul des précipitations prévu sur les 24 prochaines heures | mm |
| **Risque de pluie** | Probabilité maximale de pluie sur la journée | % |
| **Humidité** | Taux d'humidité relative | % |
| **Vent Vitesse** | Vitesse du vent actuelle | km/h |
| **Vent Direction** | Direction cardinale (ex: NE, SO, NO) | - |
| **Temp au sol** | Température proche du sol (mesure spécifique) | °C |

## 🚀 Installation

### Méthode Manuelle
1. Téléchargez les fichiers de l'intégration.
2. Copiez le dossier `pleinchamp` dans votre répertoire `custom_components/` de Home Assistant.
   * Structure attendue : `/config/custom_components/pleinchamp/`
3. Redémarrez Home Assistant pour que l'intégration soit détectée.

## ⚙️ Configuration

1. Allez dans **Paramètres** > **Appareils et services**.
2. Cliquez sur **Ajouter une intégration** en bas à droite.
3. Recherchez **Pleinchamp Météo API**.
4. Saisissez les coordonnées GPS souhaitées :
   * **Latitude** (ex: `48.004732`)
   * **Longitude** (ex: `2.675917`)
5. Validez. Toutes vos entités seront automatiquement créées et regroupées sous l'appareil **Météo Pleinchamp**.

## 🛠️ Détails Techniques (Calculs)

* **Pluie 24h** : Somme des 8 prochaines tranches de 3 heures fournies par l'API.
* **Risque de pluie** : Valeur maximale (`max`) des probabilités de précipitations sur les 8 prochaines tranches.
* **Mise à jour** : Les données sont rafraîchies toutes les 15 minutes (configurable dans `const.py`).

---

**Note** : Cette intégration est un projet communautaire non-affilié officiellement à Pleinchamp.
