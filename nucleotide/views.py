from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.pagination import PageNumberPagination

from nucleotide.nucleotide_search import fetch_nucleotide_sequence, search_pattern_in_sequence

class NucleotideSearchView(APIView):
    def get(self, request):
        pattern = request.query_params.get('pattern', None)
        if not pattern:
            return Response({"error": "No search pattern provided."}, status=status.HTTP_400_BAD_REQUEST)

        nucleotide_id = "30271926"
        try:
            sequence_data = fetch_nucleotide_sequence(nucleotide_id)
            matches = search_pattern_in_sequence(sequence_data, pattern)
            paginator = PageNumberPagination()
            paginator.page_size = 10

            if matches:
                paginated_matches = paginator.paginate_queryset(matches, request)
                return paginator.get_paginated_response(paginated_matches)
            else:
                return Response({"message": f"No matches found for pattern: {pattern}"})
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
