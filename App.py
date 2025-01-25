import os
import sys
import pygame
import random


class Coin(pygame.sprite.Sprite):
    def __init__(self, app, pos_x, pos_y):
        super().__init__(app.all_sprites, app.coin_group)
        self.image = app.load_image('coin.png')
        self.x = pos_x
        self.y = pos_y
        self.rect = self.image.get_rect().move(self.x, self.y)

    def collect(self):
        sound = pygame.mixer.Sound('data/money.mp3')
        empty_channel = pygame.mixer.find_channel()
        empty_channel.play(sound)


class Flag(pygame.sprite.Sprite):
    def __init__(self, app, pos_x, pos_y):
        super().__init__(app.all_sprites, app.flag_group)
        self.app = app
        self.image = app.load_image('flag.png')
        self.x = pos_x
        self.y = pos_y
        self.rect = self.image.get_rect().move(self.x, self.y)

    def complete(self):
        self.app.level_complete()


class Tile(pygame.sprite.Sprite):
    def __init__(self, app, pos_x, pos_y, n):
        super().__init__(app.all_sprites, app.tiles_group)
        self.image = app.load_image('platform.png')
        self.n = n
        self.x = pos_x
        self.y = pos_y
        self.rect = self.image.get_rect().move(self.x, self.y)

    def under_screen(self):
        return self.rect.y >= 600


class Hero(pygame.sprite.Sprite):
    def __init__(self, app, pos):
        self.app = app
        super().__init__(app.player_group, app.all_sprites)
        self.image = self.app.load_image("bird.png")
        self.rect = self.image.get_rect()
        self.mask = pygame.mask.from_surface(self.image)
        self.score = 0
        self.rect.x = pos[0]
        self.rect.y = pos[1]
        self.height = 57
        self.width = 86

    def update(self, pos):
        self.rect.x += pos[0]
        self.rect.y += pos[1]

    def jump(self):
        self.update((0, -40))

    def on_platform(self):
        for i in range(len(app.tiles)):
            t = app.tiles
            s = pygame.sprite.spritecollideany(self, app.tiles_group)
            if (s and self.rect.x + 50 > s.x and self.rect.x <= s.x + 50
                    and self.rect.y < s.y and s.n == i):
                return True
        return False


