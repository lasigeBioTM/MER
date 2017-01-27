import unittest

"""Tests related to the data files."""


class DataFilesTests(unittest.TestCase):

    non_testing_data_files = ['cells.txt', 'CHEMICAL.txt', 'DISEASE.txt',
                              'GENE.txt', 'PROTEIN.txt', 'UNKNOWN.txt',
                              'subcellular_structures.txt']

    def test_no_shared_terms(self):
        """There should be no shared terms between the data files."""

        all_terms = []

        for data_file in DataFilesTests.non_testing_data_files:
            with open('data/' + data_file) as f:
                terms = f.readlines()
            all_terms += terms

        no_duplicates_terms = list(set(all_terms))

        self.assertEqual(len(all_terms), len(no_duplicates_terms))


if __name__ == '__main__':
    unittest.main()
