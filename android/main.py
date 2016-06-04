import json
import urllib
import urllib2
from kivy.app import App
from jnius import PythonJavaClass, java_method, autoclass, cast
from threading import current_thread
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.clock import Clock
from functools import partial
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.progressbar import ProgressBar

def mainthread(func):
    def delayed_func(*args):
        Clock.schedule_once(partial(func, *args), 0)
    return delayed_func


class Generic3AxisSensor(PythonJavaClass):
    __javainterfaces__ = ['android/hardware/SensorEventListener']

    def __init__(self, app, tipo):
        super(Generic3AxisSensor, self).__init__()
        self.app = app
        self.tipo = tipo
        # print '---------------> AUTOCLASS'
        PythonActivity = autoclass('org.renpy.android.PythonActivity')
        Context = autoclass('android.content.Context')
        Sensor = autoclass('android.hardware.Sensor')
        SensorManager = autoclass('android.hardware.SensorManager')

        # print '---------------> CREATE MANAGER'
        self.manager = cast('android.hardware.SensorManager',
                PythonActivity.mActivity.getSystemService(Context.SENSOR_SERVICE))
        # print '---------------> GET DEFAUTL SENSOR'
        self.sensor = self.manager.getDefaultSensor(getattr(Sensor, tipo))

        # print '---------------> REGISTER LISTENER'
        self.manager.registerListener(self, self.sensor,
                SensorManager.SENSOR_DELAY_NORMAL)

        # print '---------------> DONE'
        # print '------> CURRENT THREAD IS', current_thread()

    @java_method('(Landroid/hardware/Sensor;I)V')
    def onAccuracyChanged(self, sensor, accuracy):
        print 'onAccuracyChanged()', sensor, accuracy

    @java_method('(Landroid/hardware/SensorEvent;)V')
    def onSensorChanged(self, event):
        # print 'onSensorChanged()', event
        # print 'onSensorChanged() event.values =', event.values
        # print '-> CURRENT THREAD IS', current_thread()
        self.app.update_values(event.values, self.tipo)


class Sensor3AxisBuffer(object):

    def __init__(self, x=0, y=0, z=0, **kwargs):
        self.x = x
        self.y = y
        self.z = z
        self.guardado = list()

    def guardar(self, x, y, z):
        self.guardado.append((x,y,z))

    def popAll(self):
        salida = list(self.guardado)
        self.guardado = list()
        return salida


class SensorApp(App):

    def start_acc(self, *args):
        if self.sensor_acce is None:
            self.sensor_acce = Generic3AxisSensor(self, 'TYPE_ACCELEROMETER')
            self.sensor_gyro = Generic3AxisSensor(self, 'TYPE_GYROSCOPE')
            self.buffer_acce = Sensor3AxisBuffer()
            self.buffer_gyro = Sensor3AxisBuffer()

    @mainthread
    def update_values(self, values, tipo, *args):
        if tipo == 'TYPE_ACCELEROMETER':
            self.acceX_lbl.text = 'acce x: {}'.format(values[0])
            self.acceY_lbl.text = 'acce y: {}'.format(values[1])
            self.acceZ_lbl.text = 'acce z: {}'.format(values[2])
            self.buffer_acce.guardar(*values)
        elif tipo == 'TYPE_GYROSCOPE':
            self.gyroX_lbl.text = 'gyro x: {}'.format(values[0])
            self.gyroY_lbl.text = 'gyro y: {}'.format(values[1])
            self.gyroZ_lbl.text = 'gyro z: {}'.format(values[2])
            self.buffer_gyro.guardar(*values)

    def enviar_servidor(self, nap):
        if self.sensor_acce:
            jdata = {'accelerometer': self.buffer_acce.popAll(),
                     'gyroscope': self.buffer_gyro.popAll()}
            jdata = {'data': json.dumps(jdata)}
            data = urllib.urlencode(jdata)
            request = urllib2.Request(
                    'http://192.168.50.22:8000/', 
                    data, 
                    {'Content-Tye':'application/json'})
            urllib2.urlopen(request)
        

    def build(self):
        #root = Label(text='Accelerometer', font_size='40sp')
        self.sensor_acce = None
        Clock.schedule_interval(self.enviar_servidor, 1)
        root = BoxLayout(orientation='vertical')
        root.add_widget(Button(text='Start', font_size='40sp',
                on_release=self.start_acc))
        root.add_widget(ProgressBar(value=0))
        root.add_widget(ProgressBar(value=0))
        root.add_widget(ProgressBar(value=0))
        self.acceX_lbl = Label(text="acce x")
        self.acceY_lbl = Label(text="acce y")
        self.acceZ_lbl = Label(text="acce z")
        self.gyroX_lbl = Label(text="gyro x")
        self.gyroY_lbl = Label(text="gyro y")
        self.gyroZ_lbl = Label(text="gyro z")
        root.add_widget(self.acceX_lbl)
        root.add_widget(self.acceY_lbl)
        root.add_widget(self.acceZ_lbl)
        root.add_widget(self.gyroX_lbl)
        root.add_widget(self.gyroY_lbl)
        root.add_widget(self.gyroZ_lbl)
        return root

    def on_pause(self):
        # print '-----------------------> PAUSE????'
        return True

if __name__ == '__main__':
    SensorApp().run()
