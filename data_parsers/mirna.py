terms = []

with open('mirna.txt') as f:
    for mirna in f:
        props = mirna.strip().split("\t")

        name = props[2]
        if name != "":
            terms.append(name)

        previous_names = props[3].split(";")
        if previous_names != ['']:
            terms += previous_names

with open('mirna_mature.txt') as f:
    for mirna in f:
        props = mirna.strip().split("\t")

        name = props[1]
        if name != "":
            terms.append(name)

        previous_names = props[2].split(";")
        if previous_names != ['']:
            terms += previous_names

with open('../../data/MIRNA.txt', 'w') as f:
    map(lambda term: f.write(term + '\n'), terms)
