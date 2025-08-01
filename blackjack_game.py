# imports
import os
import random
import pygame

# CONSTANTS
VIRTUAL_WIDTH, VIRTUAL_HEIGHT = 600, 900
FPS = 60
CHIP_SIZE = (160, 160)
CARD_WIDTH, CARD_HEIGHT = 130, 190
BUTTON_Y = 730

# pygame initialization
pygame.init()
pygame.font.init()
# ## geluid
# pygame.mixer.init()

### screen
screen = pygame.display.set_mode((VIRTUAL_WIDTH, VIRTUAL_HEIGHT), pygame.RESIZABLE)
    # check name with client
pygame.display.set_caption("Pygame Blackjack!")
virtual_surface = pygame.Surface((VIRTUAL_WIDTH, VIRTUAL_HEIGHT))
clock = pygame.time.Clock()

### background
def load_assets():
        # chip images
    assets = {}
    assets["background"] = pygame.transform.scale(pygame.image.load("assets/game_design/background.png").convert(), (VIRTUAL_WIDTH, VIRTUAL_HEIGHT))

    for name in ["play", "quit", "hit", "stand"]:
        assets[f"chip_{name}"] = pygame.transform.smoothscale(pygame.image.load(f"assets/game_design/chip_{name}.png"), CHIP_SIZE)

        #  fonts
    assets["font_brawler_bold"] = pygame.font.Font('assets/fonts/Brawler-Bold.ttf', 32)
    assets["font_brawler_bold_xl"] = pygame.font.Font('assets/fonts/Brawler-Bold.ttf', 64)
    assets["font_poppins_bold_xl"] = pygame.font.Font('assets/fonts/Poppins-Bold.ttf', 86)
    assets["font_poppins_bold_larger"] = pygame.font.Font('assets/fonts/Poppins-Bold.ttf', 32)
    assets["font_poppins_bold_smaller"] = pygame.font.Font('assets/fonts/Poppins-Bold.ttf', 30)

        # text colors
    assets["label_color"] = pygame.Color('#020B13')
    assets["value_color"] = pygame.Color('#91672F')
    assets["scores_color"] = pygame.Color('#CA974A')

        # cards
    assets["card_images"] = {}
    suits = ['clubs', 'diamonds', 'hearts', 'spades']
    ranks = ['2', '3', '4', '5', '6', '7', '8', '9', '10', 'J', 'Q', 'K', 'A']
    for suit in suits:
        for rank in ranks:
            card_code = f"{rank.lower()}{suit[0].lower()}"
            path = f"assets/png_card_deck/{suit}/{card_code}.png"
            # error check
            # print(f"Loading: {card_code} -> {path}")
            if os.path.exists(path):
                assets["card_images"][card_code] = pygame.image.load(path).convert_alpha()
            # error check
            # else:
            #     print(f"Image not found: {path}")
    assets["card_backside"] = pygame.image.load('assets/png_card_deck/backside.png').convert_alpha()

assets = load_assets()



### chip images
# chip_play = pygame.transform.smoothscale(pygame.image.load('assets/game_design/chip_play.png'), chip_size)
# chip_quit = pygame.transform.smoothscale(pygame.image.load('assets/game_design/chip_quit.png'), chip_size)
# chip_hit = pygame.transform.smoothscale(pygame.image.load('assets/game_design/chip_hit.png'), chip_size)
# chip_stand = pygame.transform.smoothscale(pygame.image.load('assets/game_design/chip_stand.png'), chip_size)

### fonts
# font_brawler_bold = pygame.font.Font('assets/fonts/Brawler-Bold.ttf', 32)
# font_brawler_regular = pygame.font.Font('assets/fonts/Brawler-Regular.ttf', 32)
# font_poppins_bold_xl = pygame.font.Font('assets/fonts/Poppins-Bold.ttf', 86)
# font_poppins_bold_larger = pygame.font.Font('assets/fonts/Poppins-Bold.ttf', 32)
# font_poppins_bold_smaller = pygame.font.Font('assets/fonts/Poppins-Bold.ttf', 30)
# font_poppins_regular = pygame.font.Font('assets/fonts/Poppins-Regular.ttf', 30)

