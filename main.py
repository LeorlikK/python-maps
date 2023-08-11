import json
import time
import cv2
import numpy as np
import pyautogui
import pytesseract
from mss import mss

pytesseract.pytesseract.tesseract_cmd = 'C:\\Program Files\\Tesseract-OCR\\tesseract.exe'

settings = input("Введите параметры запуска(0 - стандарт, 1 - настройка, 2 - восстановление стандартных настроек): ")
if settings == "0":
    with open("Settings.json", "r", encoding="utf-8") as file:
        file_main_settings = json.load(file)
    distance_for_two_target = file_main_settings["Settings"]["distance_for_two_target"]
    player_offset_massive_y = file_main_settings["Settings"]["player_offset_massive_y"]
    player_offset_massive_x = file_main_settings["Settings"]["player_offset_massive_x"]
    pixel_massive_x = [60, 185, 310, 430, 555, 675]
    pixel_massive_y = [60, 185, 310, 430, 555]

    print(file_main_settings)
    file.close()


if settings == "1":
    print({
        "Settings": {
            "distance_for_two_target": "Расстояние между двумя целями(80)",
            "player_offset_massive_y": "Смещение позиции игрока в массиве, после  копирования массива по Y",
            "player_offset_massive_x": "Смещение позиции игрока в массиве, после  копирования массива по X",
            "pixel_massive_x": "Расположение квадратов в пикселях по X",
            "pixel_massive_y": "Расположение квадратов в пикселях по Y"
        }
    })

    with open("Settings.json", "r", encoding="utf-8") as file:
        file1 = json.load(file)
        file.close()

    input_command = input("Введите изменение настройки(A = B): ")
    input_command = input_command.replace(" ", "")
    input_command = input_command.split("=")

    file1["Settings"][f"{input_command[0]}"] = input_command[1]

    with open("Settings.json", "w", encoding="utf-8") as file:
        json.dump(file1, file, indent=4, ensure_ascii=False)
        file.close()

if settings == "2":
    t = {"Settings": {
                 "distance_for_two_target": 80,
                 "player_offset_massive_y": 10,
                 "player_offset_massive_x": 12,
                 "pixel_massive_x": [60, 185, 310, 430, 555, 675],
                 "pixel_massive_y": [60, 185, 310, 430, 555]
             },
         }
    try:
        with open("Settings.json", "r", encoding="utf-8") as file:
            file1 = json.load(file)
            file.close()
            print(1)
    except Exception as ex:
        print(ex)
        print(2)
        with open("Settings.json", "w", encoding="utf-8") as file:
            json.dump(t, file, indent=4, ensure_ascii=False)
            file.close()


