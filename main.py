import pygame
import os
import random
from pygame import *


class GameManager:
    def __init__(self, max_misses=5):
        # Konstanten für Spielparameter
        self.SCREEN_WIDTH = 800 # Breite des Bildschirms
        self.SCREEN_HEIGHT = 600 # Höhe des Bildschirms
        self.FPS = 60 # Bildwiederholrate (Frames per Second)
        self.MOLE_WIDTH = 90 # Breite des Maulwurfs-Sprites
        self.MOLE_HEIGHT = 81 # Höhe des Maulwurfs-Sprites
        self.FONT_SIZE = 31 # Schriftgröße für Textanzeige
        self.FONT_TOP_MARGIN = 26 # Abstand des Textes von der oberen Bildschirmkante
        self.LEVEL_SCORE_GAP = 4 # Punktedifferenz zwischen den Spielstufen
        self.LEFT_MOUSE_BUTTON = 1 # Wert für die linke Maustaste
        self.GAME_TITLE = "Whack A Mole" #Titel vom Spiel
        # Variablen für Spielzustände, 
        self.score = 0
        self.misses = 0
        self.level = 1
        # Initialisierung des Bildschirms
        self.screen = pygame.display.set_mode((self.SCREEN_WIDTH, self.SCREEN_HEIGHT))
        pygame.display.set_caption(self.GAME_TITLE)
        self.background = pygame.image.load("images/bg.png")
        # Schriftart für Textanzeige
        self.font_obj = pygame.font.Font('./fonts/GROBOLD.ttf', self.FONT_SIZE)
        # Initialisierung der Maulwurf-Sprite-Sheet
        # Das Sprite-Sheet enthält 6 verschiedene Zustände des Maulwurfs
        sprite_sheet = pygame.image.load("images/mole.png")
        self.mole = []
        self.mole.append(sprite_sheet.subsurface(169, 0, 90, 81))
        self.mole.append(sprite_sheet.subsurface(309, 0, 90, 81))
        self.mole.append(sprite_sheet.subsurface(449, 0, 90, 81))
        self.mole.append(sprite_sheet.subsurface(575, 0, 116, 81))
        self.mole.append(sprite_sheet.subsurface(717, 0, 116, 81))
        self.mole.append(sprite_sheet.subsurface(853, 0, 116, 81))
        # Positionen der Löcher im Hintergrundbild
        self.hole_positions = []
        self.hole_positions.append((381, 295))
        self.hole_positions.append((119, 366))
        self.hole_positions.append((179, 169))
        self.hole_positions.append((404, 479))
        self.hole_positions.append((636, 366))
        self.hole_positions.append((658, 232))
        self.hole_positions.append((464, 119))
        self.hole_positions.append((95, 43))
        self.hole_positions.append((603, 11))
        # Initialisierung des Debuggers
        self.debugger = Debugger("debug")
        # Soundeffekte
        self.soundEffect = SoundEffect()
        # Maximale Anzahl von verpassten Klicks (Standardwert: 5)
        self.max_misses = max(max_misses, 5)
        
    # Calculiert das Spielerlevel anhand seiner aktuellen Punktzahl und der LEVEL_SCORE_GAP-Konstante
    def get_player_level(self):
        newLevel = 1 + int(self.score / self.LEVEL_SCORE_GAP)
        if newLevel != self.level:
            # Sound spielen-> neues Level
            self.soundEffect.playLevelUp()
        return 1 + int(self.score / self.LEVEL_SCORE_GAP)


        


    # Neue Zeitspanne zwischen dem Auftauchen des Maulwurfs und dem Auftauchen in den Löchern
    def get_interval_by_level(self, initial_interval):
        new_interval = initial_interval - self.level * 0.15
        if new_interval > 0:
            return new_interval
        else:
            return 0.05

    # Hier wird überpruft ob der Mausklick den Maulwurf getroffen hat oder nicht
    def is_mole_hit(self, mouse_position, current_hole_position):
        mouse_x = mouse_position[0]
        mouse_y = mouse_position[1]
        current_hole_x = current_hole_position[0]
        current_hole_y = current_hole_position[1]
        if (mouse_x > current_hole_x) and (mouse_x < current_hole_x + self.MOLE_WIDTH) and (mouse_y > current_hole_y) and (mouse_y < current_hole_y + self.MOLE_HEIGHT):
            return True
        else:
            return False

    # Aktualisiert den Spiel Status
    def update(self):
        # Aktualisiert den Score
        current_score_string = "SCORE: " + str(self.score)
        score_text = self.font_obj.render(current_score_string, True, (255, 255, 255))
        score_text_pos = score_text.get_rect()
        score_text_pos.centerx = self.background.get_rect().centerx
        score_text_pos.centery = self.FONT_TOP_MARGIN
        self.screen.blit(score_text, score_text_pos)
        # Aktualisiert die Misses
        current_misses_string = "MISSES: " + str(self.misses)
        misses_text = self.font_obj.render(current_misses_string, True, (255, 255, 255))
        misses_text_pos = misses_text.get_rect()
        misses_text_pos.centerx = self.SCREEN_WIDTH / 5 * 4
        misses_text_pos.centery = self.FONT_TOP_MARGIN
        self.screen.blit(misses_text, misses_text_pos)
        # Aktualisiert den Level
        current_level_string = "LEVEL: " + str(self.level)
        level_text = self.font_obj.render(current_level_string, True, (255, 255, 255))
        level_text_pos = level_text.get_rect()
        level_text_pos.centerx = self.SCREEN_WIDTH / 5 * 1
        level_text_pos.centery = self.FONT_TOP_MARGIN
        self.screen.blit(level_text, level_text_pos)

    
    def start(self):
        cycle_time = 0
        num = -1
        loop = True
        is_down = False
        interval = 0.1
        initial_interval = 1
        frame_num = 0
        left = 0
        # Zeitkontrollvariablen
        clock = pygame.time.Clock()

        for i in range(len(self.mole)):
            self.mole[i].set_colorkey((0, 0, 0))
            self.mole[i] = self.mole[i].convert_alpha()

        while loop:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    loop = False
                if event.type == MOUSEBUTTONDOWN and event.button == self.LEFT_MOUSE_BUTTON:
                    self.soundEffect.playFire()
                    if self.is_mole_hit(mouse.get_pos(), self.hole_positions[frame_num]) and num > 0 and left == 0:
                        num = 3
                        left = 14
                        is_down = False
                        interval = 0
                        self.score += 1  # Erhöht die Punktzahl des Spielers
                        self.level = self.get_player_level()  # Calculiert den Level
                        
                        self.soundEffect.stopPop()
                        
                        self.soundEffect.playHurt()
                        self.update()
                    else:
                        self.misses += 1
                        self.update()
                        if self.max_misses < self.misses:
                            print("Spiel Vorbei") # funktionniert nicht so gut :/
                            pygame. quit()

            if num > 5:
                self.screen.blit(self.background, (0, 0))
                self.update()
                num = -1
                left = 0

            if num == -1:
                self.screen.blit(self.background, (0, 0))
                self.update()
                num = 0
                is_down = False
                interval = 0.5
                frame_num = random.randint(0, 8)

            mil = clock.tick(self.FPS)
            sec = mil / 1000.0
            cycle_time += sec
            if cycle_time > interval:
                pic = self.mole[num]
                self.screen.blit(self.background, (0, 0))
                self.screen.blit(pic, (self.hole_positions[frame_num][0] - left, self.hole_positions[frame_num][1]))
                self.update()
                if is_down is False:
                    num += 1
                else:
                    num -= 1
                if num == 4:
                    interval = 0.3
                elif num == 3:
                    num -= 1
                    is_down = True
                    self.soundEffect.playPop()
                    interval = self.get_interval_by_level(initial_interval) 
                else:
                    interval = 0.1
                cycle_time = 0
            # Update vom Bild
            pygame.display.flip()
            


