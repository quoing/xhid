import logging
from classes import cGenericMouseOut, cParam, cDevice, feature, field, event
from pprint import pprint,pformat
from time import sleep

import i3ipc as sway

logger = logging.getLogger(__name__)

class cDisplay(cDevice):
    w = 0
    h = 0
    def __init__(self, params=None):
        super().__init__()
    def set_variables(self, params): #hostname, port=24800, validate_certificate=True, ssl=False):
        logger.debug('Setting variables, params: {}'.format(params))
        self.__params = params
        #pprint(self.__params)
    def run(self, queue=None):
        polling_interval = self.__params['polling']
        self.__queue = queue
        try:
            sway_ipc = sway.Connection()
        except:
            logger.error('Cannot find sway socket, exiting.')
            raise
        while True:
            sway_outputs = sway_ipc.get_outputs()
            #pprint(sway_outputs)
            # for now only first display is handled
            if len(sway_outputs) > 0:
                if (self.h != sway_outputs[0].rect.height or self.w != sway_outputs[0].rect.width):
                    self.w = sway_outputs[0].rect.width
                    self.h = sway_outputs[0].rect.height
                    logger.info("Resolution changed w: {} h: {}".format(self.w, self.h))
                    # reporting only resolution of first display, in future we might need to compile "global" resolution based on position of displays and it sizes
                    if (self.__queue): self.__queue.put({field.EVENT: event.SCREEN_RESOLUTION, field.WIDTH: self.w, field.HEIGHT: self.h})
            sleep(polling_interval) # get screen resolution once per minute (do we actually need to get it repeatedly? We might need to report resolution changes to server.

    pass

class cMouse(cGenericMouseOut):
    sway_ipc = None
    def __init__(self):
        try:
            self.sway_ipc = sway.Connection()
        except:
            logger.error('Cannot find sway socket, exiting.')
            raise
    def event_handler(self, props):
        logger.info('event_handler called {}'.format(pformat(props)))
        if (props[field.EVENT] == event.MOUSE_MOVE or props[field.EVENT] == event.SCREEN_IN):
            x = props[field.POSITION_X]
            y = props[field.POSITION_Y]
            self.sway_ipc.command('seat - cursor set '+str(x)+' '+str(y))
        elif (props[field.EVENT] == event.MOUSE_BUTTON_UP):
            btn_map = { 1: 272, 2: 273, 3: 274 }
            btn = btn_map[props[field.BUTTON_ID]]
            self.sway_ipc.command('seat - cursor release '+str(btn))
        elif (props[field.EVENT] == event.MOUSE_BUTTON_DOWN):
            btn_map = { 1: 272, 2: 273, 3: 274 }
            btn = btn_map[props[field.BUTTON_ID]]
            self.sway_ipc.command('seat - cursor release '+str(btn))
            self.sway_ipc.command('seat - cursor press '+str(btn))
        pass

    def initialize(self, module_type, params):
       return { 'register_event_method': self.event_handler }
    pass

class cSway(cDevice):
    params = [
                cParam('socket', mandatory=False),
                cParam('polling', mandatory=False, default=60, to_type='int'),
            ]
    def __init__(self):
        pass

    def initialize(self, module_type, params):
        if module_type == feature.DISPLAY:
            try:
                self.display = cDisplay()
                self.display.set_variables(self.validate_params(params))
                return { 'register_run_method': self.display.run }
            except:
                raise
        elif module_type == feature.MOUSE_OUT:
            try:
                #self.display.set_variables(self.validate_params(params))
                self.mouse = cMouse()
                return { 'register_event_method': self.mouse.event_handler }
            except:
                raise
        elif module_type == feature.KEYBOARD_OUT:
            logger.error("Module type {} is not implemented.".format(module_type))
        else:
            logger.error("Module type {} is not implemented.".format(module_type))
        return {}

base_class=cSway


