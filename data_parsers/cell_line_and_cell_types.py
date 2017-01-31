from lxml import etree

with open('cellosaurus.xml') as f:
    cell_xml = etree.parse(f)

names = cell_xml.findall('//name')

with open('../../data/cellosaurus.txt', 'w') as f:
    map(lambda name: f.write(name.text + '\n'), names)
