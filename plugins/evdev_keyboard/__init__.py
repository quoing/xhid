import logging
logger = logging.getLogger(__name__)
logger.info('Plugin evdev_keyboard loading...')
from pprint import pprint,pformat
from classes import cGenericKeyboardOut, cParam, cDevice, feature, field, event
from time import sleep

try:
    import evdev
    from evdev import UInput, AbsInfo, ecodes, iprops
    from evdev.iprops import INPUT_PROP_DIRECT, INPUT_PROP_POINTER, INPUT_PROP_POINTING_STICK
except:
    logger.error('python-evdev plugin missing. Please install it.')

class evdev_keyboard(cGenericKeyboardOut):
    pos_x = 0
    pos_y = 0
    def __init__(self):
        logger.info('Plugin evdev_keyboard initializing...')
        super().__init__()
        cap = {}
        self.__keyboard = UInput(cap, name='xHID evdev keyboard', version=0x1, vendor=0x1, product=0x1, props=[])
        self.__onscreen = False
    def event_handler(self, props):
        #logger.debug('event_handler called {}'.format(pformat(props)))
        if (props[field.EVENT] == event.SCREEN_IN):
            self.__onscreen = True
        elif (props[field.EVENT] == event.SCREEN_OUT):
            self.__onscreen = False
        else:
            if (self.__onscreen):
                if (props[field.EVENT] in [event.KEYBOARD_UP, event.KEYBOARD_DOWN, event.KEYBOARD_REPEAT]):
                    #logger.debug('event_handler called {}'.format(pformat(props)))
                    up_down = int(props[field.EVENT] == event.KEYBOARD_DOWN)
                    btn = props[field.BUTTON_ID]
                    self.__keyboard.write(ecodes.EV_KEY, btn, up_down)
                    self.__keyboard.syn()
        pass

    def initialize(self, module_type, params):
        return { 'register_event_method': self.event_handler }

base_class=evdev_keyboard

