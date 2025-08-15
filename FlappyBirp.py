# IMPORTANDO BIBLIOTECAS NECESSÁRIAS
import pygame
import os
import random

# DEFININDO DIMENSÕES DA TELA
LARGURA_TELA = 500
ALTURA_TELA = 800

# CARREGANDO E REDIMENSIONANDO IMAGENS DO JOGO
IMAGEM_CANO = pygame.transform.scale2x(pygame.image.load(os.path.join("imgs", "pipe.png")))
IMAGEM_CHAO = pygame.transform.scale2x(pygame.image.load(os.path.join("imgs", "base.png")))
IMAGEM_BACKGROUND = pygame.transform.scale2x(pygame.image.load(os.path.join("imgs", "bg.png")))
IMAGENS_PASSARO = [
    pygame.transform.scale2x(pygame.image.load(os.path.join("imgs", "bird1.png"))),
    pygame.transform.scale2x(pygame.image.load(os.path.join("imgs", "bird2.png"))),
    pygame.transform.scale2x(pygame.image.load(os.path.join("imgs", "bird3.png"))),
]

# CONFIGURANDO FONTE PARA EXIBIÇÃO DA PONTUAÇÃO
pygame.font.init()
FONTE_PONTOS = pygame.font.SysFont("arial", 50)


# CLASSE DO PÁSSARO
class Passaro:
    imagens = IMAGENS_PASSARO
    # CONFIGURAÇÕES DE MOVIMENTO E ANIMAÇÃO
    ROTACAO_MAXIMA = 25
    VELOCIDADE_ROTACAO = 20
    TEMPO_DA_ANIMACAO = 5

    def __init__(self, x, y):
        # POSIÇÃO INICIAL DO PÁSSARO
        self.x = x
        self.y = y
        self.angulo = 0
        self.velocidade = 0
        self.altura = self.y  # ALTURA INICIAL PARA CONTROLE DE ROTAÇÃO
        self.tempo = 0
        self.contagem_imagem = 0
        self.imagem = self.imagens[0]

    def pular(self):
        # DEFINE VELOCIDADE NEGATIVA PARA PULAR (SUBIR)
        self.velocidade = -10.5
        self.tempo = 0
        self.altura = self.y

    def mover(self):
        # INCREMENTA O TEMPO PARA CÁLCULO DA FÍSICA
        self.tempo += 1
        # CALCULA DESLOCAMENTO COM BASE NA FÍSICA (GRAVIDADE)
        deslocamento = 1.5 * (self.tempo ** 2) + self.velocidade * self.tempo

        # LIMITA O DESLOCAMENTO MÁXIMO PARA BAIXO
        if deslocamento > 16:
            deslocamento = 16
        # AJUSTE FINO QUANDO SUBINDO
        elif deslocamento < 0:
            deslocamento -= 2

        # APLICA O DESLOCAMENTO À POSIÇÃO Y
        self.y += deslocamento

        # CONTROLA A ROTAÇÃO DO PÁSSARO BASEADO NO MOVIMENTO
        if deslocamento < 0 or self.y < self.altura + 50:
            # PÁSSARO SUBINDO - INCLINA PARA CIMA
            if self.angulo < self.ROTACAO_MAXIMA:
                self.angulo = self.ROTACAO_MAXIMA
        else:
            # PÁSSARO DESCENDO - INCLINA PARA BAIXO
            if self.angulo > -90:
                self.angulo -= self.VELOCIDADE_ROTACAO

    def desenhar(self, tela):
        # CONTROLA A ANIMAÇÃO DAS ASAS DO PÁSSARO
        self.contagem_imagem += 1

        # ASA PARA CIMA (frames 0-4)
        if self.contagem_imagem < self.TEMPO_DA_ANIMACAO:
            self.imagem = self.imagens[0]
        # ASA NO MEIO DESCENDO (frames 5-9)
        elif self.contagem_imagem < self.TEMPO_DA_ANIMACAO * 2:
            self.imagem = self.imagens[1]
        # ASA PARA BAIXO (frames 10-14)
        elif self.contagem_imagem < self.TEMPO_DA_ANIMACAO * 3:
            self.imagem = self.imagens[2]
        # ASA NO MEIO SUBINDO (frames 15-19)
        elif self.contagem_imagem < self.TEMPO_DA_ANIMACAO * 4:
            self.imagem = self.imagens[1]
        # REINICIA O CICLO DE ANIMAÇÃO
        else:
            self.imagem = self.imagens[0]
            self.contagem_imagem = 0

        # QUANDO DESCENDO MUITO RÁPIDO, PARA A ANIMAÇÃO DAS ASAS
        if self.angulo <= -80:
            self.imagem = self.imagens[1]
            self.contagem_imagem = self.TEMPO_DA_ANIMACAO * 2

        # ROTACIONA A IMAGEM CONFORME O ÂNGULO
        imagem_rotacionada = pygame.transform.rotate(self.imagem, self.angulo)
        pos_centro = self.imagem.get_rect(topleft=(self.x, self.y)).center
        retangulo = imagem_rotacionada.get_rect(center=pos_centro)
        tela.blit(imagem_rotacionada, retangulo.topleft)

    def get_mask(self):
        # RETORNA MÁSCARA PARA DETECÇÃO DE COLISÃO PRECISA
        return pygame.mask.from_surface(self.imagem)


