import unittest
import subprocess


class SanityCheckTests(unittest.TestCase):

    # def test_sanity_check(self):

    #     with open('tests/sample_file.txt') as f:
    #         sample_text = f.read()

    #     with open('tests/sample_result.txt') as f:
    #         sample_result = f.read()

    #     bash_command = 'bash get_entities.sh 1 "{}"'.format(sample_text)
    #     result = subprocess.check_output(bash_command, shell=True)

    #     self.assertEqual(result, sample_result)

    def test_no_annotations(self):
        bash_command = 'bash get_entities.sh 1 T "not a entity" DrugBank'
        result = subprocess.check_output(bash_command, shell=True)

        self.assertEqual('', result)

    def test_no_overlapping_annotations(self):
        bash_command = 'bash get_entities.sh 1 T "Benzalkonium Chloride" ChEBI'
        result = subprocess.check_output(bash_command, shell=True)

        self.assertEqual('1\tT\t0\t21\t0.671541\tBenzalkonium Chloride\tunknown\t1', result)


if __name__ == '__main__':
    unittest.main()
