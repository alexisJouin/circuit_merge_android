"""Boucle de jeu Pygame : entrées, temps fixe, affichage et sauvegarde.

Le jeu suit trois couches : moteur (règles), vue (dessin), application
(orchestration). Une fenêtre de dimensions différentes ne change ni les
distances physiques ni la vitesse des composants.
"""

import os
from pathlib import Path
import time

import pygame

from . import config as C
from .audio import Audio
from .engine import GameEngine
from .model import RoundState
from .storage import SaveStore
from .view import View


def populate_demo(engine: GameEngine) -> None:
    """Montage de démonstration pour aperçus / expériences, sans jouer à la place.

    Ce scénario utilise le moteur réel : les objets tombent et se stabilisent.
    Il n'est ni une image de fond ni la situation initiale d'une partie normale.
    """
    placements = ((7, 414, 685), (8, 641, 676), (5, 392, 535),
                  (6, 545, 490), (4, 718, 506), (3, 432, 415),
                  (2, 638, 425), (1, 737, 378), (0, 370, 395))
    for level, x, y in placements:
        engine.add_piece(level, (x, y), angle=(level % 3 - 1) * 0.17)
    for _ in range(240):
        engine.step()
    engine.take_events()
    engine.score, engine.drops, engine.merge_count = 486, 42, 31
    engine.current_level, engine.next_level = 2, 0
    engine.set_aim(596)


