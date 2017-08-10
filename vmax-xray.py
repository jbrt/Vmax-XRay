#!/usr/bin/env python3
# coding: utf-8

import argparse
import logging
import sys
from vmaxray.parser import ConfigFileParser
from vmaxray.PyU4V import RestFunctions
from vmaxray.vmax_inventory import VmaxInventoryFactory
from vmaxray.formatters import XlsFormatter
from vmaxray.errors import *

__author__ = 'Julien B.'

msg = 'Vmax-XRay - Tool for Inventory a VMAX'

parser = argparse.ArgumentParser(description=msg)
parser.add_argument('config', action='store', type=str, help='config file')
parser.add_argument('-p', '--path', action='store', dest='path', type=str,
                    help='path to store the inventory file')
parser.add_argument('-d', '--debug', action='store_true', default=False,
                    help='enable the debug mode')

args = parser.parse_args()

logger = logging.getLogger('vmaxray')
stream = logging.StreamHandler()
logger.addHandler(stream)
logger.setLevel(logging.DEBUG) if args.debug else logger.setLevel(logging.INFO)


def main():
    try:
        config = ConfigFileParser(file=args.config)
    except ConfigurationError as error:
        logger.error('Error while parsing configuration: %s' % error)
        sys.exit(1)

    for array, address, user, password in config.get_arrays():
        vmax = RestFunctions(username=user, password=password,
                             server_ip=address, u4v_version='84')
        vmax.array_id = array

        # The only supported version is U4V 8.4
        # Work in progress
        version = vmax.get_uni_version()
        if not version[0]['version'].startswith('V8.4'):
            logger.error('UNISPHERE 8.4 is the only supported version')
            sys.exit(1)

        path = args.path if args.path else '.'

        try:
            filename = 'Vmax-%s.xlsx' % array
            formatter = XlsFormatter(path=path, filename=filename)

            collector = VmaxInventoryFactory(sid=array)
            collector.collect(formatter=formatter, array=vmax)
            del formatter

        except XlsFormatterError:
            sys.exit(2)
        except VmaxInventoryFactoryError:
            sys.exit(3)


if __name__ == '__main__':
    main()
