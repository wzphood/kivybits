import gobject
gobject.threads_init()
import pygst
pygst.require('0.10')
import gst
import gst.interfaces
from kivy.core.audio import Sound
from kivy.clock import Clock


class SoundLoader():
    """
    And 'kivy.core.audio.SoundPlayer' compatible class with mp3 audio format
    support.
    """

    @staticmethod
    def load(filename):
        """
        Load and start playing the specified *filename*.
        """
        return _AudioPlayer(filename)


class _AudioPlayer(Sound):
    """
    This class mimics the functionality of the 'kivy.core.audio.Sound' class
    but uses an alternative implementation to support mp3 on linux and android.

    Please see from kivy.core.audio.Sound class for details
    """
    # =================  Methods of the abstract Sound class ==================
    #source = StringProperty(None)  # Read only
    #volume = NumericProperty(1.)
    #state = OptionProperty('stop', options=('stop', 'play'))# read-only
    #loop = BooleanProperty(False)
    #
    #__events__ = ('on_play', 'on_stop')
    #
    #def on_source(self, instance, filename):
    #    self.unload()
    #    if filename is None:
    #        return
    #    self.load()
    #
    #def get_pos(self):
    #
    #def _get_length(self):
    #    return 0
    #
    #length = property(lambda self: self._get_length(),
    #                  doc='Get length of the sound (in seconds).')
    #
    #def seek(self, position):
    #    '''Go to the <position> (in seconds).'''
    #    pass
    #
    #def on_play(self):
    #    pass
    #
    #def on_stop(self):
    #    pass
    _length = 0

    def __init__(self, filename, **kwargs):
        super(_AudioPlayer, self).__init__(**kwargs)
        self.player = gst.element_factory_make("playbin2", "player")
        # This was in the original code, but seems unnecessary?
        ssfakesink = gst.element_factory_make("fakesink", "fakesink")
        self.bus = self.player.get_bus()
        self.bus.set_sync_handler(self._on_message)
        self.source = filename

    def _get_length(self):
        return self._length

    def _on_message(self, bus, message):
        """ Callback for the self.bus.set_sync_handler message handler """
        t = message.type.numerator
        # t= <flags GST_MESSAGE_EOS of type GstMessageType>
        if t == gst.MESSAGE_EOS:  # MESSAGE_EOS = 1
            self.stop()
        elif t == gst.MESSAGE_ERROR:
            self.player.set_state(gst.STATE_NULL)
            err, debug = message.parse_error()
            print "Player Error: %s" % err, debug
        return gst.BUS_PASS

    def play(self):
        """ Begin playing the file specified by the *source* property. """
        self.player.set_property('uri', "file://{0}".format(self.source))
        self.player.set_state(gst.STATE_PLAYING)
        self.state = 'play'
        self.player.set_property("volume", self.volume)

        def get_status(dt):
            self._length = self.player.get_last_stream_time()
            print "len=", str(self._length)

        Clock.schedule_once(get_status, 1)
        print "playe has=", dir(self.player)

    def stop(self):
        """ Stop any currently playing audio """
        self.player.set_state(gst.STATE_NULL)
        self.state = 'stop'

    def on_state(self, widget, value):
        """ Respond to a change of state """
        print "on_state=", value

    def on_volume(self, widget, value):
        """ Respond to a change of volume """
        self.player.set_property("volume", value)
