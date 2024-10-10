import os
import re
import time
from owlready2 import get_ontology



def read_classes_into_array(file_path):
    """Reads the classes file line by line, strips newline characters and class names,
    and returns the IRIs as a list of strings
    
    :param file_path (str): path to file
    :return list: list of IRIs
    """

    lines = []
    with open(file_path, 'r') as file:
        lines = [line.strip().split(" | ")[1] for line in file.readlines()]  # Strip newline characters and names

    return lines



def strip_label(label):
    """Cleans up labels by removing specific unwanted characters
    
    :param label (str): label 
    :return str: clean label
    """

    return str(label).replace("['", "").replace("']", "")



def start_process_owl_file(ontology, lines, labels_file, links_file, synonyms_file):
    """Takes a list of classes and iterates over the ontology, extracting labels, synonyms and IRIs
    for each matching class (also handles every subclass)
    
    :param ontology (str): ontology (.owl) file
    :param lines (list): list of strings (class IRIs)
    :param labels_file (str): path to labels file (.txt)
    :param links_file (str): path to links ([LABEL] [IRI]) file (.txt)
    :param synonyms_file (str): path to file where label and respective synonyms will be stored (.txt)
    :return side effect: creates labels file, synonyms file, and links file
    """

    ids_to_process = []

    # Iterate over all classes in the ontology
    for cls in ontology.classes():
        if cls.iri in lines:

            # Write class label and IRI to the output files
            labels_file.write(f"{strip_label(cls.label)}\n")
            synonyms_file.write(f"{strip_label(cls.label)}\n")
            links_file.write(f"{strip_label(cls.label)}|{strip_label(cls.iri)}\n")
            ids_to_process.append(cls.iri)

            # Process and write synonyms
            for synonyms in cls.hasExactSynonym:
                labels_file.write(f"{synonyms}\n")
                synonyms_file.write(f"{synonyms}\n")
                links_file.write(f"{synonyms}|{cls.iri}\n")
            for synonyms in cls.hasRelatedSynonym:
                labels_file.write(f"{synonyms}\n")
                synonyms_file.write(f"{synonyms}\n")
                links_file.write(f"{synonyms}|{cls.iri}\n")
        
            synonyms_file.write("-\n")
        

    # Recursively process subclasses of identified classes        
    if len(ids_to_process) > 0:
        process_owl_file(ontology, ids_to_process, labels_file,links_file, synonyms_file)



def process_owl_file(ontology, lines, labels_file, links_file, synonyms_file):
    """Recursively processes subclasses of the classes identified in 'start_process_owl_file'
    
    :param ontology (str): ontology (.owl) file
    :param lines (list): list of strings (class IRIs)
    :param labels_file (str): path to labels file (.txt)
    :param links_file (str): path to links ([LABEL] [IRI]) file (.txt)
    :param synonyms_file (str): path to file where label and respective synonyms will be stored (.txt)
    :return side effect: creates labels file, synonyms file, and links file
    """
    
    no_mappings = set()
    ids_to_process = []
    for id in lines:
        # Search for the class by IRI
        cls = ontology.search_one(iri=id)
        sub_ontology = ontology.search(subclass_of = cls)
        if len(sub_ontology) > 0:
            for sub_cls in sub_ontology:
                if sub_cls.iri == id :
                    continue
                
                # Check if the class has certain mappings (e.g., hasAlternativeId)
                has_mappings = False
                if hasattr(sub_cls, "oboInOwl_hasAlternativeId"):
                    has_mappings = True
                    continue

                # If no mappings were found, add to no_mappings
                if not has_mappings:
                    no_mappings.add(str(cls))

                # Write subclass label and IRI to the output files
                labels_file.write(f"{strip_label(sub_cls.label)}\n")
                synonyms_file.write(f"{strip_label(sub_cls.label)}\n")
                links_file.write(f"{strip_label(sub_cls.label)}|{strip_label(sub_cls.iri)}\n")
                ids_to_process.append(sub_cls.iri)

                # Process and write synonyms
                for synonyms in sub_cls.hasExactSynonym:
                    labels_file.write(f"{synonyms}\n")
                    synonyms_file.write(f"{synonyms}\n")
                    links_file.write(f"{synonyms}|{sub_cls.iri}\n")
                for synonyms in sub_cls.hasRelatedSynonym:
                    labels_file.write(f"{synonyms}\n")
                    synonyms_file.write(f"{synonyms}\n")
                    links_file.write(f"{synonyms}|{sub_cls.iri}\n")
                
                synonyms_file.write("-\n")
    

    print(f'Number of classes with no mappings: {len(no_mappings)}') #--------------------------------------------------- LOG: INFO
    print(f'Class IDs:')
    print('\n'.join(no_mappings)) #--------------------------------------------------------------------------------- LOG: INFO



