"""Montage PC pédagogique : règles indépendantes du dessin et de la campagne.

Une configuration compatible est choisie à l'avance. Les zones et câbles
sont schématiques : ce mode présente les rôles et dépendances, pas un guide
de manipulation électrique ni un simulateur de compatibilité commerciale.
"""
from dataclasses import dataclass

@dataclass(frozen=True)
class Part:
    title: str
    short: str
    role: str
    destination: str
    needs: tuple
    question: str

PARTS={
 'case':Part('Boîtier','Boîtier',
     'Protège les composants, offre les points de fixation et organise le flux d’air. Les entretoises isolent la carte mère du métal.',
     'Châssis de la tour',(), 'Pourquoi la carte mère ne doit-elle pas toucher directement la tôle ?'),
 'board':Part('Carte mère','Carte mère',
     'Relie les composants par des bus et connecteurs. Elle porte le socket CPU, les logements mémoire et les ports PCI Express.',
     'Plateau et entretoises',('case',),'La carte mère effectue-t-elle tous les calculs du PC ?'),
 'cpu':Part('Processeur — CPU','CPU',
     'Exécute les instructions des programmes. Son unité de contrôle coordonne les opérations ; ses unités de calcul traitent les données.',
     'Socket du processeur',('board',),'Quelle différence entre une instruction et une donnée ?'),
 'paste':Part('Pâte thermique','Pâte thermique',
     'Améliore le transfert de chaleur entre le CPU et son refroidisseur en comblant les défauts microscopiques de contact.',
     'Surface du CPU',('cpu',),'Pourquoi un processeur doit-il évacuer de la chaleur ?'),
 'ram':Part('Mémoire vive — RAM','RAM ×2',
     'Garde temporairement les programmes et données en cours d’utilisation. Son contenu est perdu quand l’alimentation est coupée.',
     'Deux emplacements DIMM',('board',),'Que devient un document non enregistré si le courant est coupé ?'),
 'ssd':Part('SSD NVMe','SSD NVMe',
     'Conserve les fichiers, logiciels et le système même sans courant. Ce modèle se connecte au port M.2 et utilise PCI Express.',
     'Connecteur M.2',('board',),'Pourquoi a-t-on besoin de RAM alors que le SSD stocke déjà des données ?'),
 'cooler':Part('Ventirad CPU','Ventirad',
     'Le radiateur reçoit la chaleur du CPU et le ventilateur la dissipe. Le câble du ventilateur rejoint CPU_FAN, connecté ici automatiquement.',
     'Au-dessus du CPU',('cpu','paste'),'Quel est le rôle du radiateur par rapport au ventilateur ?'),
 'gpu':Part('Carte graphique — GPU','Carte graphique',
     'Produit les images et accélère des calculs parallèles. Cette carte dédiée a sa propre mémoire vidéo et se branche sur PCI Express x16.',
     'Port PCI Express x16',('board',),'Pourquoi brancher l’écran sur la carte graphique dans cette configuration ?'),
 'psu':Part('Bloc d’alimentation','Alimentation',
     'Convertit le courant alternatif du secteur en tensions continues pour le PC. Sa puissance doit convenir aux composants installés.',
     'Compartiment inférieur',('case',),'Pourquoi ne branche-t-on pas directement le CPU au secteur ?'),
 'fans':Part('Ventilation du boîtier','Ventilos',
     'Fait circuler l’air : entrée à l’avant, sortie à l’arrière. Les ventilateurs sont reliés ici automatiquement aux connecteurs SYS_FAN.',
     'Façade et extraction arrière',('case','board'),'Que se passe-t-il si l’air chaud reste enfermé dans le boîtier ?'),
 'atx':Part('Câble ATX 24 broches','ATX 24 broches',
     'Apporte l’alimentation principale à la carte mère. Il ne remplace pas le câble d’alimentation dédié au processeur.',
     'Bord droit de la carte mère',('psu','board'),'Pourquoi le seul câble ATX ne suffit-il pas dans ce montage ?'),
 'eps':Part('Câble CPU / EPS','CPU / EPS',
     'Alimente l’étage de puissance du processeur. Un câble CPU/EPS et un câble GPU/PCIe ne sont pas interchangeables.',
     'Connecteur CPU en haut de la carte',('psu','board','cpu'),'À quel composant ce câble fournit-il de l’énergie ?'),
 'pcie':Part('Câble GPU / PCIe','GPU / PCIe',
     'Fournit à cette carte graphique l’énergie supplémentaire nécessaire. Le port PCIe transmet les données et fournit aussi une part de l’énergie.',
     'Connecteur sur la carte graphique',('psu','gpu'),'Un câble d’alimentation transporte-t-il les images vers l’écran ?'),
}

class PCBuild:
    def __init__(self):
        self.installed=set(); self.booted=False
    def install(self,key):
        if key not in PARTS: return False,'Composant inconnu.'
        if key in self.installed: return False,'Déjà installé : consulte son rôle à droite.'
        missing=[PARTS[k].short for k in PARTS[key].needs if k not in self.installed]
        if missing: return False,'Installe d’abord : '+', '.join(missing)+'.'
        self.installed.add(key); self.booted=False
        return True,PARTS[key].short+' installé. '+('Connexion effectuée.' if key in ('atx','eps','pcie') else '')
    def remove(self,key):
        if key not in self.installed: return False,'Cette pièce n’est pas installée.'
        users=[PARTS[k].short for k in PARTS if k in self.installed and key in PARTS[k].needs]
        if users: return False,'Retire d’abord : '+', '.join(users)+'.'
        self.installed.remove(key); self.booted=False
        return True,PARTS[key].short+' retiré. Tu peux le réinstaller.'
    def diagnostics(self):
        return [(k,PARTS[k].short) for k in PARTS if k not in self.installed]
    def boot(self):
        missing=self.diagnostics()
        if missing:
            self.booted=False
            return False,'Montage incomplet : '+', '.join(t for _,t in missing[:3])+('…' if len(missing)>3 else '.')
        self.booted=True
        return True,'POST réussi ! Matériel prêt. Il reste à installer un système d’exploitation sur le SSD.'
    def snapshot(self): return {'installed':[k for k in PARTS if k in self.installed],'booted':self.booted}
    @classmethod
    def restore(cls,data):
        if not isinstance(data,dict) or not isinstance(data.get('installed'),list): raise ValueError('Montage invalide')
        if any(not isinstance(k,str) or k not in PARTS for k in data['installed']): raise ValueError('Pièce inconnue')
        b=cls(); b.installed=set(data['installed'])
        if any(not set(PARTS[k].needs)<=b.installed for k in b.installed): raise ValueError('Dépendances invalides')
        if type(data.get('booted')) is not bool: raise ValueError('Démarrage invalide')
        b.booted=data['booted'] and len(b.installed)==len(PARTS)
        return b
