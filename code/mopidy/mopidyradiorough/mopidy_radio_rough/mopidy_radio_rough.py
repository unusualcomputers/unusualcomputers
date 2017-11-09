import pykka
from mopidy import core
import logging
from rough import GuiThread

logger = logging.getLogger()

# main mopidy extension class
# starts the gui thread stops it and passes on events to it
class MopidyRadioRough(pykka.ThreadingActor, core.CoreListener):
    def __init__(self,config,core):
        super(MopidyRadioRough, self).__init__()
        self.core = core
        self.started = False

    def __del__(self):
        pass

    def on_event(self,event,**kwargs):
        self.gui.send_to_gui(event,**kwargs)

    def on_start(self):
        logger.info('starting radio rough')
       
        if not self.started:
            self.gui = GuiThread(self.core)
            self.gui.start()
            self.started = True  

    def on_stop(self):
        logger.info('stopping radio rough')
        self.gui.stop()
 
    def on_failure(self, exception_type, exception_value, traceback):
        logger.info('*ERROR: {} {}'.format(exception_type, exception_value))

    def on_receive(self, message):
        logger.info('*MESSAGE {}'.format(message))     
