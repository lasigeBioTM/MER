# -*- coding: utf-8 -*-

import unittest
import subprocess
import json


class PubmedTests(unittest.TestCase):

    def test_return_one_article_json_with_abstract_and_title(self):

        source = u'pubmed'
        doc_id = u'345345'

        correct_abstract = (u'As is apparent from the length of this review, a '
                            'multitude of laboratory investigations can be performed on the blood '
                            'of patients with AIHA and CHD. Unfortunately, because of the '
                            'considerable complexity of some of these tests, their significance '
                            'is not always apparent to the physician who treats the patient. '
                            'Communication gaps between the laboratory scientist and the physician '
                            'at the bedside are bound to occur because of the high degree of '
                            'specialization of both immunohematology and medical care. The '
                            'purpose of this review has been to bridge the communication gap. '
                            'The agents that cause AIHA and CHD are antibodies. '
                            'Although they are often autoantibodies of complex specificity, '
                            'usually reacting with all normal red cells, '
                            'they nevertheless obey most of the rules explaining the action of '
                            'alloantibodies that sometimes complicate transfusion therapy. '
                            'By approaching AIHA and CHD as antibody-induced conditions, and by '
                            'regarding autoantibodies as similar in their actions to '
                            'alloantibodies, hopefully, physicians will appreciate the '
                            'significance of the tests performed in the laboratory. '
                            'For their part, the laboratory workers will be able not only to '
                            'report test results but also to explain the findings. This review '
                            'may aid in establishing the essential dialogue.')

        correct_title = (u'Autoimmune hemolytic anemia and cold hemagglutinin '
                         'disease: clinical disease and laboratory findings.')

        correct_dict = {}

        correct_dict[doc_id] = {}
        correct_dict[doc_id][u'doc_id'] = doc_id
        correct_dict[doc_id][u'source'] = source
        correct_dict[doc_id][u'abstract'] = correct_abstract
        correct_dict[doc_id][u'title'] = correct_title

        bash_command = 'bash external_services/pubmed.sh {}'.format(doc_id)
        result = subprocess.check_output(bash_command, shell=True)

        result_dict = json.loads(result)

        self.assertEqual(correct_dict, result_dict)

    def test_return_one_article_json_only_with_title(self):

        source = u'pubmed'
        doc_id = u'435'

        correct_title = (u'Stability of myofibrillar EDTA-ATPase in rabbit '
                         'psoas fiber bundles.')

        correct_dict = {}

        correct_dict[doc_id] = {}
        correct_dict[doc_id][u'doc_id'] = doc_id
        correct_dict[doc_id][u'source'] = source
        correct_dict[doc_id][u'title'] = correct_title

        bash_command = 'bash external_services/pubmed.sh {}'.format(doc_id)
        result = subprocess.check_output(bash_command, shell=True)

        result_dict = json.loads(result)

        self.assertEqual(correct_dict, result_dict)

    def test_one_article_send_non_valid_doc_id(self):

        source = u'pubmed'
        doc_id = u'hjkf0s'

        correct_dict = {}

        correct_dict[doc_id] = {}
        correct_dict[doc_id][u'doc_id'] = doc_id
        correct_dict[doc_id][u'source'] = source
        correct_dict[doc_id][u'error_message'] = 'Non-valid id'

        bash_command = 'bash external_services/pubmed.sh {}'.format(doc_id)
        result = subprocess.check_output(bash_command, shell=True)

        result_dict = json.loads(result)

        self.assertEqual(correct_dict, result_dict)

    def test_one_article_send_id_non_existent(self):

        source = u'pubmed'
        doc_id = u'43534253245345'

        correct_dict = {}

        correct_dict[doc_id] = {}
        correct_dict[doc_id][u'doc_id'] = doc_id
        correct_dict[doc_id][u'source'] = source
        correct_dict[doc_id][u'error_message'] = 'Non-existent id'

        bash_command = 'bash external_services/pubmed.sh {}'.format(doc_id)
        result = subprocess.check_output(bash_command, shell=True)

        result_dict = json.loads(result)

        self.assertEqual(correct_dict, result_dict)

    def test_return_more_than_one_article_json(self):

        correct_dict = {}

        source_1 = u'pubmed'
        doc_id_1 = u'345345'

        correct_abstract_1 = (u'As is apparent from the length of this review, a '
                              'multitude of laboratory investigations can be performed on the blood '
                              'of patients with AIHA and CHD. Unfortunately, because of the '
                              'considerable complexity of some of these tests, their significance '
                              'is not always apparent to the physician who treats the patient. '
                              'Communication gaps between the laboratory scientist and the physician '
                              'at the bedside are bound to occur because of the high degree of '
                              'specialization of both immunohematology and medical care. The '
                              'purpose of this review has been to bridge the communication gap. '
                              'The agents that cause AIHA and CHD are antibodies. '
                              'Although they are often autoantibodies of complex specificity, '
                              'usually reacting with all normal red cells, '
                              'they nevertheless obey most of the rules explaining the action of '
                              'alloantibodies that sometimes complicate transfusion therapy. '
                              'By approaching AIHA and CHD as antibody-induced conditions, and by '
                              'regarding autoantibodies as similar in their actions to '
                              'alloantibodies, hopefully, physicians will appreciate the '
                              'significance of the tests performed in the laboratory. '
                              'For their part, the laboratory workers will be able not only to '
                              'report test results but also to explain the findings. This review '
                              'may aid in establishing the essential dialogue.')

        correct_title_1 = (u'Autoimmune hemolytic anemia and cold hemagglutinin '
                           'disease: clinical disease and laboratory findings.')

        correct_dict[doc_id_1] = {}
        correct_dict[doc_id_1][u'doc_id'] = doc_id_1
        correct_dict[doc_id_1][u'source'] = source_1
        correct_dict[doc_id_1][u'abstract'] = correct_abstract_1
        correct_dict[doc_id_1][u'title'] = correct_title_1

        source_2 = u'pubmed'
        doc_id_2 = u'435'

        correct_title_2 = (u'Stability of myofibrillar EDTA-ATPase in rabbit '
                           'psoas fiber bundles.')

        correct_dict[doc_id_2] = {}
        correct_dict[doc_id_2][u'doc_id'] = doc_id_2
        correct_dict[doc_id_2][u'source'] = source_2
        correct_dict[doc_id_2][u'title'] = correct_title_2

        bash_command = 'bash external_services/pubmed.sh {} {}'.format(
            doc_id_1, doc_id_2
        )

        result = subprocess.check_output(bash_command, shell=True)

        result_dict = json.loads(result)

        self.assertEqual(correct_dict, result_dict)