def edit_file(original_file, new_file):
    """Takes a text file and produces a new file without duplicates and unwanted characters
    or lines, and added relevant entries

    :param original_file (str): path to original file
    :param new_file (str): path to new file
    :return side effect: creates file with unique edited entries plus additional ones
    """

    lines_seen = set()  # Holds lines already seen

    with open(original_file, 'r') as input_file:
        lines = input_file.readlines()

        with open(new_file, 'w') as output_file:
            for line in lines:

                # Remove unwanted characters
                line = re.sub("^'", '', line)
                line = re.sub("'$", '', line)
                line = re.sub(r'\[', '', line)
                line = re.sub(r'\]', '', line)

                # If line is a separator, write it to output file
                if line == '-\n':
                    output_file.write(line)

                # Only process non-empty lines that haven't been seen before
                elif line not in lines_seen and line != '' and not re.search(r'\(nom\. inval\.\)$', line, re.IGNORECASE):

                    # Include common names without the "common" prefix
                    if re.search('^common', line, re.IGNORECASE):
                        no_prefix = line.replace('common ', '')
                        if no_prefix not in lines_seen:
                            lines_seen.add(no_prefix)
                            output_file.write(f'{no_prefix}')

                    # Include group names without the "group" suffix
                    if re.search('group$', line, re.IGNORECASE):
                        no_suffix = line.replace(' group', '')
                        if no_suffix not in lines_seen:
                            lines_seen.add(no_suffix)
                            output_file.write(f'{no_suffix}')

                    # Include names without authors &/or entry year
                    if re.search(r"\(", line):
                        no_author_year = re.sub(r" \((.*)\|", '|', line)
                        if no_author_year not in lines_seen:
                            lines_seen.add(no_author_year)
                            output_file.write(f'{no_author_year}')

                    # Extract names in between " "
                    if re.search('"(.*)"', line):
                        no_accents = re.search('"(.*)"', line).group(1)
                        if no_accents not in lines_seen:
                            lines_seen.add(no_accents)
                            output_file.write(f'{no_accents}')

                    # Skip irrelevant terms
                    if re.search('^algae', line, re.IGNORECASE) or re.search('^plants', line, re.IGNORECASE) or re.search('^phyla', line, re.IGNORECASE) or re.search('^microbiota', line, re.IGNORECASE):
                        continue

                    # Add line to seen list and write it to file
                    lines_seen.add(line)
                    output_file.write(f'{line}')

    
    output_file.close()
    os.system(f'rm -f {original_file}')



def edit_labels_file():
    """Takes the temporary labels file, edits it and creates the final version

    :return str: name of the new labels file
    :return side effect: creates new file with unique edited entries and additional ones
    """

    input_file = file_labels_path
    output_file = input_file.replace('_templabels', '')
    edit_file(input_file, output_file)

    return output_file


def edit_synonyms_file():
    """Takes the temporary synonyms file, edits it and creates the final version

    :return str: name of the new synonyms file
    :return side effect: creates new file with unique edited entries and additional ones
    """

    input_file = file_synonyms_path
    output_file = input_file.replace('temp', '')
    edit_file(input_file, output_file)

    return output_file



