# Contribution à Afriova AI

Merci de votre intérêt pour contribuer à Afriova AI ! Ce document décrit le processus pour proposer des améliorations, signaler des bugs et contribuer au code.

## 📋 Comment contribuer

### 1. Signaler un bug ou proposer une fonctionnalité
- Utilisez la section [Issues](https://github.com/your-org/afriova-ai/issues) du dépôt
- Pour les bugs : incluez les étapes pour reproduire, le comportement attendu vs observé
- Pour les fonctionnalités : décrivez le problème que cela résout et les bénéfices pour les utilisateurs africains

### 2. Proposer des changements (Pull Requests)
1. Forkez le dépôt
2. Créez une branche depuis `main` : `git checkout -b feature/nom-de-votre-fonctionnalité`
3. Faites vos changements
4. Assurez-vous que les tests passent : `pytest`
5. Committez vos changements avec un message clair
6. Poussez votre branche : `git push origin feature/nom-de-votre-fonctionnalité`
7. Ouvrez une Pull Request vers la branche `main`

### 3. Style de code
- Nous suivons [PEP 8](https://pep8.org/) pour Python
- Utilisez [Ruff](https://docs.astral.sh/ruff/) pour le linting : `ruff check .`
- Utilisez [Black](https://black.readthedocs.io/) pour le formatage : `black .`
- Les docstrings doivent suivre le style [NumPy](https://numpydoc.readthedocs.io/en/latest/format.html) ou [Google](https://sphinxcontrib-napoleon.readthedocs.io/en/latest/example_google.html)

### 4. Tests
- Écrivez des tests pour vos nouvelles fonctionnalités
- Les tests unitaires vont dans le dossier `tests/` ou à côté du fichier testé
- Utilisez `pytest` avec `pytest-asyncio` pour les tests asynchrones
- Assurez-vous que votre PR ne diminue pas la couverture de tests

### 5. Documentation
- Mettez à jour la documentation si nécessaire
- Les changements majeurs nécessitent une mise à jour du README
- Les changements d'API doivent être documentés dans les docs/

## 🧭 Directives spécifiques

### Pour les nouveaux agents
1. Héritez de `agents/base.BaseAgent`
2. Implémentez les méthodes abstraites `process()` et `validate_input()`
3. Ajoutez des capacités spécifiques via `get_capabilities()`
4. Suivez le nommage conventionnel : `agents/{nom_agents}.py`
5. Ajoutez des tests dans `agents/test_{nom_agents}.py`
6. Documentez les spécificités africaines de votre agent

### Pour les intégrations
1. Placez-les dans le dossier `integrations/`
2. Suivez le modèle de l'abstraction lorsqu'applicable (ex: `MobileMoneyProvider`)
3. Gérez proprement les erreurs et les timeouts
4. Documentez les prérequis (clés API, configuration)
5. Ajoutez des exemples d'utilisation

### Pour la localisation et l'internationalisation
- Utilisez les codes de langue ISO 639-1 (fr, en, ar, etc.)
- Prenez en compte les variantes régionales quand nécessaire
- Les devises doivent utiliser les codes ISO 4217 (XOF, NGN, etc.)
- Prévoyez le support du texte de droite à gauche pour l'arabe et d'autres langues

## 🌍 Considérations spécifiques au contexte africain

### Langues et localisation
- Support prioritaire : Français, Anglais, Arabe, Swahili, Wolof, Hausa, Yoruba
- Prévoyez l'extension facile à de nouvelles langues africaines
- Les formats de date, heure, nombre doivent suivre les locales appropriées

### Infrastructures et connectivité
- Optimisez pour les connexions intermittentes et à faible bande passante
- Prévoyez des fallbacks (SMS, USSD) quand l'internet n'est pas disponible
- Soyez conscient des coûts de données élevés dans certains régions

### Paiements et économie locale
- Support des systèmes de paiement africains (Mobile Money, banques locales, etc.)
- Prévoyez la multi-devise et la conversion facile
- Respectez les réglementations financières locales par pays

### Réglementation et conformité
- Recherchez les réglementations spécifiques par pays (protection des données, financière, télécoms)
- Prévoyez la localisation des données quand requis par la loi
- Documentez clairement les limites de conformité

## 🏆 Reconnaissance
Les contributeurs sont remerciés dans le fichier `CONTRIBUTORS.md` et dans les notes de version selon leur niveau de contribution.

## 📞 Besoin d'aide ?
- Rejoignez nos discussions sur GitHub Discussions
- Contactez l'équipe à : contributors@afriova.ai
- Consultez le wiki pour des guides détaillés

Merci de contribuer à rendre l'IA accessible et utile pour l'Afrique ! 💙
