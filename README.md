# Pleinchamp Météo pour Home Assistant 🌦️

Cette intégration personnalisée permet de récupérer les données météo détaillées du site [Pleinchamp](https://www.pleinchamp.com/), particulièrement utile pour le suivi agricole en France.

## Caractéristiques
L'intégration récupère les informations suivantes pour votre commune :
- 🌡️ Température actuelle
- 🌥️ État du ciel (Condition)
- 🌧️ Précipitations (en mm)
- 📉 Températures Minimales et Maximales
- 💨 Vitesse et Direction du vent
- 💧 Taux d'humidité

## Installation

### Via HACS (Recommandé)
1. Ouvrez **HACS** dans votre instance Home Assistant.
2. Cliquez sur les trois points en haut à droite et choisissez **Dépôts personnalisés**.
3. Ajoutez l'URL de ce dépôt GitHub et sélectionnez la catégorie **Intégration**.
4. Recherchez "Pleinchamp Météo" et cliquez sur **Télécharger**.
5. Redémarrez Home Assistant.

### Installation Manuelle
1. Téléchargez le dossier `pleinchamp` situé dans `custom_components`.
2. Copiez-le dans le dossier `config/custom_components/` de votre instance Home Assistant.
3. Redémarrez Home Assistant.

## Configuration
1. Allez dans **Paramètres** > **Appareils et services**.
2. Cliquez sur **Ajouter une intégration**.
3. Cherchez **Pleinchamp Météo**.
4. Entrez l'URL Pleinchamp de votre ville (ex: `https://www.pleinchamp.com/meteo/45700-pannes`).

## Mise à jour des données
Par défaut, l'intégration vérifie les données toutes les 30 minutes pour respecter les serveurs de Pleinchamp.

---
*Note : Cette intégration utilise le scraping pour récupérer les données. Elle n'est pas affiliée officiellement à Pleinchamp.*
