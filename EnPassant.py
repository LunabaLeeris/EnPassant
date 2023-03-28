import math
from kivy import Config
from kivy.uix.button import Button
from kivy.uix.modalview import ModalView

Config.set('graphics', 'width', 700)
Config.set('graphics', 'height', 800)

import random
import time
from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.relativelayout import RelativeLayout
import requests
from kivy.core.window import Window
from kivy.uix.label import Label
from kivy.properties import Clock, NumericProperty
import os
from kivy.uix.image import Image
from kivy.graphics import Rectangle, Color

# Assets for game interface
assets_path = {'bar': os.path.join('assets', 'Bar.png'),
               'greenBar': os.path.join('assets', 'BarGreen.png'),
               'redBar': os.path.join('assets', 'BarRed.png'),
               'background': os.path.join('assets', 'Background.png'),
               'font': os.path.join('assets', 'pe______.ttf'),
               'labelFont': os.path.join('assets', 'Computer_speak.ttf'),
               'barFrame': os.path.join('assets', 'BarFrame.png'),
               'pawn': os.path.join('assets', 'Pawn.png'),
               'epawn': os.path.join('assets', 'EPawn.png'),
               'attack': os.path.join('assets', 'movements', 'attack.png'),
               'flee': os.path.join('assets', 'movements', 'flee.png'),
               'auto': os.path.join('assets', 'movements', 'auto.png'),
               'health': os.path.join('assets', 'movements', 'hearts.png'),
               'pawnKill': [os.path.join('assets', 'pawnKill', 'kill1.png'),
                            os.path.join('assets', 'pawnKill', 'kill2.png'),
                            os.path.join('assets', 'pawnKill', 'kill3.png'),
                            os.path.join('assets', 'pawnKill', 'kill4.png')],
               'pawnDamaged': [os.path.join('assets', 'pawnDamaged', '1.png'),
                               os.path.join('assets', 'pawnDamaged', '2.png'),
                               os.path.join('assets', 'pawnDamaged', '3.png'),
                               os.path.join('assets', 'pawnDamaged', '4.png')],
               'score': [os.path.join('assets', 'score', '1.png'),
                         os.path.join('assets', 'score', '2.png'),
                         os.path.join('assets', 'score', '3.png'),
                         os.path.join('assets', 'score', '4.png')],
               'time': [os.path.join('assets', 'time', '1.png'),
                        os.path.join('assets', 'time', '2.png'),
                        os.path.join('assets', 'time', '3.png'),
                        os.path.join('assets', 'time', '4.png')],
               'heart': [os.path.join('assets', 'heart', '1.png'),
                         os.path.join('assets', 'heart', '2.png'),
                         os.path.join('assets', 'heart', '3.png'),
                         os.path.join('assets', 'heart', '4.png')],
               'b_heart': [os.path.join('assets', 'b_heart', '1.png'),
                           os.path.join('assets', 'b_heart', '2.png'),
                           os.path.join('assets', 'b_heart', '3.png'),
                           os.path.join('assets', 'b_heart', '4.png')]
               }

# Responsible for requesting the words that will be used to randomize the output words on the text screen
word_site = "https://www.mit.edu/~ecprice/wordlist.10000"
response = requests.get(word_site)
words = response.content.splitlines()
WORDS = [i for i in words if len(i) < 10]
word_length = len(WORDS)

start_time = True  # has the timer been started
time_now = -1  # current time. used for solving time passed inside the player attributes
time_passed = 0  # used for solving the time survived for player attributes
game_over = False  # boolean to check whether the game has ended
correct_words = 0  # counts the number of correct words for WPM
accuracy = 0  # counts accuracy
total_score = 0  # counts total score
game_started = False  # used to check whether the game has started (player pressed a key)


class PrimaryScreen(RelativeLayout):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        # instance classes
        self.home_page = HomePage(self, opacity=.9, pos_hint={"center_x": .5, "center_y": .5},
                                  size_hint=(1, 1))
        self.main = Main(self, pos_hint={"center_x": .5, "center_y": .5},
                         size_hint=(1, 1))
        self.add_components()

    def add_components(self):
        self.add_widget(self.main)
        self.add_widget(self.home_page)

    def add_home_page(self):
        self.add_widget(self.home_page)


