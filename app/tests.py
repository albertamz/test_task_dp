from django.test import TestCase, Client
from datetime import datetime
import json

from db.models import Table, Booking


class BookingAPITestCase(TestCase):
    def setUp(self):
        self.client = Client()
        self.table1 = Table.objects.create(name="Table 1")
        self.table2 = Table.objects.create(name="Table 2")
        self.table3 = Table.objects.create(name="Table 3")

    def test_get_all_tables(self):
        """Test GET /tables/ - returns all tables"""
        response = self.client.get("/tables/")
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.content)
        self.assertIn("tables", data)
        self.assertEqual(len(data["tables"]), 3)

    def test_get_available_tables_with_date(self):
        """Test GET /tables/?date=... - returns available tables"""
        # Create a booking for table1 at 20:00
        booking_date = datetime(2023, 7, 1, 20, 0)
        Booking.objects.create(
            table=self.table1,
            date=booking_date,
            client_name="Test Client",
            client_phone="1234567890"
        )

        # Request available tables at 20:00 (should exclude table1)
        response = self.client.get("/tables/?date=01.07.2023T20:00")
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.content)
        self.assertIn("tables", data)
        table_ids = [t["id"] for t in data["tables"]]
        self.assertNotIn(self.table1.id, table_ids)
        self.assertIn(self.table2.id, table_ids)
        self.assertIn(self.table3.id, table_ids)

    def test_get_available_tables_time_window(self):
        """Test that ±2 hour window works correctly"""
        # Create booking at 20:00
        booking_date = datetime(2023, 7, 1, 20, 0)
        Booking.objects.create(
            table=self.table1,
            date=booking_date,
            client_name="Test Client",
            client_phone="1234567890"
        )

        # Request at 19:00 (1 hour before, within ±2h window)
        response = self.client.get("/tables/?date=01.07.2023T19:00")
        data = json.loads(response.content)
        table_ids = [t["id"] for t in data["tables"]]
        self.assertNotIn(self.table1.id, table_ids)

        # Request at 18:00 (2 hours before, at the edge)
        response = self.client.get("/tables/?date=01.07.2023T18:00")
        data = json.loads(response.content)
        table_ids = [t["id"] for t in data["tables"]]
        self.assertNotIn(self.table1.id, table_ids)

        # Request at 17:59 (just outside the window)
        response = self.client.get("/tables/?date=01.07.2023T17:59")
        data = json.loads(response.content)
        table_ids = [t["id"] for t in data["tables"]]
        self.assertIn(self.table1.id, table_ids)

    def test_create_booking_success(self):
        """Test POST /bookings/ - create booking successfully"""
        data = {
            "client_name": "Alex",
            "client_phone": "0931234567",
            "date": "29.06.2023T20:00",
            "table": self.table1.id
        }
        response = self.client.post(
            "/bookings/",
            data=json.dumps(data),
            content_type="application/json"
        )
        self.assertEqual(response.status_code, 201)
        response_data = json.loads(response.content)
        self.assertEqual(response_data["client_name"], "Alex")
        self.assertEqual(response_data["client_phone"], "0931234567")
        self.assertEqual(response_data["table"], self.table1.id)
        self.assertIn("id", response_data)

        # Verify booking was created in database
        booking = Booking.objects.get(id=response_data["id"])
        self.assertEqual(booking.client_name, "Alex")
        self.assertEqual(booking.table.id, self.table1.id)

    def test_create_booking_missing_fields(self):
        """Test POST /bookings/ with missing required fields"""
        data = {
            "client_name": "Alex",
            "date": "29.06.2023T20:00"
            # Missing client_phone and table
        }
        response = self.client.post(
            "/bookings/",
            data=json.dumps(data),
            content_type="application/json"
        )
        self.assertEqual(response.status_code, 400)
        response_data = json.loads(response.content)
        self.assertIn("error", response_data)

    def test_create_booking_invalid_date_format(self):
        """Test POST /bookings/ with invalid date format"""
        data = {
            "client_name": "Alex",
            "client_phone": "0931234567",
            "date": "29-06-2023 20:00",  # Wrong format
            "table": self.table1.id
        }
        response = self.client.post(
            "/bookings/",
            data=json.dumps(data),
            content_type="application/json"
        )
        self.assertEqual(response.status_code, 400)
        response_data = json.loads(response.content)
        self.assertIn("error", response_data)

    def test_create_booking_table_not_exists(self):
        """Test POST /bookings/ with non-existent table"""
        data = {
            "client_name": "Alex",
            "client_phone": "0931234567",
            "date": "29.06.2023T20:00",
            "table": 999  # Non-existent table
        }
        response = self.client.post(
            "/bookings/",
            data=json.dumps(data),
            content_type="application/json"
        )
        self.assertEqual(response.status_code, 404)
        response_data = json.loads(response.content)
        self.assertIn("error", response_data)

    def test_create_booking_conflict(self):
        """Test POST /bookings/ with conflicting booking"""
        # Create existing booking at 20:00
        booking_date = datetime(2023, 7, 1, 20, 0)
        Booking.objects.create(
            table=self.table1,
            date=booking_date,
            client_name="Existing Client",
            client_phone="1111111111"
        )

        # Try to create booking at 19:30 (within ±2h window)
        data = {
            "client_name": "New Client",
            "client_phone": "0931234567",
            "date": "01.07.2023T19:30",
            "table": self.table1.id
        }
        response = self.client.post(
            "/bookings/",
            data=json.dumps(data),
            content_type="application/json"
        )
        self.assertEqual(response.status_code, 409)
        response_data = json.loads(response.content)
        self.assertIn("error", response_data)
        self.assertIn("conflicting_booking", response_data)

    def test_create_booking_no_conflict_outside_window(self):
        """Test that bookings outside ±2h window don't conflict"""
        # Create booking at 20:00
        booking_date = datetime(2023, 7, 1, 20, 0)
        Booking.objects.create(
            table=self.table1,
            date=booking_date,
            client_name="Existing Client",
            client_phone="1111111111"
        )

        # Create booking at 17:00 (3 hours before, outside window)
        data = {
            "client_name": "New Client",
            "client_phone": "0931234567",
            "date": "01.07.2023T17:00",
            "table": self.table1.id
        }
        response = self.client.post(
            "/bookings/",
            data=json.dumps(data),
            content_type="application/json"
        )
        self.assertEqual(response.status_code, 201)  # Should succeed

    def test_create_booking_empty_client_name(self):
        """Test POST /bookings/ with empty client_name"""
        data = {
            "client_name": "   ",  # Only whitespace
            "client_phone": "0931234567",
            "date": "29.06.2023T20:00",
            "table": self.table1.id
        }
        response = self.client.post(
            "/bookings/",
            data=json.dumps(data),
            content_type="application/json"
        )
        self.assertEqual(response.status_code, 400)
        response_data = json.loads(response.content)
        self.assertIn("error", response_data)
