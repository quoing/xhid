import socket
import ssl
import sys
from pprint import pprint, pformat
from time import sleep
import logging
from classes import event, field
from .translate import translate_tables

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

class SynergyHelloPacket():
    size = 0
    pdu = b''
    version_hi = 1 # version 1.6
    version_lo = 6
    def __init__(self, hostname):
        self.pdu = b'Synergy' + (self.version_hi).to_bytes(2, byteorder='big') + (self.version_lo).to_bytes(2, byteorder='big')
        self.pdu += len(hostname).to_bytes(4, byteorder='big') + hostname.encode()
    def raw(self):
        return len(self.pdu).to_bytes(4, byteorder='big')+self.pdu

class SynergyGenericPacket():
    size = 0
    pdu = b''
    raw = b''
    def __init__(self,pduType=None, data=None):
        if not data == None:
            # decode data
            self.raw = data
            self.size = int.from_bytes(data[0:4], byteorder='big')
            self.pdu = data[4:self.size+4]
        else:
            # encode PDU type, for new packet construction
            #self.pdu = len(pduType).to_bytes(4, byteorder='big') + pduType.encode()
            self.pdu = pduType.encode()
    def addString(self, s):
        pass
    def addInt(self, i, size=2):
        self.I(i.size)
    def I(self, i, size=2):
        #self.pdu += (size).to_bytes(size, byteorder='big')+(i).to_bytes(size, byteorder='big')
        self.pdu += (i).to_bytes(size, byteorder='big')
        return self
    def getI(self, position, size=2, signed=False):
        return int.from_bytes(self.pdu[position:position+size], signed=signed, byteorder='big')
    def raw(self):
        return len(self.pdu).to_bytes(4, byteorder='big')+self.pdu
    def isType(self, pduType):
        return self.pdu.startswith(pduType.encode())
    @property
    def type(self):
        try:
            x = self.pdu[0:4].decode()
        except:
            x = 'Cannot decode value. Raw data: {}'.format(pformat(self.pdu))
        return x

