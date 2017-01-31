with open('tissue_and_organ_query_result.txt') as f:
    terms = f.readlines()[3:-1]

terms = map(lambda term: term.strip(), terms)
terms = map(lambda term: term[1:-1].strip(), terms)
terms = map(lambda term: term[1:-1], terms)

with open('../../data/TISSUE_AND_ORGAN.txt', 'w') as f:
    map(lambda term: f.write(term + '\n'), terms)
