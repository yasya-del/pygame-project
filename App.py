import os
import sys
import pygame
import random


class Tile(pygame.sprite.Sprite):
    def __init__(self, app, pos_x, pos_y):
        super().__init__(app.all_sprites, app.tiles_group)
        self.image = app.load_image('platform.png')
        self.rect = self.image.get_rect().move(
            app.tile_width * pos_x, app.tile_height * pos_y)


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
        self.down = False

    def update(self, pos):
        self.rect.x += pos[0]
        self.rect.y += pos[1]

    def jump(self):
        if self.down:
            self.update((0, 60))
        else:
            self.update((0, -60))
        self.down = not self.down

    def on_platform(self):
        pass


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
        self.width, self.height = 400, 600
        self.clock = pygame.time.Clock()
        self.screen = pygame.display.set_mode((self.width, self.height))
        pygame.display.set_caption('Прыгаем по платформам')
        pygame.key.set_repeat(200, 70)
        self.all_sprites = pygame.sprite.Group()
        self.tiles_group = pygame.sprite.Group()
        self.player_group = pygame.sprite.Group()
        self.tile_width = 40
        self.tile_height = 60
        self.tiles = []
        self.generate_level()
        x = self.tiles[6][0] * self.tile_width - 20
        y = self.tiles[6][1] * self.tile_height - 50
        self.hero = Hero(self, (x, y))
        self.fps = 50

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
            x = random.randint(0, 6)
            self.tiles_group.add(Tile(self, x, y))
            self.tiles.append([x, y])

    def run_game(self):
        run = True
        self.game_over = 0
        fon = pygame.transform.scale(self.load_image('gamefon.png'), (self.width, self.height))
        MYEVENTTYPE = pygame.USEREVENT + 1
        pygame.time.set_timer(MYEVENTTYPE, 500)
        while run:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.terminate()
                if event.type == pygame.KEYDOWN and event.key == pygame.K_1:
                    self.game_over += 1
                if event.type == MYEVENTTYPE:
                    self.hero.jump()
            keys = pygame.key.get_pressed()
            if keys[pygame.K_RIGHT]:
                self.hero.update((10, 0))
            if keys[pygame.K_LEFT]:
                self.hero.update((-10, 0))
            if self.game_over == 5:
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
                    return  # начинаем игру
            pygame.display.flip()
            self.clock.tick(self.fps)

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