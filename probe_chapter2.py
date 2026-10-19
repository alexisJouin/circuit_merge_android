import random
from circuit_merge.campaign import MissionEngine

def solve(i, strategy=1):
    e=MissionEngine(i); rng=random.Random(1)
    while e.remaining and not e.outcome:
        same=[p for p in e.pieces.values() if p.level==e.current_level]
        if strategy and same:
            x=min(same,key=lambda p:p.body.position.y).body.position.x
        elif strategy: x=rng.choice([450,500,556,610,660])
        else: x=556
        e.drop(x)
        for _ in range(720): e.step()
        e.events.clear()
    for _ in range(2400): e.step()
    return e

if __name__=='__main__':
    for i in range(10,20):
        e=solve(i)
        print(i+1,e.outcome,e.drops,e.score,e.progress,dict(e.created),flush=True)
