from kivy.app import App
from kivy.uix.button import Button
from kivy.uix.anchorlayout import AnchorLayout
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.image import Image
from kivy.uix.label import Label
from kivy.uix.widget import  Widget
from kivy.properties import NumericProperty

from kivy.config import Config
from kivy.lang.builder import Builder
from kivy.uix.screenmanager import ScreenManager, Screen 
Config.set('kivy', 'log_level', 'debug')
Config.write()

class Menu(Screen):
    number = NumericProperty(20)

class Count(Screen):
    number = NumericProperty(20)
    img = Image()

    def goCount(self):
        print(123)
        self.number = self.number + 10

class MyApp(App):
    def build(self):
        sm = ScreenManager()
        c = Count(name='Count')
        sm.add_widget(c)
        m = Menu(name='Menu')
        sm.add_widget(m)
        sm.current = 'Count'
        return sm

Builder.load_string("""
<Count>:
    BoxLayout:
        size: root.size
        orientation: 'vertical'
        Image:
            size_hint: 1, .7
            source: 'Bubbles.jpg'
        BoxLayout:
            size_hint: 1, .3
            Button:
                size_hint: .4, 1
                on_press: root.goCount()
                text: 'Count It'
            Button:
                size_hint: .4, 1
                on_press: root.manager.current = 'Menu'; root.manager.get_screen('Menu').number = root.number
                # share same var by hacking
                text: 'Menu'
            Label:
                size_hint: .2, 1
                text: str(root.number)
<Menu>:
    BoxLayout:
        size: root.size
        orientation: 'vertical'
        Label:
            text: str(root.number)
        Button:
            text: 'Count It'
            on_press: root.manager.current = 'Count'; root.manager.get_screen('Count').number = root.number
            # share same var by hacking
        Button:
            text: 'Reset'
            on_press: root.number = 0
""")

if __name__ == '__main__':
    MyApp().run()