class Main(BoxLayout):
    # Responsible for handling the logic of keyboard strokes
    orientation = 'vertical'

    def __init__(self, within, **kwargs):
        super().__init__(**kwargs)
        # Parent class
        self.within = within
        # For keyboard stuff
        self.keyboard = Window.request_keyboard(self.on_keyboard_closed, self)
        self.keyboard.bind(on_key_down=self.on_keyboard_down)
        self.keyboard.bind(on_key_up=self.on_keyboard_up)
        self.start = False  # trigger to check whether user already picked a difficulty
        # Instance classes
        self.main_game_window = Main_Game_Window(self, size_hint=(1, 4))
        self.text = Text()
        self.game_window = self.main_game_window.game_window
        self.player_attributes = self.main_game_window.game_window.player_attributes
        self.player_details = self.main_game_window.player_details
        self.game_grid = self.main_game_window.game_window.game_grid
        self.game_grid_border = self.main_game_window.game_window.game_grid_border
        # Functions for displaying text on text window
        self.add_components()
        self.adjust_text_class()
        # For computation of accuracy
        self.total_strokes = 0
        self.total_correct_char = 0
        # Handles key toggles
        self.shift_toggled = False
        # text being typed by the player
        self.my_text = ''
        # changes based on the type of difficulty specified by the player
        self.pawn_start = 0
        self.health = 0
        self.pawn_moves_per = 0
        self.pawn_spawns_per = 0
        self.hearts_spawns_per = 0
        self.bar_speed = 0

    def instantiate_classes(self):
        # will create an instance of the important classes
        self.main_game_window = Main_Game_Window(self, size_hint=(1, 4))
        self.text = Text()
        self.game_window = self.main_game_window.game_window
        self.player_attributes = self.main_game_window.game_window.player_attributes
        self.player_details = self.main_game_window.player_details
        self.game_grid = self.main_game_window.game_window.game_grid
        self.game_grid_border = self.main_game_window.game_window.game_grid_border

        self.adjust_classes()

    def adjust_classes(self):
        self.game_grid.desired_number_enemies = {'pawns': self.pawn_start}
        self.game_grid.add_pawn_per = self.pawn_spawns_per
        self.game_grid.add_hearts_per = self.hearts_spawns_per
        self.game_grid.pawn_movement_duration = self.pawn_moves_per
        self.player_details.decrease_int = self.bar_speed
        self.player_attributes.health = self.health
        self.player_attributes.add_hearts()

    def adjust_text_class(self):
        # adjusts the context of the text class for text display
        self.text.fill_text()
        self.text.display_text()

    def add_components(self):
        self.add_widget(self.main_game_window)
        self.add_widget(self.text)

    def on_keyboard_closed(self):
        self.keyboard.unbind(on_key_down=self.on_keyboard_down)
        self.keyboard.unbind(on_key_up=self.on_keyboard_up)
        self.keyboard = None

    def check_if_similar(self):
        if self.my_text == '':
            self.text.middle_text.color = (103 / 255, 81 / 255, 81 / 255)
        elif self.my_text != self.text.text[0][0:len(self.my_text)]:
            self.text.middle_text.color = (236 / 255, 114 / 255, 114 / 255)
            self.text.middle_text.x += 2
        else:
            self.total_correct_char += 1
            self.text.middle_text.y += 2
            self.text.middle_text.color = (123 / 255, 156 / 255, 104 / 255)

    def adjust_labels(self):
        self.text.last_text = self.text.text.pop(0)
        self.text.text.append(WORDS[random.randint(0, word_length)].decode('UTF-8'))
        self.text.update_text()

    def adjust_label_text(self):
        global correct_words
        text_len = len(self.text.last_text)
        if self.my_text == self.text.last_text:
            correct_words += 1
            self.text.left_text.color = (100 / 255, 126 / 255, 104 / 255)
            self.main_game_window.game_window.player_attributes.adjust_score(text_len)
            if self.player_details.increase_bar(self.player_details.rect_height / (10 / text_len)):
                self.game_window.game_grid_border.game_grid.move_pawn()
        else:
            self.text.left_text.color = (236 / 255, 114 / 255, 114 / 255)
            self.player_details.decrease_bar(self.player_details.rect_height / (10 / text_len))
            self.player_details.rect.pos = (self.player_details.rect.pos[0] + 5, self.player_details.rect.pos[1])

        self.my_text = ''
        self.text.middle_text.color = (103 / 255, 81 / 255, 81 / 255)

    def on_keyboard_down(self, keyboard, keycode, text, modifiers):
        global game_started
        global game_over

        if self.start:
            if not game_started:
                self.game_window.game_grid_border.remove_widget(self.game_window.game_grid_border.start_label)
                self.game_window.game_grid_border.animate_start_label_ev.cancel()
                game_started = True

            if not game_over:
                if keycode[1] == 'spacebar':
                    self.adjust_labels()
                    self.adjust_label_text()
                    self.text.left_text.font_size += 3
                    self.text.right_text.font_size += 3

                elif keycode[1] == "capslock":
                    self.capslock_on = False if self.capslock_on else True
                    self.text.check_capslock_state(self.capslock_on)

                elif keycode[1] == "tab":
                    self.reset()

                elif keycode[1] == "enter":
                    self.reset()
                    self.within.add_home_page()
                    self.start = False

                elif keycode[1] == 'shift':
                    self.game_grid.state = 'auto'
                    self.game_grid.change_player_pos('pawns', 'hearts')
                elif keycode[1] == '1':
                    self.game_grid.state = 'flee'
                    self.game_grid.change_player_pos('pawns', 'hearts')
                elif keycode[1] == '2':
                    self.game_grid.state = 'attack'
                    self.game_grid.change_player_pos('pawns', 'hearts')
                elif keycode[1] == '3':
                    self.game_grid.state = 'health'
                    self.game_grid.change_player_pos('pawns', 'hearts')

                else:
                    if keycode[1] == 'backspace':
                        if len(self.my_text) != 0 or self.my_text != '':
                            self.my_text = self.my_text[0:len(self.my_text) - 1]
                    else:
                        self.my_text += (keycode[1])
                        self.total_strokes += 1

                    self.check_if_similar()

    def on_keyboard_up(self, keyboard, keycode):
        self.text.middle_text.center_y = self.text.center_y
        self.text.middle_text.center_x = self.text.center_x
        self.text.left_text.font_size = self.text.Font_size
        self.text.right_text.font_size = self.text.Font_size
        self.player_details.rect.pos = (
            self.player_details.width * .5 - self.player_details.rect.size[0] * .5, self.player_details.height * .05)
        self.player_details.bar.source = assets_path['bar']
        self.player_details.bar.top = self.player_details.height * .71

    def cancel_events(self):
        # cancels all events in clock
        self.game_grid_border.cancel_events()
        self.game_grid.cancel_events()
        self.player_details.cancel_events()
        self.player_attributes.cancel_events()

    def reset(self):
        self.cancel_events()
        # will reset the instance of this class (will reset the game
        global start_time
        global time_now
        global time_passed
        global correct_words
        global accuracy
        global total_score
        global game_started
        global game_over

        start_time = True
        time_now = -1
        time_passed = 0
        game_over = False
        correct_words = 0
        accuracy = 0
        total_score = 0
        game_started = False

        self.clear_widgets()
        self.instantiate_classes()
        self.add_components()
        self.adjust_text_class()
        self.total_strokes = 0
        self.total_correct_char = 0
        self.shift_toggled = False
        self.my_text = ''


