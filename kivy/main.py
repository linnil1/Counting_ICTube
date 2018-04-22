from kivy.app import App
from kivy.uix.button import Button
from kivy.uix.image import Image
from kivy.uix.label import Label
from kivy.uix.widget import  Widget
from kivy.properties import NumericProperty
from kivy.clock import Clock
from kivy.graphics.texture import Texture
import cv2

from kivy.config import Config
from kivy.lang.builder import Builder
from kivy.uix.screenmanager import ScreenManager, Screen 
Config.set('kivy', 'log_level', 'debug')
Config.set('graphics', 'width', '600')
Config.set('graphics', 'height', '800')
Config.write()

def imageProcess(img):
    hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)
    return hsv, 12

class KivyCamera(Image):
    def __init__(self, **kwargs):
        super(KivyCamera, self).__init__(**kwargs)
        # self.capture = cv2.VideoCapture(1)
        self.fps = 1
        self.event = None
        self.img = None

    def update(self, dt):
        print("update")
        frame = cv2.imread("Bubbles.jpg")
        self.img = frame
        # ret, frame = self.capture.read()
        ret = True
        if ret:
            self.toTexture(frame)

    def toTexture(self, frame):
        buf = cv2.flip(frame, 0).tostring()
        image_texture = Texture.create(
            size=(frame.shape[1], frame.shape[0]), colorfmt='bgr')
        image_texture.blit_buffer(buf, colorfmt='bgr', bufferfmt='ubyte')
        # display image from the texture
        self.texture = image_texture

    def start(self):
        if self.event == None:
            self.event = Clock.schedule_interval(self.update, 1.0 / self.fps)

    def stop(self):
        if self.event:
            self.event.cancel()
            self.event = None
        # self.capture.release()

class Menu(Screen):
    number = NumericProperty(20)

class Count(Screen):
    number = NumericProperty(20)
    tmpnum = NumericProperty(0)

    def __init__(self, **kwargs):
        super(Count, self).__init__(**kwargs)
        self.camera = self.ids.camera
        print(self.camera)

    def goCount(self, btn):
        print(btn)
        if btn.text != 'OK?':
            btn.text = "OK?"
            self.camera.stop()
            img, self.tmpnum = imageProcess(self.camera.img)
            self.camera.toTexture(img)
        else:
            btn.text = "Count It"
            self.camera.start()
            self.number = self.number + self.tmpnum

    def goMenu(self):
        self.manager.current = 'Menu';
        self.manager.get_screen('Menu').number = self.number
        # share same var by hacking


class MyApp(App):
    def build(self):
        m = Menu(name='Menu')
        c = Count(name='Count')

        sm = ScreenManager()
        sm.add_widget(c)
        sm.add_widget(m)
        sm.current = 'Menu'
        return sm

Builder.load_string("""
<Count>:
    on_enter: root.camera.start()
    on_leave: root.camera.stop()
    BoxLayout:
        size: root.size
        orientation: 'vertical'
        KivyCamera:
            id: camera
            size_hint: 1, .7
        BoxLayout:
            size_hint: 1, .3
            Button:
                size_hint: .4, 1
                on_press: root.goCount(self)
                text: 'Count It'
            Button:
                size_hint: .4, 1
                on_press: root.goMenu()
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
