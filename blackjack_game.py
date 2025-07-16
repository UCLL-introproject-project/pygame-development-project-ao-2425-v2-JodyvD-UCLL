# imports
import copy
import random
import pygame

# game variables
pygame.init()
### cards
cards = ['2', '3', '4', '5', '6', '7', '8', '9', '10', 'J', 'Q', 'K', 'A']
one_deck = 4 * cards
decks = 4

game_denk = copy.deepcopy(decks * one_deck)
# print(game_denk)

### display
WIDTH = 600
HEIGHT = 900
screen = pygame.display.set_mode([ WIDTH, HEIGHT])
    # check name with client
pygame.display.set_caption("Pygame Blackjack!")         
fps = 60
timer = pygame.time.Clock()
pygame.font.init()
    # check font with client
font = pygame.font.Font('freesansbold.ttf', 44)


# main game loop
run = True
while run:
    # run at framerate (fps) and bg colour
    timer.tick(fps)
        # check bg colour with client
    screen.fill('black')

    # event handling >> if quit pressed then exit game
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            run = False

    pygame.display.flip()
pygame.quit()