from kivymd.app import MDApp
from kivymd.uix.label import MDLabel


class PruebaApp(MDApp):
  def build(self):
    return MDLabel(text="Kivy + KivyMD funcionando en Ubuntu", halign="center")


PruebaApp().run()