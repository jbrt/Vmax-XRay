#!/usr/bin/env python3
# coding: utf-8

import logging
from copy import deepcopy
from xlsxwriter import workbook, worksheet


class Singleton(type):
    _instances = {}

    def __call__(cls, *args, **kwargs):
        if cls not in cls._instances:
            cls._instances[cls] = super(Singleton, cls).__call__(*args, **kwargs)
        return cls._instances[cls]


class AbstractSheet(object):
    """ Abstract class that define the behavior of a Excel sheet """

    def __init__(self, book: workbook, sheet_name: worksheet):
        """ Constructor

        :param book: Workbook Excel
        :param sheet_name: name for the sheet
        """
        self._mapping = {}
        self._cells_size = {}
        self._current_row = 1

        self._logger = logging.getLogger('vmaxray')

        self._book = book
        self._sheet = book.add_worksheet(sheet_name)

    def _initialize_sheet(self):
        """ Define the sheet format """

        column_format = self._book.add_format({'bold': True,
                                               'align': 'center',
                                               'bg_color': 'D9E1F2',
                                               'top': 1,
                                               'left': 1,
                                               'right': 1,
                                               'bottom': 1})

        for label, column in self._mapping.items():
            self._sheet.set_column(column, column, self._cells_size[label])
            self._sheet.write(0, self._mapping[label], label, column_format)

        self._sheet.autofilter(0, 0, 0, max([i for i in self._mapping.values()]))
        self._sheet.freeze_panes('A2')

    def add_row(self, **data):
        """ Adding a new line to the sheet

        :param data: data for the new line (dict)
        """

        cell_format = self._book.add_format({'align': 'left'})
        for item, column in self._mapping.items():
            if item in data:
                i = data[item]
                # if 'i' contain a list of value, transform it
                value = i if not isinstance(i, list) else ', '.join(i)
                self._sheet.write(self._current_row, column, value, cell_format)

        self._current_row += 1


class InitiatorSheet(AbstractSheet, metaclass=Singleton):

    def __init__(self, book):
        super().__init__(book, sheet_name='Initiators')
        self._mapping = {'logged_in': 3,
                         'initiatorId': 0,
                         'port_flags_override': 6,
                         'maskingview': 5,
                         'flags_in_effect': 7,
                         'num_of_vols': 8,
                         'on_fabric': 4,
                         'host': 2,
                         'alias': 1}

        self._cells_size = {'logged_in': 15,
                            'initiatorId': 20,
                            'port_flags_override': 23,
                            'maskingview': 40,
                            'flags_in_effect': 90,
                            'num_of_vols': 15,
                            'on_fabric': 15,
                            'host': 20,
                            'alias': 40}
        self._initialize_sheet()


class InitiatorGroupSheet(AbstractSheet, metaclass=Singleton):

    def __init__(self, book):
        super().__init__(book, sheet_name='Initiator Groups')
        self._mapping = {'num_of_initiators': 3,
                         'initiator': 1,
                         'hostId': 0,
                         'port_flags_override': 5,
                         'consistent_lun': 2,
                         'maskingview': 4}

        self._cells_size = {'num_of_initiators': 21,
                            'initiator': 100,
                            'hostId': 30,
                            'port_flags_override': 21,
                            'consistent_lun': 21,
                            'maskingview': 40}
        self._initialize_sheet()


class InitiatorGroupCascadedSheet(AbstractSheet, metaclass=Singleton):

    def __init__(self, book):
        super().__init__(book, sheet_name='Cascaded IG')
        self._mapping = {'num_of_hosts': 4,
                         'num_of_masking_views': 5,
                         'host': 1,
                         'port_flags_override': 3,
                         'consistent_lun': 2,
                         'hostGroupId': 0}

        self._cells_size = {'num_of_hosts': 20,
                            'num_of_masking_views': 25,
                            'host': 70,
                            'port_flags_override': 25,
                            'consistent_lun': 20,
                            'hostGroupId': 40}
        self._initialize_sheet()

    def add_row(self, **data):
        """ Clean the data before call the abstract method """
        if 'host' in data:
            ig_data = deepcopy(data)
            key = 'host'
            ig_data[key] = [i['hostId'] for i in data[key]]
            super().add_row(**ig_data)


class MaskingViewSheet(AbstractSheet, metaclass=Singleton):

    def __init__(self, book):
        super().__init__(book, sheet_name='Masking Views')
        self._mapping = {'maskingViewId': 0,
                         'portGroupId': 2,
                         'storageGroupId': 3,
                         'hostId': 1}

        self._cells_size = {'maskingViewId': 40,
                            'portGroupId': 40,
                            'storageGroupId': 40,
                            'hostId': 40}
        self._initialize_sheet()


