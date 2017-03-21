# -*- coding: utf-8 -*-

import unittest
import subprocess


class SanityCheckTests(unittest.TestCase):

    def test_no_annotations(self):
        """Nothing should be returned if there are no annotations.

        https://github.com/LLCampos/IBELight/issues/7"""

        bash_command = 'bash get_entities.sh "not a entity" ChEBI'
        result = subprocess.check_output(bash_command, shell=True)

        self.assertEqual('', result)

    def test_not_match_mid_word(self):
        """https://github.com/LLCampos/IBELight/issues/10"""
        bash_command_1 = 'bash get_entities.sh "nicotinic acid amide, isonicotinic acid amide" ChEMBL'
        result_1 = subprocess.check_output(bash_command_1, shell=True)

        correct_annotations_2 = ('0\t14\tnicotinic acid\n'
                                 '22\t39\tisonicotinic acid\n'
                                 '0\t20\tnicotinic acid amide\n')

        self.assertEqual(correct_annotations_2, result_1)

        """https://github.com/LLCampos/IBELight/issues/28"""
        bash_command_2 = 'bash get_entities.sh "methanol ethanol" ChEBI'
        result_2 = subprocess.check_output(bash_command_2, shell=True)

        correct_annotations_2 = ('0\t8\tmethanol\n'
                                 '9\t16\tethanol\n')

        self.assertEqual(correct_annotations_2, result_2)

        """https://github.com/LLCampos/IBELight/issues/28#issuecomment-276020303"""
        bash_command_3 = 'bash get_entities.sh "chlorotomoxetine tomoxetine" ChEBI'
        result_3 = subprocess.check_output(bash_command_3, shell=True)

        correct_annotations_3 = ('17\t27\ttomoxetine\n')

        self.assertEqual(correct_annotations_3, result_3)

    def test_return_character_offset(self):
        """Annotation offsets returned should be character offsets, not byte
        offsets."""

        # https://github.com/LLCampos/IBELight/issues/11
        bash_command_1 = 'bash get_entities.sh "‘ oxygen" ChEBI'
        result_1 = subprocess.check_output(bash_command_1, shell=True)

        correct_annotation_1 = '2\t8\toxygen\n'

        self.assertEqual(correct_annotation_1, result_1)

        # https://github.com/LLCampos/IBELight/issues/14

        bash_command_2 = 'bash get_entities.sh "µ testosterone" ChEBI'
        result_2 = subprocess.check_output(bash_command_2, shell=True)

        correct_annotation_2 = '2\t14\ttestosterone\n'

        self.assertEqual(correct_annotation_2, result_2)

        # https://github.com/LLCampos/IBELight/issues/15

        bash_command_3 = 'bash get_entities.sh " water" ChEBI'
        result_3 = subprocess.check_output(bash_command_3, shell=True)

        correct_annotation_3 = '1\t6\twater\n'

        self.assertEqual(correct_annotation_3, result_3)

    def test_ignore_full_stop(self):
        """Terms should be annotated even if followed by a full stop.

        https://github.com/LLCampos/IBELight/issues/2"""

        bash_command = 'bash get_entities.sh "I love testosterone." ChEBI'
        result = subprocess.check_output(bash_command, shell=True)

        correct_annotation = '7\t19\ttestosterone\n'

        self.assertEqual(correct_annotation, result)

    def test_terms_with_more_than_2_words_should_be_recognized(self):
        """https://github.com/LLCampos/IBELight/issues/3"""

        bash_command = 'bash get_entities.sh "Cetyl trimethyl ammonium bromide" ChEBI'
        result = subprocess.check_output(bash_command, shell=True)

        correct_annotation = ('16\t24\tammonium\n'
                              '25\t32\tbromide\n'
                              '0\t32\tCetyl trimethyl ammonium bromide\n')

        self.assertEqual(correct_annotation, result)

    def test_word_position_indexes_consider_multi_whitespaces(self):
        """"https://github.com/LLCampos/IBELight/issues/12"""

        bash_command = 'bash get_entities.sh "the  potassium" ChEBI'
        result = subprocess.check_output(bash_command, shell=True)

        correct_annotation = ('5\t14\tpotassium\n')

        self.assertEqual(correct_annotation, result)

    def test_ignore_comma(self):
        """Terms should be annotated even if followed by a comma.

        https://github.com/LLCampos/IBELight/issues/13"""

        bash_command = 'bash get_entities.sh "water, potassium, oxygen" ChEBI'
        result = subprocess.check_output(bash_command, shell=True)

        correct_annotation = ('0\t5\twater\n'
                              '7\t16\tpotassium\n'
                              '18\t24\toxygen\n')

        self.assertEqual(correct_annotation, result)

    def test_annotate_words_between_parenthesis(self):
        """https://github.com/LLCampos/IBELight/issues/16"""

        bash_command = 'bash get_entities.sh "(water)" ChEBI'
        result = subprocess.check_output(bash_command, shell=True)

        correct_annotation = ('1\t6\twater\n')

        self.assertEqual(correct_annotation, result)

    def test_special_characters_are_retained_in_output(self):
        """https://github.com/LLCampos/IBELight/issues/17"""

        bash_command = 'bash get_entities.sh "N-methyl-D-aspartate" ChEBI'
        result = subprocess.check_output(bash_command, shell=True)

        correct_annotation = ('0\t20\tN-methyl-D-aspartate\n')

        self.assertEqual(correct_annotation, result)

    def test_case_insensitivity(self):

        bash_command = 'bash get_entities.sh "Water" ChEBI'
        result = subprocess.check_output(bash_command, shell=True)

        correct_annotation = ('0\t5\tWater\n')

        self.assertEqual(correct_annotation, result)

    def test_match_utf8_in_vocab_with_utf8_in_text(self):

        bash_command = 'bash get_entities.sh "α-amilase α-amilase" test_data'
        result = subprocess.check_output(bash_command, shell=True)

        correct_annotation = ('0\t9\tα-amilase\n'
                              '10\t19\tα-amilase\n')

        self.assertEqual(correct_annotation, result)

    def test_no_double_annot_when_em_dash_in_term(self):
        # Tests fix of issue #24

        bash_command = 'bash get_entities.sh " —ONO2;" ChEBI'
        result = subprocess.check_output(bash_command, shell=True)

        correct_annotation = ('1\t6\t—ONO2\n')

        self.assertEqual(correct_annotation, result)

    def test_do_not_match_term_non_existent_on_lexicon(self):

        bash_command = 'bash get_entities.sh "sera Ser-," ChEBI'
        result = subprocess.check_output(bash_command, shell=True)

        correct_annotation = ('1\t9\tSer-\n')

        self.assertEqual(correct_annotation, result)

    def test_period_in_term_should_not_be_wildcard(self):
        # Tests fix of issue #33

        bash_command = 'bash get_entities.sh DAP-3 test_data'
        result = subprocess.check_output(bash_command, shell=True)

        correct_annotation = ''

        self.assertEqual(correct_annotation, result)


if __name__ == '__main__':
    unittest.main()
