import os
from owlready2 import get_ontology

def read_classes_into_array(file_path):
    """Reads the classes file line by line, strips newline characters and class names,
    and returns the IRIs as a list of strings
    
    :param file_path: path to file
    :return: list of strings
    """

    lines = []
    with open(file_path, 'r') as file:
        lines = [line.strip().split(" ")[1] for line in file.readlines()]  # Strip newline characters and names
    return lines



def strip_label(label):
    """Cleans up labels by removing specific unwanted characters
    
    :param label: label string 
    :return: clean label string
    """

    return str(label).replace("['", "").replace("']", "")



def start_process_owl_file(ontology, lines, labels_file,links_file, synonyms_file):
    """Takes a list of classes and iterates over the ontology, extracting labels, synonyms and IRIs
    for each matching class (also handles every subclass)
    
    :param ontology: ontology (.owl) file
    :param lines: list of strings (class names)
    :param labels_file: path to labels file
    :param links_file: path to links ([LABEL] [IRI]) file (.txt)
    :param synonyms_file: path to file where label and respective synonyms will be stored
    :return: output labels and links to respective files
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



def process_owl_file(ontology, lines, labels_file,links_file, synonyms_file):
    """Recursively processes subclasses of the classes identified in 'start_process_owl_file'
    
    :param ontology: ontology (.owl) file
    :param lines: list of strings (class names)
    :param labels_file: path to labels file
    :param links_file: path to links ([LABEL] [IRI]) file
    :param synonyms_file: path to file where label and respective synonyms will be stored
    :return: output labels and links to respective files
    """

    ids_to_process = []
    for id in lines:
        # Search for the class by IRI
        cls = ontology.search_one(iri=id)
        sub_ontology = ontology.search(subclass_of = cls)
        if len(sub_ontology) > 0:
            for sub_cls in sub_ontology:
                if sub_cls.iri == id :
                    continue
                # Write subclass label and IRI to the output files
                labels_file.write(f"{strip_label(sub_cls.label)}\n")
                synonyms_file.write(f"{strip_label(sub_cls.label)}\n")
                links_file.write(f"{strip_label(sub_cls.label)}|{strip_label(sub_cls.iri)}\n")
                ids_to_process.append(sub_cls.iri)

                # Process and write synonyms
                for synonyms in sub_cls.hasExactSynonym:
                    labels_file.write(f"{synonyms}\n")
                    
                    links_file.write(f"{synonyms}|{sub_cls.iri}\n")
                for synonyms in sub_cls.hasRelatedSynonym:
                    labels_file.write(f"{synonyms}\n")
                    synonyms_file.write(f"{synonyms}\n")
                    links_file.write(f"{synonyms}|{sub_cls.iri}\n")
                
                synonyms_file.write("-\n")



def remove_duplicates(file):
    """Takes a text file and produces a new file without duplicates

    :param file: path to original file
    :return: final file path; outputs unique entries to final file
    """
    labels_name = file.replace('_templabels.txt','')
    new_file = f'{labels_name}.txt'
    lines_seen = set() # holds lines already seen
    with open(file, 'r') as input_file:
        lines = input_file.readlines()

        with open(new_file, 'a') as output_file:
            for line in lines:
                if line not in lines_seen: # not a duplicate
                    lines_seen.add(line)
                    output_file.write(line)

    output_file.close()
    os.system(f'rm -f {file}')

    print("Duplicates removed")
    return new_file

    
    

def split_labels_into_files(labels):
    """Divides the labels found into different files according to the number of words and uniqueness
    
    :param input_file: path to labels file (.txt)
    :return: outputs 4 files with different length labels
    """

    # Open the output files
    with open(f'./data/{filename}_word1.txt', 'w') as single_file, \
         open(f'./data/{filename}_word2.txt', 'w') as two_word_file, \
         open(f'./data/{filename}_words.txt', 'w') as multi_word_file, \
         open(f'./data/{filename}_words2.txt', 'w') as unique_two_word_file:

        two_word_seen = set()

        labels_file = remove_duplicates(labels)

        # Process each label from the input file
        with open(labels_file, 'r') as file:
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
    :return: outputs lowercase labels and IDs file (.tsv)
    """

    links_name = links_file.replace('_templinks.txt','')
    with open(links_file,'r') as input_file:
        lines = input_file.readlines()
        with open (f'{links_name}_links.tsv', 'w') as output_file:
            for line in lines:
                label = line.split('|')[0].lower()
                id = line.split('|')[1]
                entity = (f'{label}\t{id}')
                output_file.write(entity)



print(f"Starting")        

     

# Read specific classes file into array
classes_path = "./class_names_plants.txt" # Classes file you wish to use
lines = read_classes_into_array(classes_path)    
print(f"Lines read")

# Paths to files
ontology_path = "./ncbitaxon.owl" # Ontology file you wish to use
filename = classes_path.replace("./class_names_","").replace(".txt","")

# Check whether the specified path exists or not
if not os.path.exists("./data"):
   # Create a new directory because it does not exist
   os.makedirs("./data")
   print("/data/ directory created")
file_labels_path = f"./data/{filename}_templabels.txt" # To be created
file_links_path = f"./data/{filename}_templinks.txt" # To be created
file_synonyms_path = f"./data/{filename}_synonyms.txt" # To be created

# Load the ontology
ontology = get_ontology(ontology_path).load()
print(f"Ontology loaded")

# Open output files for writing
labels_file = open(file_labels_path, 'w')
links_file = open(file_links_path, 'w')
synonyms_file = open(file_synonyms_path, 'w')
print(f"Files created")

# Process the ontology file
start_process_owl_file(ontology, lines, labels_file, links_file, synonyms_file)
print(f"Processing done")

# Split the labels file into the required files
split_labels_into_files(file_labels_path)
print(f"Label splitting done")

# Lowercase all labels in links file and removes temporary file
lowercase_links_file(file_links_path)
os.system(f'rm -f {file_links_path}')
print("Final links file obtained")

labels_file.close()
links_file.close()