class PortGroupSheet(AbstractSheet, metaclass=Singleton):

    def __init__(self, book):
        super().__init__(book, sheet_name='Port Groups')
        self._mapping = {'portGroupId': 0,
                         'symmetrixPortKey': 1,
                         'num_of_masking_views': 3,
                         'num_of_ports': 2,
                         'maskingview': 4}

        self._cells_size = {'portGroupId': 30,
                            'symmetrixPortKey': 100,
                            'num_of_masking_views': 25,
                            'num_of_ports': 15,
                            'maskingview': 90}
        self._initialize_sheet()

    def add_row(self, **data):
        """ Clean the data before call the abstract method """
        if 'symmetrixPortKey' in data:
            pg_data = deepcopy(data)
            key = 'symmetrixPortKey'
            pg_data[key] = [':'.join(list(i.values())) for i in data[key]]
            super().add_row(**pg_data)


class SRPSheet(AbstractSheet, metaclass=Singleton):

    def __init__(self, book):
        super().__init__(book, sheet_name='SRP')
        self._mapping = {'effective_used_capacity_percent': 5,
                         'vp_saved_percent': 9,
                         'srpId': 0,
                         'total_allocated_cap_gb': 4,
                         'emulation': 1,
                         'compression_overall_ratio_to_one': 6,
                         'compression_vp_ratio_to_one': 7,
                         'total_usable_cap_gb': 2,
                         'total_subscribed_cap_gb': 3,
                         'total_snapshot_allocated_cap_gb': 8}

        self._cells_size = {'effective_used_capacity_percent': 35,
                            'vp_saved_percent': 25,
                            'srpId': 15,
                            'total_allocated_cap_gb': 25,
                            'emulation': 15,
                            'compression_overall_ratio_to_one': 35,
                            'compression_vp_ratio_to_one': 35,
                            'total_usable_cap_gb': 25,
                            'total_subscribed_cap_gb': 25,
                            'total_snapshot_allocated_cap_gb': 35}
        self._initialize_sheet()


class StorageGroupSheet(AbstractSheet, metaclass=Singleton):

    def __init__(self, book):
        super().__init__(book, sheet_name='Storage Group')
        self._mapping = {'VPSaved': 3,
                         'compressionRatio': 4,
                         'device_emulation': 5,
                         'maskingview': 9,
                         'num_of_snapshots': 11,
                         'cap_gb': 2,
                         'type': 7,
                         'num_of_parent_sgs': 10,
                         'slo': 8,
                         'storageGroupId': 0,
                         'srp': 6,
                         'num_of_child_sgs': 12,
                         'num_of_vols': 1}

        self._cells_size = {'VPSaved': 15,
                            'compressionRatio': 20,
                            'device_emulation': 21,
                            'maskingview': 50,
                            'num_of_snapshots': 21,
                            'cap_gb': 16,
                            'type': 16,
                            'num_of_parent_sgs': 20,
                            'slo': 15,
                            'storageGroupId': 25,
                            'srp': 20,
                            'num_of_child_sgs': 20,
                            'num_of_vols': 16}
        self._initialize_sheet()


class VolumeSheet(AbstractSheet, metaclass=Singleton):

    def __init__(self, book):
        super().__init__(book, sheet_name='TDEV')
        self._mapping = {'effective_wwn': 2,
                         'snapvx_target': 9,
                         'allocated_percent': 6,
                         'emulation': 12,
                         'type': 7,
                         'cap_cyl': 5,
                         'wwn': 1,
                         'cap_gb': 3,
                         'num_of_storage_groups': 13,
                         'storageGroupId': 11,
                         'volumeId': 0,
                         'cap_mb': 4,
                         'snapvx_source': 8,
                         'status': 10}

        self._cells_size = {'effective_wwn': 35,
                            'snapvx_target': 15,
                            'allocated_percent': 20,
                            'emulation': 12,
                            'type': 15,
                            'cap_cyl': 13,
                            'wwn': 35,
                            'cap_gb': 13,
                            'num_of_storage_groups': 27,
                            'storageGroupId': 40,
                            'volumeId': 15,
                            'cap_mb': 13,
                            'snapvx_source': 15,
                            'status': 15}
        self._initialize_sheet()


class VmaxSheet(AbstractSheet, metaclass=Singleton):

    def __init__(self, book):
        super().__init__(book, sheet_name='Vmax Details')
        self._mapping = {'effective_used_capacity_percent': 7,
                         'total_allocated_cap_gb': 5,
                         'VP_saved_percent': 8,
                         'default_fba_srp': 6,
                         'symmetrixId': 0,
                         'total_usable_cap_gb': 3,
                         'total_subscribed_cap_gb': 4,
                         'host_visible_device_count': 9,
                         'model': 1,
                         'compression_enabled': 10,
                         'ucode': 2,
                         'system_meta_data_used_percent': 12,
                         'device_count': 11}

        self._cells_size = {'effective_used_capacity_percent': 35,
                            'total_allocated_cap_gb': 25,
                            'VP_saved_percent': 20,
                            'default_fba_srp': 20,
                            'symmetrixId': 20,
                            'total_usable_cap_gb': 25,
                            'total_subscribed_cap_gb': 25,
                            'host_visible_device_count': 25,
                            'model': 15,
                            'compression_enabled': 20,
                            'ucode': 15,
                            'system_meta_data_used_percent': 35,
                            'device_count': 20}

        self._initialize_sheet()
