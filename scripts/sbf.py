import base64
import csv
import hashlib
from sys import byteorder
from pathlib import Path

import numpy as np


# noinspection PyAttributeOutsideInit
class sbf:

    # The maximum string length in bytes of each element given as input to be mapped in the SBF
    MAX_INPUT_SIZE = 128
    # This value defines the maximum  number of cells of the SBF:
    # MAX_BIT_MAPPING = 32 states that the SBF will be composed at most by 2^32 cells.
    # The value is the number of bits used for SBF indexing.
    MAX_BIT_MAPPING = 10
    # Utility byte value of the above MAX_BIT_MAPPING
    MAX_BYTE_MAPPING = MAX_BIT_MAPPING/8
    # The maximum number of allowed areas.
    MAX_AREA_NUMBER = 4
    # The maximum number of allowed digests
    MAX_HASH_NUMBER = 10
    # The available hash families
    HASH_FAMILIES = ['md4', 'md5', 'sha', 'sha1', 'sha256']
    # Path to hash salt file

    def __init__(self, bit_mapping, hash_family, num_hashes=1, num_areas=4):
        """
        Initialises the SBF class.
        :param bit_mapping: filter composed of 2^bit_mapping cells.
        :param hash_family: the hash family used
        :param num_hashes: number of digests to be produced
        :param num_areas: number of areas over which to build the filter
        :raise AttributeError: the arguments are out of bounds
        :except IOError: error with file
        """

        self.bit_mapping = bit_mapping
        self.hash_family = [x.lower() for x in hash_family]
        self.num_hashes = num_hashes
        self.num_areas = num_areas
        self.hash_salt_path = self._get_salt_path()

        # Argument validation
        if (self.bit_mapping <= 0) or (self.bit_mapping > self.MAX_BIT_MAPPING):
            raise AttributeError("Invalid bit mapping.")
        if (self.num_hashes <= 0) or (self.num_hashes > self.MAX_HASH_NUMBER):
            raise AttributeError("Invalid number of hash runs.")
        if (self.num_areas <= 0) or (self.num_areas > self.MAX_AREA_NUMBER):
            raise AttributeError("Invalid number of areas.")
        for self.i in self.hash_family:
            if self.i not in self.HASH_FAMILIES:
                raise AttributeError("Invalid hash family.")

        # The number of bytes required for each cell
        # As MAX_AREA_NUMBER is set to 4, 1 byte is enough
        self.cell_size = 1

        self.hash_salts = []
        # Tries to load the hash salts from file otherwise creates them
        try:
            with open(self.hash_salt_path) as self.salt_file:
                self.hash_salts = self._load_hash_salt(self.salt_file)
        except IOError:
            with open(self.hash_salt_path, 'w') as self.salt_file:
                self.hash_salts = self.create_hash_salt(self.salt_file)

        # The number of cells in the filter
        self.num_cells = pow(2, self.bit_mapping)

        # Initializes the cells to 0
        self.filter = np.array(np.repeat(0, self.num_cells), dtype=np.uint8)

        # Filter statistics initialization:
        # number of elements in the filter
        self.members = 0
        # number of collisions in the filter
        self.collisions = 0
        # number of members for each area
        self.area_members = [0] * (self.num_areas + 1)
        # number of cells for each area
        self.area_cells = [0] * (self.num_areas + 1)
        # number of self collisions for each area
        self.area_self_collisions = [0] * (self.num_areas + 1)
        # list of file from which elements have been inserted
        self.insert_file_list = []
        del self.i

    def __del__(self):
        """
        Destructs the SBF object
        """
        pass

    def __enter__(self):
        """
        Enters the SBF class (to be used with the 'with' statement).
        :except StopIteration:
        :raise RuntimeError:
        """
        try:
            return self
        except StopIteration:
            raise RuntimeError("Error during object generation")

    def __exit__(self, exc_type, exc_val, exc_tb):
        """
        Exits the SBF class (to be used with the 'with' statement).
        """
        pass

    def create_hash_salt(self, salt_file):
        """
        Creates a hash salt for each  num_hashes.
        Each input element will be combined with the salt via XOR, by the insert and check methods.
        The length of salts is MAX_INPUT_SIZE bytes.
        Hashes are stored encoded in base64.
        :param salt_file: the file where to store the hash salts.
        :return: list of hash salts.
        """

        self.salt_file = salt_file
        self.hash_salts = []

        for self.i in range(0, self.num_hashes):
            self.hash_salts.append(np.random.bytes(self.MAX_INPUT_SIZE))

        with open(self.salt_file, 'w') as self.hash_salt_file:
            for self.i in self.hash_salts:
                self.hash_salt_file.write(base64.b64encode(self.i).decode('UTF-8') + "\n")

        self.hash_salt_file.close()
        del self.hash_salt_file
        del self.salt_file

        return self.hash_salts

    def _load_hash_salt(self, salt_file):
        """
        Loads from the file in input the hash salts, one salt per line.
        Hashes are stored encoded in base64, and need to be decoded.
        :param salt_file: the file where to load the hash salts from.
        :return: list of hash salts.
        """
        self.salt_file = salt_file
        self.hash_salts = []

        self.salt_file_lines = self.salt_file.readlines()

        for self.line in self.salt_file_lines:
            self.hash_salts.append(base64.b64decode(self.line.strip()))

        del self.salt_file_lines
        del self.line
        self.salt_file.close()
        del self.salt_file

        return self.hash_salts

    def insert(self, element, area):
        """
        Inserts an element into the SBF filter.
        For each hash function, internal method set_cell is called, passing elements coupled with the area labels.
        The elements MUST be passed following the ascending-order of area labels.
        If this is not the case, the self-collision calculation (done by set_cell) will likely be wrong.
        :param element: element to be mapped (as a string)
        :param area: the area label (int)
        """
        self.element = element
        self.area = area

        # Computes the hash digest of the input 'num_hashes' times; each
        # iteration combines the input string with a different hash salt
        for self.i in self.hash_family:
            for self.j in range(0, self.num_hashes):

                # XOR byte by byte (as char by char) of the element string with the salt
                self.buffer = bytes(''.join([chr(ord(a) ^ b)
                                             for (a, b) in zip(self.element, self.hash_salts[self.j])]), 'latin-1')

                # Initializes the hash function according to the hash family
                if self.i == 'md5':
                    self.m = hashlib.md5()
                elif self.i in ['sha', 'sha1']:
                    self.m = hashlib.sha1()
                else:
                    self.m = hashlib.new(self.i)

                self.m.update(self.buffer)

                # We allow a maximum SBF mapping of 10 bit (resulting in 2^10 cells).
                # Thus, the hash digest is truncated after the first byte.
                # self.digest = self.m.digest()[:2]
                self.digest = int.from_bytes(self.m.digest()[:2], byteorder=byteorder) >> 6

                # self.index = int.from_bytes(self.digest , byteorder=byteorder) % (pow(2, self.bit_mapping))
                # self.index = int(int.from_bytes(self.digest, byteorder=byteorder) /
                #                  (pow(2, (self.MAX_BIT_MAPPING - self.bit_mapping))))
                self.index = int(self.digest / (pow(2, (self.MAX_BIT_MAPPING - self.bit_mapping))))

                self.set_cell(self.index, self.area)

        self.members += 1
        self.area_members[self.area] += 1

        del self.buffer
        del self.digest
        del self.m
        del self.i
        del self.j
        del self.element

    def insert_from_file(self):
        """
        Insert the elements from a dataset CSV file (dataset_path).
        The CSV has one area-element couple per line (in this order),
        separated by the value dataset_delimiter, which defaults to ','.
        """

        self.dataset_path = self._get_dataset_path()
        self.dataset_delimiter = ','

        with open(self.dataset_path, 'r') as self.dataset_file:
            self.dataset_reader = csv.reader(self.dataset_file, delimiter=self.dataset_delimiter)
            for self.row in self.dataset_reader:
                if int(self.row[0]) in [1, 2, 3, 4]:
                    self.insert(self.row[1], int(self.row[0]))

        self.insert_file_list.append(self.dataset_path)

        del self.dataset_delimiter
        del self.dataset_path
        self.dataset_file.close()
        del self.dataset_file
        del self.dataset_reader
        del self.row

    def set_cell(self, index, area):
        """
        Sets a cell in the filter to the specified area label.
        This method is called by insert with the cell index, and the area label.
        :param index: the index value pointing to the filter cell to be set.
        :param area: the area label to set the cell to.
        :raise AttributeError: the area label is out of bounds.
        """

        self.index = index
        self.area = area

        if (self.area <= 0) or (self.area > self.MAX_AREA_NUMBER):
            raise AttributeError("Invalid area number.")

        # Collisions handling
        self.cell_value = self.filter[self.index]
        if self.cell_value == 0:
            # Sets cell value
            self.filter[self.index] = self.area
            self.area_cells[self.area] += 1
        elif self.cell_value < self.area:
            # Sets cell value
            self.filter[self.index] = self.area
            self.collisions += 1
            self.area_cells[self.area] += 1
            self.area_cells[self.cell_value] -= 1
        elif self.cell_value == self.area:
            self.collisions += 1
            self.area_self_collisions[self.area] += 1
        else:
            # This condition should never be reached as long as elements are
            # processed in ascending order of area label. Self-collisions may
            # contain several miscalculations if elements are not passed
            # following the ascending order of area labels.
            self.collisions += 1

        del self.index
        del self.cell_value

    def check(self, element):
        """
        Checks if an element is a member of the areas mapped into the SBF.
        Verifies weather the input element belongs to one of the mapped areas.
        Returns the area label (i.e. the identifier of the set) if the element
        belongs to an area, 0 otherwise.
        :param element: the element (string) to be checked against the filter.
        :return: the area the element belongs to, or 0, if the element is not a member of any area.
        """

        self.element = element
        self.area = 0
        self.current_area = 0

        # Computes the hash digest of the input 'num_hashes' times; each
        # iteration combines the input string with a different hash salt
        for self.i in self.hash_family:
            for self.j in range(0, self.num_hashes):

                # XOR byte by byte (as char by char) of the element string with the salt
                self.buffer = bytes(''.join([chr(ord(a) ^ b)
                                             for (a, b) in zip(self.element, self.hash_salts[self.j])]), 'latin-1')

                # Initializes the hash function according to the hash family
                if self.i == 'md5':
                    self.m = hashlib.md5()
                elif self.i in ['sha', 'sha1']:
                    self.m = hashlib.sha1()
                else:
                    self.m = hashlib.new(self.i)

                self.m.update(self.buffer)

                # We allow a maximum SBF mapping of 10 bit (resulting in 2^10 cells).
                # Thus, the hash digest is truncated after the first byte.
                self.digest = self.m.digest()[:1]

                # self.index = int.from_bytes(self.digest , byteorder=byteorder) % (pow(2, self.bit_mapping))
                self.index = int(int.from_bytes(self.digest, byteorder=byteorder) /
                                 (pow(2, (self.MAX_BIT_MAPPING - self.bit_mapping))))

                self.current_area = self.filter[self.index]

                # If one hash points to an empty cell, the element does not belong
                # to any set.
                if self.current_area == 0:
                    return 0
                # Otherwise, stores the lower area label, among those which were returned
                elif self.area == 0:
                    self.area = self.current_area
                elif self.current_area < self.area:
                    self.area = self.current_area

        del self.buffer
        del self.digest
        del self.m
        del self.i
        del self.j
        del self.current_area
        del self.index
        del self.element

        return self.area

    def get_filter(self):
        """
        Returns the filter.
        :return the spacial bloom filter
        """
        return self.filter

    def get_stats(self):
        """
        Returns a dictionary of statistics of the SBF.
        :return: a dictionary of stats.
        """
        self.stats = {
            "Hash family": str(self.hash_family),
            "Number of hash runs": str(self.num_hashes),
            "Number of cells": str(self.num_cells),
            "Size in bytes":  str(self.cell_size * self.num_cells)
        }
        return self.stats

    def clear_filter(self):
        """
        Clear the filter and related information.
        """
        self.filter = np.array(np.repeat(0, self.num_cells), dtype=np.uint8)
        self.members = 0
        self.collisions = 0
        self.area_members = [0] * (self.num_areas + 1)
        self.area_cells = [0] * (self.num_areas + 1)
        self.area_self_collisions = [0] * (self.num_areas + 1)
        self.insert_file_list = []

    @staticmethod
    def _get_salt_path():
        """
        Returns the correct path to the hash salt file.
        :return: the path to the hash salt file.
        """
        aws = "/var/www/demo/hash_salt/hash_salt"
        if Path(aws).is_file():
            return aws
        else:
            return "hash_salt/hash_salt"

    @staticmethod
    def _get_dataset_path():
        """
        Returns the correct path to the cork csv.
        :return: the path to the cork csv.
        """
        aws = "/var/www/demo/dataset/cork.csv"
        if Path(aws).is_file():
            return aws
        else:
            return "dataset/cork.csv"