## text colors
# label_color = pygame.Color('#020B13')
# value_color = pygame.Color('#91672F')
# scores_color = pygame.Color('#CA974A')

### cards
# card_width, card_height = 90, 135
# card_images = {}
# suits = ['clubs', 'diamonds', 'hearts', 'spades']
# ranks = ['2', '3', '4', '5', '6', '7', '8', '9', '10', 'J', 'Q', 'K', 'A']

# card_backside = pygame.image.load('assets/png_card_deck/backside.png').convert_alpha()


# for suit in suits:
#     for rank in ranks:
#         card_code = f"{rank.lower()}{suit[0].lower()}"
#         # card_code = rank.lower() + suit[0].lower()
#         path = f"assets/png_card_deck/{suit}/{card_code}.png"
#         # error check
#         # print(f"Loading: {card_code} -> {path}")
#         if os.path.exists(path):
#             img = pygame.image.load(path).convert_alpha()
#             card_images[card_code] = img
#         # error check
#         else:
#             print(f"Image not found: {path}")

# game state
num_of_decks = 4
active = False
    # win, loss, draw/push
records = [0, 0, 0]
player_score = 0
dealer_score = 0
initial_deal = False
my_hand = []
dealer_hand = []
reveal_dealer = False
hand_active = False
outcome = 0
add_score = False
results = ["", "YOU'RE BUSTED", "YOU WIN!", "DEALER WINS", "IT'S A DRAW"]
game_deck = []


### functions
def build_deck():
    return [rank + suit[0].lower() for rank in ranks for suit in suits] * num_of_decks

# deal cards by selecting randomly from deck, and make function for one card at a time
def deal_cards(current_hand, current_deck):
    card = random.choice(current_deck)
        ## trouble shooting check
    print("Card dealt:", card)
    current_hand.append(card)
    current_deck.remove(card)

    # error check
    # if card.lower() not in card_images:
    #     print("WARNING: No image found for card", card.lower())

    return current_hand, current_deck

# pass in player or dealer hand and get best score possible
def calculate_score(hand):
    # calculate hand score fresh every time, check how many aces we have
    hand_total = 0
    aces_count = 0
    for card in hand:
        rank = card[:-1].upper()
        if rank in ['10', 'J', 'Q', 'K']:
            hand_total += 10
        elif rank == 'A':
            hand_total += 11
            aces_count += 1
        else:
            hand_total += int(rank)
    while hand_total > 21 and aces_count:
        hand_total -= 10
        aces_count -= 1
    return hand_total

# draw cards visually onto screen
def draw_cards(player, dealer, reveal):
    overlap_offset = 30

    # dealer hand
    total_width_dealer = (len(dealer) - 1) * overlap_offset + card_width
    start_x_dealer = (VIRTUAL_WIDTH - total_width_dealer) // 2
    y_dealer = 180
    y_player = 580

    for i, card in enumerate(dealer):
        x = start_x_dealer + i * overlap_offset
        if i == 0 and not reveal:
            card_img = card_backside
        else:
            card_img = card_images.get(card.lower())
        if card_img:
            scaled = pygame.transform.smoothscale(card_img, (card_width, card_height))
            virtual_surface.blit(scaled, (x, y_dealer))
            # error check
            # pygame.draw.rect(virtual_surface, 'red', (x, y_dealer, card_width, card_height))

    # player hand
    total_width_player = (len(player) - 1) * overlap_offset + card_width
    start_x_player = (VIRTUAL_WIDTH - total_width_player) // 2

    for i, card in enumerate(player):
        x = start_x_player + i * overlap_offset
        card_img = card_images.get(card.lower())
        if card_img:
            scaled = pygame.transform.smoothscale(card_img, (card_width, card_height))
            virtual_surface.blit(scaled, (x, y_player))
            # error check
            # pygame.draw.rect(virtual_surface, 'green', (x, y_player, card_width, card_height))

