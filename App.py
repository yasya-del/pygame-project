import os
import sys
import pygame


class Hero(pygame.sprite.Sprite):
    def __init__(self, app, pos):
        super().__init__(app.all_sprites, app.player_group)
        self.image = app.load_image("mar.png")
        self.rect = self.image.get_rect()
        self.app = app
        self.mask = pygame.mask.from_surface(self.image)
        self.rect = self.image.get_rect().move(
            self.app.tile_width * pos[0] + 15, self.app.tile_height * pos[1] + 5)

    def update(self):
        pass


class App:
    def __init__(self):
        pygame.init()
        self.width, self.height = 600, 600
        self.clock = pygame.time.Clock()
        self.screen = pygame.display.set_mode((self.width, self.height))
        pygame.display.set_caption('Прыгаем по платформам')
        pygame.key.set_repeat(200, 70)
        self.all_sprites = pygame.sprite.Group()
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


    def run_game(self):
        run = True
        self.game_over = 0
        fon = pygame.transform.scale(self.load_image('gamefon.png'), (self.width, self.height))
        while run:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.terminate()
                if event.type == pygame.KEYDOWN and event.key == pygame.K_1:
                    self.game_over += 1
            if self.game_over == 5:
                run = False
                self.end_screen()

            self.screen.blit(fon, (0, 0))
            self.all_sprites.draw(self.screen)
            pygame.display.flip()
            self.clock.tick(self.fps)

    def start_screen(self):
        intro_text = ["        Правила игры",
                      "В игре вы должны продвигаться вверх по платформам",
                      "Игра заканчивается, когда вы упадёте"
                      ' ', ' ', ' ', ' ', ' ', ' ', '                   Чтобы начать, нажмите на пробел']

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
                elif event.type == pygame.KEYDOWN or \
                        event.type == pygame.MOUSEBUTTONDOWN:
                    return  # начинаем игру
            pygame.display.flip()
            self.clock.tick(self.fps)

    def render(self, screen):
        font = pygame.font.Font(None, 50)

        text = font.render('Continue?', 1, (0, 0, 0))
        pygame.draw.rect(screen, (246, 246, 246), (0, 500, 600, 100), 0)
        screen.blit(text, (200 + (200 - text.get_width()) // 2,
                           500 + (50 - text.get_height()) // 2))

        text_yes = font.render('Yes', 1, (0, 0, 0))
        screen.blit(text_yes, (150 + (150 - text.get_width()) // 2,
                           560 + (40 - text.get_height()) // 2))

        text_no = font.render('No', 1, (0, 0, 0))
        screen.blit(text_no, (330 + (330 - text.get_width()) // 2,
                            560 + (40 - text.get_height()) // 2))

    def end_screen(self):
        fon = pygame.transform.scale(self.load_image('game over 1.jpg'), (self.width, self.height - 100))
        self.render(self.screen)
        self.screen.blit(fon, (0, 0))

        while True:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.terminate()
                elif event.type == pygame.KEYDOWN or event.type == pygame.MOUSEBUTTONDOWN:  # должна быть команда нажатия на yes
                    return  # начинаем новую игру

            pygame.display.flip()
            self.clock.tick(self.fps)


if __name__ == '__main__':
    app = App()
    app.start_screen()
    app.run_game()
    
