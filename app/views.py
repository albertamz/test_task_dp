import json
from datetime import datetime, timedelta
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt

from db.models import *


def parse_date(date_str):
    """Parse date string in format DD.MM.YYYYT HH:MM"""
    try:
        return datetime.strptime(date_str, "%d.%m.%YT%H:%M")
    except ValueError:
        return None


def tables(request):
    """
    GET /tables/ - return all tables
    GET /tables/?date=DD.MM.YYYYT HH:MM - returns a list of available tables for a given date ± 2 hours
    """
    if request.method != "GET":
        return JsonResponse({"error": "Method not allowed"}, status=405)
    
    date_param = request.GET.get("date")
    
    if date_param:
        # Return available tables for given date ± 2 hours
        booking_date = parse_date(date_param)
        if booking_date is None:
            return JsonResponse({"error": "Invalid date format. Expected: DD.MM.YYYYT HH:MM"}, status=400)

        time_window_start = booking_date - timedelta(hours=2)
        time_window_end = booking_date + timedelta(hours=2)

        # Get all tables
        all_tables = Table.objects.all()
        
        # Get booked table IDs in the time window
        booked_table_ids = Booking.objects.filter(
            date__gte=time_window_start,
            date__lte=time_window_end
        ).values_list("table_id", flat=True)

        # Filter available tables
        available_tables = all_tables.exclude(id__in=booked_table_ids)

        return JsonResponse(
            {"tables": [{"id": t.id, "name": t.name} for t in available_tables]}
        )
    
    # Return all tables
    return JsonResponse(
        {"tables": [{"id": i.id, "name": i.name} for i in Table.objects.all()]}
    )


@csrf_exempt
def bookings(request):
    """
    POST /bookings/ - Create new booking
    """
    if request.method != "POST":
        return JsonResponse({"error": "Method not allowed"}, status=405)
    
    try:
        data = json.loads(request.body)
    except json.JSONDecodeError:
        return JsonResponse({"error": "Invalid JSON"}, status=400)

    # Validate required fields
    required_fields = ["client_name", "client_phone", "date", "table"]
    for field in required_fields:
        if field not in data:
            return JsonResponse({"error": f"Missing required field: {field}"}, status=400)

    # Parse and validate date
    booking_date = parse_date(data["date"])
    if booking_date is None:
        return JsonResponse({"error": "Invalid date format. Expected: DD.MM.YYYYT HH:MM"}, status=400)

    # Validate table exists
    try:
        table = Table.objects.get(id=data["table"])
    except Table.DoesNotExist:
        return JsonResponse({"error": f"Table with id {data['table']} does not exist"}, status=404)

    # Check for conflicts in ±2 hour window
    time_window_start = booking_date - timedelta(hours=2)
    time_window_end = booking_date + timedelta(hours=2)

    conflicting_booking = Booking.objects.filter(
        table=table,
        date__gte=time_window_start,
        date__lte=time_window_end
    ).first()

    if conflicting_booking:
        return JsonResponse(
            {
                "error": "Table is already booked in this time window (±2 hours)",
                "conflicting_booking": {
                    "id": conflicting_booking.id,
                    "date": conflicting_booking.date.strftime("%d.%m.%YT%H:%M"),
                    "client_name": conflicting_booking.client_name
                }
            },
            status=409
        )

    # Validate client_name and client_phone
    client_name = data["client_name"].strip()
    client_phone = data["client_phone"].strip()

    if not client_name:
        return JsonResponse({"error": "client_name cannot be empty"}, status=400)

    if not client_phone:
        return JsonResponse({"error": "client_phone cannot be empty"}, status=400)

    # Create booking
    booking = Booking.objects.create(
        table=table,
        date=booking_date,
        client_name=client_name,
        client_phone=client_phone
    )

    return JsonResponse(
        {
            "id": booking.id,
            "client_name": booking.client_name,
            "client_phone": booking.client_phone,
            "date": booking.date.strftime("%d.%m.%YT%H:%M"),
            "table": booking.table.id,
        },
        status=201
    )