class Levels():
    def __init__(self, n, screen):
        self.size = 75
        self.ind_x = 112.5
        self.ind_y = 200

    def render(self, screen):
        for y in range(2):
            for x in range(5):
                pygame.draw.rect(screen, (0, 0, 0),
                                 ((self.ind_x + x * self.size, self.ind_y + y * self.size),
                                  (self.size, self.size)), 3)
                font = pygame.font.Font(None, 50)
                n = y * 5 + x + 1
                text = font.render(f"{n}", True, (0, 0, 0))
                screen.blit(text, (x * self.size + self.ind_x + 10, y * self.size + self.ind_y + 10))

    def check_click(self, pos):
        mpos_x = pos[0]
        mpos_y = pos[1]
        for y in range(2):
            for x in range(5):
                kx = x * self.size + self.ind_x
                ky = y * self.size + self.ind_y
                if (mpos_x > kx and mpos_x < kx + self.size and mpos_y > ky and mpos_y < ky + self.size):
                    return y * 5 + x + 1
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

        self.text_lvl = self.font.render('Change level', 1, (0, 0, 0))
        pygame.draw.rect(screen, (246, 246, 246), (0, 400, 600, 100), 0)
        screen.blit(self.text_lvl, (185 + (185 - self.text.get_width()) // 2,
                                400 + (50 - self.text.get_height()) // 2))

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

    def check_click_change_level(self, pos):
        if 185 <= pos[0] <= 185 + self.text_lvl.get_width() and 400 <= pos[1] <= 450:
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
        pygame.mixer.music.load('data/music.mp3', 'data/money.mp3')
        pygame.key.set_repeat(200, 70)
        self.tile_width = 40
        self.tile_height = 60
        self.flag_width = 40
        self.flag_height = 60
        self.fps = 60
        self.score = 0
        self.camera = Camera(self)
        self.dificulty = 'easy'
        self.gravity = 0.7

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

    def load_level(self, filename):
        filename = "levels/" + filename
        with open(filename, 'r') as mapFile:
            level_map = [line.strip() for line in mapFile]
        max_width = max(map(len, level_map))
        return list(map(lambda x: x.ljust(max_width, '.'), level_map))

    def generate_level(self, level):
        x, y = None, None
        n = 10
        if self.line + 10  >= len(level):
            n = len(level) - self.line
        for y in range(self.line, self.line + n, 1):
            print(level[y])
            for x in range(len(level[y])):
                if level[y][x] == '@':
                    self.tiles_group.add(Tile(self, x * self.tile_width, y * self.tile_height, y))
                    self.tiles.append([x * self.tile_width, y * self.tile_height])
                if level[y][x] == 'F':
                    self.tiles_group.add(Flag(self, x * self.flag_width, y * self.flag_height))
                    self.tiles.append([x * self.tile_width, y * self.tile_height])
        return x, y

    def run_game(self):
        pygame.mixer.music.play(-1)
        self.all_sprites = pygame.sprite.Group()
        self.tiles_group = pygame.sprite.Group()
        self.player_group = pygame.sprite.Group()
        self.coin_group = pygame.sprite.Group()
        self.flag_group = pygame.sprite.Group()
        self.tiles = []
        self.coins = []
        self.line = 0
        self.LEVEL = self.load_level(f'level{self.level}.txt')
        level_x, level_y = self.generate_level(self.LEVEL)
        x = self.tiles[9][0] - 20
        y = self.tiles[9][1] - 50
        self.hero = Hero(self, (x, y))
        self.coin = Coin(self, 300, 500)
        self.coins.append(self.coin)
        run = True
        fon = pygame.transform.scale(self.load_image('gamefon.png'), (self.width, self.height))
        MYEVENTTYPE = pygame.USEREVENT + 1
        pygame.time.set_timer(MYEVENTTYPE, 25)
        while run:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.terminate()
                if event.type == MYEVENTTYPE:
                    if not self.hero.on_platform():
                        self.hero.update((0, 5))
                if event.type == pygame.KEYDOWN and event.key == pygame.K_UP and self.hero.on_platform():
                    self.hero.jump()
                if event.type == pygame.KEYDOWN and event.key == pygame.K_RIGHT:
                    self.hero.update((20, 0))
                if event.type == pygame.KEYDOWN and event.key == pygame.K_LEFT:
                    self.hero.update((-20, 0))
            for el in self.tiles_group:
                if el.under_screen():
                    self.line += 1
            for el in self.coins:
                if pygame.sprite.collide_mask(el, self.hero):
                    el.rect = el.rect.move(600, 600)
                    el.collect()
            if pygame.sprite.spritecollideany(self.hero, self.flag_group):
                run = False
                self.level_complete()
            if self.hero.rect.y > 543:
                run = False
                self.end_screen()

            self.camera.update(self.hero)
            for sprite in self.all_sprites:
                self.camera.apply(sprite)
                self.tiles = []
                for el in self.tiles_group:
                    self.tiles.append([el.rect.x, el.rect.y])
            self.screen.blit(fon, (0, 0))
            self.all_sprites.draw(self.screen)
            self.player_group.draw(self.screen)
            self.tiles_group.draw(self.screen)
            self.coin_group.draw(self.screen)
            self.flag_group.draw(self.screen)
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
                        self.choice_levels()
            pygame.display.flip()
            self.clock.tick(self.fps)

    def choice_levels(self):
        fon = pygame.transform.scale(self.load_image('fon_lvl.jpg'), (self.width, self.height))
        self.screen.blit(fon, (0, 0))
        self.lvls = Levels(1, self.screen)
        self.lvls.render(self.screen)
        while True:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.terminate()
                elif event.type == pygame.MOUSEBUTTONDOWN:
                    if self.lvls.check_click(event.pos):
                        self.level = self.lvls.check_click(event.pos)
                        self.run_game()
            pygame.display.flip()
            self.clock.tick(self.fps)

    def end_screen(self):
        pygame.mixer.music.pause()
        fon = pygame.transform.scale(self.load_image('game over 1.jpg'), (self.width, self.height - 200))
        font = pygame.font.Font(None, 40)
        text = font.render(f'Счёт: {self.score}', 1, (0, 0, 0))
        fon.blit(text, (245, 30))
        with open('data/best_result.txt') as f:
            data = f.read()
        if self.score > int(data):
            data = self.score
            with open('data/best_result.txt', 'w') as f_in:
                f_in.write(str(self.score))
        text = font.render(f'Лучший результат: {data}', 1, (0, 0, 0))
        fon.blit(text, (160, 60))
        self.yes = Button('Yes', self.screen)
        self.no = Button('No', self.screen)
        self.screen.blit(fon, (0, 0))
        self.no.render(self.screen)
        self.yes.render(self.screen)
        self.score = 0
        self.count_platfroms = 0
        self.line = 0
        while True:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.terminate()
                elif event.type == pygame.MOUSEBUTTONDOWN:
                    if self.yes.check_click_change_level(event.pos):
                        self.choice_levels()
                    elif self.no.check_click(event.pos):
                        self.terminate()
                    elif self.yes.check_click(event.pos):
                        self.run_game()

            pygame.display.flip()
            self.clock.tick(self.fps)

    def level_complete(self):
        pygame.mixer.music.pause()
        fon = pygame.transform.scale(self.load_image('level_complete.png'), (self.width, self.height))
        font = pygame.font.Font(None, 60)
        text = font.render('Next level', 1, (242, 227, 139))
        fon.blit(text, (400, 550))
        self.score = 0
        self.count_platfroms = 0
        self.line = 0
        self.screen.blit(fon, (0, 0))
        while True:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.terminate()
                if event.type == pygame.MOUSEBUTTONDOWN:
                    if 400 <= event.pos[0] <= 400 + text.get_width() and 550 <= event.pos[1] <= 550 + text.get_height():
                        self.level += 1
                        self.run_game()
            pygame.display.flip()
            self.clock.tick(self.fps)


class Camera:
    def __init__(self, app):
        self.dy = 0
        self.app = app

    def apply(self, obj):
        if self.dy > 0 and not self.app.line + 10  >= len(self.app.LEVEL):
            obj.rect.y += self.dy

    def update(self, target):
        self.dy = -(target.rect.y + target.rect.h // 2 - app.height // 2)


if __name__ == '__main__':
    app = App()
    app.start_screen()
    app.run_game()