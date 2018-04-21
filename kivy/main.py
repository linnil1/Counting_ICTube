from kivy.app import App
from kivy.uix.button import Button
from kivy.uix.anchorlayout import AnchorLayout
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.image import Image
from kivy.uix.label import Label
from kivy.properties import NumericProperty

# from kivy.lang.builder import Builder
# Builder.load_string(kv_string)

class Count(BoxLayout):
    number = NumericProperty(20)
    img = Image()

    def __init__(self, **kwargs):
        super(Count, self).__init__(**kwargs)
        # self.padding = self.height / 5
        self.menu()
        # self.count_main()

    def menu(self):
        self.label = Label(text=str(self.number))
        self.add_widget(self.label)
        btn_cont = Button(text="Continue")
        btn_cont.bind(on_press=self.goMain)
        self.add_widget(btn_cont)
        btn_reset = Button(text="Reset")
        btn_reset.bind(on_press=self.countReset)
        self.add_widget(btn_reset)

    def count_main(self):
        # image
        # img = Image(source='Bubbles.jpg')
        self.add_widget(self.img)

        # counting bar: count, numbers
        countbar = BoxLayout(size_hint=(1, .3))
        btn = Button(text="Count It", size_hint=(.4, 1))
        btn.bind(on_press=self.goCount)
        countbar.add_widget(btn)

        btn_menu = Button(text="Menu", size_hint=(.4, 1))
        btn_menu.bind(on_press=self.goMenu)
        countbar.add_widget(btn_menu)

        self.label = Label(text=str(self.number), size_hint=(.2, 1))
        countbar.add_widget(self.label)

        self.add_widget(countbar)

    def goMain(self, obj):
        self.clear_widgets()
        self.count_main()

    def goMenu(self, obj):
        self.clear_widgets()
        self.menu()

    def countReset(self, obj):
        print("123")
        self.number = 0
        self.label.text = str(self.number)

    def goCount(self, obj):
        print(123)
        self.number = self.number + 10
        self.label.text = str(self.number)

class MyApp(App):
    def build(self):
        return Count(orientation='vertical')


if __name__ == '__main__':
    MyApp().run()