# druckt die Debugging Informationen aus
class Debugger:
    def __init__(self, mode):
        self.mode = mode

    def log(self, message):
        if self.mode is "debug":
            print("> DEBUG: " + str(message))


class SoundEffect:
    def __init__(self):
        self.mainTrack = pygame.mixer.music.load("sounds/themesong.wav")
        self.fireSound = pygame.mixer.Sound("sounds/fire.wav")
        self.fireSound.set_volume(1.0)
        self.popSound = pygame.mixer.Sound("sounds/pop.wav")
        self.hurtSound = pygame.mixer.Sound("sounds/hurt.wav")
        self.levelSound = pygame.mixer.Sound("sounds/point.wav")
        pygame.mixer.music.play(-1)

    def playFire(self):
        self.fireSound.play()

    def stopFire(self):
        self.fireSound.sop()

    def playPop(self):
        self.popSound.play()

    def stopPop(self):
        self.popSound.stop()

    def playHurt(self):
        self.hurtSound.play()

    def stopHurt(self):
        self.hurtSound.stop()

    def playLevelUp(self):
        self.levelSound.play()

    def stopLevelUp(self):
        self.levelSound.stop()


# Initialisiere das Spiel
pygame.mixer.init(frequency=22050, size=-16, channels=2, buffer=512)
pygame.init()

# Führt die Hauptschleife aus
my_game = GameManager()
my_game.start()

# Exit das Spiel
pygame.quit()