def edit_links_file():
    """Takes the temporary links file, edits it and creates the version to be lowercased

    :return str: name of the new links file
    :return side effect: new file with unique edited entries and additional ones
    """

    input_file = file_links_path
    output_file = input_file.replace('temp', 'temp2')
    edit_file(input_file, output_file)

    return output_file
    


def replace_text(file_path, replacement_list):
    """Replaces text in a .txt file without the need to overwrite it entirely or create a new file

    :param file_path (str): path to .txt file
    :param replacement_list (list): list of tuples with the format (original_text, replacement)
    :return side effect: applies changes to given .txt file
    """

    # Open the file in read and write mode 
    with open(file_path, 'r+') as f: 
        # Read the file content
        file_content = f.read()
        
        # Perform all replacements
        for search_text, replace_text in replacement_list:
            # Replace the patterns in the file content
            file_content = re.sub(search_text, replace_text, file_content)
        
        # Move the file pointer to the beginning
        f.seek(0)
        
        # Write the modified content once
        f.write(file_content)
        
        # Truncate the file to remove leftover content from the previous version
        f.truncate()



def final_editing_microorganisms():
    """Manual editing of dataset based on perceived missing values (run only for microorganisms data files)

    :return side effect: applies changes to microorganisms data files
    """

    # Handling labels file: only need to add the extra terms (order is irrelevant)
    with open(output_labels_file, 'a') as labels_file:
        labels_file.write(f"Bacillus megaterium\nGlomus etunicatum\nTurnip mosaic potyvirus\nSaccharibacteria")

    # Handling synonyms file: add extra terms near synonyms (order is IMPORTANT)
    replace_text(output_synonyms_file,[
        ("Priestia megaterium", f"Priestia megaterium\nBacillus megaterium"),
        ("Entrophospora etunicata", f"Entrophospora etunicata\nGlomus etunicatum"),
        ("Turnip mosaic potyvirus TuMV", f"Turnip mosaic potyvirus TuMV\nTurnip mosaic potyvirus"),
        ("Candidatus Saccharibacteria", f"Candidatus Saccharibacteria\nSaccharibacteria"),
        ])

    # Handling links file: add extra terms with corresponding links from linked synonym (order is irrelevant)
    with open(output_links_file, 'a') as links_file:
        links_file.write(
        "Bacillus megaterium|http://purl.obolibrary.org/obo/NCBITaxon_1404"
        "Glomus etunicatum|http://purl.obolibrary.org/obo/NCBITaxon_937382"
        "Turnip mosaic potyvirus|http://purl.obolibrary.org/obo/NCBITaxon_12230"
        "Saccharibacteria|http://purl.obolibrary.org/obo/NCBITaxon_95818"
        )



