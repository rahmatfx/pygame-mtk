import pygame
from sys import exit
from random import randint, choice
pygame.init()
clock = pygame.time.Clock()
font1 = pygame.font.Font('assets/slkscr.ttf', 25)
font2 = pygame.font.Font('assets/slkscr.ttf', 20)
quiz_font = pygame.font.Font('assets/cambriamath.ttf', 20)

#Sprites and functions
class Player(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        walk1 = pygame.image.load('assets/run1.png').convert_alpha()
        walk2 = pygame.image.load('assets/run2.png').convert_alpha()
        idle1 = pygame.image.load('assets/idle1.png').convert_alpha()
        scaled_walk1 = pygame.transform.scale(walk1, (120, 155))
        scaled_walk2 = pygame.transform.scale(walk2, (120, 155))
        scaled_idle1 = pygame.transform.scale(idle1, (120, 155))
        self.walk = [scaled_idle1, scaled_walk1, scaled_idle1, scaled_walk2]
        self.player_index = 0

        self.image = self.walk[self.player_index]
        self.rect = self.image.get_rect(midbottom = (100, 400))
        self.gravity = 0


        jump1 = pygame.image.load('assets/jump1.png').convert_alpha()
        self.jump = pygame.transform.scale(jump1, (120, 155))
        

    def player_input(self):
        keys = pygame.key.get_pressed()
        if keys[pygame.K_SPACE] and self.rect.bottom >= 400:
            self.gravity = -22

    def apply_gravity(self):
        self.gravity += 1
        self.rect.y += self.gravity
        if self.rect.bottom >= 400:
            self.rect.bottom = 400
            self.gravity = 0

    def player_animation(self):
        if self.rect.bottom < 400:
            self.image = self.jump
        else:
            self.player_index += 0.1
            if self.player_index > len(self.walk): self.player_index = 0
            self.image = self.walk[int(self.player_index)]    

    def update(self):
        self.player_input()
        self.apply_gravity()
        self.player_animation()

class Obstacle(pygame.sprite.Sprite):
    def __init__(self,type):
        super().__init__()
        if type == 'burung':
            burung1 = pygame.image.load('assets/burung1.png').convert_alpha()
            burung2 = pygame.image.load('assets/burung2.png').convert_alpha()
            scaled_burung1 = pygame.transform.scale(burung1, (100, 100))
            scaled_burung2 = pygame.transform.scale(burung2, (100, 100))
            self.frames = [scaled_burung1, scaled_burung2]
            y_pos = 210
        else:
            kucing1 = pygame.image.load('assets/kucing1.png').convert_alpha()
            kucing2 = pygame.image.load('assets/kucing2.png').convert_alpha()
            scaled_kucing1 = pygame.transform.scale(kucing1, (95, 70))
            scaled_kucing2 = pygame.transform.scale(kucing2, (95, 70))

            self.frames = [scaled_kucing1, scaled_kucing2]
            y_pos = 400

            kucing3 = pygame.image.load('assets/kucing3.png').convert_alpha()
            self.jump = pygame.transform.scale(kucing3, (95, 70))

        self.animation_index = 0
        self.image = self.frames[self.animation_index]
        self.rect = self.image.get_rect(midbottom = (randint(800,900), y_pos))


    def obstacle_animation(self):
        self.animation_index += 0.1
        if self.animation_index >= len(self.frames): self.animation_index = 0
        self.image = self.frames[int(self.animation_index)]

    def update(self):
        self.obstacle_animation()
        self.rect.x -= 8
        self.destroy()
        
    def destroy(self):
        if self.rect.x <= -150:
            self.kill()

def display_score():
    global current_time
    current_time = int(pygame.time.get_ticks()/10)- start_time
    score_surface = font1.render(f'{current_time}', False, 'White')
    score_rect = score_surface.get_rect(center = (360, 50))
    screen.blit(score_surface,score_rect)

def display_quiztimer():
    time_left_ms = max(0, next_quiz_time_ms - pygame.time.get_ticks())
    seconds_left = time_left_ms / 1000.0
    quiztimer_surf = font1.render(f'Quiz in: {seconds_left:.1f}s', False, 'White')
    quiztimer_rect = quiztimer_surf.get_rect(topleft=(10, 10))
    screen.blit(quiztimer_surf, quiztimer_rect)

def health_counter():
    global nyawa, game_state_active
    if pygame.sprite.spritecollide(player.sprite, obstacle_group, True):
        nyawa -= 1
    elif nyawa == 0:
            game_state_active = False

def jawaban(playerAnswer: bool):
    global correctAns, game_state_quiz, current_question, start_time, nyawa, next_quiz_time_ms
    if playerAnswer == current_question[1]:
        correctAns += 1
    else:
        nyawa -= 1    
    paused_amount = int(pygame.time.get_ticks()/10) - pause_start_time
    start_time += paused_amount
    game_state_quiz = False
    current_question = None
    pygame.time.set_timer(quiz_timer, 10000)    
    next_quiz_time_ms = pygame.time.get_ticks() + 10000

def quiz():
    global game_state_quiz, current_question, start_time, pause_start_time, quiz_timer, next_quiz_time_ms
    pygame.draw.rect(screen, 'White', pygame.Rect(0, 0, 720, 480))  
    instruction_surf = quiz_font.render('Jawab benar dengan ↑ atau salah dengan ↓', True, 'Black')
    instruction_rect = instruction_surf.get_rect(center=(360, 130))
    screen.blit(instruction_surf, instruction_rect)

    q_text = current_question[0] if current_question else "Question missing"
    question_surface = quiz_font.render(q_text, True, 'Black')
    question_rect = question_surface.get_rect(center=(360, 200))
    screen.blit(question_surface, question_rect)

    # optional: show remaining seconds
    time_left_units = max(0, quiz_end_time - int(pygame.time.get_ticks()/10))
    seconds_left = time_left_units / 100.0
    timer_surf = quiz_font.render(f'Time left: {seconds_left:.1f}s', True, 'Black')
    timer_rect = timer_surf.get_rect(center=(360, 240))
    screen.blit(timer_surf, timer_rect)

    # end quiz when time's up and resume game without counting quiz time in score
    if int(pygame.time.get_ticks()/10) >= quiz_end_time:
        paused_amount = int(pygame.time.get_ticks()/10) - pause_start_time
        start_time += paused_amount    # don't count quiz time toward score
        game_state_quiz = False
        current_question = None
        pygame.time.set_timer(quiz_timer, 10000)  # re-enable quiz timer  
        next_quiz_time_ms = pygame.time.get_ticks() + 10000


# screen
screen = pygame.display.set_mode((720, 480))

# title and icon
pygame.display.set_caption('Limit Runner')
icon = pygame.image.load('assets/smug1.png').convert_alpha()
pygame.display.set_icon(icon)

# menu assets
menu_bg = pygame.image.load('assets/menu_bg.png').convert_alpha()
menu_bg_rect = menu_bg.get_rect(topleft = (0,0))

menu_text1 = font1.render('Press Enter', False, 'White')
menu_text1_rect = menu_text1.get_rect(center = (520, 340))

menu_text2 = font1.render('to play!', False, 'White')
menu_text2_rect = menu_text2.get_rect(center = (520, 370))

# Game assets
player = pygame.sprite.GroupSingle()
player.add(Player())

obstacle_group = pygame.sprite.Group()

game_bg = pygame.image.load('assets/danau.png').convert_alpha()
scaled_game_bg = pygame.transform.scale(game_bg, (800,490))
game_bg_rect = scaled_game_bg.get_rect(topleft = (0,0))

tanah = pygame.image.load('assets/tanah.png').convert_alpha()
tanah_rect = tanah.get_rect(topleft = (0,0))

tiang = pygame.image.load('assets/tiang.png').convert_alpha()
scaled_tiang = pygame.transform.scale(tiang, (950,635))
tiang_rect = scaled_tiang.get_rect(topleft = (0,-140))

awan1 = pygame.image.load('assets/awan1.png').convert_alpha()
awan1_rect = awan1.get_rect(topleft = (0,0))

awan2 = pygame.image.load('assets/awan2.png').convert_alpha()
awan2_rect = awan2.get_rect(topleft = (0,0))

hati = pygame.image.load('assets/heart.png').convert_alpha()
scaled_hati1 = pygame.transform.scale(hati, (40, 40))
scaled_hati2 = pygame.transform.scale(hati, (40, 40))
scaled_hati3 = pygame.transform.scale(hati, (40, 40))
hati_rect1 = scaled_hati1.get_rect(midbottom = (680,50))
hati_rect2 = scaled_hati2.get_rect(midbottom = (635,50))
hati_rect3 = scaled_hati3.get_rect(midbottom = (590,50))

# Questions
easy_questions = [
    #Level mudah
    ("(B/S) Suatu fungsi adalah relasi dimana setiap input memiliki tepat satu output.", True),
    ("(B/S) Domain fungs f(x) = x² adalah semua bilangan real", True),
    ("(B/S) Fungsi f(x)= √x terdefinisi untuk semua bilangan real.", False),
    ("(B/S) Notasi lim x -> 2 f(x) artinya nilai x yang dimasukkan harus tepat 2.", False),
    ("(B/S) lim x -> 2 (2x + 1) = 7", False),
    ("(B/S) Jika f(2) = 5, maka  pasti 5.", False),
    ("(B/S) Turunan fungsi f(x) di titik x = a menyatakan gradien garis singgung di titik tersebut.", True),
    ("(B/S) Turunan dari fungsi konstan f(x) = 5 adalah 0.", True),
    ("(B/S) Notasi f' (x) menyatakan turunan pertama dari f(x).", True),
    ("(B/S) Integral adalah kebalikan dari turunan.", True),
    ("(B/S) ∫2xdx = x²+ c.", True),
    ("(B/S) Integral tentu hasilnya adalah suatu fungsi", False)]
medium_questions = [ 
    #Level tengah
    ("(B/S) Fungsi f(x) = 1/x-1 kontinu di x = 1", False),
    ("(B/S) Jika lim x->c f(x) dan lim x->c g(x) ada, maka lim x->c [f(x)•g(x)] juga ada", True),
    ("(B/S) Nilai lim x-> 0 sin x/x = 1.", True),
    ("(B/S) Jika f'(c) = 0, f(x) pasti memiliki titik maksimum atau minimum di x = c.", False),
    ("(B/S) Turunan dari f(x) = eˣ adalah eˣ", True),
    ("(B/S) Aturan rantai digunakan untuk mencari turunan dari fungsi komposisi", True),
    ("(B/S) ₐ∫ᵇ f(x)dx = -₆∫ᵃ f(x)dx.", True),
    ("(B/S) Integral ∫(3x² + 2x)dx menghasilkan x³+ x²+ c", True),
    ("(B/S) Integral tentu ₁∫³ 2xdx menyatakan luas daerah di bawah garis y = 2x dari x = 1 sampai x = 3.", True)]
hard_questions = [
    #Level sulit
    ("(B/S) Suatu fungsi dapat memiliki limit di suatu titik dimana fungsi tersebut tidak terdefinisi.", True),
    ("(B/S) Jika lim x->c f(x) = L dan lim x -> c g(x) = L, maka f(c) = g(c).", False),
    ("(B/S) Fungsi f(x) = [x², jika x ≠ 0 dan 1, jika x = 0] kontinu di x = 0", False),
    ("(B/S) Jika sebuah fungsi dapat didiferensialkan di suatu titik, "
    "maka fungsi tersebut pasti kontinu di titik tersebut.", True),
    ("(B/S) Fungsi f(x) = |x-2| memiliki turunan di x = 2.", False),
    ("(B/S) Turunan kedua f′′(x) menyatakan laju perubahan dari f′(x).", True),
    ("(B/S) Menurut teorema dasar kalkulus, d/dx ₐ∫ˣ f(t)dt = f(x)", True),
    ("(B/S) Nilai ₋₁∫¹ x³dx adalah 0", True),
    ("(B/S)  Integral ∫ln xdx adalah contoh integral yang diselesaikan dengan metode substitusi.", False),
    ]

# Timers and counters
obstacle_timer = pygame.USEREVENT + 1
quiz_timer = pygame.USEREVENT + 2
pygame.time.set_timer(obstacle_timer,1800)
pygame.time.set_timer(quiz_timer, 10000)  # quiz every something seconds
next_quiz_time_ms = pygame.time.get_ticks() + 10000

correctAns = 0
nyawa = 3

# Game state
game_state_active = False
game_state_quiz = False
start_time = 0
current_time = 0

tiang_interval = 800           
next_tiang_time = 0

awan_interval = 200
next_awan_time = 0

current_question = None
quiz_duration = 500            # units used by your code (int(pygame.time.get_ticks()/10)), ~5s
quiz_end_time = 0
pause_start_time = 0

#game functions
while True:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
                pygame.quit()
                exit()

        if event.type == pygame.KEYDOWN and game_state_quiz:   #Quiz answer input
            if event.key == pygame.K_UP:
                jawaban(True)
            if event.key == pygame.K_DOWN:
                jawaban(False)

        if game_state_active and not game_state_quiz:
            if event.type == obstacle_timer and game_state_active:
                obstacle_group.add(Obstacle(choice(['kucing', 'kucing', 'burung'])))

        if event.type == quiz_timer:
            if game_state_active and not game_state_quiz:
                game_state_quiz = True
                # pick a random question tuple (text, True/False)
                current_question = randint(0,2)
                if current_question == 0:
                    current_question = choice(easy_questions)
                    easy_questions.remove(current_question)
                    quiz_duration = 1000 
                elif current_question == 1:
                    current_question = choice(medium_questions)
                    medium_questions.remove(current_question)
                    quiz_duration = 2000
                else:
                    current_question = choice(hard_questions)
                    hard_questions.remove(current_question)
                    quiz_duration = 3000                     
                pause_start_time = int(pygame.time.get_ticks()/10)
                quiz_end_time = pause_start_time + quiz_duration
                pygame.time.set_timer(quiz_timer, 0)  # disable quiz timer during quiz

    if game_state_active:                  #Animasi background dan quiz logic
        if game_state_quiz:
            quiz()
        else:
            screen.blit(scaled_game_bg,game_bg_rect)
            screen.blit(tanah,tanah_rect)    
            
            if tiang_active and current_time >= next_tiang_time:    #Animasi tiang
                tiang_active = True
            if tiang_active:
                tiang_rect.x -= 4        # move left
                screen.blit(scaled_tiang, tiang_rect)
                if tiang_rect.right < 0: # went off-screen left
                    tiang_active = False
                    next_tiang_time = current_time + tiang_interval
            
            if awan_active and current_time >= next_awan_time:     #Animasi awan
                awan_active = True
            if awan_active:
                awan1_rect.x -= 1         # move left slower
                awan2_rect.x -= 1
                screen.blit(awan1, awan1_rect)
                screen.blit(awan2, awan2_rect)
                if awan1_rect.right < 0:  # went off-screen left
                    awan_active = False
                    next_awan_time = current_time + awan_interval    

            player.draw(screen)
            player.update()

            obstacle_group.draw(screen)
            obstacle_group.update()

            health_counter()

            if nyawa == 3:   #Menampilkan jumlah nyawa
                screen.blit(scaled_hati1, hati_rect1)
                screen.blit(scaled_hati2, hati_rect2)
                screen.blit(scaled_hati3, hati_rect3)
            elif nyawa == 2:
                screen.blit(scaled_hati1, hati_rect1)
                screen.blit(scaled_hati2, hati_rect2)
            elif nyawa == 1:
                screen.blit(scaled_hati1, hati_rect1)
            else: 
                pass

            display_score()
            display_quiztimer()

            correctAns_surf = font2.render(f'Jawaban Benar: {correctAns}', False, 'White')
            correctAns_rect = correctAns_surf.get_rect(topleft=(10, 40))
            screen.blit(correctAns_surf, correctAns_rect)

    else:
        screen.blit(menu_bg,menu_bg_rect)
        screen.blit(menu_text1, menu_text1_rect)
        screen.blit(menu_text2, menu_text2_rect)
        pygame.time.set_timer(quiz_timer, 0)

        if event.type == pygame.KEYDOWN:          #Game start
            print('mulai main')
            game_state_active = True
            nyawa = 3
            correctAns = 0 
            player.sprite.rect.midbottom = (100,400)
            player.sprite.gravity = 0
            start_time = int(pygame.time.get_ticks()/10)
            
            next_tiang_time = start_time + tiang_interval   # background animation
            tiang_rect.x = 720
            awan1_rect.x = 720
            awan2_rect.x = 720
            tiang_active = True
            awan_active = True

            pygame.time.set_timer(quiz_timer, 10000)  # enable quiz timer
            next_quiz_time_ms = pygame.time.get_ticks() + 10000


    pygame.display.update()
    clock.tick(60)