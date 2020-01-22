#!/usr/bin/env python

# 
# xHID is program for sharing keyboard, mouse and possibly other devices between computers
#
import os
import sys
import configparser
import logging
import logging.config
import argparse
import importlib
import asyncio
from time import sleep
from threading import Thread
from pprint import pprint,pformat
from queue import Queue

from classes import event, feature, field

script_path = os.path.dirname(os.path.abspath(__file__))
logging.config.fileConfig(os.path.join(script_path, 'logging.ini'))
logger = logging.getLogger('xhid.main')

VERSION="0.1-alfa"

class Task():
    method = None
    name = None
    def __init__(self, name, method):
        if not callable(method): raise Exception
        self.name = name
        self.method = method

class Dispatcher():
    __loop = None
    __tasks = []
    __event_cbs = []
    __queue = None
    queue_logger = None

    def __init__(self):
        pass

    async def queue_processor(self, queue):
        interval = 2
        if not self.queue_logger: self.queue_logger = logging.getLogger('xhid.dispatcher')
        while True: 
            item = queue.get()
            #if item[field.EVENT] not in [ event.MOUSE_MOVE ]:
                # implement some throttling for intensive events
                #self.queue_logger.info('Dispatcher:queue_processor: processing queue item: [{}]'.format(pformat(item)))
            #await asyncio.sleep(interval)
            for t in self.__event_cbs:
                t.method(item)
            queue.task_done()

    def load_module(self, module_name, module_type, params):
        logger.debug('Loading module: {}'.format(module_name))
        module = importlib.import_module('plugins.'+module_name)
        try:
            module_object = module.base_class()
            ret = module_object.initialize(module_type, params)
            try:
                self.__tasks.append(
                            Task(module_name+'_run_method', ret['register_run_method'])
                        )
            except:
                logger.debug('Module does not have run mathod.')
                pass
            try:
                self.__event_cbs.append(
                            Task(module_name+'_event_method', ret['register_event_method'])
                        )
            except:
                logger.debug('Module does not have event callback.')
                pass
        except AttributeError:
            logger.error('Plugin %s missing mandatory definitions!', module_name)
            raise
        except:
            raise

    def run(self):
        #executor = ThreadPoolExecutor(4)
        self.__queue = Queue()
        #self.__queue.put_nowait(1)
        self.__loop = asyncio.get_event_loop()
        self.__loop.set_debug(enabled=True)
        #logging.getLogger("asyncio").setLevel(logging.DEBUG)

        #self.__tasks.append(
        #            Task('dispatcher_sleeper', self.queue_processor)
        #        )
        #asyncio.run(self.sleeper())
        for task in self.__tasks:
            #pprint(task)
            logger.debug('Scheduling task: {}'.format(task.name))
            x = Thread(target=task.method, name=task.name, args=(self.__queue,)) 
            x.start()

        # start queue_processor
        asyncio.ensure_future(log_exceptions(self.queue_processor(self.__queue)))

        try:
            self.__loop.run_forever()
        except KeyboardInterrupt:
            pass
        except:
            raise

        self.__loop.close() 

async def log_exceptions(awaitable):
    try:
        return await awaitable
    except Exception:
        logger.exception("Unhandled exception")

# global dispatcher
dispatcher = Dispatcher()       

def main():
    logger.info('xhid, version %s', VERSION)

    logger.debug('reading command-line arguments')
    parser = argparse.ArgumentParser()
    parser.add_argument('-c', '--config', help='configuration file')
    parser.add_argument('-m', '--module', help='module configuration', action='append')
    args = parser.parse_args()
    #pprint(args)

    config = configparser.ConfigParser()
    if (args.config):
        logger.debug('reading configuration files(s)')
        config.read(args.config)

    # translate --module options to config
    if args.module != None:
        for module in args.module:
            mdict = module.split(':')
            mdict[0] = 'module='+mdict[0]
            mdict[1] = 'type='+mdict[1]
            xdict = dict(item.split("=") for item in mdict)
            #pprint(mdict)
            config.read_dict(
                        {'module:'+xdict['module']+'-'+xdict['type']: xdict }
                    )

    for section in config:
        if section.startswith('module:'):
            # each device must have type, module, enabled by default
            if (config[section].getboolean('enabled', True)):
                logger.info('Device {} is enabled, loading...'.format(section))
                module = config[section].get('module')
                module_type = feature.__dict__[config[section].get('type')]
                logger.info('    module: {}'.format(module))
                logger.info('      type: {}'.format(module_type.name))
                try:
                    params = {}
                    for key, val in config[section].items():
                        if val.lower() in ['true', 'yes']:
                            v = True
                        elif val.lower() in ['false', 'no']:
                            v = False
                        else:
                            v = val
                        params[key] = v
                    dispatcher.load_module( module,
                                            module_type,
                                            params
                                        )
                except:
                    logger.error('Device {} - Module cannot be loaded.'.format(section))
                    raise
    dispatcher.run()

if __name__ == '__main__':
    main()

