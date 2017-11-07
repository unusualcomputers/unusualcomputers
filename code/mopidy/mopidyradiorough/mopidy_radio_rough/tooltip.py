# tooltip class fro tkinter
# from activestate
# http://code.activestate.com/recipes/576688-tooltip-for-tkinter/
from Tkinter import *
from time import time, localtime, strftime

class ToolTip( Toplevel ):
    """
    Provides a ToolTip widget for Tkinter.
    To apply a ToolTip to any Tkinter widget, simply pass the widget to the
    ToolTip constructor
    """ 
    def __init__( self, wdgt, msg=None, msgFunc=None, delay=1, follow=True ):
        """
        Initialize the ToolTip
        
        Arguments:
          wdgt: The widget this ToolTip is assigned to
          msg:  A static string message assigned to the ToolTip
          msgFunc: A function that retrieves a string to use as the ToolTip text
          delay:   The delay in seconds before the ToolTip appears(may be float)
          follow:  If True, the ToolTip follows motion, otherwise hides
        """
        self.wdgt = wdgt
        self.parent = self.wdgt.master                                          # The parent of the ToolTip is the parent of the ToolTips widget
        Toplevel.__init__( self, self.parent, bg='black', padx=1, pady=1 )      # Initalise the Toplevel
        self.withdraw()                                                         # Hide initially
        self.overrideredirect( True )                                           # The ToolTip Toplevel should have no frame or title bar
        
        self.msgVar = StringVar()                                               # The msgVar will contain the text displayed by the ToolTip        
        self.msg=msg
        self.msgFunc=msgFunc
        self.set_msg(None)
        self.delay = delay
        self.follow = follow
        self.visible = 0
        self.lastMotion = 0
        Message( self, textvariable=self.msgVar, bg='#FFFFDD',
                 aspect=1000 ).grid()                                           # The test of the ToolTip is displayed in a Message widget
        self.last_event=None
        self.show_func=None
        self.wdgt.bind( '<Enter>', self.spawn, '+' )                            # Add bindings to the widget.  This will NOT override bindings that the widget already has
        self.wdgt.bind( '<Leave>', self.hide, '+' )
        self.wdgt.bind( '<Motion>', self.move, '+' )
    
    def set_msg(self,event):
        if self.msg is not None and self.msg!='':
            self.msgVar.set(self.msg)
            return True
        else:
            m=self.msgFunc(event)
            if m is None or m=='':
               return False
            else:
                self.msgVar.set(m)
                return True

    def spawn( self, event=None ):
        """
        Spawn the ToolTip.  This simply makes the ToolTip eligible for display.
        Usually this is caused by entering the widget
        
        Arguments:
          event: The event that called this funciton
        """
        self.last_event=event
        self.geometry( '+%i+%i' % ( event.x_root+10, event.y_root+10 ) )        # Offset the ToolTip 10x10 pixes southwest of the pointer
        self.visible = 1
        self.show_func=self.after( int( self.delay * 1000 ), self.show )                       # The after function takes a time argument in miliseconds
        
    def show( self ):
        """
        Displays the ToolTip if the time delay has been long enough
        """
        if not self.set_msg(self.last_event):
            return
        if self.visible == 1 and time() - self.lastMotion > self.delay:
            self.visible = 2
        if self.visible == 2:
            self.deiconify()
            
    def move( self, event ):
        """
        Processes motion within the widget.
        
        Arguments:
          event: The event that called this function
        """
        self.lastMotion = time()
        self.last_event=event
        self.geometry( '+%i+%i' % ( event.x_root+10, event.y_root+10 ) )        # Offset the ToolTip 10x10 pixes southwest of the pointer
        if self.follow == False:                                                # If the follow flag is not set, motion within the widget will make the ToolTip dissapear
            self.withdraw()
            self.visible = 1
            if self.show_func is not None:
                self.after_cancel(self.show_func)
        else:
            self.show_func=self.after( int( self.delay * 1000 ), self.show )
            
    def hide( self, event=None ):
        """
        Hides the ToolTip.  Usually this is caused by leaving the widget
        
        Arguments:
          event: The event that called this function
        """
        self.visible = 0
        self.withdraw()