# draw scores for player and dealer on screen
#  check visuals with client
def draw_scores(player, dealer):
    if reveal_dealer:
        virtual_surface.blit(font_poppins_bold_xl.render(str(dealer), True, scores_color), (460, 190))
    virtual_surface.blit(font_poppins_bold_xl.render(str(player), True, scores_color), (460, 590))

# score text
def draw_score_labels(record):
    # margin_x = 35
    # top_y = 18
    # padding = 20
    # num_sections = 3
    # section_width = (VIRTUAL_WIDTH - 2 * margin_x) // num_sections

    labels = ['wins', 'losses', 'draws']

    for i, label in enumerate(labels):
        x = 40 + i * 180
        virtual_surface.blit(font_poppins_bold_larger.render(label, True, label_color), (x, 15))
        virtual_surface.blit(font_poppins_bold_smaller.render(str(record[i]), True, value_color), (x + 85, 15))
        # value = record[i]

        # label_surface = font_poppins_bold_larger.render(f'{label}', True, label_color)
        # value_surface = font_poppins_bold_smaller.render(f'{value}', True, value_color)

        # section_start_x = margin_x + i * section_width

        # label_x = section_start_x
        # virtual_surface.blit(label_surface, (label_x, top_y))

        # value_x = label_x + label_surface.get_width() + padding
        # virtual_surface.blit(value_surface, (value_x, top_y))

