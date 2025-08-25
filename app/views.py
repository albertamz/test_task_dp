from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt

from db.models import *


@csrf_exempt
def booking(request):
    """
    GET: return all tables
    GET + querry param: returns a list of available tables for a given date ± 2 hours. "date": "01.07.2023T20:00"

    POST: Create new booking
    """
    if request.method == "POST":
        """Create new booking"""
        return JsonResponse(
            {
                "client_name": "Alex",
                "client_phone": "0931234567",
                "date": "29.06.2023T20:00",
                "table": 2,
            }
        )
    return JsonResponse(
        {"tables": [{"id": i.id, "name": i.name} for i in Table.objects.all()]}
    )