class HomePage(RelativeLayout):
    def __init__(self, within, **kwargs):
        super().__init__(**kwargs)
        # Parent class
        self.within = within
        # Instance Classes
        self.help_page = HelpPage(pos_hint={"center_x": .5, "center_y": .3},
                         size_hint=(.5, .35))
        # Components
        # Buttons
        self.title = Label(text="En Passant", font_name=os.path.join("assets\\DUNGRG__.TTF"),
                           font_size=self.height * 1.7, color=(248 / 255, 164 / 255, 37 / 255),
                           pos_hint={"center_x": .5, "center_y": .75})
        self.novice = Button(text="Novice", font_name=os.path.join("assets\\DUNGRG__.TTF"),
                             font_size=self.height*.5, size_hint=(.25, .1), pos_hint={"center_x": .5, "center_y": .53},
                             background_color=(54/255, 69/255, 93/255))
        self.master = Button(text="Master", font_name=os.path.join("assets\\DUNGRG__.TTF"),
                             font_size=self.height*.5, size_hint=(.25, .1), pos_hint={"center_x": .5, "center_y": .41},
                             background_color=(187/255, 132/255, 49/255))
        self.expert = Button(text="Expert", font_name=os.path.join("assets\\DUNGRG__.TTF"),
                             font_size=self.height*.5, size_hint=(.25, .1), pos_hint={"center_x": .5, "center_y": .29},
                             background_color=(180/255, 82/255, 73/255))
        self.help = Button(text="Help", font_name=os.path.join("assets\\DUNGRG__.TTF"),
                             font_size=self.height*.2, size_hint=(.2, .06), pos_hint={"center_x": .5, "center_y": .15},
                           background_color=(84/255, 84/255, 84/255))
        # Backgrounds
        with self.canvas.before:  # responsible for background
            Color(0, 0, 0)
            self.background = Rectangle(pos=(0, 0), size=self.size)
        # Important function
        self.add_components()
        self.bind_buttons()
        # for animations
        self.add = .05
        Clock.schedule_interval(self.animate_title, 1/10)

    def on_size(self, *args):
        self.background.pos = (0, 0)
        self.background.size = self.size

    def bind_buttons(self):
        self.novice.bind(on_press=self.button_press_handler)
        self.master.bind(on_press=self.button_press_handler)
        self.expert.bind(on_press=self.button_press_handler)
        self.help.bind(on_press=self.button_press_handler)

    def add_components(self):
        self.add_widget(self.title)
        self.add_widget(self.novice)
        self.add_widget(self.master)
        self.add_widget(self.expert)
        self.add_widget(self.help)

    def button_press_handler(self, button):
        pawn_start = 0
        health = 0
        pawn_moves_per = 0
        pawn_spawns_per = 0
        heart_spawns_per = 0
        bar_speed = 0

        if button == self.help:
            self.add_help_screen()
        else:
            if button == self.novice:
                pawn_start = 1
                health = 4
                pawn_moves_per = 4
                pawn_spawns_per = 12
                heart_spawns_per = 15
                bar_speed = 1000
            elif button == self.master:
                pawn_start = 1
                health = 3
                pawn_moves_per = 3
                pawn_spawns_per = 10
                heart_spawns_per = 15
                bar_speed = 900
            elif button == self.expert:
                pawn_start = 2
                health = 2
                pawn_moves_per = 2
                pawn_spawns_per = 8
                heart_spawns_per = 15
                bar_speed = 800

            self.within.remove_widget(self.within.home_page)
            self.within.main.pawn_start = pawn_start
            self.within.main.pawn_moves_per = pawn_moves_per
            self.within.main.health = health
            self.within.main.pawn_spawns_per = pawn_spawns_per
            self.within.main.hearts_spawns_per = heart_spawns_per
            self.within.main.bar_speed = bar_speed

            self.within.main.reset()
            self.within.main.start = True

    def animate_title(self, dt):
        if self.add == .05:
            if self.title.opacity >= 1:
                self.add = -.05
        else:
            if self.title.opacity <= .3:
                self.add = .05

        self.title.opacity += self.add

    def add_help_screen(self):
        self.help_page.open()


class HelpPage(ModalView):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.auto_dismiss = True
        self.text = Label(text='[size=40][b]Controls: [/b][/size]\n'
                               '[size=25]Shift  =  [size=20]auto  (automatic  movement)/size]\n'
                               '1  =  [size=20]flee (move away from the enemy pawns)[/size]\n'
                               '2  =  [size=20]attack (attack the nearest enemy pawn)[/size]\n'
                               '3  =  [size=20]heart (move towards the nearest heart)[/size]\n'
                               'Tab  =  [size=20]reset (difficulty remains unchanged)[/size]\n'
                               'Space  =  [size=20]Submit (submit inputted text)[/size]\n'
                               'Enter  =  [size=20]Home (go to home page)[/size][/size]', markup=True,
                          font_name=os.path.join("assets\\DUNGRG__.TTF"), halign="left", size_hint=(1, 1))

        self.add_widget(self.text)
        self.background_color = (104/255, 104/255, 104/255)


class Text(RelativeLayout):
    # Window for text interface
    orientation = 'lr-tb'

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.left_text = None
        self.right_text = None
        self.middle_text = None

        self.background_image = Image(source=assets_path['background'], allow_stretch=True, keep_ratio=False,
                                      size_hint=(1, 1))
        self.add_widget(self.background_image)
        self.Font_size = self.width / 9
        self.last_text = ''
        self.word_length = len(WORDS)
        self.text_length = 5
        self.text = []

        # Capslock text attributes
        self.capslock_label = Capslock_Text(size_hint=(.2, .2), pos_hint={"center_x": .5, "top": .95}, opacity=.8)
        self.capslock_added = False
        self.has_been_adjusted = False

    def on_size(self, *args):
        self.middle_text.font_size = self.width / 9
        self.left_text.font_size = self.width / 25
        self.right_text.font_size = self.width / 25
        self.Font_size = self.width / 25

    def fill_text(self):
        while len(self.text) < self.text_length:
            word = WORDS[random.randint(0, self.word_length)].decode('UTF-8')
            self.text.append(word)

    def display_text(self):
        self.middle_text = Label(text=self.text[0], font_name=assets_path['font'],
                                 center_x=self.center_x, center_y=self.center_y, font_size=self.width / 1.5,
                                 opacity=1, color=(103 / 255, 81 / 255, 81 / 255))
        self.right_text = Label(text=self.text[1], font_name=assets_path['font'],
                                pos_hint={'center_x': 4 / 5, 'center_y': .5}, font_size=self.Font_size,
                                size_hint=(self.width / 4, .5), opacity=.8, color=(103 / 255, 81 / 255, 81 / 255))
        self.left_text = Label(text=self.last_text, font_name=assets_path['font'],
                               pos_hint={'center_x': 1 / 5, 'center_y': .5}, font_size=self.Font_size,
                               size_hint=(self.width / 4, .5), opacity=.8, color=(103 / 255, 81 / 255, 81 / 255))

        self.add_widget(self.left_text)
        self.add_widget(self.right_text)
        self.add_widget(self.middle_text)

    def update_text(self):
        self.middle_text.text = self.text[0]
        self.right_text.text = self.text[1]
        self.left_text.text = self.last_text

        # keyboard stuff

    def check_capslock_state(self, is_capslock):
        if is_capslock:
            self.capslock_added = True
            self.add_widget(self.capslock_label)
        else:
            if self.capslock_added:
                self.remove_widget(self.capslock_label)
                self.capslock_added = False


