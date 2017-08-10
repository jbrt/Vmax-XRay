#!/usr/bin/env python3
# coding: utf-8

import abc
import logging
from vmaxray.errors import VmaxIteratorError
from vmaxray.PyU4V.rest_univmax2 import RestFunctions

__author__ = 'Julien B.'


class VmaxObjectIterator(object, metaclass=abc.ABCMeta):
    """ Abstract class for all iterator's """

    def __init__(self, method: RestFunctions, key_id: str, key_group: str):
        """Constructor

        :param method: method used by the iterator to extract data
        :param key_id: what group of data to extract
        :param key_group: what attribute is used to describe the data
        """

        self._logger = logging.getLogger('vmaxray')
        self._get_method = method  # Method used for collecting items
        result = self._get_method()  # First extract (for testing response)

        if result[1] != 200:
            msg = 'Error while executing the request: %s' % str(result)
            self._logger.error(msg)
            raise VmaxIteratorError

        # List of groups to audit later
        self._items = result[0][key_id] if result[0] else []
        self._key_group = key_group  # Key used for filtering

    def __iter__(self):
        return self

    def __next__(self):
        try:
            one_item = self._items.pop(0)
        except IndexError:
            raise StopIteration

        return self._get_method(one_item)[0]


class StorageGroupIterator(VmaxObjectIterator):
    """ Storage Group iterator """
    def __init__(self, vmax: RestFunctions):
        super().__init__(vmax.get_sg, 'storageGroupId', 'storageGroup')


class PortGroupIterator(VmaxObjectIterator):
    """ PortGroup iterator """
    def __init__(self, vmax: RestFunctions):
        super().__init__(vmax.get_portgroups, 'portGroupId', 'portGroup')


class MaskingViewGroupIterator(VmaxObjectIterator):
    """ Masking View iterator """
    def __init__(self, vmax: RestFunctions):
        super().__init__(vmax.get_masking_views, 'maskingViewId', 'maskingView')


class InitiatorIterator(VmaxObjectIterator):
    """ Initiators iterator """
    def __init__(self, vmax: RestFunctions):
        super().__init__(vmax.get_initiators, 'initiatorId', 'initiator')


class InitiatorGroupIterator(VmaxObjectIterator):
    """ Initiator Group iterator """
    def __init__(self, vmax: RestFunctions):
        super().__init__(vmax.get_hosts, 'hostId', 'host')


class InitiatorGroupCascadedIterator(VmaxObjectIterator):
    """ Initiator Group Cascaded iterator"""
    def __init__(self, vmax: RestFunctions):
        super().__init__(vmax.get_hostgroups, 'hostGroupId', 'hostGroup')


class SRPIterator(VmaxObjectIterator):
    """ SRP iterator """
    def __init__(self, vmax: RestFunctions):
        super().__init__(vmax.get_srp, 'srpId', 'srp')


class VolumesIterator(object):
    """ Volume iterator """
    def __init__(self, vmax: RestFunctions):
        """Constructor

        :param method: method used by the iterator to extract data
        :param key_id: what group of data to extract
        :param key_group: what attribute is used to describe the data
        """
        self._logger = logging.getLogger('vmaxray')
        self._get_method = vmax.get_volumes  # Method used for collecting items
        result = self._get_method(filters={'tdev': True})  # First extract (for testing response)

        if result[1] != 200:
            msg = 'Error while executing the request: %s' % str(result)
            self._logger.error(msg)
            raise VmaxIteratorError

        self._items = result[0]['resultList']['result']  # List of groups to audit later
        self._key_group = 'volumeId'  # Key used for filtering

    def __iter__(self):
        return self

    def __next__(self):
        try:
            one_item = self._items.pop(0)
        except IndexError:
            raise StopIteration

        return self._get_method(one_item['volumeId'])[0]
