"""Expérience NSI : comparer la chute calculée à y = g × t² / 2.

Lancer depuis la racine : ``python experiences/chute_libre.py``.
Un corps tombe sans obstacles ni frottement. Le pas fixe explique l'écart
entre le résultat numérique et la formule continue. Pymunk est la seule
dépendance utilisée ici ; il n'y a pas de fenêtre graphique.
"""

import pymunk


def experience(dt: float, gravity: float = 1080.0) -> tuple[float, float]:
    """Renvoie la position et la vitesse après une seconde de simulation."""
    space = pymunk.Space()
    space.gravity = (0, gravity)
    body = pymunk.Body(1, 1)
    body.position = (0, 0)
    space.add(body)
    steps = round(1 / dt)
    for _ in range(steps):
        space.step(1 / steps)
    return body.position.y, body.velocity.y


if __name__ == "__main__":
    print("Chute libre pendant 1 seconde (y orienté vers le bas)\n")
    print("Hz       y calculé       y théorique      écart       vitesse")
    for hz in (30, 60, 120, 240):
        y, velocity = experience(1 / hz)
        theory = 1080 / 2
        print(f"{hz:3d}     {y:10.3f} px    {theory:10.3f} px   {abs(y-theory):7.3f} px    {velocity:.1f} px/s")
    print("\nQuestion : que devient l'écart lorsque le pas de temps est divisé par 2 ?")