class Capslock_Text(RelativeLayout):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.capslock_label = Label(text="Capslock Is On!", font_size=self.height * .25,
                                    font_name=os.path.join("assets\\DUNGRG__.TTF"),
                                    pos_hint={"center_x": .5, "center_y": .5})
        with self.canvas.before:
            Color(0, 0, 0, .9)
            self.background_rect = Rectangle(pos=self.pos, size=self.size)

        self.add_components()

    def on_size(self, *args):
        self.background_rect.pos = (0, 0)
        self.background_rect.size = self.size

    def add_components(self):
        self.add_widget(self.capslock_label)


class Game_Grid_Border(RelativeLayout):
    # Game grid but the border
    global time_passed
    global correct_words
    global accuracy
    global total_score

    def __init__(self, within, **kwargs):
        super().__init__(**kwargs)
        # parent classes
        self.within = within
        # components
        self.game_over_screen = Game_Over(self, pos_hint={"center_x": .5}, size_hint=(.6, .7))
        self.game_grid = Game_Grid(self, size_hint=(.95, .95),
                                   pos_hint={'center_x': .5, 'center_y': .5})
        with self.canvas.before:
            Color(rgba=(55 / 255, 10 / 255, 0 / 255, 1))
            self.background = Rectangle(pos=(0, 0), size=(self.width, self.height))
        self.start_label = Label(text="Press Any Key To Start", font_size=self.height * .6,
                                 font_name=os.path.join("assets\\DUNGRG__.TTF"), color=(0, 0, 0, .7),
                                 pos_hint={"center_x": .5, "center_y": .5})
        self.add = .05
        self.add_components()
        # event threads
        self.animate_game_over_screen_ev = None
        self.animate_start_label_ev = Clock.schedule_interval(self.animate_start_label, 1 / 15)

    def animate_start_label(self, dt):
        if self.add == .05:
            if self.start_label.opacity >= 1:
                self.add = -.05
        elif self.add == -.05:
            if self.start_label.opacity <= .6:
                self.add = .05

        self.start_label.opacity += self.add

    def animate_game_over_screen(self, dt):
        if self.game_over_screen.center_y > self.height * .5:
            self.game_over_screen.set_center_y(self.game_over_screen.center_y - self.height * .05)
        else:
            self.animate_game_over_screen_ev.cancel()

    def on_size(self, *args):
        self.background.size = (self.width, self.height)

    def add_components(self):
        self.add_widget(self.game_grid)
        self.add_widget(self.start_label)

    def add_game_over_screen(self, pieces_killed):
        self.game_over_screen.y = self.height
        self.add_widget(self.game_over_screen)
        self.animate_game_over_screen_ev = Clock.schedule_interval(self.animate_game_over_screen, 1 / 60)
        self.game_over_screen.pieces_killed = pieces_killed
        self.game_over_screen.time_survived = time_passed
        self.game_over_screen.wpm = int(correct_words / (time_passed / 60))
        self.game_over_screen.accuracy = accuracy
        self.game_over_screen.total_score = total_score

    def cancel_events(self):
        if self.animate_game_over_screen_ev:
            self.animate_game_over_screen_ev.cancel()
        self.animate_start_label_ev.cancel()


