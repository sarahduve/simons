from django.test import TestCase
import unittest
from unittest.mock import patch
import xml.etree.ElementTree as ET
from nucleotide_search import fetch_nucleotide_sequence, search_pattern_in_sequence

class TestNucleotideSearch(unittest.TestCase):

    @patch("nucleotide_search.requests.get")
    def test_fetch_nucleotide_sequence_success(self, mock_get):
        """Test fetch_nucleotide_sequence with a successful API response"""
        mock_response = """<?xml version="1.0"?>
        <TSeqSet>
            <TSeq>
                <TSeq_sequence>AGCTAGCTAGCTAGCT</TSeq_sequence>
            </TSeq>
        </TSeqSet>"""

        mock_get.return_value.status_code = 200
        mock_get.return_value.text = mock_response

        result = fetch_nucleotide_sequence("123456")
        self.assertEqual(result, "AGCTAGCTAGCTAGCT")

    @patch("nucleotide_search.requests.get")
    def test_fetch_nucleotide_sequence_failure(self, mock_get):
        """Test fetch_nucleotide_sequence with a failed API response"""
        mock_get.return_value.status_code = 404

        with self.assertRaises(Exception) as context:
            fetch_nucleotide_sequence("123456")
        self.assertIn("Failed to fetch data", str(context.exception))

    @patch("nucleotide_search.requests.get")
    def test_fetch_nucleotide_sequence_malformed_xml(self, mock_get):
        """Test fetch_nucleotide_sequence with malformed XML"""
        mock_get.return_value.status_code = 200
        mock_get.return_value.text = "<invalid_xml>"

        with self.assertRaises(Exception) as context:
            fetch_nucleotide_sequence("123456")
        self.assertIn("Failed to parse the XML response", str(context.exception))

    def test_search_pattern_in_sequence_match(self):
        """Test search_pattern_in_sequence finds correct matches"""
        sequence = "AATCGAAGCTAATCGA"
        pattern = "AATCGA"
        result = search_pattern_in_sequence(sequence, pattern)

        expected = [
            {"start": 0, "end": 6, "match": "AATCGA"},
            {"start": 10, "end": 16, "match": "AATCGA"},
        ]
        self.assertEqual(result, expected)

    def test_search_pattern_in_sequence_no_match(self):
        """Test search_pattern_in_sequence when no match is found"""
        sequence = "AGCTAGCTAGCTAGCT"
        pattern = "AATCGA"
        result = search_pattern_in_sequence(sequence, pattern)
        self.assertEqual(result, [])

    def test_search_pattern_in_sequence_partial_match(self):
        """Test search_pattern_in_sequence when partial match exists"""
        sequence = "AATCG"
        pattern = "AATCGA"
        result = search_pattern_in_sequence(sequence, pattern)
        self.assertEqual(result, [])

if __name__ == "__main__":
    unittest.main()