class PMCTests(unittest.TestCase):

    def test_return_one_article_json_with_abstract_and_title(self):

        source = u'pmc'
        doc_id = u'PMC433970'

        correct_abstract = (u'The degradation rates of several missense '
                            'mutants of hypoxanthine-guanine '
                            'phosphoribosyltransferase (EC 2.4.2.8) in mouse L '
                            'cells are compared to those of the wild-type '
                            'enzyme. Although the rates of total protein '
                            'breakdown in the mutant cell lines are identical '
                            'to that of the parental L cell line, defective '
                            'molecules of hypoxanthine-guanine '
                            'phosphoribosyltransferase present in the mutant '
                            'cell lines are degraded much faster than the '
                            'wild-type enzyme. The level of defective '
                            'phosphoribosyltransferase molecules present in the '
                            'mutant cell lines is inversely proportional to the '
                            'breakdown rate. This observation indicates that '
                            'the major factor determining the concentrations '
                            'of the defective phosphoribosyltransferases is '
                            'their specific degradation rate. These results '
                            'strongly support the hypothesis that abnormal '
                            'proteins are selectively degraded in mammalian '
                            'cells.')

        correct_title = (u'Selective Degradation of Abnormal Proteins in '
                         'Mammalian Tissue Culture Cells')

        correct_dict = {}

        correct_dict[doc_id] = {}
        correct_dict[doc_id][u'doc_id'] = doc_id
        correct_dict[doc_id][u'source'] = source
        correct_dict[doc_id][u'abstract'] = correct_abstract
        correct_dict[doc_id][u'title'] = correct_title

        bash_command = 'bash external_services/pmc.sh {}'.format(doc_id)
        result = subprocess.check_output(bash_command, shell=True)

        result_dict = json.loads(result)

        self.assertEqual(correct_dict, result_dict)

    def test_return_one_article_json_only_with_title(self):

        source = u'pmc'
        doc_id = u'PMC3367865'

        correct_title = (u'Molecular Biology of Lung Cancer: Clinical Implications')

        correct_dict = {}

        correct_dict[doc_id] = {}
        correct_dict[doc_id][u'doc_id'] = doc_id
        correct_dict[doc_id][u'source'] = source
        correct_dict[doc_id][u'title'] = correct_title

        bash_command = 'bash external_services/pmc.sh {}'.format(doc_id)
        result = subprocess.check_output(bash_command, shell=True)

        result_dict = json.loads(result)

        self.assertEqual(correct_dict, result_dict)

    def test_return_more_than_one_article_json_with_abstract_and_title(self):

        correct_dict = {}
        source = u'pmc'

        doc_id_1 = u'PMC433970'

        correct_abstract_1 = (u'The degradation rates of several missense '
                              'mutants of hypoxanthine-guanine '
                              'phosphoribosyltransferase (EC 2.4.2.8) in mouse L '
                              'cells are compared to those of the wild-type '
                              'enzyme. Although the rates of total protein '
                              'breakdown in the mutant cell lines are identical '
                              'to that of the parental L cell line, defective '
                              'molecules of hypoxanthine-guanine '
                              'phosphoribosyltransferase present in the mutant '
                              'cell lines are degraded much faster than the '
                              'wild-type enzyme. The level of defective '
                              'phosphoribosyltransferase molecules present in the '
                              'mutant cell lines is inversely proportional to the '
                              'breakdown rate. This observation indicates that '
                              'the major factor determining the concentrations '
                              'of the defective phosphoribosyltransferases is '
                              'their specific degradation rate. These results '
                              'strongly support the hypothesis that abnormal '
                              'proteins are selectively degraded in mammalian '
                              'cells.')

        correct_title_1 = (u'Selective Degradation of Abnormal Proteins in '
                           'Mammalian Tissue Culture Cells')

        correct_dict[doc_id_1] = {}
        correct_dict[doc_id_1][u'doc_id'] = doc_id_1
        correct_dict[doc_id_1][u'source'] = source
        correct_dict[doc_id_1][u'abstract'] = correct_abstract_1
        correct_dict[doc_id_1][u'title'] = correct_title_1

        doc_id_2 = u'PMC3367865'

        correct_title_2 = (u'Molecular Biology of Lung Cancer: Clinical Implications')

        correct_dict[doc_id_2] = {}
        correct_dict[doc_id_2][u'doc_id'] = doc_id_2
        correct_dict[doc_id_2][u'source'] = source
        correct_dict[doc_id_2][u'title'] = correct_title_2

        bash_command = 'bash external_services/pmc.sh {} {}'.format(
            doc_id_1, doc_id_2
        )
        result = subprocess.check_output(bash_command, shell=True)

        result_dict = json.loads(result)

        self.assertEqual(correct_dict, result_dict)

    def test_send_non_existent_id(self):

        source = u'pmc'
        doc_id = u'PMC3fsdf65'

        error_message = 'Non-existent id'

        correct_dict = {}

        correct_dict[doc_id] = {}
        correct_dict[doc_id][u'doc_id'] = doc_id
        correct_dict[doc_id][u'source'] = source
        correct_dict[doc_id][u'error_message'] = error_message

        bash_command = 'bash external_services/pmc.sh {}'.format(doc_id)
        result = subprocess.check_output(bash_command, shell=True)

        result_dict = json.loads(result)

        self.assertEqual(correct_dict, result_dict)


