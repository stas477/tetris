import random # импортирование библиотеки для рандома
from tkinter import Tk, Canvas, PhotoImage, NW # импорт модулей тк, экрани где рисуем, для фото,

WINDOW_WIDTH = 750 # ширина
WINDOW_HEIGHT = 800 # высота
TITLE_SIZE = 44 # размер игровой клетки
TETROMINOES = (
    ((0, 0), (-1, 0), (0, -1), (1, -1)),  # S
    ((0, 0), (-1, 0), (1, 0), (2, 0)),  # I
    ((0, 0), (1, 0), (0, -1), (-1, -1)),  # Z
    ((0, 0), (-1, 0), (0, -1), (-1, -1)),  # 0
    ((0, 0), (0, -1), (-1, -1), (1, -1)),  # T
    ((0, 0), (-1, 0), (1, 0), (-1, -1)),  # J
    ((0, 0), (-1, 0), (1, 0), (1, -1)),  # L
    #(0, 0, (-1, 0), (1, 0)),  # .
    ((0, 0), (-1, 0))# /
) # фигуры
COLORS = ('green', 'red', 'yellow', 'magenta', 'blue') # создание набора цветов
FILL_BOARD = ( # прорисовка конечной заставки
    "####......",
    "#.........",
    "###.......",
    "#.........",
    "####......",
    "..#..#....",
    "..#..#....",
    "..##.#....",
    "..#.##....",
    "..#..#....",
    ".....###..",
    ".....#..#.",
    ".....#..#.",
    ".....#..#.",
    ".....###..",
)
FILL_BOARD_COLORS = {'.': 'blue', '#': 'red'} # присвоение определенного цвета определенному символу

class Tile:
    def __init__(self, canvas, x, y, color, size=TITLE_SIZE):
        self.color = color
        self.size = size # размер
        self.canvas = canvas # поле в которм рисуем
        self.image = self.canvas.create_rectangle(x, y, x + self.size, y + self.size, outline="#fb0", fill=self.color)
        # создание клеток

    def move(self, vx, vy):# движение по оси x и y
        self.canvas.move(self.image, vx, vy) # движение фигуры

    def delete(self):
        self.canvas.delete(self.image) # удоление фигуры с хоста

class Tetromino: # класс для фигур
    def __init__(self, canvas, x, y, color, kind=None, size=TITLE_SIZE, rotation=0):
        # kind = none  чтобы не ругался, задаем изначальное подожение и начальный размер клеточки из которых состоит фигура
        if kind is None: # если положение нан то должны выбрать одну из фигул из списка
            kind = random.randint(0, len(TETROMINOES) - 1)
        self.rotation = rotation #  положение фигуры
        self.kind = kind # вид фигуры
        self.shapes = [] # форма фигуры(точки )
        for i, j in TETROMINOES[kind]: # записть фигуры
            for _ in range(rotation): # определение ее положения
                i, j = -j, i # поворот
            self.shapes.append((i, j)) # запись формы фигуры в массив
        self.tiles = [] # плитки
        self.size = size # размер
        self.color = color # цвет

        for i, j in self.shapes:#прорисовка каждого квадрата
            # и зпние\се его всписок
            tile = Tile(canvas, x + i * self.size, y + j * self.size, self.color, self.size)
            self.tiles.append(tile)

    def move(self, dx, dy):#движение для всех плиток
        for tile in self.tiles:
            tile.move(dx, dy)

    def delete(self):#удаление каждкй плитка для удоление всей фигуры
        for tile in self.tiles:
            tile.delete()

