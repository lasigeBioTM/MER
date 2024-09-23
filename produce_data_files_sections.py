import os
import re
import time
from owlready2 import get_ontology

def read_classes_into_array(file_path):
    """Reads the classes file line by line, strips newline characters and class names,
    and returns the IRIs as a list of strings
    
    :param file_path: path to file
    :return: list of strings
    """

    lines = []
    with open(file_path, 'r') as file:
        lines = [line.strip().split("|")[1] for line in file.readlines()]  # Strip newline characters and names

    return lines



def strip_label(label):
    """Cleans up labels by removing specific unwanted characters
    
    :param label: label string 
    :return: clean label string
    """

    return str(label).replace("['", "").replace("']", "")



def start_process_owl_file(ontology, lines, labels_file, links_file, synonyms_file):
    """Takes a list of classes and iterates over the ontology, extracting labels, synonyms and IRIs
    for each matching class (also handles every subclass)
    
    :param ontology: ontology (.owl) file
    :param lines: list of strings (class IRIs)
    :param labels_file: path to labels file (.txt)
    :param links_file: path to links ([LABEL] [IRI]) file (.txt)
    :param synonyms_file: path to file where label and respective synonyms will be stored (.txt)
    :return: None; outputs labels and links to respective files
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
    
    :param ontology: ontology (.owl) file
    :param lines: list of strings (class IRIs)
    :param labels_file: path to labels file (.txt)
    :param links_file: path to links ([LABEL] [IRI]) file (.txt)
    :param synonyms_file: path to file where label and respective synonyms will be stored (.txt)
    :return: None; outputs labels and links to respective files
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
                    no_mappings.add(cls)

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
    

    print(f'number of classes with no mappings: {len(no_mappings)}') #------------------------------------- LOG: INFO
    print(f'class IDs: {no_mappings}') #------------------------------------------------------------------- LOG: INFO



def edit_file(original_file, new_file):
    """Takes a text file and produces a new file without duplicates and unwanted characters or lines, and added relevant entries

    :param file: path to original file
    :return: None; outputs unique edited entries and added ones to final file
    """

    lines_seen = set() # Holds lines already seen

    with open(original_file, 'r') as input_file:
        lines = input_file.readlines()

        with open(new_file, 'a') as output_file:
            for line in lines:

                # Remove unwanted characters
                line = re.sub("^'",'', line)
                line = re.sub("'$",'', line)
                line = re.sub(r'\["','', line)
                line = re.sub(r'"\]','', line)

                # Unique non-empty lines, separators in synonyms file and lines without invalid names
                if line not in lines_seen  or line == '' or line == '-\n' or re.search(r'\(nom\. inval\.\)$', line):

                    # Include common names without the "common" prefix
                    if re.search('^common', line):
                        no_prefix = line.replace('common ','')
                        lines_seen.add(line)
                        lines_seen.add(no_prefix)
                        output_file.write(f'{line}')
                        output_file.write(f'{no_prefix}')

                    # Include group names without the "group" suffix
                    if re.search('group$', line):
                        no_suffix = line.replace(' group','')
                        lines_seen.add(line)
                        lines_seen.add(no_suffix)
                        output_file.write(f'{line}')
                        output_file.write(f'{no_suffix}')

                    # Include names without authors &/or entry year
                    elif re.search(r"\(", line):
                        no_author_year = re.sub(r" \((.*)\|", '|', line)
                        lines_seen.add(line)
                        lines_seen.add(no_author_year)
                        output_file.write(f'{line}')
                        output_file.write(f'{no_author_year}')
                    
                    # Extract names in between " "
                    elif re.search('"(.*)"', line):
                        no_accents = re.search('"(.*)"', line).group(1)
                        lines_seen.add(line)
                        lines_seen.add(no_accents)
                        output_file.write(f'{line}')
                        output_file.write(f'{no_accents}')

                    # Don't include irrelevant terms in final file
                    elif re.search('^algae', line) or re.search('^plants', line) or re.search('^phyla', line) or re.search('^microbiota', line):
                        lines_seen.add(line)

                    # If none of the specified conditions applies
                    else:
                        lines_seen.add(line)
                        output_file.write(line)
    
    output_file.close()
    os.system(f'rm -f {original_file}')



def edit_labels_file():
    """Takes a text file and produces a new file without duplicates and unwanted characters or lines, and added relevant entries

    :param file: path to original file
    :return: None; outputs unique edited entries and added ones to final file
    """
    input_file = file_labels_path
    output_file = input_file.replace('_templabels', '')
    edit_file(input_file, output_file)

    return output_file


def edit_synonyms_file():
    """Takes a text file and produces a new file without duplicates and unwanted characters or lines, and added relevant entries

    :param file: path to original file
    :return: None; outputs unique edited entries and added ones to final file
    """
    input_file = file_synonyms_path
    output_file = input_file.replace('temp', '')
    edit_file(input_file, output_file)

    return output_file



def edit_links_file():
    """Takes a text file and produces a new file without duplicates and unwanted characters or lines, and added relevant entries

    :param file: path to original file
    :return: None; outputs unique edited entries and added ones to final file
    """
    input_file = file_links_path
    output_file = input_file.replace('temp', 'temp2')
    edit_file(input_file, output_file)

    return output_file
    


def replace_text(file_path, replacement_list): 
  
    # Opening the file in read and write mode 
    with open(file_path,'r+') as f: 

        # Reading the file data and store 
        # it in a file variable 
        file = f.read() 
        
        for tuple in replacement_list:
            search_text = tuple[0]
            replace_text = tuple[1]

            # Replacing the pattern with the string 
            # in the file data 
            file = re.sub(search_text, replace_text, file) 
    
            # Setting the position to the top 
            # of the page to insert data 
            f.seek(0) 
            
            # Writing replaced data in the file 
            f.write(file) 
    
            # Truncating the file size 
            f.truncate() 
        


def final_editing():
    """
    
    """

    # Handling labels file: only need to add the extra terms (order is irrelevant)
    with open(output_labels_file, 'a') as labels_file:
        labels_file.write(f"pepper\n"
                          "bell pepper\n"
                          "red peppers\n"
                          "Millet\n"
                          "sunflower\n"
                          "groundnut\n"
                          "rapeseed\n"
                          "mung bean\n"
                          "moong\n"
                          "great millet\n"
                          "grapevine\n"
                          "grape\n"
                          "grapes\n"
                          "French lavender\n"
                          "jujube\n"
                          "squash")

    # Handling synonyms file: add extra terms near synonyms (order is IMPORTANT)
    replace_text(output_synonyms_file,[
        ("Capsicum annuum", f"Capsicum annuum\npepper\nbell pepper"),
        ("Capsicum annuum var. annuum",f"Capsicum annuum var. annuum\nred peppers"),
        ("Poaceae", f"Poaceae\nmillet"),
        ("Helianthus annuus", f"Helianthus annuus\nsunflower"),
        ("Arachis hypogaea",f"Arachis hypogaea\ngroundnut"),
        ("Brassica napus", f"Brassica napus\nrapeseed"),
        ("Poaceae", f"Poaceae\nmillet"),
        ("Vigna radiata", f"Vigna radiata\nmung bean\nmoong"),
        ("Sorghum",f"Sorghum\ngreat millet"),
        ("Vitis vinifera", f"Vitis vinifera\ngrapevine\ngrapes\ngrape"),
        ("Lavandula dentata", f"Lavandula dentata\nFrench lavender"),
        ("Zizyphus jujuba", f"Zizyphus jujuba\njujube"),
        ("Galega officinalis",f"Galega officinalis\ngoat's rue"),
        ("Cucurbita", f"Cucurbita\nsquash")
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
        "rapeseeed|http://purl.obolibrary.org/obo/NCBITaxon_3708\n"
        "mung bean|http://purl.obolibrary.org/obo/NCBITaxon_157791\n"
        "moong|http://purl.obolibrary.org/obo/NCBITaxon_157791\n"
        "great millet|http://purl.obolibrary.org/obo/NCBITaxon_4557\n"
        "grapevine|http://purl.obolibrary.org/obo/NCBITaxon_29760\n"
        "grape|http://purl.obolibrary.org/obo/NCBITaxon_29760\n"
        "grapes|http://purl.obolibrary.org/obo/NCBITaxon_29760\n"
        "jujube|http://purl.obolibrary.org/obo/NCBITaxon_326968\n"
        "goat's rue|http://purl.obolibrary.org/obo/NCBITaxon_47101\n"
        "squash|http://purl.obolibrary.org/obo/NCBITaxon_3660\n"
        )
        # No class mappings for Lavandula dentata
    


def split_labels_into_files(labels):
    """Divides the labels found into different files according to the number of words and uniqueness
    
    :param input_file: path to labels file (.txt)
    :return: None; outputs 4 files with different length labels
    """

    # Open the output files
    with open(f'./data/{filename}_word1.txt', 'w') as single_file, \
         open(f'./data/{filename}_word2.txt', 'w') as two_word_file, \
         open(f'./data/{filename}_words.txt', 'w') as multi_word_file, \
         open(f'./data/{filename}_words2.txt', 'w') as unique_two_word_file:

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
    
    :param links_file: labels and IDs file (.txt)
    :return: None; outputs lowercase labels and IDs file (.tsv)
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



print("----------------------------------------\ncreating lexicon files\n----------------------------------------")        

     
#########################################################
#   HANDLE SPECIFIC CLASSES FILES FOR EACH DATA TYPE    #
#########################################################

data_sources = ['microorganisms', 'plants']         # Stress lexicon files were manually created

for data_type in data_sources:
    start_time = time.time() #----------------------------------------------------------------------------------------------- LOG: TIME

    print(f'\n{data_type} lexicon data:\n') #---------------------------------------------------------------------------------- LOG: PROGRESS

    classes_path = f"./classes_{data_type}.txt"     ### CHANGEABLE: Classes files template name ###
    lines = read_classes_into_array(classes_path)  

    # Paths to files
    ontology_path = "./ncbitaxon.owl"               ### CHANGEABLE: Ontology file you're using ###
    filename = classes_path.replace("./classes_","").replace(".txt","")
    file_labels_path = f"./data/{filename}_templabels.txt"
    file_links_path = f"./data/{filename}_templinks.txt"
    file_synonyms_path = f"./data/{filename}_tempsynonyms.txt"

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

    if data_type == 'plants':      # Only plants files are subjected to final editing
        final_editing()

    # Split the labels file into the required files
    split_labels_into_files(output_labels_file)

    # Lowercase all labels in links file and removes temporary file
    lowercase_links_file(output_links_file)
    os.system(f'rm -f {output_links_file}')
    print(f"\n{data_type} lexicon files have been created at bin/MER/data") #------------------------------------- LOG: PROGRESS

    labels_file.close()
    links_file.close()
    end_time = time.time() #----------------------------------------------------------------------------------------------- LOG: TIME

    print(f"elapsed time: {end_time - start_time} seconds\n----------------------------------------") #-------------------- LOG: INFO