class Game_Grid(RelativeLayout):
    # Main Game Grid
    global game_over

    def __init__(self, within, **kwargs):
        super().__init__(**kwargs)
        # parent classes
        self.within = within
        self.main_root_class = self.within.within.within.within
        # for movement decisions
        self.state = 'auto'  # options are 'auto', 'flee', 'attack', 'health'
        # duration for advancement of game states
        self.add_pawn_per = 10
        self.add_hearts_per = 15
        # for interactive objects on screen
        self.heart_added = 0
        self.objects = {'hearts': []}
        self.objects_pos = {'hearts': []}
        # properties
        self.before_size = (self.width, self.height)
        self.grid_len = 10
        self.x_pos = []
        self.y_pos = []
        # For tiles
        self.rect_height = None
        self.rect_width = None
        self.rects = [[] for i in range(self.grid_len)]
        self.initialize_grid()
        # For enemy movement
        self.desired_number_enemies = {'pawns': 1}  # number of enemies
        self.e_positions = {'pawns': []}  # positions of enemies
        self.e_next_positions = {'pawns': []}  # next chosen position of enemies
        self.rect_next_move = {'pawns': []}  # rectangle representation of the enemies' next move
        self.enemies = {'pawns': []}  # enemy objects
        # for player
        self.pawn_x, self.pawn_y = 4, 4
        self.choice = [1, 0]
        with self.canvas:
            Color(rgba=(100 / 255, 226 / 255, 104 / 255, .7))
            self.move_indicator = Rectangle()
        self.pawn = Image(source=assets_path['pawn'], size_hint=(.10, .115),
                          pos=(self.x_pos[self.pawn_x], self.y_pos[self.pawn_y]))
        self.add_widget(self.pawn)
        # for kill animations
        self.damaged_pawn = False
        self.damaged_pawn_tick = 0
        self.killed_pawn = False
        self.killed_pawn_tick = 0
        # For timers
        self.pawn_movement_duration = 3
        self.time_now = None
        # For data scores
        self.pawns_killed = 0
        # event threads
        self.adjust_ev = Clock.schedule_interval(self.adjust, 1 / 60)
        self.adjust_enemies_ev = Clock.schedule_interval(self.adjust_enemies, 1 / 60)
        self.adjust_game_state_ev = Clock.schedule_interval(self.adjust_game_state, 1)
        self.animate_kill_ev = Clock.schedule_interval(self.animate_kill, 1 / 8)
        self.animate_objects_ev = Clock.schedule_interval(self.animate_objects, 1 / 8)

    def cancel_events_when_game_over(self):
        self.adjust_ev.cancel()
        self.adjust_enemies_ev.cancel()
        self.adjust_game_state_ev.cancel()

    def on_size_modified(self):
        if self.width != self.before_size[0] or self.height != self.before_size[1]:
            self.before_size = (self.width, self.height)
            self.re_adjust_player_grid()
            self.re_adjust_all_enemies()
            self.re_adjust_all_objects()

    def adjust(self, dt):
        # adjusts the position of the player
        self.pawn.pos = (self.x_pos[self.pawn_x - 1], self.y_pos[self.pawn_y - 1])

    def adjust_game_state(self, dt):
        # increment pawn amount by 1 per self.add_pawn_per
        global time_now
        global game_started
        if game_started and not game_over and time_now != -1:
            # gets the supposed amount of pawn given a specific time and updates the amount on the screen
            amount = (time.time() - time_now) // self.add_pawn_per
            self.desired_number_enemies['pawns'] = int(amount + 1)
            # add a heart per self.add_hearts_per seconds
            if int(time.time() - time_now) > ((self.heart_added + 1) * self.add_hearts_per):
                self.heart_added += 1
                x, y = self.randomize_grid_pos('pawns')
                self.objects_pos['hearts'].append([x, y])
                self.objects['hearts'].append([Image(source=assets_path['heart'][0], size_hint=(.06, .07), opacity=.9,
                                                     pos=(self.x_pos[x - 1] + (self.rect_width / 2 - self.width * .03),
                                                          self.y_pos[y - 1] + (
                                                                  self.rect_height / 2 - self.height * .035))), 0])

                self.add_widget(self.objects['hearts'][len(self.objects['hearts']) - 1][0])

    def adjust_enemies(self, dt):
        # adjusts the position of the enemies as long as the game has already started and is not over yet.
        self.update_enemy_amount('pawns')
        self.update_red_rect_amount('pawns')
        self.on_size_modified()

        if game_started and not game_over:
            update_player_move = False

            for i in range(len(self.enemies['pawns'])):
                # loops on enemy dictionaries = pawn:(imageSource, size, timeLastMoved)
                # if enough time has passed for another pawn movement
                if time.time() - self.enemies['pawns'][i][1] > self.pawn_movement_duration:
                    self.enemies['pawns'][i][1] = time.time()
                    self.update_pieces_pos('pawns', i)
                    self.change_pos_pieces('pawns', i)
                    self.update_next_move_indicator('pawns', i)
                    update_player_move = True

            if update_player_move:  # if one pawn moves, update the player next move based on that
                self.change_player_pos('pawns', 'hearts')

    def animate_kill(self, dt):  # responsible for the animation of the killing
        if self.killed_pawn:
            if self.killed_pawn_tick == 4:
                self.killed_pawn_tick = 0
                self.pawn.source = assets_path['pawn']
                self.killed_pawn = False
            else:
                self.pawn.source = assets_path['pawnKill'][self.killed_pawn_tick]
                self.killed_pawn_tick += 1

        elif self.damaged_pawn:
            if self.damaged_pawn_tick == 4:
                self.damaged_pawn_tick = 0
                self.pawn.source = assets_path['pawn']
                self.damaged_pawn = False
            else:
                self.pawn.source = assets_path['pawnDamaged'][self.damaged_pawn_tick]
                self.damaged_pawn_tick += 1

    def animate_objects(self, dt):
        for i in self.objects:
            if len(self.objects[i]) > 0:
                for j in range(len(self.objects[i])):
                    source = 'heart' if i == 'hearts' else None
                    self.objects[i][j][0].source = assets_path[source][self.objects[i][j][1]]
                    self.objects[i][j][1] += 1
                    if self.objects[i][j][1] == 4:
                        self.objects[i][j][1] = 0

    def cancel_events(self):
        self.adjust_ev.cancel()
        self.adjust_enemies_ev.cancel()
        self.adjust_game_state_ev.cancel()
        self.animate_kill_ev.cancel()
        self.animate_objects_ev.cancel()

    # ---------------------------ADJUSTS ENEMIES AND OBJECTS---------------------------------------

    def re_adjust_all_objects(self):
        for i in self.objects:
            if len(self.objects[i]) > 0:
                for j in range(len(self.objects[i])):
                    x, y = self.objects_pos[i][j]
                    self.objects[i][j][0].pos = (self.x_pos[x - 1] + (self.rect_width / 2 - self.width * .03),
                                                 self.y_pos[y - 1] + (self.rect_height / 2 - self.height * .035))

    def re_adjust_all_enemies(self):
        for i in range(len(self.rect_next_move['pawns'])):
            x, y = self.e_next_positions['pawns'][i]
            x_1, y_1 = self.e_positions['pawns'][i]
            self.rect_next_move['pawns'][i].pos = (self.x_pos[x - 1], self.y_pos[y - 1])
            self.rect_next_move['pawns'][i].size = (self.rect_width, self.rect_height)
            self.enemies['pawns'][i][0].pos = (self.x_pos[x_1 - 1], self.y_pos[y_1 - 1])

    def re_adjust_player_grid(self):
        self.remove_rects()
        self.rects = [[] for i in range(self.grid_len)]
        self.initialize_grid()
        self.move_indicator.pos = (
            self.x_pos[self.pawn_x + self.choice[0] - 1], self.y_pos[self.pawn_y + self.choice[1] - 1])
        self.move_indicator.size = (self.rect_width, self.rect_height)

    def update_red_rect_amount(self, piece):
        while len(self.rect_next_move[piece]) < len(self.enemies[piece]):
            with self.canvas:
                Color(rgba=(1, 0, 0, .3))
                self.rect_next_move[piece].append(Rectangle())

            self.update_next_move_indicator('pawns', len(self.rect_next_move[piece]) - 1)

    def update_enemy_amount(self, piece):
        enemy_len = len(self.enemies[piece])
        while enemy_len < self.desired_number_enemies[piece]:
            self.enemies[piece].append([Image(source=assets_path['epawn'], size_hint=(.10, .115)), time.time()])
            enemy_len += 1
            self.add_widget(self.enemies[piece][enemy_len - 1][0])
            pos = self.randomize_grid_pos('pawns')
            self.e_positions[piece].append(pos)
            self.e_next_positions[piece].append(pos)
            self.update_pieces_pos('pawns', enemy_len - 1)

    def randomize_grid_pos(self, piece):
        x = random.randint(1, self.grid_len)
        y = random.randint(1, self.grid_len)

        while x == self.pawn_x:
            x = random.randint(1, self.grid_len)
        while y == self.pawn_y:
            y = random.randint(1, self.grid_len)

        return [x, y]

    def change_pos_pieces(self, piece, i):
        global game_over
        # adjusts the x and y position of the enemy
        # changes the next move of the enemies based on the position of the player
        pawn_pos = (self.pawn_x, self.pawn_y)
        damaged = 0  # if equals to two, then x and y are equal
        for j in range(2):
            if self.e_positions[piece][i][j] == pawn_pos[j]:
                damaged += 1
            elif self.e_positions[piece][i][j] < pawn_pos[j]:
                self.e_next_positions[piece][i][j] = self.e_positions[piece][i][j] + 1
            elif self.e_positions[piece][i][j] > pawn_pos[j]:
                self.e_next_positions[piece][i][j] = self.e_positions[piece][i][j] - 1

        if damaged == 2:
            # randomizes the position of the enemy
            pos = self.randomize_grid_pos(piece)
            x, y = pos
            self.e_positions[piece][i] = pos
            self.e_next_positions[piece][i] = pos
            self.enemies[piece][i][0].pos = (self.x_pos[x - 1], self.y_pos[y - 1])
            # decrease the heart by 1
            self.within.within.player_attributes.adjust_hearts(True)
            # animation for being damaged
            self.damaged_pawn = True
            # if hearts == 0 then game over
            if self.within.within.player_attributes.corrupted_hearts == self.within.within.player_attributes.health:
                game_over = True
                global accuracy
                accuracy = round((self.main_root_class.total_correct_char / self.main_root_class.total_strokes) * 100,
                                 1)
                self.cancel_events_when_game_over()
                self.opacity = .2
                self.within.add_game_over_screen(self.pawns_killed)

    def update_pieces_pos(self, piece, i):
        # moves the enemy on the position specified on the e_next_positions
        x, y = self.e_next_positions[piece][i]
        if [x, y] in self.e_positions[piece] and self.e_positions[piece].index([x, y]) != i:
            pass  # don't move if something is in your pat
        else:
            self.e_positions[piece][i] = [x, y]
            self.enemies[piece][i][0].pos = [self.x_pos[x - 1], self.y_pos[y - 1]]

    def update_next_move_indicator(self, piece, i):
        # updates the position and size of the rectangular representation of the next move using the data on the
        # e_next_move_positions
        x, y = self.e_next_positions[piece][i]
        self.rect_next_move[piece][i].pos = (self.x_pos[x - 1], self.y_pos[y - 1])
        self.rect_next_move[piece][i].size = (self.rect_width, self.rect_height)

    # ----------------------------------PLAYER MOVEMENT---------------------------------------

    def move_pawn(self):
        self.pawn_x += self.choice[0]
        self.pawn_y += self.choice[1]
        self.change_player_pos('pawns', 'hearts')

    def change_player_pos(self, piece, object):
        self.check_if_there_enemy(piece)
        self.check_if_there_object(object)
        if self.state == 'auto':
            self.auto(piece)
        elif self.state == 'flee':
            self.flee(piece)
        elif self.state == 'attack':
            self.attack(piece)
        elif self.state == 'health':
            self.heart()

        self.move_indicator.pos = (
            self.x_pos[self.pawn_x + self.choice[0] - 1], self.y_pos[self.pawn_y + self.choice[1] - 1])

    def check_if_there_enemy(self, piece):  # checks if enemy is on the given position
        if [self.pawn_x, self.pawn_y] in self.e_positions[piece]:
            self.within.within.player_attributes.adjust_score(100)
            self.killed_pawn = True
            self.pawns_killed += 1
            i = self.e_positions[piece].index([self.pawn_x, self.pawn_y])
            self.remove_widget(self.enemies[piece][i][0])
            self.enemies[piece].remove(self.enemies[piece][i])
            self.e_positions[piece].remove(self.e_positions[piece][i])
            self.e_next_positions[piece].remove(self.e_next_positions[piece][i])
            with self.canvas:
                self.canvas.remove(self.rect_next_move[piece][i])
            self.rect_next_move[piece].remove(self.rect_next_move[piece][i])

    def check_if_there_object(self, object):
        if [self.pawn_x, self.pawn_y] in self.objects_pos[object]:
            i = self.objects_pos[object].index([self.pawn_x, self.pawn_y])
            self.remove_widget(self.objects[object][i][0])
            self.objects[object].remove(self.objects[object][i])
            self.objects_pos[object].remove(self.objects_pos[object][i])
            if object == 'hearts':
                self.within.within.player_attributes.adjust_hearts(False)

    # ------------------------PLAYER POSSIBLE MOVEMENTS------------------------------

    def auto(self, piece):
        if len(self.enemies[piece]) > 0:
            i = self.find_closest_enemy('pawns')
            x, y = self.e_positions[piece][i]
            enemy_pos = (x, y)
            player_pos = (self.pawn_x, self.pawn_y)
            distance = int(math.sqrt((self.pawn_x - x) ** 2 + abs(self.pawn_y - y)) ** 2)
            self.choice = [0, 0]
            if distance == 1:
                self.choice = [-(self.pawn_x - x), -(self.pawn_y - y)]
            elif len(self.objects['hearts']) > 0 and self.within.within.player_attributes.corrupted_hearts > 0:
                self.heart()
            else:
                for i in range(2):
                    if enemy_pos[i] == player_pos[i]:
                        if enemy_pos[i] > self.grid_len / 2:
                            self.choice[i] = -1
                        elif enemy_pos[i] < self.grid_len / 2:
                            self.choice[i] = 1
                        else:
                            self.choice[i] = random.choice([1, -1])

                    elif enemy_pos[i] < player_pos[i]:
                        self.choice[i] = 1
                    elif enemy_pos[i] > player_pos[i]:
                        self.choice[i] = -1

                for i in range(2):
                    if player_pos[i] + self.choice[i] > self.grid_len or player_pos[i] + self.choice[i] < 1:
                        if self.choice[0 if i == 1 else 1] == 0:
                            self.choice[i] *= -1
                        else:
                            self.choice[i] = 0
        else:
            pass

    def flee(self, piece):
        self.choice = [0, 0]
        if len(self.enemies[piece]) > 0:
            i = self.find_closest_enemy('pawns')
            x, y = self.e_positions[piece][i]
            enemy_pos = (x, y)
            player_pos = (self.pawn_x, self.pawn_y)
            for i in range(2):
                if enemy_pos[i] == player_pos[i]:
                    if enemy_pos[i] > self.grid_len / 2:
                        self.choice[i] = -1
                    elif enemy_pos[i] < self.grid_len / 2:
                        self.choice[i] = 1
                    else:
                        self.choice[i] = random.choice([1, -1])

                elif enemy_pos[i] < player_pos[i]:
                    self.choice[i] = 1
                elif enemy_pos[i] > player_pos[i]:
                    self.choice[i] = -1

            for i in range(2):
                if player_pos[i] + self.choice[i] > self.grid_len or player_pos[i] + self.choice[i] < 1:
                    if self.choice[0 if i == 1 else 1] == 0:
                        self.choice[i] *= -1
                    else:
                        self.choice[i] = 0
        else:
            pass

    def attack(self, piece):
        self.choice = [0, 0]
        if len(self.enemies[piece]) > 0:
            i = self.find_closest_enemy('pawns')
            x, y = self.e_positions[piece][i]
            enemy_pos = (x, y)
            player_pos = (self.pawn_x, self.pawn_y)
            for i in range(2):
                if player_pos[i] == enemy_pos[i]:
                    pass
                elif player_pos[i] < enemy_pos[i]:
                    self.choice[i] = 1
                elif player_pos[i] > enemy_pos[i]:
                    self.choice[i] = -1

    def heart(self):
        self.choice = [0, 0]
        if len(self.objects_pos['hearts']) > 0:
            i = self.find_closest_object('hearts')
            x, y = self.objects_pos['hearts'][i]
            heart_pos = (x, y)
            player_pos = (self.pawn_x, self.pawn_y)
            for i in range(2):
                if player_pos[i] == heart_pos[i]:
                    pass
                elif player_pos[i] < heart_pos[i]:
                    self.choice[i] = 1
                elif player_pos[i] > heart_pos[i]:
                    self.choice[i] = -1

    def find_closest_enemy(self, piece):
        closest = 0
        distance = -1

        for i in range(len(self.enemies[piece])):
            x, y = self.e_positions[piece][i]
            if (abs(self.pawn_x - x) + abs(self.pawn_y - y)) < distance or distance == -1:
                distance = int(math.sqrt((self.pawn_x - x) ** 2 + abs(self.pawn_y - y)) ** 2)
                closest = i
            if distance == 1:
                return i

        return closest

    def find_closest_object(self, object):
        closest = 0
        distance = -1

        for i in range(len(self.objects[object])):
            x, y = self.objects_pos[object][i]
            if (abs(self.pawn_x - x) + abs(self.pawn_y - y)) < distance or distance == -1:
                distance = int(math.sqrt((self.pawn_x - x) ** 2 + abs(self.pawn_y - y)) ** 2)
                closest = i
            if distance == 1:
                return i

        return closest

    def remove_rects(self):
        for i in self.rects:
            for j in i:
                with self.canvas:
                    self.canvas.before.remove(j)

    def initialize_grid(self):
        partition_x = self.width / self.grid_len
        partition_y = self.height / self.grid_len
        self.x_pos = [i * partition_x for i in range(self.grid_len)]
        self.y_pos = [i * partition_y for i in reversed(range(self.grid_len))]
        self.draw_rects()

    def draw_rects(self):
        self.rect_width = self.width / self.grid_len
        self.rect_height = self.height / self.grid_len
        with self.canvas.before:
            for i in range(self.grid_len):
                for j in range(self.grid_len):
                    Color(rgba=(102 / 255, 90 / 255, 72 / 255, 1) if (i + j) % 2 == 0 else (
                        238 / 255, 227 / 255, 203 / 255, 1))
                    self.rects[i].append(
                        Rectangle(pos=(self.x_pos[j], self.y_pos[i]), size=(self.rect_width, self.rect_height)))


