from enum import Enum, auto
import logging

logger = logging.getLogger(__name__)
logger.info(__name__)
#logger.setLevel(logging.DEBUG)

class feature(Enum):
    CLIENT = auto()
    SERVER = auto()
    DISPLAY = auto()
    MOUSE_IN = auto()
    MOUSE_OUT = auto()
    KEYBOARD_IN = auto()
    KEYBOARD_OUT = auto()
    OTHER = auto()

class field(Enum):
    EVENT = auto()
    STATUS = auto()
    POSITION_X = auto()
    POSITION_Y = auto()
    RELATIVE_X = auto()
    RELATIVE_Y = auto()
    WIDTH = auto()
    HEIGHT = auto()
    DISPLAY_ID = auto()
    BUTTON_ID = auto()

class event(Enum):
    CONNECTION = auto()
    SCREEN_IN = auto()
    SCREEN_OUT = auto()
    SCREEN_RESOLUTION = auto()
    MOUSE_MOVE = auto()
    MOUSE_BUTTON_UP = auto()
    MOUSE_BUTTON_DOWN = auto()
    MOUSE_WHEEL = auto()
    KEYBOARD_UP = auto()
    KEYBOARD_DOWN = auto()
    KEYBOARD_REPEAT = auto()

class cParam():
    __param_name = None
    __mandatory = False
    __default = None
    __to_type = None
    def __init__(self, param_name, mandatory=False, default=None, to_type=None):
        self.__param_name = param_name
        self.__mandatory = mandatory
        self.__default = default
        self.__to_type = to_type
    @property
    def name(self): return self.__param_name
    @property
    def is_mandatory(self): return self.__mandatory
    @property
    def default(self): return self.__default
    def convert(self, value):
        if (self.__to_type != None): return eval('('+self.__to_type+')('+value+')') #type(self.__to_type)(value)
        return value

class cDevice():
    __implements = [] # list of feature-s
    params = []
    def __init__(self):
        pass
    @property
    def implements(self):
        out = ""
        return self.__implements
    def __str__(self):
        out = [','.join(name) for name,v in self.__implements]
        return out
    def add_feature(self, f):
        self.__implements.append(f)
    def validate_params(self, input_params):
        #logger.debug('Validating params, input {}'.format(input_params))
        out_params = {}
        for param in self.params:
            out_params[param.name] = None
            # check if all mandatory params are present
            if param.is_mandatory:
                if param.name not in input_params: 
                    raise Exception
                out_params[param.name] = param.convert(input_params[param.name])
            else:
                # is not mandatory
                if param.name not in input_params: 
                    out_params[param.name] = param.default
                else:
                    out_params[param.name] = param.convert(input_params[param.name])
        return out_params



class cGenericServer(cDevice):
    def __init__(self):
        self.add_feature(feature.SERVER)

class cGenericClient(cDevice):
    def __init__(self):
        self.add_feature(feature.CLIENT)

class cGenericMouseIn(cDevice):
    def __init__(self):
        self.add_feature(feature.MOUSE_IN)

class cGenericMouseOut(cDevice):
    def __init__(self):
        self.add_feature(feature.MOUSE_OUT)

class cGenericKeyboardIn(cDevice):
    def __init__(self):
        self.add_feature(feature.KEYBOARD_IN)

class cGenericKeyboardOut(cDevice):
    def __init__(self):
        self.add_feature(feature.KEYBOARD_OUT)