def final_editing_plants():
    """Manual editing of dataset based on perceived missing values (run only for plants data files)

    :return side effect: applies changes to plants data files
    """

    # Handling labels file: only need to add the extra terms (order is irrelevant)
    with open(output_labels_file, 'a') as labels_file:
        labels_file.write(f"pepper\n"
                          "bell pepper\n"
                          "red peppers\n"
                          "Millet\n"
                          "sunflower\n"
                          "groundnut\n"
                          "groundnuts\n"
                          "rapeseed\n"
                          "mungbean\n"
                          "mung bean\n"
                          "moong\n"
                          "great millet\n"
                          "grapevine\n"
                          "grape\n"
                          "grapes\n"
                          "French lavender\n"
                          "jujube\n"
                          "squash\n"
                          "common bean\n"
                          "beans\n"
                          "bean\n"
                          "Lavandula spica\n"
                          "lettuce")

    # Handling synonyms file: add extra terms near synonyms (order is IMPORTANT)
    replace_text(output_synonyms_file,[
        ("Capsicum annuum", f"Capsicum annuum\npepper\nbell pepper"),
        ("Capsicum annuum var. annuum",f"Capsicum annuum var. annuum\nred peppers"),
        ("Poaceae", f"Poaceae\nmillet"),
        ("Helianthus annuus", f"Helianthus annuus\nsunflower"),
        ("Arachis hypogaea",f"Arachis hypogaea\ngroundnut\ngroundnuts"),
        ("Brassica napus", f"Brassica napus\nrapeseed"),
        ("Poaceae", f"Poaceae\nmillet"),
        ("Vigna radiata", f"Vigna radiata\nmung bean\nmoong\nmungbean"),
        ("Sorghum",f"Sorghum\ngreat millet"),
        ("Vitis vinifera", f"Vitis vinifera\ngrapevine\ngrapes\ngrape"),
        ("Lavandula dentata", f"Lavandula dentata\nFrench lavender"),
        ("Zizyphus jujuba", f"Zizyphus jujuba\njujube"),
        ("Galega officinalis",f"Galega officinalis\ngoat's rue"),
        ("Cucurbita", f"Cucurbita\nsquash"),
        ("Phaseolus vulgaris",f"Phaseolus vulgaris\ncommon bean\nbeans\nbean"),
        ("Lavandula latifolia", f"Lavandula latifolia\nLavandula spica"),
        ("Lactuca sativa", f"Lactuca sativa\nlettuce")
        ])

    # Handling links file: add extra terms with corresponding links from linked synonym (order is irrelevant)
    with open(output_links_file, 'a') as links_file:
        links_file.write(
        "pepper|http://purl.obolibrary.org/obo/NCBITaxon_4072\n"
        "bell pepper|http://purl.obolibrary.org/obo/NCBITaxon_4072\n"
        "red peppers|http://purl.obolibrary.org/obo/NCBITaxon_40321\n"
        "Millet|http://purl.obolibrary.org/obo/NCBITaxon_4479\n"
        "sunflower|http://purl.obolibrary.org/obo/NCBITaxon_4232\n"
        "groundnut|http://purl.obolibrary.org/obo/NCBITaxon_3818\n"
        "groundnuts|http://purl.obolibrary.org/obo/NCBITaxon_3818\n"
        "rapeseeed|http://purl.obolibrary.org/obo/NCBITaxon_3708\n"
        "mung bean|http://purl.obolibrary.org/obo/NCBITaxon_157791\n"
        "mungbean|http://purl.obolibrary.org/obo/NCBITaxon_157791\n"
        "moong|http://purl.obolibrary.org/obo/NCBITaxon_157791\n"
        "great millet|http://purl.obolibrary.org/obo/NCBITaxon_4557\n"
        "grapevine|http://purl.obolibrary.org/obo/NCBITaxon_29760\n"
        "grape|http://purl.obolibrary.org/obo/NCBITaxon_29760\n"
        "grapes|http://purl.obolibrary.org/obo/NCBITaxon_29760\n"
        "Lavandula dentata|http://purl.obolibrary.org/obo/NCBITaxon_1441374"
        "jujube|http://purl.obolibrary.org/obo/NCBITaxon_326968\n"
        "goat's rue|http://purl.obolibrary.org/obo/NCBITaxon_47101\n"
        "squash|http://purl.obolibrary.org/obo/NCBITaxon_3660\n"
        "common bean|http://purl.obolibrary.org/obo/NCBITaxon_3885"
        "Lavandula spica|http://purl.obolibrary.org/obo/NCBITaxon_39331"
        "beans|http://purl.obolibrary.org/obo/NCBITaxon_3885"
        "bean|http://purl.obolibrary.org/obo/NCBITaxon_3885"
        "lettuce|http://purl.obolibrary.org/obo/NCBITaxon_4236"
        )    