class Game_Window(BoxLayout):
    # Holds the game grid border with game grid and the player attributes(time, score, hearts)
    orientation = 'vertical'

    def __init__(self, within, **kwargs):
        super().__init__(**kwargs)
        self.within = within
        self.grid_len = 10
        self.player_attributes = Player_Attributes()
        self.game_grid_border = Game_Grid_Border(self, size_hint=(1, 10))
        self.game_grid = self.game_grid_border.game_grid
        self.add_components()

    def add_components(self):
        self.add_widget(self.game_grid_border)
        self.add_widget(self.player_attributes)


class Main_Game_Window(BoxLayout):
    # Holds the game window and the player details (bar, chosen movement type)
    def __init__(self, within, **kwargs):
        super().__init__(**kwargs)
        self.within = within
        self.game_window = Game_Window(self, size_hint=(5, 1))
        self.player_details = Player_Details(self)
        self.add_components()

    def add_components(self):
        self.add_widget(self.game_window)
        self.add_widget(self.player_details)


class Player_Details(RelativeLayout):
    # Interface for bar and movement type chosen(1, 2, 3, shift)
    def __init__(self, within, **kwargs):
        super().__init__(**kwargs)
        # Parents and spouses
        self.within = within
        self.game_grid = self.within.game_window.game_grid
        # stuff
        self.rect = Rectangle()
        self.rect_height = self.height * .6
        self.previous_height = self.rect_height  # previous height of the screen before being resized
        self.rect_width = self.width * .4
        self.decrease_int = 1000
        self.decrease_rate = self.height / self.decrease_int
        # images
        self.movement_icon = Image(source=assets_path['attack'], pos_hint={'center_x': .5, 'center_y': .85},
                                   size_hint=(.8, .23), allow_stretch=True, keep_ratio=False)
        self.bar = Image(source=assets_path['bar'], pos_hint={'center_x': .53}, allow_stretch=True,
                         keep_ratio=False)
        self.bar_frame = Image(source=assets_path['barFrame'], pos_hint={'center_x': .5, 'center_y': .5},
                               allow_stretch=True,
                               keep_ratio=False, size_hint=(1, 1))
        self.draw_bar()
        # event threads
        self.update_ev = Clock.schedule_interval(self.update, 1 / 60)
        self.adjust_ev = Clock.schedule_interval(self.adjust, 1 / 30)

    def adjust(self, dt):
        self.movement_icon.source = assets_path[self.game_grid.state]

    def update(self, dt):
        self.rect.size = (self.rect.size[0], self.rect.size[1] - (self.decrease_rate * dt * 30))
        if self.rect.size[1] <= 0:
            self.rect.size = (self.rect.size[0], 0)
            # game over or punish the player or just disallow his movement

    def on_size(self, *args):
        self.rect_height = self.height * .6
        self.decrease_rate = self.height / self.decrease_int
        self.rect_width = self.width * .4
        self.rect.size = (self.rect_width, (self.rect.size[1] / self.previous_height) * self.rect_height)
        self.rect.pos = (self.width * .5 - self.rect.size[0] * .5, self.height * .06)
        self.bar.size = self.width * 2, self.rect_height * 1.2
        self.bar.top = self.height * .71
        self.previous_height = self.rect_height

    def draw_bar(self):
        self.bar.size_hint = (None, None)
        self.add_widget(self.bar_frame)
        self.add_widget(self.bar)
        self.add_widget(self.movement_icon)
        with self.canvas:
            Color(rgba=(255 / 255, 211 / 255, 132 / 255, .5))
            self.rect = Rectangle()
        self.rect.size = (self.rect_width, 0)

    def increase_bar(self, amount):
        self.rect.size = (self.rect.size[0], self.rect.size[1] + amount)
        self.bar.source = assets_path['greenBar']
        if self.rect.size[1] > self.rect_height:
            self.rect.size = (self.rect.size[0], self.rect.size[1] - self.rect_height)
            self.bar.y += 5
            return True

    def decrease_bar(self, amount):
        self.rect.size = (self.rect.size[0], self.rect.size[1] - (amount / 2))
        self.bar.source = assets_path['redBar']
        if self.rect.size[1] < 0:
            self.rect.size = (self.rect.size[0], 0)

    def cancel_events(self):
        self.update_ev.cancel()
        self.adjust_ev.cancel()


