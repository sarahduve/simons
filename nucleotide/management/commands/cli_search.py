import os
import requests
import xml.etree.ElementTree as ET
from django.core.management.base import BaseCommand
from tqdm import tqdm
import re

def download_file_with_progress(nucleotide_id):
    url = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/efetch.fcgi"
    params = {
        "db": "nucleotide",
        "id": nucleotide_id,
        "rettype": "fasta",
        "retmode": "xml",
    }

    response = requests.get(url, params=params, stream=True)
    total_size_in_bytes = int(response.headers.get('Content-Length', 0))

    file_name = f"{nucleotide_id}.fasta"

    if not os.path.exists(file_name):
        if response.status_code == 200:
            with open(file_name, 'wb') as file, tqdm(
                    desc=file_name,
                    total=total_size_in_bytes,
                    unit='B',
                    unit_scale=True,
                    ncols=100
            ) as bar:
                for data in response.iter_content(chunk_size=1024):
                    file.write(data)
                    bar.update(len(data))
            print(f"Sequence for nucleotide ID {nucleotide_id} saved to {file_name}")
        else:
            print(f"Failed to fetch data. Status code: {response.status_code}")
    else:
        print(f"File {file_name} already exists. Skipping download.")

def search_pattern_in_file(file_name, pattern):
    with open(file_name, 'r') as file:
        lines = file.readlines()

    sequence = ''.join(line.strip() for line in lines if not line.startswith('>'))

    matches = []
    for match in re.finditer(pattern, sequence):
        matches.append({
            'start': match.start(),
            'end': match.end(),
            'match': match.group(0)
        })

    return matches

class Command(BaseCommand):
    help = 'Download and search for a pattern in a nucleotide sequence file.'

    def add_arguments(self, parser):
        parser.add_argument('nucleotide_id', type=str, help="The Nucleotide ID (e.g. 224589800)")
        parser.add_argument('pattern', type=str, help="The pattern to search for (e.g. AATCGA)")

    def handle(self, *args, **options):
        nucleotide_id = options['nucleotide_id']
        pattern = options['pattern']

        file_name = f"{nucleotide_id}.fasta"

        download_file_with_progress(nucleotide_id)

        if os.path.exists(file_name):
            matches = search_pattern_in_file(file_name, pattern)
            if matches:
                for match in matches:
                    self.stdout.write(f"Pattern '{match['match']}' found at position {match['start']} to {match['end']}")
            else:
                self.stdout.write(f"Pattern '{pattern}' not found in the sequence.")
        else:
            self.stdout.write(f"File for nucleotide ID {nucleotide_id} does not exist after download attempt.")
