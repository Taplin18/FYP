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
        self.stats = {
            "Hash family": str(self.hash_family),
            "Number of cells": str(self.num_cells),
        }
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
                self.digest = self._bits_of(self.m.digest(), self.bit_mapping)

                self.index = int(self.digest % pow(2, self.bit_mapping))

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
        self.current_area = 0
        self.value_indexes = {}

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
                self.digest = self._bits_of(self.m.digest(), self.bit_mapping)

                self.index = int(self.digest % pow(2, self.bit_mapping))

                self.current_area = self.filter[self.index]

                self.value_indexes[self.i] = [self.index, self.current_area]

        del self.buffer
        del self.digest
        del self.m
        del self.i
        del self.j
        del self.current_area
        del self.index
        del self.element

        return self.value_indexes

    def update_stats(self, precision=4):
        """
        Update the stats about the SBF filter.
        """
        self.precision = precision
        self.stats["Filter sparsity"] = str('{:.{prec}f}'.format(round(self._filter_sparsity(), self.precision),
                                                                 prec=self.precision))
        self.stats["Filter false positive probability"] = str('{:.{prec}f}'.format(round(self._filter_fpp(),
                                                                                         self.precision),
                                                                                   prec=self.precision))

    def _filter_sparsity(self):
        """
        Returns the sparsity of the entire SBF filter.
        :return: the filter sparsity
        """

        self.sparsity_sum = 0

        for self.i in range(1, self.num_areas + 1):
            self.sparsity_sum += self.area_cells[self.i]

        return 1 - (self.sparsity_sum / self.num_cells)

    def _filter_fpp(self):
        """
        Computes the a-posteriori false positive probability over the entire filter.
        :return: the filter a-posteriori fpp.
        """

        self.c = 0

        # Counts non-zero cells
        for self.i in range(1, self.num_areas + 1):
            self.c += self.area_cells[self.i]

        self.p = self.c / self.num_cells

        return pow(self.p, self.num_hashes)

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
        self.stats = {
            "Hash family": str(self.hash_family),
            "Number of cells": str(self.num_cells),
        }

    def _bits_of(self, byte, nbits):
        """
        Return the number of bits need for mapping the hash digest.
        :param byte: the hash digest.
        :param nbits: the number of bits needed for mapping
        :raise ValueError: the bytes need for truncation is greater than the number of bytes provided.
        :return: the bits needed for mapping
        """
        self.byte = byte
        self.nbits = nbits

        # Calculate where to truncate the hash digest
        self.bytes_needed = (self.nbits + 7) // 8
        if self.bytes_needed > len(self.byte):
            raise ValueError("Require {} bytes, received {}".format(self.bytes_needed, len(byte)))

        self.x = int.from_bytes(byte[:self.bytes_needed], byteorder=byteorder)
        # If there were a non-byte aligned number of bits requested,
        # shift off the excess from the right (which came from the last byte processed)
        if self.nbits % 8:
            self.x >>= 8 - self.nbits % 8

        del self.byte
        del self.nbits
        del self.bytes_needed
        return self.x

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
