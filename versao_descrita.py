# ===== Inicialização =====
# ----- Importa e inicia pacotes
import pygame
import random
from os import path
from config import IMG_DIR,FPS, GAME, QUIT
from pygame import mixer 
from assets import *


pygame.init()
pygame.mixer.init()

# ----- Gera tela principal
FPS = 60
Clock = pygame.time.Clock()
 
W, H = 10, 20  #constantes de proporcionalidade
PECA = 38      #tamanho da peça
width = W * PECA  #largura do jogo considerando o tamnaho da peça e a constante
height = H * PECA #altura do jogo considerando o  tamanho e a constante
RES = 750, 760  #tamanho ta tela total
game_res = width, height #area dda tela do jogo
screen = pygame.display.set_mode(RES) #Esta função criará uma superfície de exibição(tamanho) - total
game_screen = pygame.Surface(game_res) #Esta função criará uma superfície de exibição(tamanho) - jogo

pygame.display.set_caption('Tetris')


# ----- Inicia assets
font = pygame.font.SysFont(None, 48)
background = pygame.image.load('assets/img/fundo_inicio_fim2.png').convert()
background_img_small = pygame.transform.scale(background, (width, height))

# Define as cores
cores = [(0, 255, 0), (255, 0, 0), (0, 255, 255), (255, 255, 0), (255, 165, 0), (0, 0, 255), (120, 37, 179)]

# ----- Inicia estruturas de dados
game = True
peca_x = width/2
peca_y = -PECA
peca_speedx = 1
peca_speedy = 1  # Velocidade y da peça (velocidades positivas em y significam que a peça vai se mover para baixo)

# definição dos blocos
class Block(pygame.sprite.Sprite):

# matriz de peças e suas rotações em uma matriz 4x4
    pecas = [
        [[6, 7, 9, 10], [1, 5, 6, 10]],
        [[4, 5, 9, 10], [2, 6, 5, 9]],
        [[1, 5, 9, 13], [4, 5, 6, 7]],
        [[1, 4, 5, 6], [1, 4, 5, 9], [4, 5, 6, 9], [1, 5, 6, 9]],
        [[1, 2, 5, 9], [0, 4, 5, 6], [1, 5, 9, 8], [4, 5, 6, 10]],
        [[1, 2, 6, 10], [5, 6, 7, 9], [2, 6, 10, 11], [3, 5, 6, 7]],
        [[1, 2, 5, 6]],
    ]

#sorteio da peça e da cor
    def __init__(self, x, y):
        pygame.sprite.Sprite.__init__(self) 
#A classe base para seus objetos de jogo visíveis. 
#A classe sprite deve ser usada como uma classe base para os objetos em seu jogo. 
#Ele apenas fornece funções para se manter em diferentes grupos.


        self.x = x  #coordedadas do bloco 
        self.y = y
        self.type = random.randint(0, len(self.pecas) - 1)  #where we randomly pick a type and a color.
        self.color = random.randint(1, len(cores) - 1)  #where we randomly pick a type and a color.
        self.rotation = 0  #rotação 0

#função definidora da imagem na hora
    def image(self):
        return self.pecas[self.type][self.rotation]

# define a rotação da figura de acordo com o resto da divisão
    def rotate(self):
        self.rotation = (self.rotation + 1) % len(self.pecas[self.type])

# definições do jogo
class Tetris:
    W, H = 10, 20 #constatentes de proporção
    x = 0 #local x 
    y = 0 # local y
    PECA = 38 #tamanho da peça
    width = W * PECA
    height = H * PECA
    level = 2  #capacidade de mudar a velocidade no jogo
    score = 0
    state = "start"
    grid = []
    figure = None #não figuras no momento
