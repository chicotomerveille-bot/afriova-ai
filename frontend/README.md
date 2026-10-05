# Afriova AI Dashboard

Tableau de bord web Next.js pour gérer les agents IA et connecteurs.

## Stack technique
- Next.js 14 + React 18
- TypeScript
- TailwindCSS
- shadcn/ui
- TanStack Query
- Zustand
- Framer Motion

## Features
- Dashboard des agents avec statut en temps réel
- Gestion des connecteurs (connexion, déconnexion, tests)
- Console d'exécution d'actions
- Analytics et métriques
- Gestion multi-tenant
- Interface mobile-first pour l'Afrique

## Démarrage
```bash
npm install
npm run dev
```

## Structure
- app/ - Pages Next.js App Router
- components/ - Composants UI réutilisables
- hooks/ - Hooks React personnalisés
- lib/ - Utilitaires et clients API
- services/ - Services backend
- stores/ - État global Zustand
