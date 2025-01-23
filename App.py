import os
import sys
import pygame
import random


class Tile(pygame.sprite.Sprite):
    def __init__(self, app, pos_x, pos_y, n):
        super().__init__(app.all_sprites, app.tiles_group)
        self.image = app.load_image('platform.png')
        self.n = n
        self.x = pos_x
        self.y = pos_y
        self.rect = self.image.get_rect().move(self.x, self.y)


class Hero(pygame.sprite.Sprite):
    def __init__(self, app, pos):
        self.app = app
        super().__init__(app.player_group, app.all_sprites)
        self.image = self.app.load_image("bird.png")
        self.rect = self.image.get_rect()
        # вычисляем маску для эффективного сравнения
        self.mask = pygame.mask.from_surface(self.image)
        self.rect.x = pos[0]
        self.rect.y = pos[1]

    def update(self, pos):
        self.rect.x += pos[0]
        self.rect.y += pos[1]

    def jump(self):
        self.update((0, -90))

    def on_platform(self):
        for i in range(len(app.tiles)):
            s = pygame.sprite.spritecollideany(self, app.tiles_group)
            t = app.tiles
            if (s and self.rect.x + 65 >  t[i][0] and self.rect.x <= t[i][0] + 65
                    and self.rect.y < t[i][1]):
                if s.x == t[i][0] and s.y == t[i][1] and s.n == i:
                    return True
        return False



class Button():
    def __init__(self, s, screen):
        self.s = s
        if self.s == 'Yes':
            self.x = 150
        else:
            self.x = 330

        self.font = pygame.font.Font(None, 50)
        self.text = self.font.render('Continue?', 1, (0, 0, 0))
        pygame.draw.rect(screen, (246, 246, 246), (0, 500, 600, 100), 0)
        screen.blit(self.text, (200 + (200 - self.text.get_width()) // 2,
                           500 + (50 - self.text.get_height()) // 2))

    def render(self, screen):
        self.text_btn = self.font.render(self.s, 1, (0, 0, 0))
        screen.blit(self.text_btn, (self.x + (self.x - self.text.get_width()) // 2,
                               560 + (40 - self.text.get_height()) // 2))

    def check_click(self, pos):
        if (self.x + (self.x - self.text_btn.get_width()) // 2 - self.text_btn.get_width() <= pos[0]
                <= self.x + (self.x - self.text_btn.get_width()) // 2
                and 560 <= pos[1] <= 600):
            return True
        return False

    def level(self, pos):
        if 373 > pos[1] > 227:
            return True


class App:
    def __init__(self):
        pygame.init()
        self.width, self.height = 600, 600
        self.clock = pygame.time.Clock()
        self.screen = pygame.display.set_mode((self.width, self.height))
        pygame.display.set_caption('Прыгаем по платформам')
        pygame.mixer.music.load('data/music.mp3')
        pygame.key.set_repeat(200, 70)
        self.tile_width = 40
        self.tile_height = 60
        self.fps = 60

    def terminate(self):
        pygame.quit()
        sys.exit()


    def load_image(self, name, colorkey=None):
        fullname = os.path.join('data', name)
        if not os.path.isfile(fullname):
            print(f"Файл с изображением '{fullname}' не найден")
            sys.exit()
        image = pygame.image.load(fullname)
        if colorkey is not None:
            image = image.convert()
            if colorkey == -1:
                colorkey = image.get_at((0, 0))
            image.set_colorkey(colorkey)
        else:
            image = image.convert_alpha()
        return image

    def generate_level(self):
        for y in range(0, 11):
            x = random.randint(3, 9)
            self.tiles_group.add(Tile(self, x * self.tile_width, y * self.tile_height, y))
            self.tiles.append([x * self.tile_width, y * self.tile_height])

    def run_game(self):
        pygame.mixer.music.play(-1)
        self.all_sprites = pygame.sprite.Group()
        self.tiles_group = pygame.sprite.Group()
        self.player_group = pygame.sprite.Group()
        self.tiles = []
        self.generate_level()
        x = self.tiles[9][0] - 20
        y = self.tiles[9][1] - 50
        self.hero = Hero(self, (x, y))
        run = True
        fon = pygame.transform.scale(self.load_image('gamefon.png'), (self.width, self.height))
        MYEVENTTYPE = pygame.USEREVENT + 1
        pygame.time.set_timer(MYEVENTTYPE, 25)
        while run:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.terminate()
                if event.type == pygame.KEYDOWN and event.key == pygame.K_1:
                    self.game_over += 1
                if event.type == MYEVENTTYPE:
                    if not self.hero.on_platform():
                        self.hero.update((0, 5))
            keys = pygame.key.get_pressed()
            if keys[pygame.K_RIGHT]:
                self.hero.update((10, 0))
            if keys[pygame.K_LEFT]:
                self.hero.update((-10, 0))
            if keys[pygame.K_UP] and self.hero.on_platform():
                self.hero.jump()
            if self.hero.rect.y > 600:
                run = False
                self.end_screen()

            self.screen.blit(fon, (0, 0))
            self.all_sprites.draw(self.screen)
            self.player_group.draw(self.screen)
            self.tiles_group.draw(self.screen)
            pygame.display.flip()
            self.clock.tick(self.fps)

    def start_screen(self):
        intro_text = ["        Правила игры",
                      "В игре вы должны продвигаться вверх",
                      "по платформам",
                      "Игра заканчивается, когда вы упадёте"]

        fon = pygame.transform.scale(self.load_image('fon.jpg'), (self.width, self.height))
        self.lvl = Button('', self.screen)
        self.screen.blit(fon, (0, 0))
        self.lvl.render(self.screen)
        font = pygame.font.Font(None, 30)
        text_coord = 50
        for line in intro_text:
            string_rendered = font.render(line, 1, pygame.Color('black'))
            intro_rect = string_rendered.get_rect()
            text_coord += 10
            intro_rect.top = text_coord
            intro_rect.x = 10
            text_coord += intro_rect.height
            self.screen.blit(string_rendered, intro_rect)
        while True:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.terminate()
                elif event.type == pygame.MOUSEBUTTONDOWN:
                    if self.lvl.level(event.pos):
                        return
            pygame.display.flip()
            self.clock.tick(self.fps)

    def choice_levels(self):
        pass

    def end_screen(self):
        fon = pygame.transform.scale(self.load_image('game over 1.jpg'), (self.width, self.height - 100))
        self.yes = Button('Yes', self.screen)
        self.no = Button('No', self.screen)
        self.screen.blit(fon, (0, 0))
        self.no.render(self.screen)
        self.yes.render(self.screen)
        while True:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.terminate()
                elif event.type == pygame.MOUSEBUTTONDOWN:
                    if self.no.check_click(event.pos):
                        self.terminate()
                    elif self.yes.check_click(event.pos):
                        self.run_game()

            pygame.display.flip()
            self.clock.tick(self.fps)


if __name__ == '__main__':
    app = App()
    app.start_screen()
    app.run_game()