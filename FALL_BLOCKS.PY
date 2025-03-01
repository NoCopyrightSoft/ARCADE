import pygame
import math
import random

# --- CONFIGURACIÓN INICIAL ---
WIDTH, HEIGHT = 800, 600
FPS = 60
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
BLUE = (0, 0, 255)
YELLOW = (255, 255, 0)
ROSE = (255, 204, 204)
GREEN = ( 0, 255, 0)
RED = (255, 0, 0)
ORANGE = (255, 165, 0)
PURPLE = (128, 0, 128)
PINK = (255, 192, 203)
GRAY = (128, 128, 128)
CYAN = (0, 255, 255)
MAGENTA = (255, 0, 255)

# --- CLASE LANZADOR ---
class Launcher:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.speed = 2  #  Velocidad de movimiento
        self.line_length = 25  #  Longitud de la línea de apuntado

    def move(self, direction):
        """Mover el lanzador a la izquierda o derecha."""
        if direction == "left" and self.x > 50:
            self.x -= self.speed
        elif direction == "right" and self.x < WIDTH - 50:
            self.x += self.speed

    def draw(self, screen):
        """Dibujar el lanzador como un círculo y una línea de apuntado."""
        pygame.draw.circle(screen, WHITE, (self.x, self.y), 12)  #  Círculo del lanzador
        pygame.draw.line(screen, WHITE, (self.x, self.y), (self.x, self.y - self.line_length), 8)  #  Línea de apuntado

