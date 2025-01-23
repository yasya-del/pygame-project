import os
import random
import sys
import pygame

D = {'easy': ['easy_level1.txt'],
     'medium': [''],
     'hard': ['']}


class Tile(pygame.sprite.Sprite):
    def __init__(self, app, pos_x, pos_y):
        self.pos_x = pos_x
        self.pos_y = pos_y
        super().__init__(app.all_sprites, app.tiles_group)
        self.image = app.load_image('platform.png')
        self.rect = self.image.get_rect().move(
            app.tile_width * pos_x, app.tile_height * pos_y)

    def under_screen(self):
        return self.rect.y >= 600


class Hero(pygame.sprite.Sprite):
    def __init__(self, app, pos):
        self.app = app
        super().__init__(app.player_group, app.all_sprites)
        self.image = self.app.load_image("bird.jpg")
        self.rect = self.image.get_rect()
        self.mask = pygame.mask.from_surface(self.image)
        self.rect.x = pos[0]
        self.rect.y = pos[1]
        self.height = 57
        self.width = 86

    def update(self, pos):
        self.rect.x += pos[0]
        self.rect.y += pos[1]

    def jump(self):
        self.update((0, -13))


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


class App:
    def __init__(self):
        pygame.init()
        self.width, self.height = 600, 600
        self.clock = pygame.time.Clock()
        self.screen = pygame.display.set_mode((self.width, self.height))
        pygame.display.set_caption('Прыгаем по платформам')
        pygame.mixer.music.load('data/music.mp3')
        # pygame.key.set_repeat(200, 70)
        self.tile_width = 40
        self.tile_height = 60
        self.fps = 60
        self.score = 0
        self.camera = Camera(self)
        self.count_platfroms = 0
        self.dificulty = 'easy'

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
        for y in range(len(level)):
            for x in range(len(level[y])):
                if level[y][x] == '@':
                    self.tiles_group.add(Tile(self, x, y))
                    self.tiles.append([x, y])
        return x, y

    def run_game(self):
        pygame.mixer.music.play(-1)
        self.all_sprites = pygame.sprite.Group()
        self.tiles_group = pygame.sprite.Group()
        self.player_group = pygame.sprite.Group()
        self.tiles = []
        level_x, level_y = self.generate_level(self.load_level('easy_level1.txt'))
        x = self.tiles[9][0] * self.tile_width - 20
        y = self.tiles[9][1] * self.tile_height - 50
        self.hero = Hero(self, (x, y))
        run = True
        self.fon = pygame.transform.scale(self.load_image('gamefon.png'), (self.width, self.height))
        MYEVENTTYPE = pygame.USEREVENT + 1
        pygame.time.set_timer(MYEVENTTYPE, 25)
        while run:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.terminate()
                if event.type == MYEVENTTYPE:
                    if not pygame.sprite.spritecollideany(self.hero, app.tiles_group):
                        self.hero.update((0, 5))
            keys = pygame.key.get_pressed()
            if keys[pygame.K_RIGHT]:
                self.hero.update((10, 0))
            if keys[pygame.K_LEFT]:
                self.hero.update((-10, 0))
            if keys[pygame.K_UP] and pygame.sprite.spritecollideany(self.hero, app.tiles_group):
                self.hero.jump()
            '''self.score += 1
                if self.score >= 100:
                    self.dificulty = 'hard'
                elif self.score >= 50:
                    self.dificulty = 'medium'
                for el in self.tiles_group:
                    if el.under_screen():
                        s = D[self.dificulty]
                        print(s)
                        with open(f'levels/{random.choice(s)}') as f:
                            lvl = []
                            data = f.readlines()
                            lvl.append(data[9 - self.count_platfroms % 10].strip())
                            lvl += ['\n..............\n',
                                    '..............\n',
                                    '..............\n',
                                    '..............\n',
                                    '..............\n',
                                    '..............\n',
                                    '..............\n',
                                    '..............\n',
                                    '..............\n']
                            level_x, level_y = self.generate_level(lvl)
                            self.count_platfroms += 1
                            break'''
            if self.hero.rect.y > 543:
                run = False
                self.end_screen()

            self.camera.update(self.hero)
            for sprite in self.all_sprites:
                self.camera.apply(sprite)

            self.screen.blit(self.fon, (0, 0))
            self.all_sprites.draw(self.screen)
            self.player_group.draw(self.screen)
            self.tiles_group.draw(self.screen)
            pygame.display.flip()
            self.clock.tick(self.fps)

    def start_screen(self):
        intro_text = ["        Правила игры",
                      "В игре вы должны продвигаться вверх",
                      "по платформам",
                      "Игра заканчивается, когда вы упадёте"
                      ' ', ' ', ' ', ' ', ' ', ' ', '    Чтобы начать, нажмите на пробел']

        fon = pygame.transform.scale(self.load_image('fon.jpg'), (self.width, self.height))
        self.screen.blit(fon, (0, 0))
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
                elif event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE:
                    return
            pygame.display.flip()
            self.clock.tick(self.fps)

    def end_screen(self):
        pygame.mixer.music.pause()
        fon = pygame.transform.scale(self.load_image('game over 1.jpg'), (self.width, self.height - 100))
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