#!/usr/bin/env python3
# coding: utf-8

import logging
from vmaxray.errors import VmaxInventoryFactoryError
from vmaxray.vmax_iterators import *
from vmaxray.formatters import Formatter
from vmaxray.PyU4V import RestFunctions


class VmaxInventoryFactory(object):
    """ Produce the right VMAX object depend on SID number """

    def __new__(cls, *args, **kwargs):
        cls._logger = logging.getLogger('vmaxray')
        # SID information can be found in articles 000333474 & 000323234
        # Knowledge base EMC
        # Map the SID number to the right model of VMAX
        cls._classes = {'26': Vmax2InventoryCollector,
                        '49': Vmax2InventoryCollector,
                        '57': Vmax2InventoryCollector,
                        '59': Vmax2InventoryCollector,
                        '87': Vmax2InventoryCollector,
                        '67': Vmax3InventoryCollector,
                        '68': Vmax3InventoryCollector,
                        '72': Vmax3InventoryCollector,
                        '70': Vmax3InventoryCollector,
                        '75': Vmax3InventoryCollector,
                        '77': Vmax3InventoryCollector,
                        '78': Vmax3InventoryCollector}

        model_type = kwargs['sid'][5:7]  # Model type is in the middle of the SID

        if model_type not in cls._classes:
            msg = "The SID %s doesn't match with any VMAX Array model" % \
                  kwargs['sid']
            cls._logger.error(msg)
            raise VmaxInventoryFactoryError

        return cls._classes[model_type]()


class VmaxInventoryCollector(object):
    """ Abstract class that define how to inventory an array """

    def __init__(self):
        self._formatter = None
        self._array = None
        self._order = []  # have to be overload by the child
        self._logger = logging.getLogger('vmaxray')

    def _get_initiators(self):
        self._logger.info('- Extraction of initiators')
        for initiator in InitiatorIterator(self._array):
            self._formatter.add_initiator(initiator)

    def _get_initiator_groups(self):
        self._logger.info('- Extraction of initiators groups')
        for initiator in InitiatorGroupIterator(self._array):
            self._formatter.add_initiator_group(initiator)

    def _get_initiator_groups_cascaded(self):
        self._logger.info('- Extraction of cascaded initiators groups')
        for initiator in InitiatorGroupCascadedIterator(self._array):
            self._formatter.add_initiator_cascaded_group(initiator)

    def _get_port_groups(self):
        self._logger.info('- Extraction of port groups')
        for port in PortGroupIterator(self._array):
            self._formatter.add_port_group(port)

    def _get_views(self):
        self._logger.info('- Extraction of masking views')
        for view in MaskingViewGroupIterator(self._array):
            self._formatter.add_masking_view(view)

    def _get_volumes(self):
        self._logger.info('- Extraction of TDEVs')
        for volume in VolumesIterator(self._array):
            self._formatter.add_volume(volume)

    def _get_srp(self):
        self._logger.info('- Extraction of SRPs')
        for srp in SRPIterator(self._array):
            self._formatter.add_srp(srp)

    def _get_storage_groups(self):
        self._logger.info('- Extraction of storage groups')
        for sg in StorageGroupIterator(self._array):
            self._formatter.add_storage_group(sg)

    def collect(self, formatter: Formatter, array: RestFunctions):
        self._array = array
        self._formatter = formatter

        self._logger.info('Beginning of data extraction (%s)' % self._array)
        for collect_method in self._order:
            collect_method()

        self._logger.info('End of data extraction (%s)' % self._array)
        formatter.close()


class Vmax2InventoryCollector(VmaxInventoryCollector):
    """ Concrete class that define how to inventory an VMAX-2 array """

    def __init__(self):
        super().__init__()
        self._order = [self._get_volumes,
                       self._get_initiators,
                       self._get_views,
                       self._get_initiator_groups,
                       self._get_initiator_groups_cascaded,
                       self._get_port_groups,
                       self._get_storage_groups]


class Vmax3InventoryCollector(VmaxInventoryCollector):
    """ Concrete class that define how to inventory an VMAX-3 array """

    def __init__(self):
        super().__init__()
        self._formatter = None
        self._array = None
        self._order = [self._get_srp,
                       self._get_volumes,
                       self._get_initiators,
                       self._get_views,
                       self._get_initiator_groups,
                       self._get_initiator_groups_cascaded,
                       self._get_port_groups,
                       self._get_storage_groups]