# CLASSE DOS CANOS (OBSTÁCULOS)
class Cano:
    # CONFIGURAÇÕES DOS CANOS
    DISTANCIA = 200  # ESPAÇO ENTRE CANO SUPERIOR E INFERIOR
    VELOCIDADE = 5  # VELOCIDADE DE MOVIMENTO DOS CANOS

    def __init__(self, x):
        # POSIÇÃO HORIZONTAL DO CANO
        self.x = x
        self.altura = 0
        self.posicao_cano_de_cima = 0
        self.posicao_cano_de_baixo = 0
        # CRIA CANO SUPERIOR (INVERTIDO) E INFERIOR
        self.CANO_DE_CIMA = pygame.transform.flip(IMAGEM_CANO, False, True)
        self.CANO_DE_BAIXO = IMAGEM_CANO
        self.passou = False  # CONTROLA SE PÁSSARO JÁ PASSOU PELO CANO
        self.definir_altura()

    def definir_altura(self):
        # DEFINE ALTURA ALEATÓRIA PARA O BURACO ENTRE OS CANOS
        self.altura = random.randrange(50, 450)
        self.posicao_cano_de_cima = self.altura - self.CANO_DE_CIMA.get_height()
        self.posicao_cano_de_baixo = self.altura + self.DISTANCIA

    def mover(self):
        # MOVE O CANO PARA A ESQUERDA
        self.x -= self.VELOCIDADE

    def desenhar(self, tela):
        # DESENHA OS CANOS SUPERIOR E INFERIOR
        tela.blit(self.CANO_DE_CIMA, (self.x, self.posicao_cano_de_cima))
        tela.blit(self.CANO_DE_BAIXO, (self.x, self.posicao_cano_de_baixo))

    def colidir(self, passaro):
        # VERIFICA COLISÃO ENTRE PÁSSARO E CANOS USANDO MÁSCARAS
        passaro_mask = passaro.get_mask()
        cima_mask = pygame.mask.from_surface(self.CANO_DE_CIMA)
        baixo_mask = pygame.mask.from_surface(self.CANO_DE_BAIXO)

        # CALCULA DISTÂNCIA RELATIVA ENTRE PÁSSARO E CANOS
        distancia_cima = (self.x - passaro.x, self.posicao_cano_de_cima - round(passaro.y))
        distancia_baixo = (self.x - passaro.x, self.posicao_cano_de_baixo - round(passaro.y))

        # VERIFICA SE HOUVE SOBREPOSIÇÃO (COLISÃO)
        ponto_cima = passaro_mask.overlap(cima_mask, distancia_cima)
        ponto_baixo = passaro_mask.overlap(baixo_mask, distancia_baixo)

        return ponto_cima or ponto_baixo


# CLASSE DO CHÃO
class Chao:
    # CONFIGURAÇÕES DO CHÃO
    VELOCIDADE = 5
    LARGURA = IMAGEM_CHAO.get_width()
    IMAGEM = IMAGEM_CHAO

    def __init__(self, y):
        # POSIÇÃO VERTICAL DO CHÃO
        self.y = y
        # DUAS IMAGENS PARA CRIAR EFEITO DE MOVIMENTO CONTÍNUO
        self.x1 = 0
        self.x2 = self.LARGURA

    def mover(self):
        # MOVE AS DUAS IMAGENS DO CHÃO PARA A ESQUERDA
        self.x1 -= self.VELOCIDADE
        self.x2 -= self.VELOCIDADE

        # REPOSICIONA AS IMAGENS PARA CRIAR LOOP INFINITO
        if self.x1 + self.LARGURA < 0:
            self.x1 = self.x2 + self.LARGURA
        if self.x2 + self.LARGURA < 0:
            self.x2 = self.x1 + self.LARGURA

    def desenhar(self, tela):
        # DESENHA AS DUAS IMAGENS DO CHÃO
        tela.blit(self.IMAGEM, (self.x1, self.y))
        tela.blit(self.IMAGEM, (self.x2, self.y))