class cSynergyClient():
    log = logging.getLogger('ClassSynergyClient')
    s = None
    debug = True
    screenWidth = 1024
    screenHeight = 768
    connected = False
    timeout = 5
    reconnect_delay = 0
    __queue = None
    __params = {}

    #def __init__(self, width, height, hostname, port=24800, use_ssl=True, validate_certificate=True):
    def __init__(self):
        logger.debug('SynergyClient initialized')

    def set_variables(self, params): #hostname, port=24800, validate_certificate=True, ssl=False):
        logger.debug('Setting variables, params: {}'.format(params))
        self.__params = params
        #self.hostname = params['hostname']
        #self.port = params['port']
        #self.validate_certificate = params['validate_certificate']
        #self.use_ssl = params['use_ssl']
        #self.client_id = params['client_id']

    def reconnect(self):
        self.reconnect_delay = 0
        if (self.__params['use_ssl']):
            context = ssl.SSLContext(ssl.PROTOCOL_TLS)
            #context = ssl.SSLContext(ssl.PROTOCOL_TLSv1_2)
            if (self.__params['validate_certificate'] == False):
                context.verify_mode = ssl.CERT_NONE
                context.check_hostname = False 
            else:
                context.verify_mode = ssl.CERT_REQUIRED
                context.check_hostname = True
            context.load_default_certs()
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.settimeout(self.timeout)
        if (self.__params['use_ssl']):
            self.s = context.wrap_socket(s, server_hostname=self.__params['hostname'])
            #pprint(self.__params)
            self.s.settimeout(10)
            self.s.connect((self.__params['hostname'], self.__params['port']))
        else:
            self.s = s
        self.connected = True
        if (self.__queue): self.__queue.put({field.EVENT: event.CONNECTION, field.STATUS: True})

    def disconnect(self):
        self.s.shutdown(socket.SHUT_RD)

    def event_handler(self, props):
        #logger.info('event_handler called {}'.format(pformat(props)))
        if (props[field.EVENT] == event.SCREEN_RESOLUTION):
            x = 0
            y = 0
            warp = 0
            changed = False
            if (self.screenWidth != props[field.WIDTH]):
                self.screenWidth = props[field.WIDTH]
                changed = True
            if (self.screenHeight != props[field.HEIGHT]):
                self.screenHeight = props[field.HEIGHT]
                changed = True
            if changed:
                logger.info('SynergyClient: Resolution change')
                x = SynergyGenericPacket('DINF').I(x).I(y).I(self.screenWidth).I(self.screenHeight).I(warp).I(0).I(0)
                self.send(x.raw())

    def run(self, queue=None):
        self.__queue = queue
        while True:
            if not self.connected: 
                if (self.__queue): self.__queue.put({field.EVENT: event.CONNECTION, field.STATUS: False})
                sleep(self.reconnect_delay)
                try:
                    logger.info('Connecting to {}:{}.. using client_id: {}'.format(self.__params['hostname'], self.__params['port'], self.__params['client_id']))
                    self.reconnect()
                except:
                    logger.exception(sys.exc_info())
                    logger.warning('Cannot reconnect will retry in 10s.')
                    self.reconnect_delay = 10
                    pass
            else:
                try:
                    data = self.s.recv(4096)
                except socket.timeout:
                    logger.debug("Sending NOP packet")
                    self.send(SynergyGenericPacket('CNOP').raw())
                except ConnectionResetByPeer:
                    logger.error('Connection reset by peer. Reconnecting...')
                    self.connected = False
                    self.reconnect_delay = 0
                except:
                    logger.exception('Other exception', sys.exc_info())
                else:
                    if (len(data) > 0):
                        logger.debug('Received RAW packet: {}'.format(pformat(data)))
                        self.process_packet(data)
                    else: 
                        # nothing received, connection is broken
                        self.connected = False
                        self.reconnect_delay = 0

    def send(self, data):
        if (self.connected):
            logger.debug('Sending RAW packet: {}'.format(pformat(data)))
            try:
                self.s.send(data)
            except:
                logger.warning('Server disconnected, reconnecting in 2s.')
                self.connected = False
                self.reconnect_delay = 2
                pass

    def process_packet(self, data):
        pdu = SynergyGenericPacket(data=data)
        if pdu.isType('Synergy'):
            logger.debug('Responding HelloPacket')
            self.send(SynergyHelloPacket(self.__params['client_id']).raw())
            reply_cnop = False
        elif pdu.isType('QINF'):
            # request client information
            # DINF,x,y,Width,Height,warp,mx?,my?
            x = 0
            y = 0
            warp = 0
            x = SynergyGenericPacket('DINF').I(x).I(y).I(self.screenWidth).I(self.screenHeight).I(warp).I(0).I(0)
            self.send(x.raw())
            reply_cnop = False
        elif pdu.isType('CALV'):
            # alive?
            self.send(SynergyGenericPacket('CALV').raw())
        elif pdu.isType('DCLP'):
            # clipboard copy, ignore for now
            pass
        elif pdu.isType('CINN'):
            # control entered
            x = pdu.getI(4)
            y = pdu.getI(6)
            z = pdu.getI(8, 4)
            a = pdu.getI(12)
            #logger.debug('Event: ScreenEnter X: {} Y: {} Z: {} A: {}'.format(pformat(x), pformat(y), pformat(z), pformat(a)))
            if (self.__queue): self.__queue.put({field.EVENT : event.SCREEN_IN, field.POSITION_X: x, field.POSITION_Y: y})
        elif pdu.isType('COUT'):
            # control exit
            if (self.__queue): self.__queue.put({field.EVENT : event.SCREEN_OUT})
        # MOUSE EVENTS
        elif pdu.isType('DMMV'):
            # mouse move
            #pdu.log()
            x = pdu.getI(4)
            y = pdu.getI(6)
            #logger.info('Event: MouseMove X: {} Y: {}'.format(pformat(x), pformat(y)))
            if (self.__queue): self.__queue.put({field.EVENT : event.MOUSE_MOVE, field.POSITION_X: x, field.POSITION_Y: y})
        elif pdu.isType('DMWM'):
            #mouse wheel
            x = pdu.getI(4, signed=True)
            y = pdu.getI(6, signed=True)
            logger.debug('Event: MouseWheel X: {} Y: {}'.format(pformat(x), pformat(y)))
            if (self.__queue): self.__queue.put({field.EVENT : event.MOUSE_WHEEL, field.RELATIVE_X: x, field.RELATIVE_Y: y})
            pass
        elif pdu.isType('DMDN'):
            #mouse button down
            btn = pdu.getI(4,1)
            logger.debug('Event: Mouse Button Down Btn: {}'.format(pformat(btn)))
            #self.ed.mouseButton(btn, True)
            if (self.__queue): self.__queue.put({field.EVENT : event.MOUSE_BUTTON_DOWN, field.BUTTON_ID: btn})
            pass
        elif pdu.isType('DMUP'):
            #mouse button up
            btn = pdu.getI(4,1)
            logger.debug('Event: Mouse Button Up Btn: {}'.format(pformat(btn)))
            #self.ed.mouseButton(btn, False)
            if (self.__queue): self.__queue.put({field.EVENT : event.MOUSE_BUTTON_UP, field.BUTTON_ID: btn})
            pass
        # KEYBOARD EVENTS
        elif pdu.isType('DKDN'):
            #key down
            #pdu.log()
            mod = pdu.getI(4)
            key = pdu.getI(6)
            x = pdu.getI(8)
            logger.info('Event: KeyDOWN Mod: {} Key: {} X: {}'.format(pformat(mod), pformat(key), pformat(x)))
            if x in translate_tables[self.__params['translate']]:
                xo = x
                x = translate_tables[self.__params['translate']][x]
                logger.info('Event: KeyDOWN translation available {} -> {}'.format(pformat(xo), pformat(x)))
            if (self.__queue): self.__queue.put({field.EVENT : event.KEYBOARD_DOWN, field.BUTTON_ID: x})
            pass
        elif pdu.isType('DKRP'):
            #key repeat
            #pdu.log()
            mod = pdu.getI(4)
            key = pdu.getI(6)
            x = pdu.getI(8)
            logger.debug('Event: KeyRepeat Mod: {} Key: {} X: {}'.format(pformat(mod), pformat(key), pformat(x)))
            pass
        elif pdu.isType('DKUP'):
            #key up
            #pdu.log()
            mod = pdu.getI(4)
            key = pdu.getI(6)
            x = pdu.getI(8)
            logger.debug('Event: KeyUP Mod: {} Key: {} X: {}'.format(pformat(mod), pformat(key), pformat(x)))
            if x in translate_tables[self.__params['translate']]:
                xo = x
                x = translate_tables[self.__params['translate']][x]
                logger.info('Event: KeyUP translation available {} -> {}'.format(pformat(xo), pformat(x)))
            if (self.__queue): self.__queue.put({field.EVENT : event.KEYBOARD_UP, field.BUTTON_ID: x})
            pass
        # OTHER EVENTS
        elif pdu.isType('DSOP'):
            # Set options
            #self.send(SynergyGenericPacket('CNOP').raw())
            x = pdu.getI(4,4)
            logger.debug('Event: Set Options: {}'.format(pformat(x)))
            pass
        elif pdu.isType('CIAK'):
            # Info ACK
            pass
        elif pdu.isType('CROP'):
            # Reset Options
            pass
        elif pdu.size < 4:
            # malformed packet, ignore it
            #logger.info("x")
            pass
        else:
            #logger.error('Unknown packet: {}'.format(pdu.type))
            #logger.info(".")
            self.send(SynergyGenericPacket('CNOP').raw())
            pass


