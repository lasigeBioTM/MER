import unittest
import subprocess


class SanityCheckTests(unittest.TestCase):

    def test_sanity_check(self):

        with open('tests/sample_file.txt') as f:
            sample_text = f.read()

        with open('tests/sample_result.txt') as f:
            sample_result = f.read()

        bash_command = 'bash get_entities.sh 1 "{}"'.format(sample_text)
        result = subprocess.check_output(bash_command, shell=True)

        self.assertEqual(result, sample_result)


if __name__ == '__main__':
    unittest.main()