def split_labels_into_files(labels):
    """Divides the labels found into different files according to the number of words and uniqueness
    
    :param input_file (str): path to labels file (.txt)
    :return side effect: creates 4 files, each with different length labels
    """

    # Open the output files
    with open(f'./bin/MER/data/{filename}_word1.txt', 'w') as single_file, \
         open(f'./bin/MER/data/{filename}_word2.txt', 'w') as two_word_file, \
         open(f'./bin/MER/data/{filename}_words.txt', 'w') as multi_word_file, \
         open(f'./bin/MER/data/{filename}_words2.txt', 'w') as unique_two_word_file:

        two_word_seen = set()

        # Process each label from the input file
        with open(labels, 'r') as file:
            for line in file:
                words = line.strip().split()

                if len(words) == 1:
                    # Single word
                    single_file.write(line.lower())
                
                elif len(words) == 2:
                    # Two-word combination
                    two_word_file.write(line.lower())
                    
                    # Process unique two-word combinations
                    combination = tuple(sorted(words))
                    if combination not in two_word_seen:
                        unique_two_word_file.write(line.lower())
                        two_word_seen.add(combination)
                
                elif len(words) > 2:
                    # Multiple words (3 or more)
                    multi_word_file.write(line.lower())



def lowercase_links_file(links_file):
    """Lowercases every label for matching with get_entities.sh
    
    :param links_file (str): labels and IDs file (.txt)
    :return side effect: creates lowercase labels and IDs file (.tsv)
    """

    links_name = links_file.replace('_temp2links.txt','')
    with open(links_file,'r') as input_file:
        lines = input_file.readlines()
        with open (f'{links_name}_links.tsv', 'w') as output_file:
            for line in lines:
                label = line.split('|')[0].lower()
                id = line.split('|')[1]
                entity = (f'{label} {id}')
                output_file.write(entity)






print("---------------------------\n  CREATING LEXICON FILES\n---------------------------")        

     
#########################################################
#   HANDLE SPECIFIC CLASSES FILES FOR EACH DATA TYPE    #
#########################################################

data_sources = ['microorganisms', 'plants']         # Stress lexicon files were manually created

for data_type in data_sources:
    start_time = time.time() #----------------------------------------------------------------------------------------------- LOG: TIME

    print(f'\n** {data_type.title()} lexicon data **\n')

    classes_path = f"./bin/MER/classes_{data_type}.txt"     ### CHANGEABLE: Classes files template name ###
    lines = read_classes_into_array(classes_path)  

    # Paths to files
    ontology_path = "./bin/MER/ncbitaxon.owl"               ### CHANGEABLE: Ontology file you're using ###
    filename = classes_path.replace("./bin/MER/classes_","").replace(".txt","")
    file_labels_path = f"./bin/MER/data/{filename}_templabels.txt"
    file_links_path = f"./bin/MER/data/{filename}_templinks.txt"
    file_synonyms_path = f"./bin/MER/data/{filename}_tempsynonyms.txt"

    # Load the ontology
    ontology = get_ontology(ontology_path).load()

    # Open output files for writing
    labels_file = open(file_labels_path, 'w')
    links_file = open(file_links_path, 'w')
    synonyms_file = open(file_synonyms_path, 'w')

    # Process the ontology file and remove duplicates from resulting synonyms file
    start_process_owl_file(ontology, lines, labels_file, links_file, synonyms_file)
    output_labels_file = edit_labels_file()
    output_synonyms_file = edit_synonyms_file()
    output_links_file = edit_links_file()

    if data_type == 'microorganisms':       # Only microorganisms files are subjected to this step
        final_editing_microorganisms()
        
    if data_type == 'plants':               # Only plants files are subjected to this step
        final_editing_plants()

    # Split the labels file into the required files
    split_labels_into_files(output_labels_file)

    # Lowercase all labels in links file and removes temporary file
    lowercase_links_file(output_links_file)
    os.system(f'rm -f {output_links_file}')
    print(f"\n{data_type.capitalize()} lexicon files have been created at bin/MER/data")

    labels_file.close()
    links_file.close()
    end_time = time.time() #----------------------------------------------------------------------------------------------- LOG: TIME

    print(f'RUNTIME: {end_time - start_time:8.1f} seconds\n----------------------------------------') #-------------------- LOG: INFO