# --- CLASE PELOTA ---
class Ball(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        self.image = pygame.Surface((7, 7))
        self.image.fill(WHITE)
        self.rect = self.image.get_rect(center=(x, y))
        self.speed_y = -10  #  Movimiento recto hacia arriba

    def update(self):
        """Actualizar la posición de la bola."""
        self.rect.y += self.speed_y  

        #  Eliminar la bola si sale de la pantalla
        if self.rect.bottom < 0:
            self.kill()

# --- CLASE BLOQUE ---
class Block(pygame.sprite.Sprite):
    def __init__(self, x, y, resistance):
        super().__init__()
        self.resistance = resistance
        colors = [BLUE, YELLOW, ROSE, GREEN, RED, ORANGE, PURPLE, PINK, GRAY, CYAN, MAGENTA]  
        self.image = pygame.Surface((30, 30))
        self.image.fill(colors[min(resistance - 1, 10)])
        self.rect = self.image.get_rect(topleft=(x, y))
        self.font = pygame.font.Font(None, 20)
        self.shake_timer = 0

    def hit(self):
        """Reduce la resistencia del bloque y lo destruye si llega a 0."""
        self.resistance -= 1
        self.shake_timer = 500
        
        if self.resistance <= 0:
            self.kill()
            
    def draw(self, screen):
        """Dibuja el bloque con su resistencia en el centro."""
        screen.blit(self.image, self.rect.topleft)
        text = self.font.render(str(self.resistance), True, BLACK)
        text_rect = text.get_rect(center=self.rect.center)
        screen.blit(text, text_rect)
        
    def update (self):
        """Sacudir el bloque si ha sido golpeado recientemente"""
        if self.shake_timer >= 0:
            self.rect.x += random.choice([-5, 5])  # 🔹 Mover ligeramente el bloque
            self.shake_timer -= 1
            if self.shake_timer == 0:
                self.rect.x -= random.choice([-5, 5])  # 🔹 Volver a su posición original

# CLASE POWER UP
class PowerUp(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        self.image = pygame.Surface((20, 20), pygame.SRCALPHA)  #  Tamaño doble que las bolas normales
        pygame.draw.circle(self.image, WHITE, (10, 10), 10)  #  Bola blanca
        self.rect = self.image.get_rect(center=(x, y))

# --- CLASE PRINCIPAL DEL JUEGO ---
class Game:
    def __init__(self):
        """Inicializa el juego y la ventana."""
        pygame.init()
        self.screen = pygame.display.set_mode((WIDTH, HEIGHT))
        pygame.display.set_caption("FALL BLOCKS")
        self.clock = pygame.time.Clock()
        self.running = True
        self.launcher = Launcher(WIDTH // 2, HEIGHT - 50)
        self.balls = pygame.sprite.Group()
        self.blocks = pygame.sprite.Group()
        self.powerups = pygame.sprite.Group()
        self.create_blocks()
        self.turn = "IA"
        self.turn_active = False  
        self.turn_delay = 60
        self.player_balls = 10
        self.ai_balls = 10
        self.shooting = False  
        self.balls_to_shoot = 0
        self.shoot_timer = 0  
        self.player_score = 0
        self.ai_score = 0
        self.powerup_timer = 0  #  Contador para la generación de power-ups
        self.powerup_interval = 10 * 60  #  10 segundos en frames (asumiendo 60 FPS)
        self.block_move_counter = 0  #  Contador de turnos antes de mover los bloques
        self.history = []  # 🔹 Lista para almacenar los últimos 5 resultados

    def create_blocks(self):
        """Crea bloques y genera power-ups en lugares aleatorios."""
        for row in range(2):
            for col in range(20):
                x = 50 + col * 35
                y = 50 + row * 35
                resistance = random.randint(1, 5)
                block = Block(x, y, resistance)
                self.blocks.add(block)

        #  Generar power-ups en posiciones aleatorias
        for _ in range(5):  #  Se generan 3 power-ups
            x = random.randint(50, WIDTH - 50)
            y = random.randint(100, HEIGHT // 2)  #  No aparecen en la parte inferior
            powerup = PowerUp(x, y)
            self.powerups.add(powerup)

    def handle_events(self):
        """Maneja los eventos del juego."""
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE and self.turn == "Player" and not self.turn_active and not self.shooting:
                    self.shoot_ball()
                   
        # 🔹 Bloquear movimiento si hay bolas en pantalla
        if len(self.balls) > 0:
            return
                    
        #  Solo permitir movimiento si no está disparando
        if self.turn == "Player":
            keys = pygame.key.get_pressed()
            if keys[pygame.K_LEFT]:
                self.launcher.move("left")
            if keys[pygame.K_RIGHT]:
                self.launcher.move("right")

    def shoot_ball(self):
        """Dispara bolas en línea recta hacia arriba."""
        if self.turn == "Player":
            self.balls_to_shoot = self.player_balls
            self.shooting = True
        else:
            self.balls_to_shoot = self.ai_balls
            self.shooting = True

        self.shoot_timer = 10  

    def is_block_reachable(self, block):
        """Verifica si un bloque no está bloqueado por otros."""
        if not self.blocks:  #  Evitar error si no hay bloques
            return False  

        dx = block.rect.centerx - self.launcher.x
        dy = block.rect.centery - self.launcher.y
        angle = math.atan2(dy, dx)

        steps = 10
        for i in range(1, steps + 1):
            check_x = int(self.launcher.x + (dx / steps) * i)
            check_y = int(self.launcher.y + (dy / steps) * i)

            for other_block in self.blocks:
                if other_block != block and other_block.rect.collidepoint(check_x, check_y):
                    return False  #  Bloque no alcanzable

        return True  #  Si no hay bloqueos, es alcanzable
 
    def handle_shooting(self):
        """Dispara una bola cada cierto tiempo hasta que termine la ráfaga."""
        if self.shooting and self.balls_to_shoot > 0:
            self.shoot_timer -= 1  
            if self.shoot_timer <= 0:
                ball = Ball(self.launcher.x, self.launcher.y - 10)  #  Disparo desde el lanzador
                self.balls.add(ball)
                self.balls_to_shoot -= 1
                self.shoot_timer = 10  

            if self.balls_to_shoot == 0:
                self.shooting = False
                self.turn_active = True  

    def ai_turn(self):
        """La IA mueve su lanzador en X y dispara en línea recta."""
        target_x = None  
    
        #  Priorizar power-ups accesibles
        for powerup in self.powerups:
            target_x = powerup.rect.centerx
            break  

        #  Si no hay power-ups, buscar el bloque más débil accesible
        if not target_x and self.blocks:
            target_x = min(self.blocks, key=lambda block: block.resistance).rect.centerx

        #  Mover el lanzador hacia el objetivo
        if target_x:
            if self.launcher.x < target_x:
                self.launcher.move("right")
            elif self.launcher.x > target_x:
                self.launcher.move("left")

        #  Disparar cuando esté alineado con el objetivo
        if abs(self.launcher.x - target_x) < 5:
            self.shoot_ball()
            self.turn_active = True  

    def add_new_blocks(self):
        """Genera nuevos bloques en la parte superior alineados con los bloques existentes."""
        existing_x_positions = {block.rect.x for block in self.blocks}  # 🔹 Obtener posiciones X de bloques existentes
        num_new_blocks = random.randint(3, 9)  # 🔹 Cantidad aleatoria de nuevos bloques
        
        # 🔹 Determinar la fila más alta ocupada actualmente
        highest_y = min((block.rect.y for block in self.blocks), default=50)  

        new_y = highest_y - 35  # 🔹 Colocar los nuevos bloques en la fila superior

        for _ in range(num_new_blocks):
            if existing_x_positions:  
                x = random.choice(list(existing_x_positions))  # 🔹 Elegir posición alineada con los bloques inferiores
            else:  
                x = random.randint(50, WIDTH - 50)  # 🔹 Si no hay bloques, generar en cualquier posición

            new_block = Block(x, new_y, random.randint(1, 5))  # 🔹 Crear bloque con resistencia aleatoria
            self.blocks.add(new_block)

    def move_blocks_down(self):
        """Mueve los bloques una unidad hacia abajo y verifica si han alcanzado el límite."""
        for block in self.blocks:
            block.rect.y += 25  # 🔹 Baja una unidad (ajustable)
        for powerups in self.powerups:
            powerups.rect.y += 20  # 🔹 Baja una unidad (ajustable)

        # 🔹 Verificar si algún bloque tocó el fondo
        if max(block.rect.bottom for block in self.blocks) >= HEIGHT - 70:
            if self.player_score > self.ai_score:
                loser = "IA"
            elif self.player_score < self.ai_score:
                loser = "Player"
            else:
                loser = None  # 🔹 Empate si los puntajes son iguales

            print(f"Fin del juego - Perdedor: {loser}")  # 🔹 Depuración
            self.show_winner_screen(loser)  
            self.running = False  # 🔹 Detener el bucle principal

    def switch_turn(self):
        """Cambia el turno entre el jugador y la IA de manera segura."""
        pygame.time.delay(50)
        self.move_blocks_down()
        
        self.block_move_counter += 1  # 🔹 Contar los turnos
        if self.block_move_counter >= 1:  # 🔹 Cada 2 turnos, añadir nuevos bloques
            self.add_new_blocks()
            self.block_move_counter = 0 
        
        if self.turn == "Player":
            self.turn = "IA"
        else:
            self.turn = "Player"

        self.turn_active = False  
        self.shooting = False  
        self.turn_delay = 60  
    
    def show_winner_screen(self, loser=None):
        """Muestra el ganador y regresa a la pantalla de inicio después de 3 segundos."""
        self.screen.fill(BLACK)
        font = pygame.font.Font(None, 50)
        
        if loser:
            if loser == "Player":
                result_text = "Tú pierdes UwU"
            else:
                result_text = "Tú ganas ^_~"
        else:
            result_text = "Empate X_X"
            
        # 🔹 Guardar el resultado en el historial
        self.history.append(result_text)
        if len(self.history) > 5:  # 🔹 Mantener solo los últimos 5 resultados
            self.history.pop(0)


        text = font.render(result_text, True, WHITE)
        text_rect = text.get_rect(center=(WIDTH // 2, HEIGHT // 2))
        self.screen.blit(text, text_rect)
        pygame.display.flip()

        pygame.time.delay(3000)  
        self.reset_game()  # 🔹 Reiniciar correctamente el juego
        self.run()  # 🔹 Volver a ejecutar el bucle principal

    def show_start_screen(self):
        """Muestra la pantalla de inicio con el mensaje 'Clic para empezar'."""
        self.screen.fill(BLACK)
        font_title = pygame.font.Font(None, 70)
        font_subtitle = pygame.font.Font(None, 30)
        font_history = pygame.font.Font(None, 25)

        title_text = font_title.render("FALL BLOCKS", True, WHITE)
        title_rect = title_text.get_rect(center=(WIDTH // 2, HEIGHT // 3))
        self.screen.blit(title_text, title_rect)

        subtitle_text = font_subtitle.render("Clic para empezar", True, WHITE)
        subtitle_rect = subtitle_text.get_rect(center=(WIDTH // 2, HEIGHT // 2))
        self.screen.blit(subtitle_text, subtitle_rect)
        
        # 🔹 Mostrar historial en la parte inferior izquierda
        y_offset = HEIGHT - 150  
        for i, result in enumerate(reversed(self.history)):
            history_text = font_history.render(f"Partida {i + 1}: {result}", True, WHITE)
            self.screen.blit(history_text, (10, y_offset))
            y_offset += 25  # 🔹 Espacio entre líneas

        pygame.display.flip()
        
        pygame.event.clear()  


        #  Esperar a que el usuario haga clic para iniciar
        waiting = True
        while waiting:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    exit()
                if event.type == pygame.MOUSEBUTTONDOWN:  #  Empezar el juego al hacer clic
                    waiting = False

        self.reset_game()

    def spawn_powerup(self):
        """Genera un power-up en una posición válida sin superposición."""
        if len(self.powerups) >= 5:  #  No más de 5 power-ups a la vez
            return  

        block = random.choice(list(self.blocks))  # 🔹 Seleccionar un bloque aleatorio
        x, y = block.rect.centerx, block.rect.centery  # 🔹 Centrar el power-up en el bloque

        powerup = PowerUp(x, y)
        self.powerups.add(powerup)

    def reset_game(self):
        """Reinicia el juego y los puntajes para empezar desde cero."""
        self.balls.empty()
        self.blocks.empty()
        self.powerups.empty()
        self.create_blocks()
        
        self.player_balls = 10
        self.ai_balls = 10
        self.player_score = 0
        self.ai_score = 0
        
        self.turn = "IA"
        self.turn_active = False
        self.turn_delay = 60
        self.block_move_counter = 0
        self.running = True

    def update(self):
        """Actualizar la lógica del juego y contar turnos fallidos correctamente."""
        self.balls.update()
        self.powerups.update()
        self.handle_shooting()
        
        #  Manejar temporizador de power-ups
        self.powerup_timer += 1  
        if self.powerup_timer >= self.powerup_interval:
            self.spawn_powerup()
            self.powerup_timer = 0  #  Reiniciar el temporizador


        #  Detectar colisión entre pelotas y bloques
        collisions = pygame.sprite.groupcollide(self.balls, self.blocks, False, False)
        balls_to_remove = []
        
        for ball, hit_blocks in collisions.items():
            for block in hit_blocks:
                block.hit()
                if block.resistance <= 0:
                    block.kill()
                    if self.turn == "Player":
                        self.player_score += 1  
                    else:
                        self.ai_score += 1  
                balls_to_remove.append(ball)

        for ball in balls_to_remove:
            ball.kill()
    
        #  Detectar colisión entre pelotas y power-ups
        powerup_collisions = pygame.sprite.groupcollide(self.balls, self.powerups, False, True)

        for ball, powerups in powerup_collisions.items():  #  Iterar correctamente sobre los power-ups
            for powerup in powerups:
                if self.turn == "Player":
                    self.player_balls += 1
                else:
                    self.ai_balls += 1

        if not self.blocks:
            self.show_winner_screen()
            return  

        if self.turn == "IA" and not self.turn_active and not self.shooting:
            self.ai_turn()

        if self.turn_active and not self.balls and not self.shooting and self.turn_delay <= 0:
            self.switch_turn()

        self.turn_delay -= 1  

    def draw(self):
        """Dibujar en la pantalla."""
        self.screen.fill(BLACK)
        self.launcher.draw(self.screen)
        self.balls.draw(self.screen)

        for block in self.blocks:
            block.draw(self.screen)

        self.powerups.draw(self.screen)  #  Dibujar los power-ups correctamente

        font = pygame.font.Font(None, 30)
        ball_count = self.player_balls if self.turn == "Player" else self.ai_balls
        ball_text = font.render(f"Bolas: {ball_count}", True, WHITE)
        self.screen.blit(ball_text, (self.launcher.x + 30, self.launcher.y - 20))

        turn_text = font.render(f"Turno: {self.turn}", True, WHITE)
        self.screen.blit(turn_text, (10, 10))
        
        #  Mostrar puntajes (bloques destruidos por cada jugador)
        score_text = font.render(f"Jugador: {self.player_score} | IA: {self.ai_score}", True, WHITE)
        self.screen.blit(score_text, (10, 40))

        pygame.display.flip()

    def run(self):
        self.show_start_screen()  #  Mostrar la pantalla de inicio antes de empezar
        """Bucle principal del juego."""
        self.player_balls = 10
        self.ai_balls = 10  

        while self.running:
            self.handle_events()
            self.update()
            self.draw()
            self.clock.tick(FPS)

        pygame.quit()

# --- EJECUCIÓN ---
if __name__ == "__main__":
    game = Game()
    game.run()
