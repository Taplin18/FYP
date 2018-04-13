import base64
import csv
import sys
import hashlib
from sys import byteorder
from pathlib import Path
from random import randint

import numpy as np

if sys.version_info < (3, 6):
    import sha3


class sbf:

    # This value defines the maximum  number of cells of the SBF:
    # MAX_BIT_MAPPING = 32 states that the SBF will be composed at most by 2^32 cells.
    # The value is the number of bits used for SBF indexing.
    MAX_BIT_MAPPING = 10
    # Utility byte value of the above MAX_BIT_MAPPING
    MAX_BYTE_MAPPING = MAX_BIT_MAPPING/8
    # The maximum number of allowed digests
    MAX_HASH_NUMBER = 10
    # The available hash families
    HASH_FAMILIES = ['md4', 'md5', 'sha1', 'sha224', 'sha256', 'sha384', 'sha512', 'sha3_256', 'sha3_512']

    def __init__(self, hash_family, bit_mapping=10, num_areas=4):
        """
        Initialises the SBF class.
        :param bit_mapping: filter composed of 2^bit_mapping cells.
        :param hash_family: the hash family used
        :param num_areas: number of areas over which to build the filter
        :raise AttributeError: the arguments are out of bounds
        :except IOError: error with file
        """

        self.bit_mapping = bit_mapping
        self.hash_family = [x.lower() for x in hash_family]
        self.num_areas = num_areas
        self.hash_salt_path = self._get_salt_path()

        # Argument validation
        if (self.bit_mapping <= 0) or (self.bit_mapping > self.MAX_BIT_MAPPING):
            raise AttributeError("Invalid bit mapping.")
        for self.i in self.hash_family:
            if self.i not in self.HASH_FAMILIES:
                raise AttributeError("Invalid hash family.")

        # The number of bytes required for each cell
        self.cell_size = 1

        self.hash_salts = []
        # Tries to load the hash salts from file otherwise creates them
        try:
            with open(self.hash_salt_path) as self.salt_file:
                self.hash_salts = self._load_hash_salt(self.salt_file)
        except IOError:
            raise IOError("Error opening hash salts")

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
        # all the coordinates in the csv
        self.all_coors = []
        self._coors()
        # incorrect SBF values
        self.incorrect_areas = {}
        # fpp SBF values
        self.fp_coor = {}
        # initial stats of filter
        self.stats = {
            "Hash Family": str(self.hash_family),
            "Number of Cells": str(self.num_cells),
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

    def _insert(self, element, area):
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

        for self.i in self.hash_family:

            # XOR byte by byte (as char by char) of the element string with the salt
            self.buffer = bytes(''.join([chr(ord(a) ^ b)
                                         for (a, b) in zip(self.element, self.hash_salts[0])]), 'latin-1')

            # Initializes the hash function according to the hash family
            if self.i == 'sha3_256':
                self.m = hashlib.sha3_256()
            elif self.i == 'sha3_512':
                self.m = hashlib.sha3_512()
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
        del self.element

    def insert_from_file(self):
        """
        Insert the elements from a dataset CSV file (dataset_path).
        The CSV has one area-element couple per line (in this order),
        separated by the value dataset_delimiter, which defaults to ','.
        """

        self.dataset_path = self._get_dataset_path()
        self.dataset_delimiter = ','
        self._coors()

        with open(self.dataset_path, 'r') as self.dataset_file:
            self.dataset_reader = csv.reader(self.dataset_file, delimiter=self.dataset_delimiter)
            for self.row in self.dataset_reader:
                self._insert(self.row[1], int(self.row[0]))
                self.all_coors.remove(self.row[1])

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

        if (self.area <= 0) or (self.area > self.num_areas):
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

        for self.i in self.hash_family:

            # XOR byte by byte (as char by char) of the element string with the salt
            self.buffer = bytes(''.join([chr(ord(a) ^ b)
                                         for (a, b) in zip(self.element, self.hash_salts[0])]), 'latin-1')

            # Initializes the hash function according to the hash family
            if self.i == 'sha3_256':
                self.m = hashlib.sha3_256()
            elif self.i == 'sha3_512':
                self.m = hashlib.sha3_512()
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
        del self.current_area
        del self.index
        del self.element

        return self.value_indexes

    def update_stats(self, precision=4):
        """
        Update the stats about the SBF filter.
        """
        self.precision = precision

        self._area_fpp()
        self._area_isep()

        self.stats["Filter Sparsity"] = str('{:.{prec}f}'.format(
            round(self._filter_sparsity(), self.precision), prec=self.precision))

        self.stats["Filter False Positive Probability"] = str('{:.{prec}f}'.format(
            round(self._filter_fpp(), self.precision), prec=self.precision))

        self.stats['Number of Mapped Elements'] = str(self.members)
        self.stats['Number of Hash Collisions'] = str(self.collisions)

    def area_stats(self):
        self.area_properties, self.area_stats2 = {}, {}

        for self.j in range(1, self.num_areas + 1):
            self.potential_elements = self.area_members[self.j] * len(self.hash_family)
            stats1 = [str(self.area_members[self.j]), str(self.area_cells[self.j]),
                      str(self.potential_elements), str(self.area_self_collisions[self.j])]

            self.area_properties[str(self.j).rjust(len(str(self.num_areas)))] = stats1

        for self.j in range(1, self.num_areas + 1):
            stats2 = [str('{:.{prec}f}'.format(round(self._area_emersion(self.j), self.precision),
                                               prec=self.precision)),
                      str('{:.{prec}f}'.format(round(self.area_fpp[self.j], self.precision),
                                               prec=self.precision)),
                      str('{:.{prec}f}'.format(round(self.area_isep[self.j], self.precision),
                                               prec=self.precision))]

            self.area_stats2[str(self.j).rjust(len(str(self.num_areas)))] = stats2

        del self.j
        del self.potential_elements

        return self.area_properties, self.area_stats2

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
        Computes the false positive probability over the entire filter.
        :return: the filter false positive probability.
        """

        self.c = 0

        # Counts non-zero cells
        for self.i in range(1, self.num_areas + 1):
            self.c += self.area_cells[self.i]

        self.p = self.c / self.num_cells

        return pow(self.p, len(self.hash_family))

    def get_filter(self):
        """
        Returns the filter.
        :return the spacial bloom filter
        """
        return self.filter

    def get_hash_family(self):
        """
        Returns the hash family.
        :return: list of hash family.
        """
        return self.hash_family

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
        self.insert_file_list.clear()
        self.incorrect_areas.clear()
        self.fp_coor.clear()
        self.all_coors.clear()
        self._coors()
        self.stats = {
            "Hash Family": str(self.hash_family),
            "Number of Cells": str(self.num_cells),
        }

    def incorrect_values(self):
        """
        Create a dictionary of coordinates where its area has been overwritten.
        The coordinate is the key with and list [real_area, [returned areas]] as the key.
        :return: a dictionary of incorrect checks.
        """
        self.dataset_path = self._get_dataset_path()
        self.dataset_delimiter = ','

        with open(self.dataset_path, 'r') as self.dataset_file:
            self.dataset_reader = csv.reader(self.dataset_file, delimiter=self.dataset_delimiter)
            for row in self.dataset_reader:
                self.check_val = self.check(row[1])
                self.areas = []
                for hf in self.hash_family:
                    self.areas.append(self.check_val[hf][1])
                if str(min(int(m) for m in self.areas)) != row[0]:
                    self.incorrect_areas[row[1]] = [int(row[0]), self.areas]

        del self.dataset_path
        del self.dataset_delimiter
        del self.dataset_file
        del self.dataset_reader
        del self.check_val
        del self.areas

        return self.incorrect_areas

    def allowed_hashes(self):
        """
        Return a list of allowed hash functions.
        :return: list of hash functions.
        """
        # return self.HASH_FAMILIES.remove('sha')
        return self.HASH_FAMILIES

    def find_false_positives(self):
        """
        Find the coordinates are not in the SBF but falsely return an Area of Interest.
        :return: a dictionary of 10 false positive coordinates.( key: coordinate, value:[area of interests])
        """
        indexes = []
        while len(indexes) != 100:
            indexes.append(randint(0, len(self.all_coors)))
        for i in indexes:
            if len(self.fp_coor) == 10:
                return self.fp_coor
            aoi = []
            self.check_result = self.check(self.all_coors[i])
            for hf in self.hash_family:
                aoi.append(self.check_result[hf][1])
            if min(int(m) for m in aoi) != 0:
                self.fp_coor[self.all_coors[i]] = aoi

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

    def _coors(self):
        long1, long2, lat1, lat2 = 8945, 9020, 4694, 4844
        for x in range(long1, long2 + 1):
            for y in range(lat1, lat2 + 2):
                self.all_coors.append("51.{}#-8.{}".format(x, y))

    def _area_fpp(self):
        """
        Computes false positives probability for each area.
        :return: list of false positives probability for the areas.
        """

        self.area_fpp = [0] * (self.num_areas + 1)

        for self.i in range(self.num_areas, 0, -1):

            self.c = 0

            for self.j in range(self.i, self.num_areas + 1):
                self.c += self.area_cells[self.j]

            self.p = self.c / self.num_cells
            self.area_fpp[self.i] = pow(self.p, len(self.hash_family))

            for self.j in range(self.i, self.num_areas):
                self.area_fpp[self.i] -= self.area_fpp[self.j + 1]

            if self.area_fpp[self.i] < 0:
                self.area_fpp[self.i] = 0

        del self.j
        del self.c
        del self.p
        del self.i

        return self.area_fpp

    def _area_isep(self):
        """
        Computes inter-set error probability for each area.
        :return: list of inter-set error probability for the areas.
        """

        self.area_isep = [0] * (self.num_areas + 1)

        for self.i in range(self.num_areas, 0, -1):
            self.p = 1 - self._area_emersion(self.i)
            self.p = pow(self.p, len(self.hash_family))

            self.area_isep[self.i] = self.p

        del self.p

        return self.area_isep

    def _area_emersion(self, area):
        """
        Computes the emersion value for an area.
        :param area: the area for which to calculate the emersion value.
        :return: the emersion value.
        """

        self.area = area

        if self.area_members[self.area] == 0:
            return -1
        else:
            return (self.area_cells[self.area] / (
                    (self.area_members[self.area] * len(self.hash_family)) - self.area_self_collisions[self.area]))

    @staticmethod
    def _get_salt_path():
        """
        Returns the correct path to the hash salt file.
        :return: the path to the hash salt file.
        """
        aws = "/var/www/demo/hash_salt/hash_salt"
        if Path(aws).is_file():
            return aws

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

        return "dataset/cork.csv"
