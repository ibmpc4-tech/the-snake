from random import choice, randint

import pygame

# Константы для размеров поля и сетки:
SCREEN_WIDTH, SCREEN_HEIGHT = 640, 480
GRID_SIZE = 20
GRID_WIDTH = SCREEN_WIDTH // GRID_SIZE
GRID_HEIGHT = SCREEN_HEIGHT // GRID_SIZE

# Направления движения:
UP = (0, -1)
DOWN = (0, 1)
LEFT = (-1, 0)
RIGHT = (1, 0)

# Цвет фона - чёрный:
BOARD_BACKGROUND_COLOR = (0, 0, 0)

# Цвет границы ячейки
BORDER_COLOR = (93, 216, 228)

# Цвет яблока
APPLE_COLOR = (255, 0, 0)

# Цвет змейки
SNAKE_COLOR = (0, 255, 0)

# Скорость движения змейки:
SPEED = 20

# Настройка игрового окна:
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT), 0, 32)

# Заголовок окна игрового поля:
pygame.display.set_caption('Змейка')

# Настройка времени:
clock = pygame.time.Clock()


class GameObject:
    """Базовый класс для всех игровых объектов.

    Хранит общие атрибуты: позицию на поле и цвет.
    Дочерние классы переопределяют метод draw().
    """

    def __init__(self, body_color=None):
        """Инициализирует объект в центре экрана с заданным цветом."""
        self.position = (
            (SCREEN_WIDTH // GRID_SIZE // 2) * GRID_SIZE,
            (SCREEN_HEIGHT // GRID_SIZE // 2) * GRID_SIZE,
        )
        self.body_color = body_color

    def draw(self):
        """Отрисовывает объект на экране. Переопределяется в дочерних классах."""
        pass


class Apple(GameObject):
    """Класс яблока — еды для змейки.

    Яблоко занимает одну клетку и появляется в случайной точке поля.
    """

    def __init__(self, body_color=APPLE_COLOR):
        """Инициализирует яблоко и задаёт ему случайную позицию."""
        super().__init__(body_color)
        self.randomize_position()

    def randomize_position(self):
        """Задаёт яблоку новую случайную позицию в пределах поля."""
        self.position = (
            randint(0, GRID_WIDTH - 1) * GRID_SIZE,
            randint(0, GRID_HEIGHT - 1) * GRID_SIZE,
        )

    def draw(self):
        """Отрисовывает яблоко как квадрат размером в одну клетку."""
        rect = pygame.Rect(self.position, (GRID_SIZE, GRID_SIZE))
        pygame.draw.rect(screen, self.body_color, rect)
        pygame.draw.rect(screen, BORDER_COLOR, rect, 1)


class Snake(GameObject):
    """Класс змейки — главного игрового объекта.

    Хранит сегменты тела, управляет движением,
    ростом, столкновениями и отрисовкой.
    """

    def __init__(self, body_color=SNAKE_COLOR):
        """Инициализирует змейку в центре поля длиной 1, движение вправо."""
        super().__init__(body_color)
        self.length = 1
        self.positions = [self.position]
        self.direction = RIGHT
        self.next_direction = None
        self.last = None

    def get_head_position(self):
        """Возвращает координаты головы змейки (первый элемент списка)."""
        return self.positions[0]

    def update_direction(self):
        """Обновляет направление движения на основе next_direction."""
        if self.next_direction:
            self.direction = self.next_direction
            self.next_direction = None

    def move(self):
        """Сдвигает змейку на одну клетку в текущем направлении.

        Добавляет новую голову, удаляет хвост при превышении длины.
        Координаты оборачиваются по краям поля (телепортация).
        """
        head_x, head_y = self.get_head_position()
        dir_x, dir_y = self.direction
        new_head = (
            (head_x + dir_x * GRID_SIZE) % SCREEN_WIDTH,
            (head_y + dir_y * GRID_SIZE) % SCREEN_HEIGHT,
        )
        self.positions.insert(0, new_head)

        if len(self.positions) > self.length:
            self.last = self.positions.pop()
        else:
            self.last = None

    def draw(self):
        """Отрисовывает все сегменты змейки и очищает след хвоста."""
        for position in self.positions[:-1]:
            rect = pygame.Rect(position, (GRID_SIZE, GRID_SIZE))
            pygame.draw.rect(screen, self.body_color, rect)
            pygame.draw.rect(screen, BORDER_COLOR, rect, 1)

        # Отрисовка головы змейки
        head_rect = pygame.Rect(self.positions[0], (GRID_SIZE, GRID_SIZE))
        pygame.draw.rect(screen, self.body_color, head_rect)
        pygame.draw.rect(screen, BORDER_COLOR, head_rect, 1)

        # Затирание последнего сегмента
        if self.last:
            last_rect = pygame.Rect(self.last, (GRID_SIZE, GRID_SIZE))
            pygame.draw.rect(screen, BOARD_BACKGROUND_COLOR, last_rect)

    def reset(self):
        """Сбрасывает змейку в начальное состояние после столкновения с собой."""
        self.length = 1
        self.positions = [self.position]
        self.direction = choice([UP, DOWN, LEFT, RIGHT])
        self.next_direction = None
        self.last = None
        screen.fill(BOARD_BACKGROUND_COLOR)


def handle_keys(game_object):
    """Обрабатывает нажатия клавиш и меняет направление змейки.

    Запрещает разворот на 180 градусов за одно нажатие.
    """
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            raise SystemExit
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_UP and game_object.direction != DOWN:
                game_object.next_direction = UP
            elif event.key == pygame.K_DOWN and game_object.direction != UP:
                game_object.next_direction = DOWN
            elif event.key == pygame.K_LEFT and game_object.direction != RIGHT:
                game_object.next_direction = LEFT
            elif event.key == pygame.K_RIGHT and game_object.direction != LEFT:
                game_object.next_direction = RIGHT


def main():
    """Основная функция: инициализация и игровой цикл."""
    pygame.init()

    snake = Snake()
    apple = Apple()

    while True:
        clock.tick(SPEED)

        handle_keys(snake)
        snake.update_direction()
        snake.move()

        # Проверка съеденного яблока
        head_pos = snake.get_head_position()
        if head_pos == apple.position:
            snake.length += 1
            apple.randomize_position()

        # Проверка столкновения змейки с собой
        if head_pos in snake.positions[1:]:
            snake.reset()

        apple.draw()
        snake.draw()

        pygame.display.update()


if __name__ == '__main__':
    main()
