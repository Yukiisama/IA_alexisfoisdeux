Readme :  Equipe Alexisfoisdeux
Alexis Perignon , Alexis Flazinska

Nous avons fait le choix d'utiliser un algorithme negamax pour trouver le coup que veut jouer notre IA:
Associé avec l'iterative deepning, on lance plusieurs fois l'algorithme en incrémentant la profondeur jusqu'à ce que nous ayons plus de temps
Chaque coup reçoit un temps de 5.8s pour aller le plus loin possible.
Quand le temps est écoulé , qu'une situation de game over a été rencontrée, ou que nous avons atteint la profondeur donnée, 
nous évaluons à l'aide de nos heuristiques et leurs coefficients respectifs pour évaluer la situation.
Nous avons à ce jour codé différentes heuristiques (Toutes présentes dans le fichier Reversi2):
-Une pour la mobilité, c'est à dire jouer le plus de coups possibles ( et minimiser ceux adverses)
-Une pour éviter les cases dangereuses autour des corners,
-Une pour evaluer les différentes cases sur le board en leur accordant plus ou moins d'importances: les corners sont très importants,
-Une pour evaluer la stabilité, c'est à dire le nombres de pieces ne pouvant plus être volée.

Nous disposons de killer move sur les corners : c'est à dire que si un corner est disponible nous prenons ce mouvement, sans laisser d'algorithme de
recherche.

Nous avions également codée d'autres heuristiques pour entourer l'adversaire, compter les pieces, 
construire des vecteurs allié/ennemi/.../allie ou ennemi, mais à ce jour elles ne sont plus utilisées:
Il devenait de plus en plus dur d'ajuster les coefficients entre eux, cela aurait du être le travail d'un deep learning mais nous n'avions pas le temps.

Nous avons essayé plusieurs tentatives d'autres algorithmes qui sont à ce jour pas utilisées: 
-AlphaBeta classique,
-AlphaBeta avec parallelisation sur la première couche de noeuds ( un thread = un move de la premier couche)
-NegaScout avec tri des noeuds sur la première couche.
-Table de hachage avec zobrist key: on xor la key zobrist avec la case pour obtenir la nouvelle valeur ( problème de collision nous n'avons pas réussi à conclure)

Les anciennes tentatives sont disponibles à l'adresse suivante  : https://github.com/Yukiisama/IA_alexisfoisdeux
Parallel.py est l'ancienne implémentation avec thread sur la première couche + hashing avec zobrist
