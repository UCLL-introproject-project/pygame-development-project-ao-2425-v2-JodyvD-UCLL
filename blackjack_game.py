# imports
import os
import random
import pygame

# CONSTANTS
VIRTUAL_WIDTH, VIRTUAL_HEIGHT = 600, 900
FPS = 60
NUM_OF_DECKS = 4
CHIP_SIZE = (160, 160)
CARD_WIDTH, CARD_HEIGHT = 130, 190
BUTTON_Y = 730

# pygame initialization
pygame.init()
pygame.font.init()
# ## geluid
pygame.mixer.init()

### screen ###
screen = pygame.display.set_mode((VIRTUAL_WIDTH, VIRTUAL_HEIGHT), pygame.RESIZABLE)
    # check name with client
pygame.display.set_caption("Pygame Blackjack!")
virtual_surface = pygame.Surface((VIRTUAL_WIDTH, VIRTUAL_HEIGHT))
clock = pygame.time.Clock()

### background
def load_assets():
        # chip images
    assets = {}
    assets["background"] = pygame.transform.scale(
        pygame.image.load("assets/game_design/background.png").convert(), (VIRTUAL_WIDTH, VIRTUAL_HEIGHT)
        )

    for name in ["play", "quit", "hit", "stand"]:
        assets[f"chip_{name}"] = pygame.transform.smoothscale(
            pygame.image.load(f"assets/game_design/chip_{name}.png"), CHIP_SIZE
        )

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

    return assets

assets = load_assets()

# sound assets
chip_sound = pygame.mixer.Sound("assets/sounds/poker_chip_sound.mp3")
card_sound = pygame.mixer.Sound("assets/sounds/card_sound.mp3")
result_sound = pygame.mixer.Sound("assets/sounds/neutral_notification_ping.mp3")

# game state
# num_of_decks = 4  >> turned into constant
records = [0, 0, 0] # win, loss, draw/push
results = ["", "YOU'RE BUSTED", "YOU WIN!", "DEALER WINS", "IT'S A DRAW"]
active = False 
initial_deal = False
my_hand = []
dealer_hand = []
hand_active = False
outcome = 0
add_score = False
game_deck = []
player_score = 0
dealer_score = 0
dealer_face_down = True

    ### functions ###
def build_deck():
    suits = ["clubs", "diamonds", "hearts", "spades"]
    ranks = ['2', '3', '4', '5', '6', '7', '8', '9', '10', 'J', 'Q', 'K', 'A']

    return [rank + suit[0].lower() for rank in ranks for suit in suits] * NUM_OF_DECKS

# deal cards by selecting randomly from deck, and make function for one card at a time
def deal_card(current_hand, current_deck):
    card = random.choice(current_deck)
    # error check
    # print("Card dealt:", card)
    current_hand.append(card)
    current_deck.remove(card)
    # error check
    # if card.lower() not in card_images:
    #     print("WARNING: No image found for card", card.lower())
    card_sound.play()

    return current_hand, current_deck

# pass in player or dealer hand and get best score possible
def calculate_score(hand):
    # calculate hand score fresh every time, check how many aces we have
    hand_total = 0
    aces_count = 0
    for card in hand:
        rank = card[:-1].upper()
        if rank in ["10", "J", "Q", "K"]:
            hand_total += 10
        elif rank == "A":
            hand_total += 11
            aces_count += 1
        else:
            hand_total += int(rank)
    while hand_total > 21 and aces_count:
        hand_total -= 10
        aces_count -= 1
    return hand_total

# game graphics
def draw_background():
    virtual_surface.blit(assets["background"], (0,0))

# score text
def draw_score_labels(record):
    labels = ["wins", "losses", "draws"]
    font_label = assets["font_poppins_bold_larger"]
    font_value = assets["font_poppins_bold_smaller"]
    spacing = VIRTUAL_WIDTH // 3

    for i in range(3):
        label_surface = font_label.render(labels[i], True, assets["label_color"])
        value_surface = font_value.render(str(record[i]), True, assets["value_color"])
        center_x = int((i + 0.5) * spacing)
        y = 36
        total_width = label_surface.get_width() + 12 + value_surface.get_width()
        label_x = center_x - total_width // 2
        value_x = label_x + label_surface.get_width() + 12
        virtual_surface.blit(label_surface, (label_x, y))
        virtual_surface.blit(value_surface, (value_x, y))