class Player_Attributes(RelativeLayout):
    # holds the score, time survived and hearts interfaces
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        with self.canvas.before:
            Color(rgba=(55 / 255, 10 / 255, 0 / 255, 1))
            self.background = Rectangle()
            Color(rgba=(30 / 255, 10 / 255, 0 / 255, 1))
            self.background1 = Rectangle()
        # for hearts
        self.health = 3
        self.hearts = []
        self.corrupted_hearts = 0
        # other stuff
        self.labels = {'score': Label(text='0', pos_hint={'x': .06, 'center_y': .5}, size_hint=(.3, .3),
                                      font_name=assets_path['labelFont'], color=(255 / 255, 211 / 255, 132 / 255)),
                       'time': Label(text='0,00', pos_hint={'x': .45, 'center_y': .5}, size_hint=(.3, .3),
                                     font_name=assets_path['labelFont'], color=(255 / 255, 211 / 255, 132 / 255))}
        self.components = {'score_icon': [Image(source=assets_path['score'][0], size_hint=(.12, .7),
                                                pos_hint={'center_x': .06, 'center_y': .5}, opacity=.8), 'score', 0],
                           'time_icon': [Image(source=assets_path['time'][0], size_hint=(.12, .7),
                                               pos_hint={'center_x': .45, 'center_y': .5}, opacity=.8), 'time', 0]}
        self.add_components()
        self.add_labels()
        # thread events
        self.animate_icons_ev = Clock.schedule_interval(self.animate_icons, 1 / 8)
        self.tick_ev = Clock.schedule_interval(self.tick, 1 / 60)

    def tick(self, dt):
        global start_time
        global time_now
        global time_passed
        global game_over
        if game_started and start_time and time_now == -1:
            time_now = time.time()
        if game_started and (not game_over) and start_time:
            time_passed = round(time.time() - time_now, 1)
            self.labels['time'].text = str(time_passed)

    def animate_icons(self, dt):
        for i in self.components:
            if i == 'heart':
                pass
            else:
                self.components[i][0].source = assets_path[self.components[i][1]][self.components[i][2]]
                self.components[i][2] += 1
                if self.components[i][2] == 4:
                    self.components[i][2] = 0

        for j in range(len(self.hearts)):
            self.hearts[j][0].source = assets_path[self.hearts[j][1]][self.hearts[j][2]]
            self.hearts[j][2] += 1
            if self.hearts[j][2] == 4:
                self.hearts[j][2] = 0

    def add_labels(self):
        for i in self.labels:
            self.add_widget(self.labels[i])

    def add_components(self):
        for i in self.components:
            if i == 'heart':
                pass
            else:
                self.add_widget(self.components[i][0])

    def add_hearts(self):
        for j in range(self.health):
            self.hearts.append([Image(source=assets_path['heart'][0],
                                      size_hint=(.12, .6),
                                      pos_hint={'center_x': 1 - (.05 * (j + 1)), 'center_y': .5},
                                      opacity=.8), 'heart', j])
            self.add_widget(self.hearts[len(self.hearts) - 1][0])

    def adjust_score(self, amount):
        global total_score

        total_score = int(self.labels['score'].text) + amount
        self.labels['score'].text = str(total_score)

    def adjust_hearts(self, decrease):
        if decrease and self.corrupted_hearts < self.health:
            self.corrupted_hearts += 1
            self.hearts[self.health - self.corrupted_hearts][1] = 'b_heart'
        elif self.corrupted_hearts > 0:
            self.hearts[self.health - self.corrupted_hearts][1] = 'heart'
            self.corrupted_hearts -= 1

    def on_size(self, *args):
        self.background.size = (self.width, self.height)
        self.background1.pos = (self.width * .02, self.height * .07)
        self.background1.size = (self.width * .96, self.height * .90)

    def cancel_events(self):
        self.animate_icons_ev.cancel()
        self.tick_ev.cancel()


class Game_Over(BoxLayout):
    # Game over popup screen
    time_survived = NumericProperty(0)
    pieces_killed = NumericProperty(0)
    wpm = NumericProperty(0)
    accuracy = NumericProperty(0)
    total_score = NumericProperty(0)

    def __init__(self, within, **kwargs):
        super().__init__(**kwargs)
        self.within = within


class EnPassant(App):
    def build(self):
        pass


def run_ep():
    EnPassant().run()


if __name__ == "__main__":
    run_ep()