#criação da tela (matriz)
    def __init__(self, height, width):
        #tela do jogo
        self.width = width
        self.height = height
        self.grid = [] #criacao da matriz
        self.score = 0
        self.state = "start"

        #criação da matriz na tela
        for i in range(height): # de 0 a height - 1
            newline = []        # criação de uma linha para cada valor de altura
            for j in range(width): # de 0 a width - 1
                newline.append(0)  # para cada linha criada na alturar, criar uma coluna  
            self.grid.append(newline)  # criação da matriz


    # Cria uma nova peça pela classe BLOCK e posiciona em x = 3 e y = 0
    def nova_peca(self): 
        self.figure = Block(3, 0)

    # Verifica se a peça atual encosta em algo fixo na tela
    def intersects(self): 
        intersection = False
        for i in range(4): 
            for j in range(4): #matriz 4x4
                if i * 4 + j in self.figure.image(): 
                    if i + self.figure.y > self.height - 1 or \
                            j + self.figure.x > self.width - 1 or \
                            j + self.figure.x < 0 or \
                            self.grid[i + self.figure.y][j + self.figure.x] > 0:
                        intersection = True
                        #game bounds e análise de cor na matriz ( 0 == vazio )
        return intersection

    # Quebra a linha se a fileira horizontal estiver completa
    def break_lines(self): 
        lines = 0 #quantidade de linhas nao vazias
        for i in range(1, self.height): #para cada espaço na altura 
            z = 0  # quantiade de zeros
            for j in range(self.width): # para cada espaço na largura 
                if self.grid[i][j] == 0:  #espaço da matriz
                    z += 1 # quantiade de zeros
            if z == 0: #não há zeros 
                lines += 1 #quantidade de linhas nao vazias
                for i1 in range(i, 1, -1): #a destruição da linha vai do fundo a parte superior 
                    for j in range(self.width): #destruição feita na largura 
                        self.grid[i1][j] = self.grid[i1 - 1][j]
        self.score += lines**2 # Guarda a pontuação

    # velocidade da peça em eixo y 
    # ativada, tambem, quando go_down for verdadeiro/tecla para baixo apertada
    def down(self): 
        self.figure.y += 1 #movimentação
        if self.intersects(): #se a peça bateu em outra
            self.figure.y -= 1 #movimentação 
            self.freeze() #parar

    # Congela a peça quando ela toca no chão ou intersecciona outra peça
    def freeze(self): 
        for i in range(4):
            for j in range(4): #matriz 4x4
                if i * 4 + j in self.figure.image(): #se o espaço em questão estiver sendo ocupado pela peça
                    self.grid[i + self.figure.y][j + self.figure.x] = self.figure.color #o espaço da matriz será preenchido com a cor da peca ao seu formato
        self.break_lines() #se a fileira horizontal for completada
        self.nova_peca() # Cria uma nova peça
        if self.intersects(): #se a peça enconstar no topo
            self.state = "gameover" #novo estado no jogo

    # Move a peça para a esquerda ou para a direita
    # funções relacionadas com "comandos do jogo" no loop do jogo em 
    def side(self, dx): 
        old_x = self.figure.x
        self.figure.x += dx #altera o lugar em que a peça se encontra
        if self.intersects(): # se houver algum contato com outra peça
            self.figure.x = old_x #local da figurá será aquele onde ela encostou 

    # Rotaciona a peça quando aperta espaço
    def rotate(self):
        old_rotation = self.figure.rotation #analisa a rotação
        self.figure.rotate() 
        if self.intersects():
            self.figure.rotation = old_rotation
    

# Depois de tudo definido

# loop de reinício de jogo:

replay = True