class Application:
    """Application locale Windows / macOS / Linux.

    ``persist=False`` permet de tester l'interface sans écrire chez l'utilisateur.
    ``mode`` indique le menu qui suspend la simulation, ou None pour jouer.
    """

    def __init__(self, *, seed: int | None = None, fresh: bool = False,
                 save_path: Path | None = None, persist: bool = True,
                 demo: bool = False, muted: bool = False) -> None:
        self.persist = persist
        self.seed = seed
        pygame.display.init()
        pygame.display.set_caption("Circuit Merge V2 — Les composants prennent vie")
        info = pygame.display.Info()
        scale = min(1.0, max(0.5, (info.current_w - 60) / C.WIDTH),
                    max(0.5, (info.current_h - 95) / C.HEIGHT))
        size = (round(C.WIDTH * scale), round(C.HEIGHT * scale))
        self.screen = pygame.display.set_mode(size, pygame.RESIZABLE)
        self.windowed_size = size
        self.fullscreen = False
        self.view = View()
        pygame.display.set_icon(self.view.sprites.get(5, 24))
        self.store = SaveStore(save_path)
        data = self.store.load() if persist else {"best": 0, "sound": not muted}
        self.best = int(data.get("best", 0))
        self.engine = GameEngine(seed)
        self.mode: str | None = "welcome"
        self.audio = Audio(bool(data.get("sound", True)) and not muted)
        snapshot = data.get("round")
        if snapshot and not fresh:
            try:
                self.engine = GameEngine.from_snapshot(snapshot)
                self.mode = "pause" if self.engine.state is RoundState.PLAYING else "game_over"
                self.view.notify("Partie V1 convertie en V2 : reprise en pause." if self.store.migrated
                                 else "Votre dernière partie a été restaurée.")
            except (KeyError, ValueError, TypeError, IndexError, OverflowError):
                self.view.notify("Partie sauvegardée incompatible : nouveau départ.", 5)
        if self.store.error:
            self.view.notify(self.store.error, 6)
        if demo:
            self.engine = GameEngine(seed)
            populate_demo(self.engine)
            self.mode = None

        self.running = True
        self.debug = False
        self.slow = False
        self.inspect_uid: int | None = None
        self.dragging = False
        self.mouse = (-1.0, -1.0)
        self.accumulator = 0.0
        self.clock = pygame.time.Clock()
        self.last_autosave = time.monotonic()
        self._fitted = self._viewport()
        self.draw()  # construit les boutons avant le premier événement

    def _viewport(self) -> pygame.Rect:
        """Rectangle du canevas dans la fenêtre, avec bandes si nécessaire."""
        width, height = self.screen.get_size()
        scale = min(width / C.WIDTH, height / C.HEIGHT)
        return pygame.Rect((width - round(C.WIDTH * scale)) // 2,
                           (height - round(C.HEIGHT * scale)) // 2,
                           round(C.WIDTH * scale), round(C.HEIGHT * scale))

    def logical_position(self, pos: tuple[float, float]) -> tuple[float, float]:
        """Inverse le changement d'échelle, pour souris et écran tactile."""
        rect = self._viewport()
        if not rect.collidepoint(pos):
            return -1.0, -1.0
        return ((pos[0] - rect.x) * C.WIDTH / rect.width,
                (pos[1] - rect.y) * C.HEIGHT / rect.height)

    @property
    def active(self) -> bool:
        """La simulation est suspendue par tous les menus."""
        return self.mode is None and self.engine.state is RoundState.PLAYING

    def save(self) -> None:
        """Sauvegarde record, options et état courant sans bloquer le jeu."""
        if not self.persist:
            return
        self.best = max(self.best, self.engine.score)
        ok = self.store.save(self.best, self.audio.enabled, self.engine.snapshot())
        if not ok:
            self.view.notify(self.store.error, 5)
        self.last_autosave = time.monotonic()

    def _new_round(self) -> None:
        """Réinitialise toute la simulation, conserve le record et les options."""
        self.best = max(self.best, self.engine.score)
        self.engine = GameEngine(self.seed)
        self.mode = None
        self.accumulator = 0
        self.view.effects.clear()
        self.view.particles.clear()
        self.view.goal_time = 0
        self.view.personalities.clear()
        self.view.preview_face = self.view.preview_face.__class__(-1)
        self.view._projection_key = None
        self.inspect_uid = None
        self.dragging = False
        self.save()

    def action(self, name: str) -> None:
        """Actions communes aux boutons et au clavier."""
        if name == "sound":
            self.audio.enabled = not self.audio.enabled
            self.view.notify("Son activé" if self.audio.enabled else "Son coupé")
            self.save()
        elif name == "debug":
            self.debug = not self.debug
            self.inspect_uid = None
            self.view.notify("Mode NSI : polygones, centres de masse, vitesses" if self.debug else "Mode de jeu")
        elif name == "help":
            self.mode = "help"
        elif name == "pause":
            if self.engine.state is RoundState.PLAYING:
                self.mode = None if self.mode is not None else "pause"
                self.dragging = False
                self.save()
        elif name == "close":
            self.mode = "game_over" if self.engine.state is RoundState.GAME_OVER else None
        elif name == "new":
            if self.engine.drops > 0 or self.engine.pieces:
                self.mode = "restart"
            else:
                self._new_round()
        elif name == "confirm_new":
            self._new_round()
        self.accumulator = 0.0  # pas de rattrapage après une pause ou un menu

    def _press(self, pos: tuple[float, float], button: int = 1) -> None:
        """Un clic sur l'interface ne devient jamais un lâcher dans le bac."""
        self.mouse = self.logical_position(pos)
        if button == 3 and self.debug:
            piece = self.engine.piece_at(*self.mouse)
            self.inspect_uid = piece.uid if piece else None
            return
        if button != 1:
            return
        for name, rect in self.view.buttons.items():
            if rect.collidepoint(self.mouse):
                self.action(name)
                self.draw()
                return
        x, y = self.mouse
        if self.active and C.LEFT <= x <= C.RIGHT and 106 <= y <= C.FLOOR:
            self.engine.set_aim(x)
            self.dragging = True

    def _release(self, pos: tuple[float, float]) -> None:
        self.mouse = self.logical_position(pos)
        if self.dragging and self.active and self.mouse != (-1.0, -1.0):
            self.engine.drop(self.mouse[0])
        self.dragging = False

    def handle_event(self, event: pygame.event.Event) -> None:
        """Traite un événement. Méthode publique pour les tests d'intégration."""
        if event.type == pygame.QUIT:
            self.running = False
        elif event.type == pygame.WINDOWFOCUSLOST:
            if self.active:
                self.action("pause")
        elif event.type == pygame.VIDEORESIZE and not self.fullscreen:
            size = (max(500, event.w), max(420, event.h))
            self.screen = pygame.display.set_mode(size, pygame.RESIZABLE)
            self.windowed_size = size
        elif event.type == pygame.KEYDOWN:
            key = event.key
            if key in (pygame.K_ESCAPE, pygame.K_p):
                self.action("pause")
            elif key == pygame.K_F1:
                self.action("debug")
            elif key == pygame.K_F2:
                self.slow = not self.slow
                self.view.notify("Physique au ralenti : ×0,25" if self.slow else "Vitesse normale")
            elif key == pygame.K_m:
                self.action("sound")
            elif key in (pygame.K_h, pygame.K_F3):
                self.action("help")
            elif key == pygame.K_F11:
                self.fullscreen = not self.fullscreen
                self.screen = pygame.display.set_mode((0, 0), pygame.FULLSCREEN) if self.fullscreen else pygame.display.set_mode(self.windowed_size, pygame.RESIZABLE)
            elif key in (pygame.K_e, pygame.K_UP, pygame.K_DOWN) and self.active:
                self.engine.rotate_aim(-C.ROTATION_STEP if key == pygame.K_DOWN else C.ROTATION_STEP)
            elif key == pygame.K_r:
                self.action("confirm_new" if self.engine.state is RoundState.GAME_OVER else "new")
            elif key in (pygame.K_RETURN, pygame.K_SPACE):
                if self.mode == "restart":
                    self.action("confirm_new")
                elif self.engine.state is RoundState.GAME_OVER:
                    self.action("confirm_new")
                elif self.mode is not None:
                    self.action("close")
                elif self.active:
                    self.engine.drop()
        # SDL produit parfois un événement souris supplémentaire pour le toucher.
        # On ignore ce doublon pour éviter de lâcher deux composants.
        elif event.type == pygame.MOUSEWHEEL and self.active:
            self.engine.rotate_aim(event.y * C.ROTATION_STEP)
        elif event.type == pygame.MOUSEBUTTONDOWN and not getattr(event, "touch", False):
            self._press(event.pos, event.button)
        elif event.type == pygame.MOUSEBUTTONUP and event.button == 1 and not getattr(event, "touch", False):
            self._release(event.pos)
        elif event.type == pygame.MOUSEMOTION and not getattr(event, "touch", False):
            self.mouse = self.logical_position(event.pos)
            if self.active and C.LEFT <= self.mouse[0] <= C.RIGHT:
                self.engine.set_aim(self.mouse[0])
        elif event.type in (pygame.FINGERDOWN, pygame.FINGERUP, pygame.FINGERMOTION):
            width, height = self.screen.get_size()
            pos = (event.x * width, event.y * height)
            if event.type == pygame.FINGERDOWN:
                self._press(pos)
            elif event.type == pygame.FINGERUP:
                self._release(pos)
            else:
                self.mouse = self.logical_position(pos)
                if self.active and self.dragging:
                    self.engine.set_aim(self.mouse[0])

    def update(self, elapsed: float) -> None:
        """Accumulateur : plusieurs petits pas de physique pour une image.

        Le temps réel est plafonné à 0,1 s : si l'ordinateur se bloque pendant
        plusieurs secondes, on évite un rattrapage géant et instable. Le jeu
        peut ralentir sur un PC chargé mais n'accélère jamais brutalement.
        """
        dt = min(max(elapsed, 0.0), 0.1)
        if self.active:
            keys = pygame.key.get_pressed()
            direction = int(keys[pygame.K_RIGHT] or keys[pygame.K_d]) - int(keys[pygame.K_LEFT] or keys[pygame.K_a] or keys[pygame.K_q])
            if direction:
                self.engine.set_aim(self.engine.aim_x + direction * 420 * dt)
            self.accumulator += dt * (0.25 if self.slow else 1.0)
            while self.accumulator + 1e-12 >= C.FIXED_DT:
                self.engine.step()
                self.accumulator -= C.FIXED_DT
                if self.engine.state is RoundState.GAME_OVER:
                    break
            self.view.animate(dt * (0.25 if self.slow else 1.0), self.engine)
        else:
            self.accumulator = 0.0
            # Les messages d'information restent temporaires même dans un menu.
            self.view.toast_time = max(0.0, self.view.toast_time - dt)

        events = self.engine.take_events()
        self.view.consume(events)
        for event in events:
            self.audio.play(event.kind, event.level)
            if event.kind == "game_over":
                self.mode = "game_over"
                self.dragging = False
                self.save()
        self.best = max(self.best, self.engine.score)
        if time.monotonic() - self.last_autosave > 10:
            self.save()

    def draw(self) -> None:
        """Adapte le canevas à la fenêtre ; conserve le rapport largeur/hauteur."""
        canvas = self.view.render(self.engine, self.best, self.mouse, mode=self.mode,
                                  debug=self.debug, muted=not self.audio.enabled,
                                  fps=self.clock.get_fps(), slow=self.slow,
                                  inspect_uid=self.inspect_uid)
        self._fitted = self._viewport()
        self.screen.fill((5, 10, 16))
        scaled = pygame.transform.smoothscale(canvas, self._fitted.size)
        self.screen.blit(scaled, self._fitted)
        pygame.display.flip()

    def run(self, frames: int | None = None) -> None:
        """Boucle principale ; une limite de frames sert au test sans écran."""
        count = 0
        try:
            while self.running and (frames is None or count < frames):
                elapsed = self.clock.tick(C.RENDER_FPS) / 1000.0
                for event in pygame.event.get():
                    self.handle_event(event)
                self.update(elapsed)
                self.draw()
                count += 1
        finally:
            self.save()
            pygame.quit()


def launch(*, seed: int | None = None, fresh: bool = False, save_path: Path | None = None,
           demo: bool = False, screenshot: Path | None = None,
           smoke_test: int | None = None, muted: bool = False) -> None:
    """Lancement normal, démonstration ou vérification automatisée."""
    if smoke_test is not None or screenshot is not None:
        os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
        os.environ.setdefault("SDL_AUDIODRIVER", "dummy")
    app = Application(seed=seed, fresh=fresh, save_path=save_path,
                      persist=smoke_test is None and screenshot is None and not demo,
                      demo=demo, muted=muted)
    if screenshot is not None:
        app.mode = None
        app.draw()
        screenshot.parent.mkdir(parents=True, exist_ok=True)
        pygame.image.save(app.view.canvas, str(screenshot))
        pygame.quit()
    else:
        if smoke_test is not None:
            app.mode = None
            app.engine.drop()
        app.run(smoke_test)