class Player:
    monitor_all_window = {  # Весь эран
        'left': 0,
        'top': 0,
        'width': 1920,
        'height': 1080,
    }

    def __init__(self):
        self.massive = np.zeros([11, 13], dtype=float)

        self.test_error = 0
        self.test_error_massive = []

        self.player_screen_v1 = None
        self.player_screen_v2 = None
        self.red_screen_v1 = None
        self.green_screen_v1 = None
        self.yellow_screen_v1 = None
        self.blue_screen_v1 = None

        self.screen = 0
        self.screen_mask = 0
        self.player = 0

        self.quantity_target = 0
        self.target_red = 0
        self.target_green = 0
        self.target_yellow = 0
        self.target_blue = 0

        self.number_of_units = 0
        self.test_massive = []

        self.index = 0
        self.target = 0
        self.commands = []
        print(f"Инициализация класса: успех...")

    def __str__(self):
        print("Class:Player")

    def load_img(self, player_v1, player_v2, red, green, yellow, blue):
        self.player_screen_v1 = cv2.imread(str(player_v1))
        self.player_screen_v1 = cv2.cvtColor(self.player_screen_v1, cv2.COLOR_BGR2HSV)
        self.player_screen_v1 = np.array(self.player_screen_v1)

        self.player_screen_v2 = cv2.imread(str(player_v2))
        self.player_screen_v2 = cv2.cvtColor(self.player_screen_v2, cv2.COLOR_BGR2HSV)
        self.player_screen_v2 = np.array(self.player_screen_v2)

        self.red_screen_v1 = cv2.imread(str(red))
        self.red_screen_v1 = cv2.cvtColor(self.red_screen_v1, cv2.COLOR_BGR2HSV)
        self.red_screen_v1 = np.array(self.red_screen_v1)

        self.green_screen_v1 = cv2.imread(str(green))
        self.green_screen_v1 = cv2.cvtColor(self.green_screen_v1, cv2.COLOR_BGR2HSV)
        self.green_screen_v1 = np.array(self.green_screen_v1)

        self.yellow_screen_v1 = cv2.imread(str(yellow))
        self.yellow_screen_v1 = cv2.cvtColor(self.yellow_screen_v1, cv2.COLOR_BGR2HSV)
        self.yellow_screen_v1 = np.array(self.yellow_screen_v1)

        self.blue_screen_v1 = cv2.imread(str(blue))
        self.blue_screen_v1 = cv2.cvtColor(self.blue_screen_v1, cv2.COLOR_BGR2HSV)
        self.blue_screen_v1 = np.array(self.blue_screen_v1)
        print(f"Загрузка изображений: успех...")

    def screen_monitor(self):
        """
        Скрин центральной части экрана, перевод RGB в BGR, создание массива
        """
        monitor_all_window = {  # Весь эран
            'left': 592,
            'top': 150,
            'width': 735,
            'height': 611,

        }

        m = mss()
        img = m.grab(monitor_all_window)
        img = np.array(img)
        self.screen = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)

    def mask(self):
        """
        Формирует маску определенного цвета и возвращает лишь цвет макси
        """
        low = np.array((36, 187, 162), np.uint8)
        upper = np.array((96, 217, 192), np.uint8)
        mask = cv2.inRange(self.screen, low, upper)
        self.screen_mask = cv2.bitwise_and(self.screen, self.screen, mask=mask)
        print(f"Маска изображения: успех...")

    def row(self, y, yy, col=0):
        """
        Проверяет, есть ли в ряду по оси Х препятствие
        и заносит его в матрицу
        :param y:
        :param yy:
        :param col:
        """
        massive_zero = [
            [y, yy, 0, 13],  # 0!
            [y, yy, 34, 81],  # 1!
            [y, yy, 113, 135],  # 2!
            [y, yy, 156, 209],  # 3!
            [y, yy, 235, 256],  # 4!
            [y, yy, 281, 330],  # 5!
            [y, yy, 359, 380],  # 6!
            [y, yy, 397, 453],  # 7!
            [y, yy, 480, 502],  # 8!
            [y, yy, 520, 578],  # 9!
            [y, yy, 601, 625],  # 10!
            [y, yy, 650, 705],  # 11!
            [y, yy, 722, 733]  # 12!
        ]

        cell = 0
        for x in massive_zero:
            cut = self.screen_mask[x[0]:x[1], x[2]: x[3]]
            not_black = cut[cut > 5]
            if len(not_black) > 5:
                self.massive[col][cell] = 99
            else:
                self.massive[col][cell] = 0
            cell += 1

    @staticmethod
    def column():
        """
        Использует метод 'row' и прогоняет его по всем осям Y
        """
        player.row(0, 14)
        player.row(28, 89, col=1)
        player.row(112, 134, col=2)
        player.row(149, 218, col=3)
        player.row(232, 258, col=4)
        player.row(270, 333, col=5)
        player.row(355, 379, col=6)
        player.row(397, 463, col=7)
        player.row(480, 502, col=8)
        player.row(517, 585, col=9)
        player.row(600, 610, col=10)
        print(f"Разметка по квадратам: успех...")

    def find_load_img(self, img, similarity, x_offset, y_offset):
        self.quantity_target = 0
        try:
            res = cv2.matchTemplate(self.screen, img, cv2.TM_CCOEFF_NORMED)
            loc = np.where(res >= similarity)
            max_min_x = max(loc[1]) - min(loc[1])
            max_min_y = max(loc[0]) - min(loc[0])
            if (max_min_x > distance_for_two_target) or (max_min_y > distance_for_two_target):
                self.quantity_target = 2
                x = []
                y = []
                x.append(loc[1][0] + x_offset)
                x.append(loc[1][len(loc[1]) - 1] + x_offset)
                y.append(loc[0][0] + y_offset)
                y.append(loc[0][len(loc[0]) - 1] + y_offset)
                return [x, y]
            else:
                self.quantity_target = 1
                x, y = loc[1][0] + x_offset, loc[0][0] + y_offset
                return [x, y]
        except Exception as ex:
            return None

    def add_table(self, xy, color):
        if xy:
            num = 0
            for x in range(self.quantity_target):
                massive_x = []
                #massive_x1 = [60, 185, 310, 430, 555, 675]
                massive_x1 = pixel_massive_x
                massive_x2 = [1, 3, 5, 7, 9, 11]
                for item in massive_x1:
                    if self.quantity_target == 2:
                        massive_x.append(abs(item - xy[0][num]))
                    else:
                        massive_x.append(abs(item - xy[0]))
                x = massive_x2[massive_x.index(min(massive_x))]

                massive_y = []
                massive_y1 = pixel_massive_y
                massive_y2 = [1, 3, 5, 7, 9]
                for item in massive_y1:
                    if self.quantity_target == 2:
                        massive_y.append(abs(item - xy[1][num]))
                    else:
                        massive_y.append(abs(item - xy[1]))
                y = massive_y2[massive_y.index(min(massive_y))]

                if color == "player":
                    self.player = [y + player_offset_massive_y, x + player_offset_massive_x]  # 11 13
                    print(f"Игрок найден: {self.player}")
                    self.massive[self.player[0]][self.player[1]] = 1.5
                    try:
                        player_step_one = [self.player[0], self.player[1]]
                        player_step_one[1] += 1
                        if self.massive[player_step_one[0]][player_step_one[1]] == 0:
                            self.massive[player_step_one[0]][player_step_one[1]] = 1
                    except:
                        pass

                    try:
                        player_step_one = [self.player[0], self.player[1]]
                        player_step_one[1] -= 1
                        if self.massive[player_step_one[0]][player_step_one[1]] == 0:
                            self.massive[player_step_one[0]][player_step_one[1]] = 1
                    except:
                        pass

                    try:
                        player_step_one = [self.player[0], self.player[1]]
                        player_step_one[0] += 1
                        if self.massive[player_step_one[0]][player_step_one[1]] == 0:
                            self.massive[player_step_one[0]][player_step_one[1]] = 1
                    except:
                        pass

                    try:
                        player_step_one = [self.player[0], self.player[1]]
                        player_step_one[0] -= 1
                        if self.massive[player_step_one[0]][player_step_one[1]] == 0:
                            self.massive[player_step_one[0]][player_step_one[1]] = 1
                    except:
                        pass
                    print(f"Персонаж найден: Y={y}, X={x}")
                if color == "red":
                    self.test_error_massive.append("red_")
                    self.target_red = [y, x]
                    self.massive[self.target_red[0]][self.target_red[1]] = 2.5
                    self.number_of_units += 1
                    print(f".............................................................Красный найден: Y={y}, X={x}")
                if color == "green":
                    self.test_error_massive.append("green_")
                    self.target_green = [y, x]
                    self.massive[self.target_green[0]][self.target_green[1]] = 3.5
                    self.number_of_units += 1
                    print(f".............................................................Зеленый найден: Y={y}, X={x}")
                if color == "yellow":
                    self.test_error_massive.append("yellow_")
                    self.target_yellow = [y, x]
                    self.massive[self.target_yellow[0]][self.target_yellow[1]] = 4.5
                    self.number_of_units += 1
                    print(f".............................................................Желтый найден: Y={y}, X={x}")
                if color == "blue":
                    self.test_error_massive.append("blue_")
                    self.target_blue = [y, x]
                    self.massive[self.target_blue[0]][self.target_blue[1]] = 5.5
                    self.number_of_units += 1
                    print(f".............................................................Синий найден: Y={y}, X={x}")
                num += 1
        else:
            pass

    def multiplication_massive(self):
        """
        Размножает матрицу:
        - два раза вправо
        - два раза вниз
        """
        cut_h = np.delete(self.massive, 0, axis=1)

        massive_row = np.hstack([self.massive, cut_h])
        massive_row = np.hstack([massive_row, cut_h])

        cut_v = np.delete(massive_row, 0, axis=0)

        massive_col = np.vstack([massive_row, cut_v])
        massive_all = np.vstack([massive_col, cut_v])
        print(f"Умножение массива: успех...")
        return massive_all

    def wave_iteration(self):
        """
        Формирует волну от персонажа, до ближайшей точки назначения
        """
        self.test_massive = []
        step = 2
        num = 1
        block_2 = 0
        block_3 = 0
        block_4 = 0
        block_5 = 0

        for x in range(950):
            h_step = 0
            self.index = np.where(self.massive == num)
            for item in range(len(self.index[0])):
                x, y = self.index[0][h_step], self.index[1][h_step]
                h_step += 1
                try:
                    player_wave = [x, y]
                    player_wave[0] -= 1
                    if player_wave[0] > -1:
                        if self.massive[player_wave[0]][player_wave[1]] == 0:
                            self.massive[player_wave[0]][player_wave[1]] = step
                        if self.massive[player_wave[0]][player_wave[1]] == 99:
                            pass
                        if self.massive[player_wave[0]][player_wave[1]] == 2.5\
                                or self.massive[player_wave[0]][player_wave[1]] == 3.5\
                                or self.massive[player_wave[0]][player_wave[1]] == 4.5\
                                or self.massive[player_wave[0]][player_wave[1]] == 5.5:
                            if block_2 != self.massive[player_wave[0]][player_wave[1]]\
                                    and block_3 != self.massive[player_wave[0]][player_wave[1]] \
                                    and block_4 != self.massive[player_wave[0]][player_wave[1]] \
                                    and block_5 != self.massive[player_wave[0]][player_wave[1]]:
                                self.test_massive.append(
                                    [player_wave[0], player_wave[1], self.massive[player_wave[0]][player_wave[1]], step])
                                if self.massive[player_wave[0]][player_wave[1]] == 2.5:
                                    block_2 = 2.5
                                if self.massive[player_wave[0]][player_wave[1]] == 3.5:
                                    block_3 = 3.5
                                if self.massive[player_wave[0]][player_wave[1]] == 4.5:
                                    block_4 = 4.5
                                if self.massive[player_wave[0]][player_wave[1]] == 5.5:
                                    block_5 = 5.5
                except:
                    pass

                try:
                    player_wave = [x, y]
                    player_wave[1] += 1
                    if player_wave[1] > -1:
                        if self.massive[player_wave[0]][player_wave[1]] == 0:
                            self.massive[player_wave[0]][player_wave[1]] = step
                        if self.massive[player_wave[0]][player_wave[1]] == 99:
                            pass
                        if self.massive[player_wave[0]][player_wave[1]] == 2.5\
                                or self.massive[player_wave[0]][player_wave[1]] == 3.5\
                                or self.massive[player_wave[0]][player_wave[1]] == 4.5\
                                or self.massive[player_wave[0]][player_wave[1]] == 5.5:
                            if block_2 != self.massive[player_wave[0]][player_wave[1]] \
                                    and block_3 != self.massive[player_wave[0]][player_wave[1]] \
                                    and block_4 != self.massive[player_wave[0]][player_wave[1]] \
                                    and block_5 != self.massive[player_wave[0]][player_wave[1]]:
                                self.test_massive.append(
                                    [player_wave[0], player_wave[1], self.massive[player_wave[0]][player_wave[1]], step])
                                if self.massive[player_wave[0]][player_wave[1]] == 2.5:
                                    block_2 = 2.5
                                if self.massive[player_wave[0]][player_wave[1]] == 3.5:
                                    block_3 = 3.5
                                if self.massive[player_wave[0]][player_wave[1]] == 4.5:
                                    block_4 = 4.5
                                if self.massive[player_wave[0]][player_wave[1]] == 5.5:
                                    block_5 = 5.5
                except:
                    pass

                try:
                    player_wave = [x, y]
                    player_wave[0] += 1
                    if player_wave[0] > -1:
                        if self.massive[player_wave[0]][player_wave[1]] == 0:
                            self.massive[player_wave[0]][player_wave[1]] = step
                        if self.massive[player_wave[0]][player_wave[1]] == 99:
                            pass
                        if self.massive[player_wave[0]][player_wave[1]] == 2.5\
                                or self.massive[player_wave[0]][player_wave[1]] == 3.5\
                                or self.massive[player_wave[0]][player_wave[1]] == 4.5\
                                or self.massive[player_wave[0]][player_wave[1]] == 5.5:
                            if block_2 != self.massive[player_wave[0]][player_wave[1]] \
                                    and block_3 != self.massive[player_wave[0]][player_wave[1]] \
                                    and block_4 != self.massive[player_wave[0]][player_wave[1]] \
                                    and block_5 != self.massive[player_wave[0]][player_wave[1]]:
                                self.test_massive.append(
                                    [player_wave[0], player_wave[1], self.massive[player_wave[0]][player_wave[1]], step])
                                if self.massive[player_wave[0]][player_wave[1]] == 2.5:
                                    block_2 = 2.5
                                if self.massive[player_wave[0]][player_wave[1]] == 3.5:
                                    block_3 = 3.5
                                if self.massive[player_wave[0]][player_wave[1]] == 4.5:
                                    block_4 = 4.5
                                if self.massive[player_wave[0]][player_wave[1]] == 5.5:
                                    block_5 = 5.5
                except:
                    pass

                try:
                    player_wave = [x, y]
                    player_wave[1] -= 1
                    if player_wave[1] > -1:
                        if self.massive[player_wave[0]][player_wave[1]] == 0:
                            self.massive[player_wave[0]][player_wave[1]] = step
                        if self.massive[player_wave[0]][player_wave[1]] == 99:
                            pass
                        if self.massive[player_wave[0]][player_wave[1]] == 2.5\
                                or self.massive[player_wave[0]][player_wave[1]] == 3.5\
                                or self.massive[player_wave[0]][player_wave[1]] == 4.5\
                                or self.massive[player_wave[0]][player_wave[1]] == 5.5:
                            if block_2 != self.massive[player_wave[0]][player_wave[1]] \
                                    and block_3 != self.massive[player_wave[0]][player_wave[1]] \
                                    and block_4 != self.massive[player_wave[0]][player_wave[1]] \
                                    and block_5 != self.massive[player_wave[0]][player_wave[1]]:
                                self.test_massive.append(
                                    [player_wave[0], player_wave[1], self.massive[player_wave[0]][player_wave[1]], step])
                                if self.massive[player_wave[0]][player_wave[1]] == 2.5:
                                    block_2 = 2.5
                                if self.massive[player_wave[0]][player_wave[1]] == 3.5:
                                    block_3 = 3.5
                                if self.massive[player_wave[0]][player_wave[1]] == 4.5:
                                    block_4 = 4.5
                                if self.massive[player_wave[0]][player_wave[1]] == 5.5:
                                    block_5 = 5.5
                except:
                    pass
            step += 1
            num += 1
        print(f"Распространение волны: успех(всего шагов = {step})")
        return step

    def priority(self):
        massive = self.test_massive[0:self.number_of_units]
        index_massive = []
        print(f"Массив позиций_1: {massive}")
        t = 0

        for x in massive:
            h = x[2]
            if h == 2.5:
                massive[t][2] = 8000 - 800 * (x[3] / 2)
                index_massive.append(massive[t][2])
                self.test_error_massive.append([2.5, massive[t][2]])

            if h == 3.5:
                massive[t][2] = 4000 - 400 * (x[3] / 2)
                index_massive.append(massive[t][2])
                self.test_error_massive.append([3.5, massive[t][2]])

            if h == 4.5:
                massive[t][2] = 2000 - 200 * (x[3] / 2)
                index_massive.append(massive[t][2])
                self.test_error_massive.append([4.5, massive[t][2]])

            if h == 5.5:
                massive[t][2] = 1000 - 100 * (x[3] / 2)
                index_massive.append(massive[t][2])
                self.test_error_massive.append([5.5, massive[t][2]])

            t += 1
        self.test_massive = massive[index_massive.index(max(index_massive))]
        print(f"Массив позиций_2: {self.test_massive}")
        self.target = [self.test_massive[0], self.test_massive[1]]
        #cv2.imwrite(f"{self.test_error_massive}__{self.test_error}.png", self.screen)
        self.test_error += 1

    def wave_revers(self, step_wave):
        """
        Формирует обратную волну с нахождением оптимального маршрута
        :param step_wave: первое число(последний шаг), который нужно искать
        """
        error = 0
        self.commands = []
        target_finish = True
        while target_finish:
            if error > 1000:
                target_finish = False
            x, y = self.target[0], self.target[1]
            turn = "пробел"

            try:
                revers_wave = [x, y]
                revers_wave[0] -= 1
                if self.massive[revers_wave[0]][revers_wave[1]] == step_wave:
                    turn = "Вверх"
                    self.target = revers_wave
                if self.massive[revers_wave[0]][revers_wave[1]] == 1.5:
                    turn = "Вверх"
                    target_finish = False
            except:
                pass

            try:
                revers_wave = [x, y]
                revers_wave[0] += 1
                if self.massive[revers_wave[0]][revers_wave[1]] == step_wave:
                    turn = "Вниз"
                    self.target = revers_wave
                if self.massive[revers_wave[0]][revers_wave[1]] == 1.5:
                    turn = "Вниз"
                    target_finish = False
            except:
                pass

            try:
                revers_wave = [x, y]
                revers_wave[1] += 1
                if self.massive[revers_wave[0]][revers_wave[1]] == step_wave:
                    turn = "Право"
                    self.target = revers_wave
                if self.massive[revers_wave[0]][revers_wave[1]] == 1.5:
                    turn = "Право"
                    target_finish = False
            except:
                pass

            try:
                revers_wave = [x, y]
                revers_wave[1] -= 1
                if self.massive[revers_wave[0]][revers_wave[1]] == step_wave:
                    turn = "Лево"
                    self.target = revers_wave
                if self.massive[revers_wave[0]][revers_wave[1]] == 1.5:
                    turn = "Лево"
                    target_finish = False
            except:
                pass

            if turn != "пробел":
                self.commands.append(str(turn))
            step_wave -= 1
            error += 1
        print(f"Обратная волна: успех(всего шагов = {step_wave + 1}")

    def interpreter(self):
        commands_revers = []
        self.commands.reverse()
        for item in self.commands:
            if item == "Вверх":
                commands_revers.append("down")
            if item == "Вниз":
                commands_revers.append("up")
            if item == "Право":
                commands_revers.append("left")
            if item == "Лево":
                commands_revers.append("right")
        real_commands = commands_revers[::2]
        print(real_commands)
        print(f"Интерпретатор: успех...")
        return real_commands

    @staticmethod
    def key(command):
        for x in command:
            pyautogui.keyDown(f"{x}")
            time.sleep(0.1)
            pyautogui.keyUp(f"{x}")
            time.sleep(0.1)
            print(f"Команда: {x}")
        print(f"Команды: успех...")
        time.sleep(0.5)

    def close(self):
        self.test_error_massive = []
        self.massive = np.zeros([11, 13], dtype=float)

        self.screen = 0
        self.screen_mask = 0
        self.player = 0

        self.quantity_target = 0
        self.target_red = 0
        self.target_green = 0
        self.target_yellow = 0
        self.target_blue = 0

        self.number_of_units = 0
        self.test_massive = []

        self.index = 0
        self.target = 0
        self.commands = []
        print(f"Очищение данных: успех...")

    @staticmethod
    def all_func():
        while True:
            xyz = None
            while not xyz:
                #print("Ищу персонажа на эркане...")
                player.screen_monitor()
                xyz = player.find_load_img(player.player_screen_v1, 0.6, 20, 30)
                if not xyz:
                    xyz = player.find_load_img(player.player_screen_v2, 0.6, 20, 30)
            if xyz:
                try:
                    player.mask()
                    player.column()
                    player.add_table(xy=player.find_load_img(player.red_screen_v1, 0.7, 17, 17), color="red")
                    player.add_table(xy=player.find_load_img(player.green_screen_v1, 0.7, 20, 30), color="green")
                    player.add_table(xy=player.find_load_img(player.yellow_screen_v1, 0.7, 15, 25), color="yellow")
                    player.add_table(xy=player.find_load_img(player.blue_screen_v1, 0.7, 20, 30), color="blue")
                    player.massive = player.multiplication_massive()
                    player.add_table(xy=player.find_load_img(player.player_screen_v1, 0.6, 20, 30), color="player")
                    player.add_table(xy=player.find_load_img(player.player_screen_v2, 0.6, 20, 30), color="player")

                    step = player.wave_iteration()
                    print(player.number_of_units)
                    player.priority()
                    player.wave_revers(step_wave=player.test_massive[3])
                    player.key(command=player.interpreter())
                except:
                    xyz = None
                    player.close()
                player.close()
                xyz = None
                time.sleep(1)


player = Player()
player.load_img("player_v1.png", "player_v2.png", "red_v1.png", "green_v1.png", "yellow_v1.png", "blue_v1.png")
time.sleep(5)
player.all_func()