# FUNÇÃO PARA DESENHAR TODOS OS ELEMENTOS NA TELA
def desenhar_tela(tela, passaros, canos, chao, pontos):
    # DESENHA O FUNDO
    tela.blit(IMAGEM_BACKGROUND, (0, 0))

    # DESENHA TODOS OS PÁSSAROS
    for passaro in passaros:
        passaro.desenhar(tela)

    # DESENHA TODOS OS CANOS
    for cano in canos:
        cano.desenhar(tela)

    # DESENHA A PONTUAÇÃO NO CANTO SUPERIOR DIREITO
    texto = FONTE_PONTOS.render(f"Pontuação: {pontos}", 1, (0, 255, 0))
    tela.blit(texto, (LARGURA_TELA - 10 - texto.get_width(), 10))

    # DESENHA O CHÃO
    chao.desenhar(tela)

    # ATUALIZA A TELA
    pygame.display.update()


# FUNÇÃO PRINCIPAL DO JOGO
def main():
    # INICIALIZA O PYGAME
    pygame.init()

    # CRIA OBJETOS INICIAIS DO JOGO
    passaros = [Passaro(230, 350)]  # LISTA DE PÁSSAROS (PERMITE MÚLTIPLOS)
    chao = Chao(730)  # CHÃO NA PARTE INFERIOR
    canos = [Cano(700)]  # LISTA DE CANOS

    # CONFIGURA A TELA DO JOGO
    tela = pygame.display.set_mode((LARGURA_TELA, ALTURA_TELA))
    pygame.display.set_caption("Flappy Bird")

    # VARIÁVEIS DE CONTROLE DO JOGO
    pontos = 0
    relogio = pygame.time.Clock()
    rodando = True

    # LOOP PRINCIPAL DO JOGO
    while rodando:
        # CONTROLA FPS DO JOGO
        relogio.tick(30)

        # PROCESSA EVENTOS (TECLADO, FECHAR JANELA, ETC.)
        for evento in pygame.event.get():
            if evento.type == pygame.QUIT:
                # SAIR DO JOGO
                rodando = False
                pygame.quit()
                quit()
            if evento.type == pygame.KEYDOWN:
                if evento.key == pygame.K_SPACE:
                    # TECLA ESPAÇO - PÁSSARO PULA
                    for passaro in passaros:
                        passaro.pular()

        # MOVE TODOS OS OBJETOS
        for passaro in passaros:
            passaro.mover()
        chao.mover()

        # CONTROLE DE CANOS E PONTUAÇÃO
        adicionar_cano = False
        remover_canos = []

        # PROCESSA CADA CANO
        for cano in canos:
            # VERIFICA COLISÃO E PONTUAÇÃO PARA CADA PÁSSARO
            for i, passaro in enumerate(passaros):
                if cano.colidir(passaro):
                    # REMOVE PÁSSARO QUE COLIDIU
                    passaros.pop(i)
                if not cano.passou and passaro.x > cano.x:
                    # PÁSSARO PASSOU PELO CANO - MARCA PONTO
                    cano.passou = True
                    adicionar_cano = True

            # MOVE O CANO
            cano.mover()

            # MARCA CANOS PARA REMOÇÃO (SAÍRAM DA TELA)
            if cano.x + cano.CANO_DE_CIMA.get_width() < 0:
                remover_canos.append(cano)

        # ADICIONA NOVO CANO E INCREMENTA PONTUAÇÃO
        if adicionar_cano:
            pontos += 1
            canos.append(Cano(600))

        # REMOVE CANOS QUE SAÍRAM DA TELA
        for cano in remover_canos:
            canos.remove(cano)

        # VERIFICA COLISÃO COM CHÃO E TETO
        for i, passaro in enumerate(passaros):
            if (passaro.y + passaro.imagem.get_height()) >= chao.y or passaro.y < 0:
                # REMOVE PÁSSARO QUE COLIDIU COM CHÃO OU TETO
                passaros.pop(i)

        # DESENHA TODOS OS ELEMENTOS NA TELA
        desenhar_tela(tela, passaros, canos, chao, pontos)


# EXECUTA O JOGO APENAS SE ESTE ARQUIVO FOR EXECUTADO DIRETAMENTE
if __name__ == "__main__":
    main()