class PatentServerTests(unittest.TestCase):

    def test_return_json_with_abstract_and_title(self):

        correct_result = []

        correct_dict1 = {}
        correct_result.append(correct_dict1)

        doc_id = u'CN101371925B'

        correct_abstract = (u'The invention relates to a sustained-release '
                            'matter of a cell peptide growth factor. The '
                            'invention further relates to a preparation method '
                            'of the sustained-release matter of the cell '
                            'peptide growth factor and a use thereof. The '
                            'provided sustained-release matter of the cell '
                            'peptide growth factor is a nano-silver-cell '
                            'growth factor complex, the peptide growth factor '
                            'bonds with Ag by the nano-absorption or/and -COO, '
                            '-CN and -H, thereby being absorbed on the surface '
                            'of the nano-silver to form the complex. The '
                            'sustained-release matter utilizes the natural '
                            'anti-inflection effect of the nano-silver to '
                            'provide a clean micro-environment for the '
                            'biological action of the growth factor, promotes '
                            'faster repair and healing of wound/wound surface, '
                            'reduces adverse reactions, reduces the times of '
                            'drug administration and the waste of drugs, '
                            'alleviates suffering of patients and '
                            'simultaneously reduces medical costs.')

        correct_title = (u'Nano silver-cell growth factor sustained-release '
                         'composite body as well as preparation method and use '
                         'thereof')

        correct_dict1[u'externalId'] = doc_id
        correct_dict1[u'abstractText'] = correct_abstract
        correct_dict1[u'title'] = correct_title

        bash_command = 'bash external_services/patent_server.sh {}'.format(doc_id)
        result = subprocess.check_output(bash_command, shell=True)

        result = json.loads(result)

        self.assertEqual(correct_result, result)

    def test_return_more_than_one_article_json_with_abstract_and_title(self):

        correct_result = []

        correct_dict1 = {}
        correct_result.append(correct_dict1)

        doc_id_1 = u'CN101371925B'

        correct_abstract_1 = (u'The invention relates to a sustained-release '
                              'matter of a cell peptide growth factor. The '
                              'invention further relates to a preparation method '
                              'of the sustained-release matter of the cell '
                              'peptide growth factor and a use thereof. The '
                              'provided sustained-release matter of the cell '
                              'peptide growth factor is a nano-silver-cell '
                              'growth factor complex, the peptide growth factor '
                              'bonds with Ag by the nano-absorption or/and -COO, '
                              '-CN and -H, thereby being absorbed on the surface '
                              'of the nano-silver to form the complex. The '
                              'sustained-release matter utilizes the natural '
                              'anti-inflection effect of the nano-silver to '
                              'provide a clean micro-environment for the '
                              'biological action of the growth factor, promotes '
                              'faster repair and healing of wound/wound surface, '
                              'reduces adverse reactions, reduces the times of '
                              'drug administration and the waste of drugs, '
                              'alleviates suffering of patients and '
                              'simultaneously reduces medical costs.')

        correct_title_1 = (u'Nano silver-cell growth factor sustained-release '
                           'composite body as well as preparation method and use '
                           'thereof')

        correct_dict1[u'externalId'] = doc_id_1
        correct_dict1[u'abstractText'] = correct_abstract_1
        correct_dict1[u'title'] = correct_title_1

        correct_dict2 = {}
        correct_result.append(correct_dict2)

        doc_id_2 = u'WO2010018435A1'

        correct_abstract_2 = (u'The invention relates to the O-glucosylated '
                              'amide derivatives, which are inhibitors of '
                              'Sodium dependent glucose co transporter '
                              '(SGLT), particularly SGLT2 and method of '
                              'treating diseases, conditions and/or disorders '
                              'inhibited by SGLT2 with them, and processes '
                              'for preparing them.')

        correct_title_2 = (u'Amide glycosides')

        correct_dict2[u'externalId'] = doc_id_2
        correct_dict2[u'abstractText'] = correct_abstract_2
        correct_dict2[u'title'] = correct_title_2

        bash_command = 'bash external_services/patent_server.sh {} {}'.format(
            doc_id_1, doc_id_2
        )
        result = subprocess.check_output(bash_command, shell=True)
        result = json.loads(result)

        self.assertEqual(correct_result, result)


if __name__ == '__main__':
    unittest.main()