class Tetris:
    def __init__(self, parent):
        self.v = 2 # изначальная скорость
        self.v0 = 0 # для паузы
        self.score = 0 # счет

        self.fill = -1 # стартовая заливка
        self.pause = False # пауза
        self.game_over = False # завершение игры
        self.fall = False #  падение

        self.start_x = 10 # стартовые координаты
        self.start_y = 80

        self.board = [[0] * (WINDOW_WIDTH // TITLE_SIZE) for _ in range(WINDOW_HEIGHT // TITLE_SIZE)]
        # задаем параметры для границ

        try:#если получится
            with open('record.dat', 'r') as file:# открытие файла на чтение
                self.record = int(file.read())
        except FileNotFoundError:# ели не найден
            self.record = 0# рекорд = 0

       # window properties
        self.parent = parent
        # parent =  ему присвоены все привелениего и возмижности модуля tk
        self.parent.resizable(width=False, height=False)
        self.parent.title("Tetris")
        window_x = self.parent.winfo_screenwidth() / 2 - WINDOW_WIDTH / 2
        window_y = self.parent.winfo_screenheight() / 2 - WINDOW_HEIGHT / 2 - 40# задаем новые размеры ока
        self.parent.geometry("%dx%d+%d+%d" % (WINDOW_WIDTH, WINDOW_HEIGHT, window_x, window_y))# метод для создания окна

        self.canvas = Canvas(
            self.parent,
            width=WINDOW_WIDTH,# ширина/высота
            height=WINDOW_HEIGHT,
            background="#7777BB", # цвет игрового фона
            bd=0,#ширина бардюра
            highlightthickness=0#толщина стенки
        )
        self.canvas.pack() # фукциядля запаковки

        #  bind keys
        self.parent.bind('<KeyPress-space>', self.start_fall)
        self.parent.bind('<KeyPress-Down>', self.move_down)
        self.parent.bind('<KeyRelease-Down>', self.move_down_cancel)
        self.parent.bind('<KeyPress-Left>', self.move_left)
        self.parent.bind('<KeyPress-Right>', self.move_right)
        self.parent.bind('<KeyPress-Up>', self.rotate)
        self.parent.bind('<KeyPress-Escape>', self.exit)
        self.parent.bind('<KeyPress-F1>', self.get_pause)
        self.parent.bind('+', self.change_speed)
        self.parent.bind('-', self.change_speed)

        #  Canvas objects
        self.background_img = PhotoImage(file="img/fon_new.png") # создание фона
        self.background = self.canvas.create_image(0, 0, anchor=NW, image=self.background_img) # расположенеи картинки
        self.board_bgr_img = PhotoImage(file="img/k_3_new.png") # создание фона для игры
        self.board_bgr = self.canvas.create_image(self.start_x + TITLE_SIZE, self.start_y, anchor=NW, image=self.board_bgr_img)
         # созданеи надписей
        self.score_msg = self.canvas.create_text(650, 100, text='SCORE', fill='white', font="Arial 30")
        self.score_msg_value = self.canvas.create_text(650, 150, text='0', fill='white', font="Arial 30")
        self.speed_msg = self.canvas.create_text(650, 450, text='SPEED', fill='white', font="Arial 20")
        self.speed_msg_value = self.canvas.create_text(650, 500, text=str(self.v), fill='white', font="Arial 20")
        self.record_msg = self.canvas.create_text(650, 300, text='RECORD', fill='white', font="Arial 20")
        self.record_msg_value = self.canvas.create_text(650, 350, text=str(self.record), fill='white', font="Arial 20")

        self.tetromino = Tetromino(self.canvas, self.start_x + TITLE_SIZE * 6, self.start_y - TITLE_SIZE,
                                   random.choice(COLORS),
                                   size=TITLE_SIZE)
        # задаем расположение старта фигуры, задаем рандомный цвет, размер фигуры задается константой
        self.next_tetromino = Tetromino(self.canvas, 620, 600, random.choice(COLORS),
                                        size=TITLE_SIZE)
        # создаем фигуру которая пойдет следующая

        self.wall = []
        # созданеи стен
        for i in range(0, 16):
            self.wall.append(Tile(self.canvas, self.start_x, self.start_y + i * TITLE_SIZE, 'grey', TITLE_SIZE))
            self.board[i][0] = 1
            self.wall.append(Tile(self.canvas, self.start_x + TITLE_SIZE * 11, self.start_y + i * TITLE_SIZE, 'grey', TITLE_SIZE))
            self.board[i][11] = 1
        for i in range(0, 12):
            self.board[15][i] = 1
            self.wall.append(Tile(self.canvas, self.start_x + TITLE_SIZE * i, self.start_y + 15 * TITLE_SIZE, 'grey', TITLE_SIZE))

    def get_pause(self, _): # пауза
        self.pause = not self.pause

    def start_fall(self, _): # падение
        if self.fill != -1 or self.pause or self.game_over or self.fall:
            #пауза, конец игры, падени и заполнение
            return# выход из функции
        self.fall = True

    def change_speed(self, event):# ускорение/ замедление
        if event.char == '+':
            self.v = min(10, self.v + 1)
        else:
            self.v = max(1, self.v - 1)
        self.canvas.itemconfigure(self.speed_msg_value, text=str(self.v)) # запись фактической скорости

    def get_grid_pos(self, tile):#определение положенеи
        x, y, _, _ = self.canvas.coords(tile.image)
        # координаты на доске
        return (int(x) - self.start_x) // TITLE_SIZE, (int(y) - self.start_y) // TITLE_SIZE
        # кординаты в стакане

    def can_move_tetromino(self, di, dj):
        # проверка на возможность движения
        for tile in self.tetromino.tiles:
            i, j = self.get_grid_pos(tile)
            if self.board[j + dj][i + di] != 0: #проверяем каждую точку на возможность движения
                #если не можем пройти проверку выходим из функции
                return False
        return True

    def can_rotate_tetromino(self):
        # проверка на возможность поворотов
        i0, j0 = self.get_grid_pos(self.tetromino.tiles[0])
        # берем координаты 0 плитки
        for tile in self.tetromino.tiles:
            i, j = self.get_grid_pos(tile)
            i, j = i0 - (j - j0), j0 + (i - i0)
            # относительно центральной клетки
            if self.board[j][i] != 0 or self.board[j + 1][i] != 0:
                # клетка не равна 0 т е ранята то выходим из функции
                return False
        return True

    def fill_board(self, no): # плавная прорисовка заставки
        i = no % 10 + 1# по x
        j = no // 10# по y
        color = FILL_BOARD_COLORS[FILL_BOARD[j][i - 1]]
        tile = Tile(self.canvas, self.start_x + i * TITLE_SIZE, self.start_y + j * TITLE_SIZE,
                    color=color,
                    size=TITLE_SIZE)
        self.board[j][i] = tile.image
        self.canvas.update() # не обязательный элемент для обновления 'пикселей'

    def clear_board(self, no):# плавная отчисти полсле заставки
        i = no % 10 + 1
        j = no // 10
        self.canvas.delete(self.board[j][i])
        self.board[j][i] = 0
        self.canvas.update()

    def delete_line(self, row): # удаление заполненых линий
        global col, col
        for col in range(1, 11): # нижнее основание
            self.canvas.delete(self.board[row][col])
        for col in range(1, 11):
            for i in range(row - 1, -1, -1): # после удаления идет смещение всех прорисованных пикселей вниз
                self.canvas.move(self.board[i][col], 0, TITLE_SIZE)
                self.board[i + 1][col] = self.board[i][col]
        self.score += 10 # запить в счет

    def delete_lines(self): # проверка на заполненость линий
        for row in range(15):
            delete = True
            for col in range(1, 11):
                if self.board[row][col] == 0:
                    # идет проверка на заполненость каждой линии и если есть полностью
                    # заолненая линия вызывактся функция и удоляетт ее
                    delete = False
            if delete:
                self.delete_line(row)

    def check_game_over(self):#провека не завершение игры
        for tile in self.tetromino.tiles:
            i, j = self.get_grid_pos(tile)
            if j == 0:
                # если стоит на 0 координнаете по y то конец ишры
                return True
        return False

    def rotate(self, _):# поворот фигуры
        if self.fill != -1 or self.pause or self.game_over or self.fall:
            return
        if not self.can_rotate_tetromino(): # проверка на возможность переворота
            return
        x, y, _, _ = self.canvas.coords(self.tetromino.tiles[0].image)
        # присваеваес к координатам начальное положение фигуры

        self.tetromino.delete()# удаление фигуры
        self.tetromino = Tetromino(# и заново прорисовываем ее
            self.canvas,
            x,# x
            y,# y
            self.tetromino.color,
            self.tetromino.kind,
            self.tetromino.size,
            rotation=(self.tetromino.rotation + 1) % 4
            # чтобы можно было сделать поворот 3 раза если больше то становится =0 те начальному положению
        )

    def move_down(self, _):# движение вниз при нажатой стелочке
        if self.v0 == 0:
            self.v0 = self.v
             # сохранение скорости
        self.v = 10

    def move_down_cancel(self, _):# возвращаем старую скорость
        self.v = self.v0
        # возвращенеие сохраненого орезультата
        self.v0 = 0
        # обнуление

    def move_left(self, _):# движение  влево
        if self.fill != -1 or self.pause or self.game_over or self.fall:
            return
        if self.can_move_tetromino(-1, 1):# проверка на возможность движения
            self.tetromino.move(-self.tetromino.size, 0)

    def move_right(self, _):# движение вправо
        if self.fill != -1 or self.pause or self.game_over or self.fall:
            return
        if self.can_move_tetromino(1, 1): # проверка движение
            self.tetromino.move(self.tetromino.size, 0)

    @staticmethod
    # выход их приложения
    def exit(_):
        exit()

    def start(self):# начало игры
        self.canvas.itemconfig(self.score_msg_value, text=str(self.score))# вписывается значения чсеа

        if self.pause:
            #если пауза тру пререзапускаем
            self.parent.after(5, self.start)
            return

        if self.fall:
            for _ in range(self.v):# чтобы не проскакивать
                # мы v раз на одну клетку
                if self.can_move_tetromino(0, 1):# проверка на возможнось вдижения
                    self.tetromino.move(0, 1)
                    if self.v0 == 0:
                        self.v0 = self.v
                    self.v = 5 # скорость падение
                else:
                    self.fall = False
                    self.v = self.v0
                    self.v0 = 0
                    break# если не можем падать то возвращаем старую скарость и возвращаемся в старт

            self.parent.after(1, self.start)
            return

        if self.fill != -1:
            self.next_tetromino.delete()
            if self.fill < 15 * 10:
                self.fill_board(self.fill)# заполняем 150 плиток игрового поля
                self.fill += 1
            elif self.fill < 15 * 10 * 2:
                self.clear_board(self.fill - 15 * 10)# отчистка клеток постепенно
                self.fill += 1
            else:
                self.fill = -1 # возвращаем значение

                self.tetromino = Tetromino(
                                            self.canvas,
                    self.start_x + TITLE_SIZE * 6,
                    self.start_y - TITLE_SIZE,
                    random.choice(COLORS),
                    size=TITLE_SIZE,
                    rotation=random.randint(0, 3))

                self.next_tetromino = Tetromino(
                    self.canvas,
                    620,
                    600,
                    random.choice(COLORS),
                    size=TITLE_SIZE,
                    rotation=random.randint(0, 3)
                )

            self.parent.after(5, self.start)
            return # перезапуск цикла старт

        if self.game_over:
            self.tetromino.delete()# удаление фигуры
            for i in range(1, 11):# очищение игрового поля
                for j in range(0, 15):
                    if self.board[j][i] > 0:
                        # если на канвасе чтото есть то удоляем
                        self.canvas.delete(self.board[j][i])
                        self.board[j][i] = 0
                        # обнуленеие поля

            if self.score > self.record:# если новый рекород был больше то записываем его
                with open('record.dat', 'w') as file:
                    self.record = self.score
                    file.write(str(self.record))
                    self.canvas.itemconfig(self.record_msg_value, text=str(self.record))

            self.fill = 0
            # начало заполнения массива
            self.game_over = False
            self.score = 0
            self.parent.after(5, self.start)# перезапуск игры
            return

        for _ in range(self.v):
            if self.can_move_tetromino(0, 1):
                self.tetromino.move(0, 1)
                # если может двигатиься
            else:
                self.score += 4
                # прибавим 4
                self.game_over = self.check_game_over()
                #и проверка на завершенеи

                for tile in self.tetromino.tiles:
                    i, j = self.get_grid_pos(tile)
                    if 1 <= i <= 10 and 1 <= j <= 15:
                        self.board[j][i] = tile.image
                        # указывает что еть обьекты на доске
                    else:
                        self.canvas.delete(tile.image)

                self.delete_lines()
                if self.game_over:
                    break

                self.tetromino = Tetromino(
                    self.canvas,
                    self.start_x + TITLE_SIZE * 6,
                    self.start_y - TITLE_SIZE,
                    color=self.next_tetromino.color,
                    size=TITLE_SIZE,
                    kind=self.next_tetromino.kind,
                    rotation=self.next_tetromino.rotation
                )
                self.next_tetromino.delete()
                self.next_tetromino = Tetromino(
                    self.canvas,
                    620,
                    600,
                    random.choice(COLORS),
                    size=TITLE_SIZE,
                    rotation=random.randint(0, 3)
                )
        self.parent.after(5, self.start)


main = Tk()
tetris = Tetris(main)
tetris.start()
main.mainloop()
