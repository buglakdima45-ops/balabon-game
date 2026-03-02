from kivy.app import App
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.widget import Widget
from kivy.clock import Clock
from kivy.graphics import Color, Rectangle, Ellipse
from kivy.core.window import Window

# Налаштування скінів: (Колір тіла, Колір очей)
SKINS = {
    "Balabon (Black)": [(0.1, 0.1, 0.1), (1, 1, 1)],
    "Snowball (White)": [(0.9, 0.9, 0.9), (0, 0, 0)],
    "Ninja (Dark)": [(0, 0, 0), (1, 0, 0)]
}

class GameData:
    current_skin = "Balabon (Black)"

# --- Клас кота Балабона ---
class BalabonWidget(Widget):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.size = (100, 100)
        self.velocity_y = 0
        self.gravity = -0.9

    def draw(self):
        self.canvas.clear()
        body_col, eye_col = SKINS[GameData.current_skin]
        with self.canvas:
            # Тіло
            Color(*body_col)
            Rectangle(pos=self.pos, size=self.size)
            # Вушка
            Rectangle(pos=(self.x + 5, self.y + 90), size=(30, 40))
            Rectangle(pos=(self.x + 65, self.y + 90), size=(30, 40))
            # Очі
            Color(*eye_col)
            Ellipse(pos=(self.x + 20, self.y + 55), size=(20, 20))
            Ellipse(pos=(self.x + 60, self.y + 55), size=(20, 20))

# --- Екран гри ---
class GameScreen(Screen):
    def on_enter(self):
        self.layout = Widget()
        self.add_widget(self.layout)
        
        with self.layout.canvas.before:
            Color(0.8, 0.8, 0.8) # Підлога
            self.floor = Rectangle(pos=(0, 0), size=(Window.width, 120))

        self.cat = BalabonWidget(pos=(150, 120))
        self.layout.add_widget(self.cat)
        
        self.obstacles = []
        self.game_speed = 8
        self.score = 0
        self.score_label = Label(text="Score: 0", pos=(100, Window.height-150), font_size=40, color=(0,0,0,1))
        self.add_widget(self.score_label)
        
        self.game_event = Clock.schedule_interval(self.update, 1.0/60.0)
        self.spawn_event = Clock.schedule_interval(self.spawn_obstacle, 1.5)

    def spawn_obstacle(self, dt):
        with self.layout.canvas:
            Color(0.2, 0.2, 0.2)
            obs = Rectangle(pos=(Window.width, 120), size=(70, 70))
        self.obstacles.append(obs)

    def update(self, dt):
        self.cat.velocity_y += self.cat.gravity
        self.cat.y += self.cat.velocity_y
        
        if self.cat.y <= 120:
            self.cat.y = 120
            self.cat.velocity_y = 0
            
        self.cat.draw()

        for obs in self.obstacles[:]:
            obs.pos = (obs.pos[0] - self.game_speed, obs.pos[1])
            
            # Перевірка зіткнення
            if self.cat.collide_point(obs.pos[0], obs.pos[1]) or \
               self.cat.collide_point(obs.pos[0]+70, obs.pos[1]+70):
                self.game_over()

            if obs.pos[0] < -70:
                self.obstacles.remove(obs)
                self.score += 1
                self.score_label.text = f"Score: {self.score}"
                self.game_speed += 0.2 # Кожен блок швидше!

    def on_touch_down(self, touch):
        if self.cat.y <= 125:
            self.cat.velocity_y = 20

    def game_over(self):
        Clock.unschedule(self.game_event)
        Clock.unschedule(self.spawn_event)
        self.manager.current = 'menu'

# --- Головне меню ---
class MenuScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        layout = BoxLayout(orientation='vertical', padding=100, spacing=30)
        with self.canvas.before:
            Color(1, 1, 1)
            self.bg = Rectangle(pos=(0,0), size=(2000, 2000))

        layout.add_widget(Label(text="BALABON DASH", font_size=60, color=(0,0,0,1), bold=True))
        
        btn_play = Button(text="ГРАТИ", background_color=(0,0,0,1), font_size=30)
        btn_play.bind(on_press=lambda x: setattr(self.manager, 'current', 'game'))
        
        btn_shop = Button(text="МАГАЗИН", background_color=(0.3, 0.3, 0.3, 1), font_size=30)
        btn_shop.bind(on_press=lambda x: setattr(self.manager, 'current', 'shop'))
        
        layout.add_widget(btn_play)
        layout.add_widget(btn_shop)
        self.add_widget(layout)

# --- Магазин ---
class ShopScreen(Screen):
    def on_enter(self):
        self.clear_widgets()
        layout = BoxLayout(orientation='vertical', padding=50, spacing=20)
        with self.canvas.before:
            Color(0.9, 0.9, 0.9)
            Rectangle(pos=(0,0), size=(2000, 2000))

        layout.add_widget(Label(text="ОБЕРИ КОТА", font_size=40, color=(0,0,0,1)))
        
        for name in SKINS.keys():
            txt = f"{name} [ОБРАНО]" if GameData.current_skin == name else name
            btn = Button(text=txt, background_color=(0,0,0,1))
            btn.bind(on_press=self.select_skin)
            layout.add_widget(btn)
            
        back = Button(text="НАЗАД", size_hint=(1, 0.5))
        back.bind(on_press=lambda x: setattr(self.manager, 'current', 'menu'))
        layout.add_widget(back)
        self.add_widget(layout)

    def select_skin(self, instance):
        name = instance.text.replace(" [ОБРАНО]", "")
        GameData.current_skin = name
        self.on_enter()

# --- Запуск ---
class BalabonApp(App):
    def build(self):
        sm = ScreenManager()
        sm.add_widget(MenuScreen(name='menu'))
        sm.add_widget(GameScreen(name='game'))
        sm.add_widget(ShopScreen(name='shop'))
        return sm

if __name__ == '__main__':
    BalabonApp().run()
