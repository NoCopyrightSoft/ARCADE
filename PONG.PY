import pygame
import random
import time

# Inicializar pygame
pygame.init()

# Configuración de pantalla
WIDTH, HEIGHT = 800, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("PONG - Nivel Dios")

# Colores
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)

# Configuración de la pelota
ball_radius = 10
ball_x, ball_y = WIDTH // 2, HEIGHT // 2
ball_speed = 6
ball_dx, ball_dy = ball_speed * random.choice((1, -1)), ball_speed * random.choice((1, -1))

# Configuración de las palas
paddle_width, paddle_height = 10, 100
player_x, player_y = 20, HEIGHT // 2 - paddle_height // 2
ai_x, ai_y = WIDTH - 30, HEIGHT // 2 - paddle_height // 2
paddle_speed = 8
ai_speed = 7  # Aumentado para mejorar la dificultad

# Puntuación
player_score = 0
ai_score = 0
font = pygame.font.Font(None, 50)
title_font = pygame.font.Font(None, 80)

# Reloj para controlar FPS
clock = pygame.time.Clock()


def draw_objects():
    """Dibuja los elementos en pantalla"""
    screen.fill(BLACK)
    pygame.draw.rect(screen, WHITE, (player_x, player_y, paddle_width, paddle_height))
    pygame.draw.rect(screen, WHITE, (ai_x, ai_y, paddle_width, paddle_height))
    pygame.draw.circle(screen, WHITE, (ball_x, ball_y), ball_radius)
    score_text = font.render(f"{player_score} - {ai_score}", True, WHITE)
    screen.blit(score_text, (WIDTH // 2 - 40, 20))
    pygame.display.flip()


def show_start_screen():
    """Muestra la pantalla de inicio con 'PONG' y 'Click to start'"""
    screen.fill(BLACK)
    title_text = title_font.render("PONG", True, WHITE)
    screen.blit(title_text, (WIDTH // 2 - 90, HEIGHT // 3))

    start_text = font.render("Click to start", True, WHITE)
    screen.blit(start_text, (WIDTH // 2 - 100, HEIGHT // 2))
    
    pygame.display.flip()

    # Esperar clic para iniciar
    waiting = True
    while waiting:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                exit()
            if event.type == pygame.MOUSEBUTTONDOWN:
                waiting = False


def reset_ball():
    """Reinicia la pelota en el centro y la pausa un momento"""
    global ball_x, ball_y, ball_dx, ball_dy, ball_speed
    ball_x, ball_y = WIDTH // 2, HEIGHT // 2
    ball_speed = 6  # Restablece la velocidad
    ball_dx = ball_speed * random.choice((1, -1))
    ball_dy = ball_speed * random.choice((1, -1))

    draw_objects()
    pygame.display.flip()
    time.sleep(1)  # Pausa tras un gol


# Mostrar pantalla de inicio antes de empezar
show_start_screen()

# Bucle principal
running = True
while running:
    clock.tick(60)  # 60 FPS

    # Capturar eventos
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    # Controles del jugador
    keys = pygame.key.get_pressed()
    if keys[pygame.K_w] and player_y > 0:
        player_y -= paddle_speed
    if keys[pygame.K_s] and player_y < HEIGHT - paddle_height:
        player_y += paddle_speed

    # IA "nivel Dios" con movimiento más natural
    ai_target = ball_y - paddle_height // 2
    if ai_y < ai_target:
        ai_y += min(ai_speed, ai_target - ai_y)
    elif ai_y > ai_target:
        ai_y -= min(ai_speed, ai_y - ai_target)

    # Mover la pelota
    ball_x += ball_dx
    ball_y += ball_dy

    # Evitar trayectorias completamente horizontales
    if abs(ball_dx) < 3:
        ball_dx += random.choice((-1, 1)) * 2

    # Rebote en la parte superior e inferior
    if ball_y - ball_radius <= 0 or ball_y + ball_radius >= HEIGHT:
        ball_dy *= -1

    # Colisión con la pala del jugador
    if player_x < ball_x < player_x + paddle_width and player_y < ball_y < player_y + paddle_height:
        ball_dx *= -1  # Cambia dirección en X
        offset = (ball_y - player_y) - (paddle_height / 2)
        ball_dy += offset * 0.2  # Rebote con ángulo según impacto

    # Colisión con la pala de la IA
    if ai_x < ball_x < ai_x + paddle_width and ai_y < ball_y < ai_y + paddle_height:
        ball_dx *= -1  # Cambia dirección en X
        offset = (ball_y - ai_y) - (paddle_height / 2)
        ball_dy += offset * 0.2  # Rebote con ángulo según impacto

    # Aumentar velocidad de la pelota con el tiempo
    ball_speed += 0.001
    ball_dx = (ball_speed if ball_dx > 0 else -ball_speed)
    ball_dy = (ball_speed if ball_dy > 0 else -ball_speed)

    # Puntos cuando la pelota sale de la pantalla
    if ball_x < 0:
        ai_score += 1
        reset_ball()
    if ball_x > WIDTH:
        player_score += 1
        reset_ball()

    draw_objects()

pygame.quit()
