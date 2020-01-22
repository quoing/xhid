import logging
#from time import sleep
import asyncio
from random import uniform
from classes import cGenericClient, cParam, cDevice, feature
from pprint import pprint,pformat
from time import sleep
from .client import cSynergyClient

import socket
import ssl

logger = logging.getLogger(__name__)
#logger.info('Plugin synergy loading...')

class cSynergy(cDevice):
    params = [
                cParam('hostname', mandatory=True),
                cParam('port', mandatory=False, default=24800, to_type='int'),
                cParam('use_ssl', mandatory=False, default=True),
                cParam('validate_certificate', mandatory=False, default=False),
                cParam('client_id', mandatory=False, default='DEFAULT_CLIENT'), # TODO: replace default with hostname
                cParam('translate', mandatory=False, default='default'), 
            ]
    def __init__(self):
        pass

    def initialize(self, module_type, params):
        if module_type == feature.CLIENT:
            logger.info('Creating synergy client')
            self.client = cSynergyClient()
            try:
                #self.validate_params
                #vparams=self.validate_params(params)
                #pprint(vparams)
                self.client.set_variables(self.validate_params(params))
                return { 'register_run_method': self.client.run, 
                         'register_event_method': self.client.event_handler
                        }
            except:
                raise
        elif module_type == feature.SERVER:
            logger.error("Synergy server is not /yet/ implemented.")
        else:
            logger.error("Module type {} is not implemented.".format(module_type))
        return {}

base_class=cSynergy

