#!/usr/bin/env python3
# coding: utf-8

import os
import logging
import xlsxwriter
from abc import ABCMeta
from vmaxray.errors import XlsFormatterError
from vmaxray.xls_sheet import *

__author__ = 'Julien B.'


class Formatter(object, metaclass=ABCMeta):
    """ Abstract class Formatter
        Purpose of that class : define the skel of a Vmax inventory class
    """

    def __init__(self):
        self._logger = logging.getLogger('vmaxray')

    def add_initiator(self, init_data):
        raise NotImplementedError

    def add_initiator_group(self, init_data):
        raise NotImplementedError

    def add_initiator_cascaded_group(self, init_data):
        raise NotImplementedError

    def add_port_group(self, pg_data):
        raise NotImplementedError

    def add_storage_group(self, sg_data):
        raise NotImplementedError

    def add_masking_view(self, view_data):
        raise NotImplementedError

    def add_thin_pool(self):
        raise NotImplementedError

    def add_srp(self, srp_data):
        raise NotImplementedError

    def add_volume(self, vol_data):
        raise NotImplementedError

    def close(self):
        raise NotImplementedError


class XlsFormatter(Formatter):
    """ Format the data under an XLS file """

    def __init__(self, path: str, filename: str):
        """Constructor
        :param path: Where create the inventory file
        :param filename: Filename of that Excel workbook
        """
        super().__init__()

        if not os.path.isdir(path):
            self._logger.error('Path incorrect (%s)' % path)
            raise XlsFormatterError

        if not os.access(path, os.W_OK):
            self._logger.error('Insufficient rights on %s' % path)
            raise XlsFormatterError

        self._logger.info('Initializing a Excel workbook (%s)' % filename)
        self._book = xlsxwriter.Workbook(path + os.path.sep + filename)
        self._book.set_properties({'title':    'EMC Vmax-XRay Inventory',
                                   'subject':  'Make an inventory of a VMAX',
                                   'author':   'Julien B.',
                                   'category': 'SAN Storage',
                                   'keywords': 'SAN, Symmetrix, VMAX',
                                   'comments': "It's better when it's not a "
                                               "manual task :-)"})

    def __del__(self):
        self._logger.debug('Now closing the workbook')
        self._book.close()

    def add_volume(self, vol_data):
        VolumeSheet(self._book).add_row(**vol_data)

    def add_initiator_cascaded_group(self, init_data):
        InitiatorGroupCascadedSheet(self._book).add_row(**init_data)

    def add_storage_group(self, sg_data):
        StorageGroupSheet(self._book).add_row(**sg_data)

    def add_masking_view(self, view_data):
        MaskingViewSheet(self._book).add_row(**view_data)

    def add_thin_pool(self):
        pass

    def add_initiator_group(self, init_data):
        InitiatorGroupSheet(self._book).add_row(**init_data)

    def add_initiator(self, init_data):
        InitiatorSheet(self._book).add_row(**init_data)

    def add_srp(self, srp_data):
        SRPSheet(self._book).add_row(**srp_data)

    def add_port_group(self, pg_data):
        PortGroupSheet(self._book).add_row(**pg_data)

    def add_array(self, array_data):
        VmaxSheet(self._book).add_row(**array_data)

    def close(self):
        self._book.close()
