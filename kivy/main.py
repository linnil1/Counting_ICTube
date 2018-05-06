import kivy
from kivy.app import App
from kivy.uix.button import Button
from kivy.uix.image import Image
from kivy.uix.label import Label
from kivy.uix.widget import  Widget
from kivy.uix.camera import Camera
from kivy.properties import NumericProperty
from kivy.clock import Clock
from kivy.graphics.texture import Texture
import cv2

from kivy.config import Config
from kivy.lang.builder import Builder
from kivy.uix.screenmanager import ScreenManager, Screen 
Config.set('kivy', 'log_level', 'debug')
#Config.write()
#Config.set('graphics', 'width', '600')
#Config.set('graphics', 'height', '800')

# Get path to SD card Android
try:
    from jnius import autoclass  # SDcard Android
    import os
    Environment = autoclass('android.os.Environment')
    sdpath = Environment.getExternalStorageDirectory().getAbsolutePath()
    print("SD card")
    print(sdpath)
    imagePath = os.path.join(sdpath, 'test.png')
    print("Image Path")
    print(imagePath)
# Not on Android
except:
    imagePath = './test.png'

def imageProcess(img):
    hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)
    return hsv, 12

def rotate(img):
    (h, w) = img.shape[:2]
    a = min(h, w)
    center = (a / 2, a / 2)
    M = cv2.getRotationMatrix2D(center, -90, 1)
    return cv2.warpAffine(img, M, (h, w))

class MyCamera(Camera):
    def __init__(self, **kwargs):
        super(MyCamera, self).__init__(**kwargs)
        self.mysize = (640, 480)
        self.tmpimg = None

    def _camera_loaded(self, *largs):
        psize = self.parent.size
        self.mysize = (psize[0], int(psize[1] * 0.7))
        if kivy.platform == 'android':
            self.texture = Texture.create(size=self.mysize, colorfmt='rgb')
            self.texture_size = list(self.texture.size)
        else:
            self.texture = Texture.create(size=self.mysize, colorfmt='rgb')
            self.texture_size = list(self.texture.size)

    def getFrame(self):
        if kivy.platform == 'android':
            buf = self._camera.grab_frame()
            if buf is None:
                return None
            frame = self._camera.decode_frame(buf)
            frame = cv2.flip(rotate(frame), 0)
        else:
            ret, frame = self._camera._device.read()
            frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            # frame = rotate(frame) # debug

        if frame is None:
            return None
        return frame

    def on_tex(self, *l):
        frame = self.getFrame()
        if frame is None:
            return

        self.process_frame(frame)
        super(MyCamera, self).on_tex(*l)

    def process_frame(self, frame):
        print(frame.shape)
        print(self.mysize)
        frame = cv2.resize(frame, self.mysize)
        buf = frame.tostring()
        self.texture.blit_buffer(buf, colorfmt='rgb', bufferfmt='ubyte')

    def saveTo(self, path):
        frame = self.getFrame()
        self.tmpimg = frame.copy()
        if frame is None:
            return None
        cv2.imwrite(path, frame)
        return self.tmpimg

class Menu(Screen):
    number = NumericProperty(0)

class Count(Screen):
    number = NumericProperty(0)
    tmpnum = NumericProperty(0)

    def __init__(self, **kwargs):
        super(Count, self).__init__(**kwargs)
        self.camera = self.ids.camera
        self.camera.play = False

    def goCount(self, btn):
        if btn.text == 'Count It':
            img  = self.camera.saveTo(imagePath)
            self.camera.play = False
            if img is None:
                print("Error")
            img, self.tmpnum = imageProcess(img)
            self.camera.process_frame(img)
            btn.text = str(self.tmpnum) + " OK?"
        else:
            btn.text = "Count It"
            self.number = self.number + self.tmpnum
            self.camera.play = True

    def goMenu(self):
        self.manager.current = 'Menu';
        self.manager.get_screen('Menu').number = self.number
        # share same var by hacking

    def enter(self):
        # self.camera.play()
        self.camera.play = True
        self.ids.id_count.text = "Count It"

    def leave(self):
        self.camera.play = False


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
    on_enter: root.enter()
    on_leave: root.leave()
    BoxLayout:
        size: root.size
        orientation: 'vertical'
        MyCamera:
            id: camera
            index: 0
            resolution: (640, 480)
            size_hint: 1, .7
        BoxLayout:
            size_hint: 1, .3
            Button:
                id: id_count
                size_hint: .4, 1
                on_press: root.goCount(self)
                text: 'Count It'
            Button:
                size_hint: .4, 1
                on_press: root.goMenu()
                text: 'Menu'
            BoxLayout:
                id: num
                size_hint: .2, 1
                orientation: 'vertical'
                Label:
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
