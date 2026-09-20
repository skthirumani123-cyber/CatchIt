"""
Comprehensive Automated Test Suite for BusFlow
Validates Backend, REST APIs, Smart Schedule Engine, Role Access, and What-If Contingency Engine.
"""

import sys
from app import app
from models import get_db

def run_tests():
    print("==================================================")
    print("   BUSFLOW SYSTEM VERIFICATION & TEST SUITE       ")
    print("==================================================")

    client = app.test_client()
    passed = 0
    total = 0

    def assert_test(name, condition, extra=""):
        nonlocal passed, total
        total += 1
        if condition:
            passed += 1
            print(f"[PASS] {name} {extra}")
        else:
            print(f"[FAIL] {name} {extra}")
            sys.exit(1)

    # 1. Test Home Landing Page
    resp = client.get('/')
    assert_test("GET / (Home Page)", resp.status_code == 200 and b"Your Journey" in resp.data)

    # 2. Test Login Page
    resp = client.get('/login')
    assert_test("GET /login", resp.status_code == 200 and b"Welcome Back" in resp.data)

    # 3. Test Register Page
    resp = client.get('/register')
    assert_test("GET /register", resp.status_code == 200 and b"Create Your Account" in resp.data)

    # 4. Test API: Route Search (Tumkur -> Bangalore)
    resp = client.get('/api/schedules/search?source=Tumkur&destination=Bangalore')
    data = resp.get_json()
    assert_test("API /api/schedules/search", resp.status_code == 200 and data.get('success') and len(data.get('schedules', [])) > 0, f"(Found {len(data.get('schedules', []))} schedules)")

    # 5. Test API: What-If Contingency Simulator
    resp = client.get('/api/what-if?bus_id=1')
    data = resp.get_json()
    assert_test("API /api/what-if (Bus 1 Breakdown)", resp.status_code == 200 and data.get('success') and len(data['simulation']['recommendations']) > 0, f"(Generated {len(data['simulation']['recommendations'])} reroute recs)")

    # 6. Test API: Live GPS Telemetry Corridor
    resp = client.get('/api/live-tracking')
    data = resp.get_json()
    assert_test("API /api/live-tracking", resp.status_code == 200 and data.get('success') and len(data.get('fleet', [])) > 0, f"(Tracking {len(data.get('fleet', []))} active buses)")

    # 7. Test Smart Delay Cascading Engine
    resp = client.post('/api/schedules/1/delay', json={'delay_minutes': 25, 'reason': 'Peenya traffic bottleneck'})
    data = resp.get_json()
    assert_test("API /api/schedules/1/delay", resp.status_code == 200 and data.get('success') and data['schedule']['status'] == 'Delayed', f"(Updated ETA: {data['schedule']['expected_arrival_time']})")

    # 8. Test Occupancy Update
    resp = client.post('/api/schedules/1/occupancy', json={'occupancy': 'Full'})
    data = resp.get_json()
    assert_test("API /api/schedules/1/occupancy", resp.status_code == 200 and data.get('occupancy') == 'Full')

    # 9. Test Demo Login - Admin Flow
    with client.session_transaction() as sess:
        sess['user_id'] = 1
        sess['name'] = 'Admin In-Charge'
        sess['role'] = 'admin'
        sess['email'] = 'admin@busflow.com'

    resp = client.get('/admin')
    assert_test("GET /admin (Admin Dashboard)", resp.status_code == 200 and b"Control Center" in resp.data)

    resp = client.get('/admin/buses')
    assert_test("GET /admin/buses (Fleet Management)", resp.status_code == 200 and b"Fleet Management" in resp.data)

    resp = client.get('/admin/routes')
    assert_test("GET /admin/routes (Routes Management)", resp.status_code == 200 and b"Route Management" in resp.data)

    resp = client.get('/admin/schedules')
    assert_test("GET /admin/schedules (Schedules Management)", resp.status_code == 200 and b"Schedule Management" in resp.data)

    resp = client.get('/admin/what-if')
    assert_test("GET /admin/what-if (Simulator View)", resp.status_code == 200 and b"Contingency" in resp.data)

    resp = client.get('/admin/analytics')
    assert_test("GET /admin/analytics (Analytics & Reports)", resp.status_code == 200 and b"Transit Analytics" in resp.data)

    # 10. Test Driver Portal
    with client.session_transaction() as sess:
        sess['user_id'] = 2
        sess['name'] = 'Ravi Kumar'
        sess['role'] = 'driver'
        sess['email'] = 'driver@busflow.com'
        sess['license_number'] = 'KA-123456'

    resp = client.get('/driver')
    assert_test("GET /driver (Driver Console)", resp.status_code == 200 and b"Ravi Kumar" in resp.data)

    # 11. Test Passenger Portal & Seat Booking
    with client.session_transaction() as sess:
        sess['user_id'] = 3
        sess['name'] = 'Skanda Bharadwaj'
        sess['role'] = 'passenger'
        sess['email'] = 'passenger@busflow.com'

    resp = client.get('/passenger')
    assert_test("GET /passenger (Passenger Dashboard)", resp.status_code == 200 and b"Skanda Bharadwaj" in resp.data)

    resp = client.post('/api/book-seat', json={'schedule_id': 1, 'seat_number': 7, 'passenger_name': 'Skanda Bharadwaj'})
    data = resp.get_json()
    assert_test("API /api/book-seat (Ticket Reservation)", resp.status_code == 200 and data.get('success') and 'booking_code' in data, f"(Code: {data.get('booking_code')})")

    print("==================================================")
    print(f" ALL {passed}/{total} VERIFICATION TESTS PASSED SUCCESSFULLY! ")
    print("==================================================")

if __name__ == '__main__':
    run_tests()
