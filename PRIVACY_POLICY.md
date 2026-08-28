# Politique de confidentialité — Cinebot

*Dernière mise à jour : 28 aout 2026*

Cette politique de confidentialité explique quelles données sont
collectées par cinebot (ci-après « le Bot »), pourquoi, et comment
elles sont utilisées.

## 1. Données collectées

Lorsque vous utilisez les commandes du Bot, les données suivantes sont
collectées et stockées :

| Donnée | Origine | Pourquoi |
|---|---|---|
| Votre identifiant Discord (ID) | Commande `!film` | Identifier qui a proposé le film, pour permettre `!removefilm` |
| Votre pseudo Discord | Commande `!film` | Affiché publiquement dans le message d'ajout et lors du tirage |
| Le titre du film que vous soumettez | Commande `!film` | Constituer la liste de suggestions |
| Titre, année et affiche du film | Réponse de l'API OMDb (service tiers) | Afficher les informations du film |
| Date et heure de l'ajout | Commande `!film` | Traçabilité interne |

Le Bot **ne collecte pas** : votre adresse email, votre adresse IP, votre
historique de messages en dehors des commandes `!film` / `!removefilm`, ni
aucune autre donnée personnelle.

## 2. Comment les données sont stockées

Les données sont stockées dans un fichier local (`films.json`) sur le
serveur hébergeant le Bot. Elles ne sont **pas** revendues, partagées avec
des annonceurs, ni utilisées à des fins publicitaires.

## 3. Partage avec des tiers

Pour rechercher les films, le Bot envoie le **titre du film** (uniquement,
sans donnée personnelle) à l'API publique **OMDb**
(http://www.omdbapi.com/). Consulte leur politique de confidentialité pour
en savoir plus sur le traitement de ces requêtes.

Aucune autre donnée n'est transmise à un service tiers, à l'exception des
échanges strictement nécessaires avec l'infrastructure de Discord pour le
fonctionnement du Bot (conformément à la [politique de confidentialité de
Discord](https://discord.com/privacy)).

## 4. Durée de conservation

- Les informations d'un film (titre, auteur de la suggestion) sont
  conservées **jusqu'au tirage au sort hebdomadaire suivant**, moment
  auquel la liste est intégralement réinitialisée.
- Un film retiré via `!removefilm` est supprimé immédiatement des données
  stockées.

## 5. Vos droits

Vous pouvez à tout moment :

- Retirer une suggestion que vous avez ajoutée, via `!removefilm`.
- Demander la suppression manuelle de vos données stockées en contactant
  l'administrateur du Bot (coordonnées ci-dessous).

Si le Bot est utilisé dans l'Union européenne, vous disposez des droits
prévus par le RGPD (accès, rectification, effacement, opposition) sur les
données décrites ci-dessus.

## 6. Sécurité

Des mesures raisonnables sont prises pour protéger les données stockées,
mais aucun système n'est infaillible. Le Bot étant un projet personnel/
associatif, aucune garantie de sécurité absolue n'est fournie.

## 7. Contact

Pour toute question ou demande relative à vos données :
**gonin.flavien1@gmail.com**.

---

*Ce document est un modèle générique adapté aux fonctionnalités réelles du
Bot. Il ne constitue pas un avis juridique. Adapte-le si tu ajoutes de
nouvelles fonctionnalités collectant d'autres données.*
