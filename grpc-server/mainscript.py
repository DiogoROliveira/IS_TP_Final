import csv
import os
import sys
import xml.etree.ElementTree as ET
from xml.dom import minidom
from lxml import etree
import xmlschema

# --- Função para converter CSV em XML ---
def csv_to_xml(csv_file, xml_file, objname):
    root = ET.Element("root")

    with open(csv_file, mode='r', newline='', encoding='utf-8') as csvfile:
        reader = csv.DictReader(csvfile, delimiter=',')
        for line in reader:
            obj = ET.Element(objname)
            for field, value in line.items():
                element = ET.SubElement(obj, field)
                element.text = value
            root.append(obj)

    xml_string = ET.tostring(root, encoding='utf-8')
    xml_pretty = minidom.parseString(xml_string).toprettyxml(indent='  ')

    with open(xml_file, mode='w', encoding='utf-8') as xmlfile:
        xmlfile.write(xml_pretty)

    print(f"XML file created successfully! - {xml_file}")


def fill_empty_fields(xml_file):
    tree = ET.parse(xml_file)
    root = tree.getroot()

    for airport in root.findall("Airport"):
        for field in airport:
            if field.text is None or field.text.strip() == "":
                field.text = "0"

    tree.write(xml_file, encoding='utf-8', xml_declaration=True)

# --- Função para validar XML contra XSD ---
def validate_xml(xml_file, xsd_file):
    try:
        schema = xmlschema.XMLSchema(xsd_file)
        if schema.is_valid(xml_file):
            print("XML file is valid!")
        else:
            print("XML file is invalid!")
            for error in schema.iter_errors(xml_file):
                print(error)
    except Exception as e:
        print("An error occurred during validation:", e)


# --- Função para transformação XSLT ---
def xslt_transform(xml_file, xslt_file, output_file):
    xml_base = etree.parse(xml_file)
    xslt = etree.parse(xslt_file)
    transform = etree.XSLT(xslt)
    sub_xml = transform(xml_base)

    with open(output_file, "wb") as f:
        f.write(etree.tostring(sub_xml, pretty_print=True, encoding="UTF-8", xml_declaration=True))

    print(f"Sub-XML created successfully: {output_file}")


# --- Execução Principal ---
def main():
    # Diretórios definidos como variáveis de ambiente
    dirname = os.getenv('DIRNAME', './schemas/')
    resultdir = os.getenv('RESULTDIR', './data/output/')
    os.makedirs(resultdir, exist_ok=True)

    # Parâmetros de entrada como argumentos de linha de comando
    if len(sys.argv) < 5:
        print("Usage: script.py <csv_file> <xml_file> <root_object_name> <result_xml_file>")
        sys.exit(1)

    csvfile = sys.argv[1]
    xmlfile = sys.argv[2]
    objname = sys.argv[3]
    resultfile = sys.argv[4]

    # Verificar a existência de arquivos essenciais
    xsdfile = os.path.join(dirname, "schema.xsd")
    xsltfile = os.path.join(dirname, "filter.xsl")

    if not os.path.exists(xsdfile) or not os.path.exists(xsltfile):
        print("Schema or XSLT files are missing!")
        sys.exit(1)

    # Conversão CSV para XML
    csv_to_xml(csvfile, xmlfile, objname)

    fill_empty_fields(xmlfile)

    # Validação do XML
    validate_xml(xmlfile, xsdfile)

    # Transformação XSLT
    output_path = os.path.join(resultdir, resultfile)
    xslt_transform(xmlfile, xsltfile, output_path)


if __name__ == "__main__":
    main()
