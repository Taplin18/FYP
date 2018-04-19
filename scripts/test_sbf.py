from unittest import TestCase
from scripts.sbf import sbf
import numpy as np
import ast


class TestSbf(TestCase):

    def test_invalid_hash_family(self):
        with self.assertRaisesRegex(AttributeError, "Invalid hash family."):
            sbf(['sha512', 'md5', 'sha'])

    def test_invalid_bit_mapping(self):
        with self.assertRaisesRegex(AttributeError, "Invalid bit mapping."):
            sbf(['sha512', 'md5', 'sha1'], bit_mapping=65)

    def test_hash_salt_path(self):
        with self.assertRaisesRegex(IOError, "Error opening hash salts"):
            sbf(['sha512', 'md5', 'sha1'])

    def test_get_stats(self):
        fltr = sbf(['sha512', 'md5', 'sha1'], bit_mapping=4, hash_salt_path="../hash_salt/hash_salt")
        fltr_stats = fltr.get_stats()

        self.assertEqual(int(fltr_stats['Number of Cells']), pow(2, 4))
        self.assertEqual(ast.literal_eval(fltr_stats['Hash Family']), ['sha512', 'md5', 'sha1'])

    def test_insert(self):
        fltr = sbf(['sha512', 'md5', 'sha1'], bit_mapping=4, hash_salt_path="../hash_salt/hash_salt")
        fltr.insert("51.8989#-8.4825", 1)

        self.assertNotEqual(np.count_nonzero(fltr.get_filter()), 0)

    def test_check(self):
        fltr = sbf(['sha512', 'md5', 'sha1'], bit_mapping=4, hash_salt_path="../hash_salt/hash_salt")
        fltr.insert("51.8989#-8.4825", 1)
        fltr_check_positive = fltr.check("51.8989#-8.4825")
        fltr_check_negative = fltr.check("51.8980#-8.4845")

        areas_1, areas_2 = [], []
        for i in ['sha512', 'md5', 'sha1']:
            areas_1.append(fltr_check_positive[i][1])
            areas_2.append(fltr_check_negative[i][1])

        self.assertEqual(min(int(m) for m in areas_1), 1)
        self.assertEqual(min(int(m) for m in areas_2), 0)

    def test_get_filter(self):
        fltr = sbf(['sha512', 'md5', 'sha1'], bit_mapping=4, hash_salt_path="../hash_salt/hash_salt")
        sbf_fltr = fltr.get_filter()

        self.assertEqual(np.count_nonzero(sbf_fltr), 0)

    def test_clear_filter(self):
        fltr = sbf(['sha512', 'md5', 'sha1'], bit_mapping=4, hash_salt_path="../hash_salt/hash_salt")
        fltr.insert("51.8989#-8.4825", 1)
        fltr.clear_filter()

        self.assertEqual(np.count_nonzero(fltr.get_filter()), 0)