while replay:

    # Antes de começar o jogo, uma tela de início deve aparecer para introduzir ao jogador o jogo
    estado = 'inicio'
    if estado == 'inicio': 

        clock = pygame.time.Clock()

        # Carrega o fundo da tela inicial
        #fundo
        background_if = pygame.image.load(path.join(IMG_DIR, 'fundo2.png')).convert_alpha()
        background_rect = background_if.get_rect()
        tamanho_background = pygame.transform.scale(background_if, (width*2,height))  
        #logo
        LOGO = pygame.image.load(path.join(IMG_DIR, 'logo2-removebg-preview.png')).convert_alpha()
        tamanho_logo = pygame.transform.scale(LOGO, (550,400)) #345,300
        logo_rect = LOGO.get_rect()
        logo_x = 90
        logo_y = 150   
        #icone
        ICONE = pygame.image.load(path.join(IMG_DIR, 'icone-removebg-preview.png')).convert_alpha()
        tamanho_icone = pygame.transform.scale(ICONE, (60,60))
        icone_x = 10
        icone_y = 10 
        #texto
        font = pygame.font.SysFont('Britannic Bold', 40, True, False) 
        texto = font.render('Aperte qualquer tecla para começar!', True, (150, 50, 250)) 
        texto_x = 85
        texto_y = 580

        inicio = True
        while inicio:

            # Ajusta a velocidade do jogo.
            clock.tick(FPS)

            # Processa os eventos (mouse, teclado, botão, etc).
            for event in pygame.event.get():
                # Verifica se foi fechado.
                if event.type == pygame.QUIT:
                    state = QUIT
                    inicio = False
                    pygame.quit()

                #para qualquer tecla apertada, a tela sai e vai para as instruçoes
                if event.type == pygame.KEYUP:
                    state = GAME
                    inicio = False

            # A cada loop, redesenha o fundo e os sprites
            screen.blit(tamanho_background, background_rect)
            screen.blit(tamanho_logo, (logo_x,logo_y))
            screen.blit(texto, (texto_x, texto_y)) 
            screen.blit(tamanho_icone, (icone_x,icone_y))

            # Depois de desenhar tudo, inverte o display.
            pygame.display.flip()


    # após inicío, haverá uma tela de instruções
    estado = 'manual'
    if estado == 'manual':
        clock = pygame.time.Clock()

        # Carrega o fundo da tela inicial
        #fundo
        background_if = pygame.image.load(path.join(IMG_DIR, 'fundo2.png')).convert_alpha()
        background_rect = background_if.get_rect()
        tamanho_background = pygame.transform.scale(background_if, (width*2,height))  
        #logo
        LOGO = pygame.image.load(path.join(IMG_DIR, 'logo2-removebg-preview.png')).convert_alpha()
        tamanho_logo = pygame.transform.scale(LOGO, (130,100)) #345,300
        logo_rect = LOGO.get_rect()
        logo_x = 600
        logo_y = 10   
        #icone
        ICONE = pygame.image.load(path.join(IMG_DIR, 'icone-removebg-preview.png')).convert_alpha()
        tamanho_icone = pygame.transform.scale(ICONE, (60,60))
        icone_x = 10
        icone_y = 10
        #texto
        font = pygame.font.SysFont('Britannic Bold', 50, True, False) 
        texto1 = font.render('instruções', True, (150, 50, 250)) 
        texto1_x = 85
        texto1_y = 100 
        #tecla
        TECLA = pygame.image.load(path.join(IMG_DIR, 'teclado.png')).convert_alpha()
        tamanho_tecla = pygame.transform.scale(TECLA, (600,300))
        tecla_x = 80
        tecla_y = 150
        #teclas
        TECLAS = pygame.image.load(path.join(IMG_DIR, 'Desenho sem título-PhotoRoom.png')).convert_alpha()
        tamanho_teclas = pygame.transform.scale(TECLAS, (100,50))
        teclas_x = 80
        teclas_y = 480
        #enter
        ENTER = pygame.image.load(path.join(IMG_DIR, 'enter.png')).convert_alpha()
        tamanho_enter = pygame.transform.scale(ENTER, (100,50))
        enter_x = 80
        enter_y = 540
        #espaço
        ESPACO= pygame.image.load(path.join(IMG_DIR, 'espaço.png')).convert_alpha()
        tamanho_espaco = pygame.transform.scale(ESPACO, (100,50))
        espaco_x = 80
        espaco_y = 600
        #texto2
        font = pygame.font.SysFont('Britannic Bold', 30, True, False) 
        texto2 = font.render('mover esquerda/direita + acelerar', True, (150, 50, 250)) 
        texto2_x = 110
        texto2_y = 500 
        #texto3
        font = pygame.font.SysFont('Britannic Bold', 30, True, False) 
        texto3 = font.render('reiniciar quando acabar', True, (150, 50, 250)) 
        texto3_x = 180
        texto3_y = 560  
        #texto4
        font = pygame.font.SysFont('Britannic Bold', 30, True, False) 
        texto4 = font.render('girar a peça', True, (150, 50, 250)) 
        texto4_x = 180
        texto4_y = 610   
        #texto
        font = pygame.font.SysFont('Britannic Bold', 40, True, False) 
        texto = font.render('Aperte qualquer tecla para começar!', True, (150, 50, 250)) 
        texto_x = 85
        texto_y = 660

        inicio = True
        while inicio:

            # Ajusta a velocidade do jogo.
            clock.tick(FPS)

            # Processa os eventos (mouse, teclado, botão, etc).
            for event in pygame.event.get():
                # Verifica se foi fechado.
                if event.type == pygame.QUIT:
                    state = QUIT
                    inicio = False
                    pygame.quit()

                #´para qualquer tecla apertada, o jogo começa
                if event.type == pygame.KEYUP:
                    state = GAME
                    inicio = False

            # A cada loop, redesenha o fundo e os sprites
            screen.blit(tamanho_background, background_rect)
            screen.blit(tamanho_logo, (logo_x,logo_y))
            screen.blit(texto1, (texto1_x, texto1_y))
            screen.blit(texto, (texto_x, texto_y)) 
            screen.blit(texto2, (texto2_x, texto2_y))
            screen.blit(texto3, (texto3_x, texto3_y))
            screen.blit(texto4, (texto4_x, texto4_y)) 
            screen.blit(tamanho_icone, (icone_x,icone_y))
            screen.blit(tamanho_tecla, (tecla_x,tecla_y))
            screen.blit(tamanho_teclas, (teclas_x,teclas_y))
            screen.blit(tamanho_enter, (enter_x,enter_y))
            screen.blit(tamanho_espaco, (espaco_x,espaco_y))

            # Depois de desenhar tudo, inverte o display.
            pygame.display.flip()


    #após a instruçao, o jogo devera começar 
    # ===== Loop principal =====

    estado = 'continua'
    done = False
    game = Tetris(20, 10)
    counter = 0
    BLACK = (0, 0, 0)
    WHITE = (255, 255, 255)
    go_down = False
 
    # looping da música de fundo
    pygame.mixer.music.load(os.path.join(SND_DIR, 'Tetris.wav'))
    pygame.mixer.music.set_volume(0.7) 
    pygame.mixer.music.play() 
    pygame.mixer.music.play(loops=-1)

    # enquanto o jogo estiver acontecendo
    while not done:
        # a tela será preenchida 
        screen.fill(BLACK) 
        screen.blit(background_img_small, (width, 0))
        if game.figure is None: #momento em que não há peça: jogo começou ou quando uma parou
            game.nova_peca() #adicionar nova peça 
        counter += 1 # a cada looping feito soma-se um
        if counter > 100000:
            counter = 0 

        #capacidade de mudar a velocidade: quanto maior o level, mais rápido a conta será zero, fazneod com que o down seja rápido tambem
        if counter % (FPS // game.level // 2) == 0 or go_down: 
            # se o resto da divisao interira do frames por segundo pelo nivel (2) por dois pela contidade de loopings for zero ou se go_down (tecla de baixo apertada) for True
            if game.state == "start": # se o jogo ja estiver começado
                game.down() # a peça adicionada vai para baixo de acordo com a função estabelecida
        

    # saida
        for event in pygame.event.get():
            # comandos do jogo
            if event.type == pygame.QUIT:
                done = True # DONE
                pygame.quit()

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_DOWN:
                    go_down = True #aumento da velocidade da decida 
                if event.key == pygame.K_LEFT:
                    game.side(-1) #a peça vai um quadrado para a esquerda de acordo com a função
                if event.key == pygame.K_RIGHT:
                    game.side(1) # a peça vai um quadrado para a direita de acordo com a função
                if event.key == pygame.K_SPACE: 
                    game.rotate() #ativa a rotação da peça de acordo com a função
                if event.key == pygame.K_ESCAPE:
                    game.__init__(20, 10) 

    
        if event.type == pygame.KEYUP:
            if event.key == pygame.K_DOWN:
                go_down = False # o aumento da velocidade é pontual, ou seja, só acontece no momento em que a tecla é apertada

#desenhos da peça no jogo
        for i in range(game.height): #para cada espaço na altura
            for j in range(game.width): #para cada espaço da largura
                pygame.draw.rect(screen, WHITE, [game.x + game.PECA * j, game.y + game.PECA * i, game.PECA, game.PECA], 1)
                #na tela do jogo, deverá ser feita as grades do jogo em branco com 1 de largura de acordo com a quantidade de espaço na largura e na altura
                if game.grid[i][j] > 0:
                    pygame.draw.rect(screen, cores[game.grid[i][j]],
[game.x + game.PECA * j + 1, game.y + game.PECA * i + 1, game.PECA - 2, game.PECA - 1])
# definição da cor, do local e do espaçamento quando a peça parar


# no momemnto em que há peças, ou sseja, quando alguma peça estiver sendo movimentada
        if game.figure is not None:
            for i in range(4):
                for j in range(4):
                    p = i*4 + j
                    if p in game.figure.image():
                        pygame.draw.rect(screen, cores[game.figure.color],
                                        [game.x + game.PECA * (j + game.figure.x) + 1,
                                        game.y + game.PECA * (i + game.figure.y) + 1,
                                        game.PECA - 2, game.PECA - 2])
# definição de:
#               cor 
#               desenho da altura 
#               desenho da largura
#               preenchimento de cor na vertical e na horizontal 

# score na tela 
        font = pygame.font.SysFont('Britannia Bold', 40, True, False)
        font1 = pygame.font.SysFont('Britannia Bold', 65, True, False)
        text = font.render("Score: " + str(game.score), True, BLACK)

#game over: o jogo acabou
        screen.blit(text, [400, 0])
        if game.state == "gameover":
            done = True # DONE
        
        pygame.display.flip()
        Clock.tick(FPS)

    #Quando o jogador perder, uma tela de game over deve aparecer
    if done == True:
        clock = pygame.time.Clock()

        # Carrega o fundo da tela inicial
        #fundo
        background_if = pygame.image.load(path.join(IMG_DIR, 'fundo_inicio_fim2.png')).convert_alpha()
        background_rect = background_if.get_rect()
        tamanho_background = pygame.transform.scale(background_if, (width*2,height))  
        #logo
        LOGO = pygame.image.load(path.join(IMG_DIR, 'logo2-removebg-preview.png')).convert_alpha()
        tamanho_logo = pygame.transform.scale(LOGO, (550,400)) #345,300
        logo_rect = LOGO.get_rect()
        logo_x = 90
        logo_y = 50   
        #icone
        ICONE = pygame.image.load(path.join(IMG_DIR, 'icone-removebg-preview.png')).convert_alpha()
        tamanho_icone = pygame.transform.scale(ICONE, (60,60))
        icone_x = 10
        icone_y = 10 
        #texto
        font1 = pygame.font.SysFont('Britannic Bold', 50, True, False) 
        texto1 = font1.render('FIM DE JOGO!', True, (0, 0, 0)) 
        texto1_x = 250
        texto1_y = 540
        #texto
        font2 = pygame.font.SysFont('Britannic Bold', 40, True, False)
        texto2 = font2.render('Aperte ENTER para jogar novamente', True, (0, 0, 0)) 
        texto2_x = 100
        texto2_y = 620
        #texto
        texto3 = font2.render('Aperte ESPAÇO para sair', True, (0, 0, 0)) 
        texto3_x = 170
        texto3_y = 670
        #texto do score
        text = font.render("Score final: " + str(game.score), True, WHITE)

        # ----- Inicia estruturas de dados
        perdeu = True

        # ===== Loop principal =====
        while perdeu:
            # Processa os eventos (mouse, teclado, botão, etc).
            for event in pygame.event.get():
                # Verifica se foi fechado.
                if event.type == pygame.QUIT:
                    
                    state = QUIT
                    perdeu = False
                    pygame.quit()
                
                if event.type == pygame.KEYDOWN:

                    #sair do jogo aperte espaço
                    if event.key == pygame.K_SPACE:
                        done = True
                        estado = 'fim'
                        perdeu = False
                        replay = False
                        pygame.quit()

                    # o jogo deve recomeçar para as instruções caso a pessoa aperte return
                    if event.key == pygame.K_RETURN:
                        done = False
                        estado = 'inicio'
                        perdeu = False
                        replay = True

            screen.blit(tamanho_background, background_rect)
            screen.blit(tamanho_logo, (logo_x,logo_y))
            screen.blit(texto1, (texto1_x, texto1_y)) 
            screen.blit(texto2, (texto2_x, texto2_y))
            screen.blit(texto3, (texto3_x, texto3_y))
            screen.blit(tamanho_icone, (icone_x,icone_y))
            screen.blit(text, [270, 470])
            # ----- Atualiza estado do jogo
            pygame.display.update()  # Mostra o novo frame para o jogador


# ===== Finalização =====
pygame.quit()   # Função do PyGame que finaliza os recursos utilizados