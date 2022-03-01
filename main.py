import imp
from turtle import width
from kivy.app import App
from kivy.uix.widget import Widget
from kivy.clock import Clock
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.uix.scrollview import ScrollView
from kivy.loader import Loader  
import recordquran as rq
from functools import partial
import threading

class HomePage(Widget):

    def __init__(self, **kwargs):
        super(HomePage, self).__init__(**kwargs)
        self.load_widget = Label(text='Loading 1.8 GB Model Please wait ...',font_size=30,color=(1,1,1,1),pos=(300,100))
        self.add_widget(self.load_widget)
        self.still_loading = True
        # Clock.schedule_once(partial(rq.load,self.on_load_data),5)
        self.recording_helper_2_thread = threading.Thread(target=self.recording_helper_2)
        self.loadThread = threading.Thread(target=rq.load,args=(self.on_load_data,))

        self.loadThread.start()

        
        self.added_load_widget = True

        self.juzz_amma = True
        self.juzz_amma_button = Button(text='Juzz Amma', on_press=self.select_juzz,pos=(100,450))
        self.juzz_amma_button.background_color = (0,1,0,1)
        self.add_widget(self.juzz_amma_button)

        self.whole_quran = Button(text='Whole Quran', on_press=self.select_quran,pos=(600, 450 ))
        self.whole_quran.background_color = (1,0,0,1)
        self.add_widget(self.whole_quran)

        self.record_button = Button(text='Record', pos=(300,370),on_press=self.select_record)
        self.record_button.background_color = (0,0,1,1)
        self.record_button.font_size = 30
        self.record_button.width = 200

        self.recording = False

        self.add_widget(self.record_button)


        self.record_finished = Label(text='Record Finished', pos=(100,200))
        self.record_finished.disabled = True

        self.prediction_label = Label(text=u'بسم الله', pos=(200,300),font_name='Uthmaniyan.otf')
        self.prediction_label.font_size = 24
        self.added_prediction_label = False

        self.quran_view = ScrollView(do_scroll_x=False,do_scroll_y = True, pos=(100,100),width=510,height=210)

        self.prediction_text = Label(text= u'بسم الله' ,size_hint_y=None,height=200,width=500,padding=[10,10],font_size=24,font_name='Uthmaniyan.otf')

        self.quran_view.add_widget(self.prediction_text)
        # self.add_widget(self.quran_view)

        self.added_prediction_text = False
        
    def on_load_data(self):
        self.load_widget.text = 'Loading Finished Hit Record Button to start recording'
        print('data loaded')
        self.still_loading = False
        
        

    def select_juzz(self,instance):
        self.juzz_amma = True
        print('juzz ammar selected',instance)
        self.juzz_amma_button.background_color = (0,1,0,1)
        self.whole_quran.background_color = (1,0,0,1)
    def select_quran(self,instance):
        self.juzz_amma = False
        print('whole quran selected',instance)
        self.juzz_amma_button.background_color = (1,0,0,1)
        self.whole_quran.background_color = (0,1,0,1)

    def select_record(self,instance):
        print('record selected')
        if self.still_loading:
            return
        if self.added_load_widget:
            self.remove_widget(self.load_widget)
            self.added_load_widget = False

        if self.recording:
            pass
        else:
            self.recording = True
            self.record_button.background_color = (0,1,0,1)
            Clock.schedule_once(self.record_finished_callback, 8)
            if self.added_prediction_label == True:
                self.remove_widget(self.prediction_label)
                self.added_prediction_label = False
            if self.added_prediction_text == True:
                self.remove_widget(self.quran_view)
                self.added_prediction_text = False

            self.record_button.text = 'Recording'

            self.pipeline_func = rq.pipeline_whole_quran

            if self.juzz_amma:
                self.pipeline_func = rq.pipeline_last_para
            
            Clock.schedule_once(self.recording_helper, 0.5)

    def recording_helper(self,*args):
        self.predicted = self.pipeline_func()
        self.prediction_label.text = "وتوقع:  " + self.predicted
        self.add_widget(self.prediction_label)
        self.added_prediction_label = True
        self.record_button.text = 'Recorded'
        self.record_button.background_color = (1,0,0,1)
        Clock.schedule_once(self.recording_helper_2, 1)
        # self.recording_helper_2_thread.start()
    
    def recording_helper_2(self,*args):
        self.matches, self.distance = rq.quran_finder(self.predicted,whole_quran=not self.juzz_amma)
        # self.prediction_text.text = "Quran Text:  " '\n\n'.join(self.matches)
        self.prediction_text.text = "نص القرآن:  " + self.matches[-1]
        self.add_widget(self.quran_view)
        self.added_prediction_text = True
        print("Added Quran Text")

    def record_finished_callback(self,*args):
        self.record_button.text = 'Record'
        self.record_button.background_color = (0,0,1,1)
        self.recording = False
        self.record_finished.disabled = False
        self.add_widget(self.record_finished)
        Clock.schedule_once(self.record_finished_callback_remove, 2)

    def record_finished_callback_remove(self,dt):
        self.remove_widget(self.record_finished)
        self.record_finished.disabled = True


class QuranASRApp(App):
    def build(self):
        # global root
        # root = self.root
        home = HomePage()
        return home



if __name__ == "__main__":
    QuranASRApp().run()
