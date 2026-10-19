"""Comparer l'encombrement selon l'angle ; lancer depuis la racine du projet."""
import math
from pathlib import Path
import sys
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from circuit_merge.config import COMPONENTS
from circuit_merge.geometry import geometry_for

if __name__ == "__main__":
    for level, spec in enumerate(COMPONENTS):
        print(spec.name)
        geometry = geometry_for(level)
        for degrees in (0, 45, 90):
            left, top, right, bottom = geometry.bounds(math.radians(degrees))
            print(f"  {degrees:2d} degrés : {right-left:.1f} × {bottom-top:.1f} pixels")
