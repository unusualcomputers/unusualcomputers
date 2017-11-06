import pykka
from mopidy import core
import logging
from rough import GuiThread

logger = logging.getLogger()

class MopidyRoughRadio(pykka.ThreadingActor, core.CoreListener):
    def __init__(self,config,core):
        super(MopidyRoughRadio, self).__init__()
        self.core = core
        self.started = False

    def __del__(self):
        pass

    def on_event(self,event,**kwargs):
        self.gui.send_to_gui(event,**kwargs)

    def on_start(self):
        logger.info('starting rough radio')
       
        if not self.started:
            self.gui = GuiThread(self.core)
            self.gui.start()
            self.started = True  

    def on_stop(self):
        logger.info('stopping rough radio')
        self.gui.stop()
 
    def on_failure(self, exception_type, exception_value, traceback):
        logger.info('*ERROR: {} {}'.format(exception_type, exception_value))

    def on_receive(self, message):
        logger.info('*MESSAGE {}'.format(message))     