def draw_play_quit_buttons():
    x_left = 60
    x_right = VIRTUAL_WIDTH - 60 - CHIP_SIZE[0]
    virtual_surface.blit(assets["chip_play"], (x_left, BUTTON_Y))
    virtual_surface.blit(assets["chip_quit"], (x_right, BUTTON_Y))

    return [
        pygame.Rect(x_left, BUTTON_Y, *CHIP_SIZE),
        pygame.Rect(x_right, BUTTON_Y, *CHIP_SIZE)
    ]

def draw_hit_stand_buttons():
    x_left = 60
    x_right = VIRTUAL_WIDTH - 60 - CHIP_SIZE[0]
    virtual_surface.blit(assets["chip_hit"], (x_left, BUTTON_Y))
    virtual_surface.blit(assets["chip_stand"], (x_right, BUTTON_Y))

    return [
        pygame.Rect(x_left, BUTTON_Y, *CHIP_SIZE),
        pygame.Rect(x_right, BUTTON_Y, *CHIP_SIZE)
    ]

# draw cards visually onto screen
def draw_cards(player, dealer, face_down):
    overlap_offset = 45

    # dealer hand
    total_width_dealer = (len(dealer) - 1) * overlap_offset + CARD_WIDTH
    start_x_dealer = (VIRTUAL_WIDTH - total_width_dealer) // 2
    y_dealer = 180

    for i, card in enumerate(dealer):
        x = start_x_dealer + i * overlap_offset
        if i == 0 and face_down:
            card_img = assets["card_backside"]
        else:
            card_img = assets["card_images"].get(card.lower())
        if card_img:
            scaled = pygame.transform.smoothscale(card_img, (CARD_WIDTH, CARD_HEIGHT))
            virtual_surface.blit(scaled, (x, y_dealer))
            # error check
            # pygame.draw.rect(virtual_surface, 'red', (x, y_dealer, CARD_WIDTH, card_height))

    # player hand
    total_width_player = (len(player) - 1) * overlap_offset + CARD_WIDTH
    start_x_player = (VIRTUAL_WIDTH - total_width_player) // 2
    y_player = 470

    for i, card in enumerate(player):
        x = start_x_player + i * overlap_offset
        card_img = assets["card_images"].get(card.lower())
        if card_img:
            scaled = pygame.transform.smoothscale(card_img, (CARD_WIDTH, CARD_HEIGHT))
            virtual_surface.blit(scaled, (x, y_player))
            # error check
            # pygame.draw.rect(virtual_surface, 'green', (x, y_player, CARD_WIDTH, CARD_HEIGHT))

# draw scores for player and dealer on screen
#  check visuals with client
def draw_scores(player, dealer, face_down):
    font_score = assets["font_poppins_bold_xl"]
    # dealer score
    if not face_down:
        y_dealer = 180
        big_card_height = CARD_HEIGHT
        x_score_dealer = VIRTUAL_WIDTH // 2 + 180
        y_score_dealer = y_dealer + big_card_height // 2 - 50
        virtual_surface.blit(font_score.render(str(dealer), True, assets["scores_color"]), (x_score_dealer, y_score_dealer))

    # player score
    y_player = 470
    big_card_height = CARD_HEIGHT
    x_score_player = VIRTUAL_WIDTH // 2 + 180
    y_score_player = y_player + big_card_height // 2 - 50
    virtual_surface.blit(font_score.render(str(player), True, assets["scores_color"]), (x_score_player, y_score_player))

