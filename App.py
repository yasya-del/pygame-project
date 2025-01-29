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

    def update(self, n):
        self.n = n


class Pause():
    def __init__(self, screen):
        self.font = pygame.font.Font(None, 50)
        self.text = self.font.render('| |', 1, (150, 0, 200))
        pygame.draw.rect(screen, (200, 162, 200), (540, 10, 50, 50), 0)
        pygame.draw.rect(screen, (150, 0, 200), (540, 10, 50, 50), 4)
        screen.blit(self.text, (551, 16))

    def check_click(self, pos):
        mpos_x = pos[0]
        mpos_y = pos[1]
        if mpos_x > 540 and mpos_x < 590 and mpos_y > 10 and mpos_y < 60:
            return True
        return False

    def render(self, screen):
        self.font = pygame.font.Font(None, 50)
        self.text = self.font.render('Game on pause', 1, (0, 0, 0))
        screen.blit(self.text, (200 + (200 - self.text.get_width()) // 2,
                                100 + (50 - self.text.get_height()) // 2))
        self.text = self.font.render('Continue?', 1, (0, 0, 0))
        screen.blit(self.text, (200 + (200 - self.text.get_width()) // 2,
                                150 + (50 - self.text.get_height()) // 2))
        pygame.draw.rect(screen, (200, 162, 200), (125, 300, 150, 75), 0)
        pygame.draw.rect(screen, (200, 162, 200), (300, 300, 150, 75), 0)
        self.text = self.font.render('YES', 1, (0, 0, 0))
        screen.blit(self.text, (165, 325))
        self.text = self.font.render('NO', 1, (0, 0, 0))
        screen.blit(self.text, (350, 325))

    def check_click2(self, pos):
        mpos_x = pos[0]
        mpos_y = pos[1]
        if mpos_x > 125 and mpos_x < 275 and mpos_y > 300 and mpos_y < 375:
            return 1
        elif mpos_x > 300 and mpos_x < 450 and mpos_y > 300 and mpos_y < 375:
            return 2
        return False


class Hero(pygame.sprite.Sprite):
    def __init__(self, app, pos):
        self.app = app
        super().__init__(app.player_group, app.all_sprites)
        self.image = self.app.load_image("yellow_bird.png", directory='skins')
        self.img2 = pygame.transform.flip(self.image, True, False)
        self.rect = self.image.get_rect()
        self.mask = pygame.mask.from_surface(self.image)
        self.rect.x = pos[0]
        self.rect.y = pos[1]
        self.score = 0
        self.height = 57
        self.width = 86
        self.d = 'Right'

    def update(self, pos):
        self.rect.x += pos[0]
        if pos[0] < 0:
            if self.d == 'Right':
                self.d = 'Left'
                self.image = self.img2
        elif pos[0] != 0:
            if self.d == 'Left':
                self.d = 'Right'
                self.image = self.app.load_image('yellow_bird.png', directory='skins')
        self.rect.y += pos[1]

    def jump(self):
        self.update((0, -70))

    def on_platform(self):
        for el in self.app.tiles:
            if pygame.sprite.collide_mask(el, self.app.hero) and el.rect.y > self.app.hero.rect.y + 20\
                    and el and self.app.hero.rect.x + 50 > el.x:
                if self.score < len(app.tiles) - el.n - 1:
                    self.score = len(app.tiles) - el.n - 1
                return True
        return False


class Particle(pygame.sprite.Sprite):
    # сгенерируем частицы разного размера

    def __init__(self, pos, dx, dy):
        super().__init__(app.par_sprites)
        self.fire = [app.load_image("star.png")]
        for scale in (5, 10, 20):
            self.fire.append(pygame.transform.scale(self.fire[0], (scale, scale)))
        self.image = random.choice(self.fire)
        self.rect = self.image.get_rect()

        # у каждой частицы своя скорость — это вектор
        self.velocity = [dx, dy]
        # и свои координаты
        self.rect.x, self.rect.y = pos

        # гравитация будет одинаковой (значение константы)
        self.gravity = 0.1

    def update(self):
        # применяем гравитационный эффект:
        # движение с ускорением под действием гравитации
        self.velocity[1] += self.gravity
        self.rect.x += self.velocity[0]
        self.rect.y += self.velocity[1]
        # убиваем, если частица ушла за экран
        if not self.rect.colliderect(app.screen_rect):
            self.kill()


class Levels():
    def __init__(self, n, screen):
        self.size = 75
        self.ind_x = 112.5
        self.ind_y = 200
        self.font = pygame.font.Font(None, 50)
        self.text = self.font.render('Choose level', 1, (0, 0, 0))
        screen.blit(self.text, (200 + (200 - self.text.get_width()) // 2,
                                100 + (50 - self.text.get_height()) // 2))

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
        self.par_sprites = pygame.sprite.Group()
        self.screen_rect = (0, 0, self.width, self.height)
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

    def create_particles(self, position):
        particle_count = 20
        numbers = range(-5, 6)
        for _ in range(particle_count):
            Particle(position, random.choice(numbers), random.choice(numbers))

    def load_image(self, name, colorkey=None, directory='data'):
        fullname = os.path.join(directory, name)
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
        if self.line_now == 0:
            for y in range(0, 10, 1):
                for x in range(len(level[y])):
                    if level[y][x] == '@':
                        t = Tile(self, x * self.tile_width, y * self.tile_height, y)
                        self.tiles_group.add(t)
                        self.tiles.append(t)
                        self.tiles_coords.append([x * self.tile_width, y * self.tile_height])
                    if level[y][x] == 'F':
                        self.flag_group.add(Flag(self, x * self.flag_width, y * self.flag_height))
                        self.tiles_coords.append([x * self.tile_width, y * self.tile_height])
        elif 9 + self.line_now + 1 <= 30:
            for y in range(9 + self.line_now, 9 + self.line_now + 1, 1):
                for x in range(len(level[y])):
                    if level[y][x] == '@':
                        t = Tile(self, x * self.tile_width, 1 * self.tile_height, 1)
                        self.tiles_group.add(t)
                        self.tiles.append(t)
                        self.tiles_coords.append([x * self.tile_width, 1 * self.tile_height])
                    if level[y][x] == 'F':
                        self.flag_group.add(Flag(self, x * self.flag_width, 1 * self.flag_height))
                        self.tiles_coords.append([x * self.tile_width, 1 * self.tile_height])
        return x, y

    def new_game(self):
        self.all_sprites = pygame.sprite.Group()
        self.tiles_group = pygame.sprite.Group()
        self.player_group = pygame.sprite.Group()
        self.coin_group = pygame.sprite.Group()
        self.flag_group = pygame.sprite.Group()
        self.tiles_coords = []
        self.tiles = []
        self.coins = []
        self.line_now = 0
        self.score = 0
        self.count_platfroms = 0
        self.LEVEL = self.load_level(f'level{self.level}.txt')
        level_x, level_y = self.generate_level(self.LEVEL)
        x = self.tiles_coords[-1][0] - 20
        y = self.tiles_coords[-1][1] - 55
        self.hero = Hero(self, (x, y))
        self.coin = Coin(self, 300, 500)
        self.coins.append(self.coin)
        self.run_game()

    def run_game(self):
        pygame.mixer.music.play(-1)
        run = True
        fon = pygame.transform.scale(self.load_image('gamefon.png'), (self.width, self.height))
        MYEVENTTYPE = pygame.USEREVENT + 1
        pygame.time.set_timer(MYEVENTTYPE, 25)
        while run:
            self.line = 0
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.terminate()
                if event.type == MYEVENTTYPE:
                    if not self.hero.on_platform():
                        self.hero.update((0, 5))
                if event.type == pygame.MOUSEBUTTONDOWN:
                    if self.pause.check_click(event.pos):
                        self.gamepause()
                if event.type == pygame.KEYDOWN and event.key == pygame.K_UP and self.hero.on_platform():
                    self.hero.jump()
                keys = pygame.key.get_pressed()
                if keys[pygame.K_RIGHT]:
                    self.hero.update((10, 0))
                if keys[pygame.K_LEFT]:
                    self.hero.update((-10, 0))
            for el in self.coins:
                if pygame.sprite.collide_mask(el, self.hero):
                    el.rect = el.rect.move(600, 600)
                    el.collect()
            if pygame.sprite.spritecollideany(self.hero, self.flag_group):
                run = False
                self.level_complete()
            if self.hero.rect.y > 600:
                run = False
                self.end_screen()

            self.camera.update(self.hero)
            for sprite in self.all_sprites:
                self.camera.apply(sprite)
                self.tiles_coords = []
                for el in self.tiles_group:
                    self.tiles_coords.append([el.rect.x, el.rect.y])
            self.tiles_y = list(map(lambda x: x[1], self.tiles_coords))
            tiles_y = []
            for el in self.tiles_group:
                if el.under_screen():
                    x, y = el.rect.x, el.rect.y
                    if [x, y] in self.tiles_coords:
                        i = self.tiles_coords.index([x, y])
                        del self.tiles_coords[i]
                    if self.tiles_y.count(el.rect.y) > 1:
                            if not el.rect.y in tiles_y:
                                self.line += 1
                                tiles_y.append(el.rect.y)
                    else:
                        self.line += 1
            if self.line_now != self.line:
                self.line_now = self.line
                for el in self.tiles:
                    el.update(el.n - 1)
                level_x, level_y = self.generate_level(self.LEVEL)

            self.screen.blit(fon, (0, 0))
            self.pause = Pause(self.screen)
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
                        self.new_game()
            pygame.display.flip()
            self.clock.tick(self.fps)

    def end_screen(self):
        pygame.mixer.music.pause()
        fon = pygame.transform.scale(self.load_image('game over 1.jpg'), (self.width, self.height - 200))
        font = pygame.font.Font(None, 40)
        text = font.render(f'Счёт: {self.hero.score}', 1, (0, 0, 0))
        fon.blit(text, (245, 30))
        with open('data/best_result.txt') as f:
            data = f.read()
        if self.hero.score > int(data):
            data = self.hero.score
            with open('data/best_result.txt', 'w') as f_in:
                f_in.write(str(self.hero.score))
        text = font.render(f'Лучший результат: {data}', 1, (0, 0, 0))
        fon.blit(text, (160, 60))
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
                    if self.yes.check_click_change_level(event.pos):
                        self.choice_levels()
                    elif self.no.check_click(event.pos):
                        self.terminate()
                    elif self.yes.check_click(event.pos):
                        self.new_game()

            pygame.display.flip()
            self.clock.tick(self.fps)

    def level_complete(self):
        pygame.mixer.music.pause()
        fon = pygame.transform.scale(self.load_image('level_complete.png'), (self.width, self.height))
        font = pygame.font.Font(None, 60)
        text = font.render('Next level', 1, (242, 227, 139))
        with open('data/best_result.txt') as f:
            data = f.read()
        if self.hero.score > int(data):
            data = self.hero.score
            with open('data/best_result.txt', 'w') as f_in:
                f_in.write(str(self.hero.score))
        fon.blit(text, (400, 550))
        self.screen.blit(fon, (0, 0))
        k = 0
        while True:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.terminate()
                if event.type == pygame.MOUSEBUTTONDOWN:
                    if 400 <= event.pos[0] <= 400 + text.get_width() and 550 <= event.pos[1] <= 550 + text.get_height():
                        self.level += 1
                        self.new_game()
            if k % 3 == 0:
                self.create_particles((random.randrange(0, 600), random.randrange(0, 100)))
            self.par_sprites.update()
            self.screen.blit(fon, (0, 0))
            self.par_sprites.draw(self.screen)
            pygame.display.flip()
            self.clock.tick(self.fps)
            k += 1

    def gamepause(self):
        pygame.mixer.music.pause()
        fon = pygame.transform.scale(self.load_image('gamefon.png'), (self.width, self.height))
        self.screen.blit(fon, (0, 0))
        self.pause.render(self.screen)
        while True:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.terminate()
                if event.type == pygame.MOUSEBUTTONDOWN:
                    if self.pause.check_click2(event.pos) == 1:
                        self.run_game()
                    elif self.pause.check_click2(event.pos) == 2:
                        self.start_screen()
            pygame.display.flip()
            self.clock.tick(self.fps)


class Camera:
    def __init__(self, app):
        self.dy = 0
        self.app = app

    def apply(self, obj):
        if self.dy > 0:
            obj.rect.y += self.dy

    def update(self, target):
        self.dy = -(target.rect.y + target.rect.h // 2 - app.height // 2)


if __name__ == '__main__':
    app = App()
    app.start_screen()
    app.run_game()