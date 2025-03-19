import requests
import xml.etree.ElementTree as ET
import re
import time
from tqdm import tqdm

def fetch_nucleotide_sequence(nucleotide_id):
    url = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/efetch.fcgi"
    params = {
        "db": "nucleotide",
        "id": nucleotide_id,
        "rettype": "fasta",
        "retmode": "xml",
    }

    response = requests.get(url, params=params)

    if response.status_code == 200:
        try:
            root = ET.fromstring(response.text)
            sequence_data = root.find(".//TSeq_sequence").text
            return sequence_data
        except ET.ParseError:
            raise Exception("Failed to parse the XML response.")
    else:
        raise Exception(f"Failed to fetch data. Status code: {response.status_code}")

def search_pattern_in_sequence(sequence_data, pattern):
    matches = []
    for match in re.finditer(pattern, sequence_data):
        matches.append({
            "start": match.start(),
            "end": match.end(),
            "match": match.group(),
        })
    return matches