def draw_result_text(result):
    if result:
        msg = results[result]
        font_big = assets["font_brawler_bold_xl"]
        txt = font_big.render(msg, True, assets["value_color"])
        rect = txt.get_rect(center=(VIRTUAL_WIDTH // 2, 420))
        virtual_surface.blit(txt, rect)

def check_endgame():
    # check end game scenarios is player has stood, busted or blackjacked
    # result 1-player bust, 2-win, 3-loss, 4-push
    global outcome, add_score
    if not hand_active and not dealer_face_down:
        # 1-player bust
        if player_score > 21:
            next_outcome = 1
        # 2-win
        elif dealer_score > 21 or player_score > dealer_score:
            next_outcome = 2
        elif player_score < dealer_score:
            next_outcome = 3
        else:
            outcome = 4
        if outcome != next_outcome:
            result_sound.play()
        outcome = next_outcome
        if add_score:
            if outcome == 1 or outcome == 3:
                records[1] += 1
            elif outcome == 2:
                records[0] += 1
            else:
                records[2] += 1
            add_score = False

def start_new_round():
    global active, initial_deal, outcome, hand_active, add_score, dealer_face_down
    active = True
    initial_deal = True
    outcome = 0
    hand_active = True
    add_score = True
    dealer_face_down = True

# main game loop
run = True

while run:
    clock.tick(FPS)
    virtual_surface.fill((0, 0, 0))
    draw_background()
    draw_score_labels(records)
    buttons = []

    if active:
        player_score = calculate_score(my_hand)
        draw_cards(my_hand, dealer_hand, dealer_face_down)
        draw_scores(player_score, dealer_score, dealer_face_down)
        if hand_active and player_score < 21 and not outcome:
            buttons = draw_hit_stand_buttons()
        else: 
            buttons = draw_play_quit_buttons()
    else:
        buttons = draw_play_quit_buttons()

    draw_result_text(outcome)

    # initial deal
    if initial_deal:
        my_hand = []
        dealer_hand = []
        game_deck = build_deck()
        for _ in range(2):
            my_hand, game_deck = deal_card(my_hand, game_deck)
            dealer_hand, game_deck = deal_card(dealer_hand, game_deck)
            ## trouble shooting check
            # print(my_hand, dealer_hand)
        initial_deal = False
        dealer_score = calculate_score(dealer_hand)
        dealer_face_down = True

    # dealer turn after stand/bust
    if active and not hand_active and not dealer_face_down and not outcome:
        dealer_score = calculate_score(dealer_hand)
        while dealer_score < 17:
            dealer_hand, game_deck = deal_card(dealer_hand, game_deck)
            dealer_score = calculate_score(dealer_score)

    # event handling, if quit pressed, then exit game
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            run = False
        elif event.type == pygame.MOUSEBUTTONUP:
            if not active or outcome or (active and not hand_active):
                if buttons and buttons[0].collidepoint(event.pos):
                    chip_sound.play()
                    start_new_round()
                elif buttons and len(buttons) > 1 and buttons[1].collidepoint(event.pos):
                    chip_sound.play()
                    run = False
            else:
                # hit
                if buttons and buttons[0].collidepoint(event.pos) and player_score < 21 and hand_active:
                    chip_sound.play()
                    my_hand, game_deck = deal_card(my_hand, game_deck)
                    if dealer_face_down:
                        dealer_face_down = False
                # stand
                elif buttons and len(buttons) > 1 and buttons[1].collidepoint(event.pos) and hand_active: 
                    chip_sound.play()
                    hand_active = False
                    if dealer_face_down:
                        dealer_face_down = False

    if hand_active and player_score >= 21:
        hand_active = False
        if dealer_face_down:
            dealer_face_down = False

    if active and not hand_active and not dealer_face_down and not outcome:
        dealer_score = calculate_score(dealer_hand)
        while dealer_score < 17:
            dealer_hand, game_deck = deal_card(dealer_hand, game_deck)
            dealer_score = calculate_score(dealer_hand)

    check_endgame()

    window_witdh, window_height = screen.get_size()
    scale = min(window_witdh / VIRTUAL_WIDTH, window_height / VIRTUAL_HEIGHT)
    scaled_surface = pygame.transform.smoothscale(virtual_surface, (int(VIRTUAL_WIDTH * scale), (int(VIRTUAL_HEIGHT * scale))))
    offset_x = (window_witdh - scaled_surface.get_width()) // 2
    offset_y = (window_height - scaled_surface.get_height()) // 2
    screen.fill((0,0,0))
    screen.blit(scaled_surface, (offset_x, offset_y))
    pygame.display.flip()

pygame.quit()