# game graphics
def draw_game(act, record, result):
    button_list = []
    x_left = 60
    x_right = VIRTUAL_WIDTH - 60 - chip_size[0]
    y = 730

    # initially on startup (not active) only option is to deal new hand

    if not active or outcome:
        virtual_surface.blit(chip_play, (x_left, y))
        virtual_surface.blit(chip_quit, (x_right, y))
        button_list += [pygame.Rect(x_left, y, *chip_size), pygame.Rect(x_right, y, *chip_size)]
    else: 
        virtual_surface.blit(chip_hit, (x_left, y))
        virtual_surface.blit(chip_stand, (x_right, y))
        button_list += [pygame.Rect(x_left, y, *chip_size), pygame.Rect(x_right, y, *chip_size)]
    if outcome:
        msg = results[outcome]
        txt = font_brawler_bold.render(msg, True, value_color)
        rect = txt.get_rect(center=(VIRTUAL_WIDTH // 2, 400))
        virtual_surface.blit(txt, rect)
    
    draw_score_labels(record)
    return button_list

    # if not act:
    #     virtual_surface.blit(chip_play, (x_left, y))
    #     virtual_surface.blit(chip_quit, (x_right, y))

    #     button_list.append(pygame.Rect(x_left, y, *chip_size))
    #     button_list.append(pygame.Rect(x_right, y, *chip_size))
    # # once game started, shot hit and stand buttons and win/loss records
    # else:
    #     virtual_surface.blit(chip_hit, (x_left, y))
    #     virtual_surface.blit(chip_stand, (x_right, y))

    #     button_list.append(pygame.Rect(x_left, y, *chip_size))
    #     button_list.append(pygame.Rect(x_right, y, *chip_size))

    # draw_score_labels(record)

    # if result != 0:
    #     msg = results[result]
    #     surface = font_brawler_bold.render(msg, True, value_color)
    #     rect = surface.get_rect(center=(VIRTUAL_WIDTH // 2, 400))

    #     virtual_surface.blit(surface, rect)
    #     virtual_surface.blit(chip_play, (x_left, y))
    #     virtual_surface.blit(chip_quit, (x_right, y))

    #     button_list.append(pygame.Rect(x_left, y, *chip_size))
    #     button_list.append(pygame.Rect(x_right, y, *chip_size))
    
    # return button_list

# check endgame conditions function
# def check_endgame(hand_act, deal_score, play_score, result, totals, add):
def check_endgame(hand_act, deal_score, play_score, result, totals, add):
    # check end game scenarios is player has stood, busted or blackjacked
    # result 1-player bust, 2-win, 3-loss, 4-push
    if not hand_act and deal_score >= 17:
        # 1-player bust
        if play_score > 21:
            result = 1
        # 2-win
        elif deal_score < play_score <= 21 or deal_score > 21:
            result = 2
        # 3-loss
        elif play_score < deal_score <= 21:
            result = 3
        else:
        # 4-push (tie)
            result = 4
        if add:
        # win[0], loss[1], draw[2]
            if result in [1, 3]:
                totals[1] += 1
            elif result == 2:
                totals[0] += 1
            else:
                totals[2] += 1
            add = False
    return result, totals, add

# main game loop
run = True

while run:
    clock.tick(fps)
    virtual_surface.fill((0, 0, 0))
    virtual_surface.blit(background, (0,0))
        ### scalable screen
    # scaled_background = pygame.transform.scale(background, (VIRTUAL_WIDTH, VIRTUAL_HEIGHT))
    

    window_witdh, window_height = screen.get_size()
    scale = min(window_witdh / VIRTUAL_WIDTH, window_height / VIRTUAL_HEIGHT)
    scaled_surface = pygame.transform.smoothscale(virtual_surface, (int(VIRTUAL_WIDTH * scale), (int(VIRTUAL_HEIGHT * scale))))
    # scaled_witdh = int(VIRTUAL_WIDTH * scale)
    # scaled_height= int(VIRTUAL_HEIGHT * scale)
    offset_x = (window_witdh - scaled_surface.get_width()) // 2
    offset_y = (window_height - scaled_surface.get_height()) // 2
    buttons = draw_game(active, records, outcome)

    # initial deal to player and dealer
    if initial_deal:
        my_hand = []
        dealer_hand = []
        game_deck = build_deck()
        for _ in range(2):
            my_hand, game_deck = deal_cards(my_hand, game_deck)
            dealer_hand, game_deck = deal_cards(dealer_hand, game_deck)
            ## trouble shooting check
            # print(my_hand, dealer_hand)
        initial_deal = False
    # once game is activated, and dealt, calculate scores and display cards
    if active:
        player_score = calculate_score(my_hand)
        draw_cards(my_hand, dealer_hand, reveal_dealer)
        if reveal_dealer:
            dealer_score = calculate_score(dealer_hand)
            while calculate_score(dealer_hand) < 17:
                dealer_hand, game_deck = deal_cards(dealer_hand, game_deck)
                dealer_score = calculate_score(dealer_hand)
        draw_scores(player_score, dealer_score)

    # event handling, if quit pressed, then exit game
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            run = False
        elif event.type == pygame.MOUSEBUTTONUP:
            if not active:
                if buttons[0].collidepoint(event.pos):
                    active = True
                    initial_deal = True
                    # game_deck = copy.deepcopy(decks * one_deck)
                    # my_hand = []
                    # dealer_hand = []
                    outcome = 0
                    hand_active = True
                    reveal_dealer = False
                    # outcome = 0
                    add_score = True
                elif buttons[1].collidepoint(event.pos):
                    run = False
            else:
                # if player can hit, allow them to draw a card
                if buttons[0].collidepoint(event.pos) and player_score < 21 and hand_active:
                    my_hand, game_deck = deal_cards(my_hand, game_deck)
                # allow player to end turn (stand)
                elif buttons[1].collidepoint(event.pos):
                    reveal_dealer = True
                    hand_active = False
                elif len(buttons) > 2 and buttons[2].collidepoint(event.pos):
                    if buttons[2].collidepoint(event.pos):
                        active = True
                        initial_deal = True
                        # game_deck = copy.deepcopy(decks * one_deck)
                        # my_hand = []
                        # dealer_hand = []
                        outcome = 0
                        hand_active = True
                        reveal_dealer = False
                        # outcome = 0
                        add_score = True
                        # dealer_score = 0
                        # player_score = 0


    # if player busts, automatically end turn - treat like a stand
    if hand_active and player_score >= 21:
        hand_active = False
        reveal_dealer = True

    outcome, records, add_score = check_endgame(hand_active, dealer_score, player_score, outcome, records, add_score)
    


    screen.fill((0,0,0))
    screen.blit(scaled_surface, (offset_x, offset_y))
    pygame.display.flip()

pygame.quit()