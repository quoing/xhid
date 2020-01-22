import logging
logger = logging.getLogger(__name__)
logger.info('Plugin evdev_mouse loading...')
from pprint import pprint,pformat
from classes import cGenericMouseOut, cParam, cDevice, feature, field, event
from time import sleep

try:
    import evdev
    from evdev import UInput, AbsInfo, ecodes, iprops
    from evdev.iprops import INPUT_PROP_DIRECT, INPUT_PROP_POINTER, INPUT_PROP_POINTING_STICK
except:
    logger.error('python-evdev plugin missing. Please install it.')

btn_map = { 1: ecodes.BTN_LEFT, 2: ecodes.BTN_MIDDLE, 3: ecodes.BTN_RIGHT }

class evdev_mouse(cGenericMouseOut):
    pos_x = 0
    pos_y = 0
    def __init__(self):
        logger.info('Plugin evdev_mouse initializing...')
        super().__init__()
        width=1920
        height=1080
        cap = {
            ecodes.EV_KEY: [
                    ecodes.BTN_LEFT,
                    ecodes.BTN_MIDDLE,
                    ecodes.BTN_RIGHT,
                    ],
            ecodes.EV_REL: [
                    ecodes.REL_WHEEL,
                    ecodes.REL_HWHEEL,
                    ],
            ecodes.EV_ABS: [
                    (ecodes.ABS_X,        AbsInfo(value=0, min=0, max=width,  fuzz=0, flat=0, resolution=0)),
                    (ecodes.ABS_Y,        AbsInfo(value=0, min=0, max=height, fuzz=0, flat=0, resolution=0)),
                    (ecodes.ABS_PRESSURE, AbsInfo(value=0, min=0, max=70,     fuzz=0, flat=0, resolution=0)),
                    ],
        }
        self.__mouse = UInput(cap, name='xHID evdev pointer', version=0x1, vendor=0x1, product=0x1, props=[])
        self.__onscreen = False
    def event_handler(self, props):
        #logger.debug('event_handler called {}'.format(pformat(props)))
        if (props[field.EVENT] == event.SCREEN_IN):
            self.__onscreen = True
        elif (props[field.EVENT] == event.SCREEN_OUT):
            self.__onscreen = False
        else:
            if (self.__onscreen):
                if (props[field.EVENT] == event.MOUSE_MOVE):
                    x = props[field.POSITION_X]
                    y = props[field.POSITION_Y]
                    self.__mouse.write(ecodes.EV_ABS, ecodes.ABS_X, x)
                    self.__mouse.write(ecodes.EV_ABS, ecodes.ABS_Y, y)
                    self.__mouse.syn()
                elif (props[field.EVENT] == event.MOUSE_BUTTON_UP or props[field.EVENT] == event.MOUSE_BUTTON_DOWN):
                    up_down = int(props[field.EVENT] == event.MOUSE_BUTTON_DOWN)
                    btn = btn_map.get(props[field.BUTTON_ID], 0)
                    if btn > 0:
                        self.__mouse.write(ecodes.EV_KEY, btn, up_down)
                        self.__mouse.syn()
                elif (props[field.EVENT] == event.MOUSE_WHEEL):
                    x = props[field.RELATIVE_X]
                    y = props[field.RELATIVE_Y]
                    self.__mouse.write(ecodes.EV_REL, ecodes.REL_WHEEL, y)
                    self.__mouse.write(ecodes.EV_REL, ecodes.REL_HWHEEL, x)
                    self.__mouse.syn()

        pass

    def initialize(self, module_type, params):
        return { 'register_event_method': self.event_handler }

base_class=evdev_mouse

