"""Android adapter; desktop game rules and rendering remain shared."""
import os
from pathlib import Path
import pygame
from .project_app import ProjectApplication
from . import config as C


def launch_android():
    from android.storage import app_storage_path
    folder = Path(app_storage_path())
    folder.mkdir(parents=True, exist_ok=True)
    app = AndroidApplication(save_path=folder / 'project_q_v3.json')
    app.screen = pygame.display.set_mode((0, 0), pygame.FULLSCREEN)
    app.fullscreen = True
    app.draw()
    app.run()


class AndroidApplication(ProjectApplication):
    """Landscape viewport, persistent navigation, single-finger ownership."""
    finger = None
    toolbar_finger = None

    def _viewport(self):
        w, h = self.screen.get_size()
        bar = max(48, round(h * .075))
        scale = min(w / C.WIDTH, (h - bar) / C.HEIGHT)
        size = round(C.WIDTH * scale), round(C.HEIGHT * scale)
        return pygame.Rect((w-size[0])//2, (h-bar-size[1])//2, *size)

    def _toolbar(self):
        w, h = self.screen.get_size()
        bar = max(48, round(h * .075))
        return [pygame.Rect(i*w//4, h-bar, (i+1)*w//4-i*w//4, bar) for i in range(4)]

    def _cancel_pointer(self):
        self.finger = None
        self.toolbar_finger = None
        self.dragging = False
        self.pc_drag = None
        self.accumulator = 0

    def _back(self):
        self._cancel_pointer()
        if self.page == 'pc' and self.pc_confirm:
            self.pc_confirm = False
        elif self.page == 'play' and self.view.tool:
            self.view.tool = None
        elif self.page == 'play' and self.mode is None:
            self.action('pause')
        elif self.page != 'hub':
            self.action('hub')
        else:
            self.save()
            self.running = False

    def handle_event(self, event):
        backgrounds = tuple(getattr(pygame, n, -1) for n in
                            ('APP_WILLENTERBACKGROUND', 'APP_DIDENTERBACKGROUND', 'WINDOWFOCUSLOST'))
        if event.type in backgrounds:
            self._cancel_pointer()
            if self.active:
                self.action('pause')
            self.save()
            return
        if event.type == pygame.QUIT:
            self.save()
            self.running = False
            return
        if event.type == pygame.KEYDOWN and event.key in (pygame.K_ESCAPE, pygame.K_AC_BACK):
            self._back()
            return
        if event.type in (pygame.MOUSEBUTTONDOWN, pygame.MOUSEBUTTONUP, pygame.MOUSEMOTION) and getattr(event, 'touch', False):
            return
        if event.type in (pygame.FINGERDOWN, pygame.FINGERUP, pygame.FINGERMOTION):
            if event.type == pygame.FINGERDOWN:
                if self.finger is not None:
                    return
                self.finger = event.finger_id
            elif self.finger != event.finger_id:
                return
            w, h = self.screen.get_size()
            pos = event.x*w, event.y*h
            if event.type == pygame.FINGERDOWN and self._toolbar_press(pos):
                self.toolbar_finger = event.finger_id
                return
            if self.toolbar_finger == event.finger_id:
                if event.type == pygame.FINGERUP:
                    self._cancel_pointer()
                return
            super().handle_event(event)
            if event.type == pygame.FINGERUP:
                self.finger = None
            return
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1 and self._toolbar_press(event.pos):
            return
        super().handle_event(event)

    def _toolbar_press(self, pos):
        for i, rect in enumerate(self._toolbar()):
            if rect.collidepoint(pos):
                self.dragging = False
                self.pc_drag = None
                if i == 0:
                    self.action('hub')
                elif i == 1 and self.page == 'play':
                    self.action('pause')
                elif i >= 2 and self.active:
                    self.engine.rotate_aim(C.ROTATION_STEP * (-1 if i == 2 else 1))
                return True
        return False

    def draw(self):
        super().draw()
        if not getattr(self, 'ready', False):
            return
        font = pygame.font.Font(None, max(20, self._toolbar()[0].height//3))
        for rect, label in zip(self._toolbar(), ('Accueil', 'Pause', 'Rotation -', 'Rotation +')):
            pygame.draw.rect(self.screen, C.PANEL, rect.inflate(-4, -4), border_radius=8)
            text = font.render(label, True, C.TEXT)
            self.screen.blit(text, text.get_rect(center=rect.center))
        pygame.display.flip()
