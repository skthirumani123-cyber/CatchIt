"""
CatchIt: Smart Bus Schedule & Management System
Smart Schedule Engine, Seat Layout & Most Wanted Heatmap,
Driver Working Hours, Ticket Verification, and Best-Way Route Engine
"""

from datetime import datetime, timedelta, date
from models import get_db

def parse_time(time_str):
    """Parses 'HH:MM' string into a datetime.time object."""
    return datetime.strptime(time_str.strip(), "%H:%M")

def add_minutes_to_time(time_str, minutes):
    """Adds integer minutes to a 'HH:MM' string and returns new 'HH:MM'."""
    dt = datetime.strptime(time_str.strip(), "%H:%M")
    new_dt = dt + timedelta(minutes=int(minutes))
    return new_dt.strftime("%H:%M")

def calculate_stop_times(departure_time_str, delay_minutes, stops):
    """Calculates scheduled and expected (delay-adjusted) arrival times for each stop."""
    results = []
    for stop in stops:
        offset = stop.get('offset_minutes', 0)
        scheduled = add_minutes_to_time(departure_time_str, offset)
        expected = add_minutes_to_time(departure_time_str, offset + delay_minutes)
        results.append({
            'stop_id': stop.get('stop_id'),
            'stop_name': stop.get('stop_name'),
            'sequence': stop.get('sequence'),
            'offset_minutes': offset,
            'scheduled_time': scheduled,
            'expected_time': expected,
            'is_delayed': delay_minutes > 0,
            'delay_minutes': delay_minutes,
            'latitude': stop.get('latitude'),
            'longitude': stop.get('longitude')
        })
    return results

def get_schedule_details(schedule_id):
    """Returns complete schedule details with real-time calculated stop timings and fare."""
    conn = get_db()
    cursor = conn.cursor()

    cursor.execute("""
    SELECT s.*, 
           b.bus_number, b.bus_type, b.capacity, b.status AS bus_status,
           r.route_name, r.source, r.destination, r.distance_km, r.base_fare,
           u.name AS driver_name, u.phone AS driver_phone, u.license_number AS driver_license
    FROM schedules s
    JOIN buses b ON s.bus_id = b.bus_id
    JOIN routes r ON s.route_id = r.route_id
    LEFT JOIN users u ON s.driver_id = u.id
    WHERE s.schedule_id = ?
    """, (schedule_id,))
    schedule = cursor.fetchone()

    if not schedule:
        conn.close()
        return None

    # Fetch stops for this route
    cursor.execute("""
    SELECT * FROM stops 
    WHERE route_id = ? 
    ORDER BY sequence ASC
    """, (schedule['route_id'],))
    stops = cursor.fetchall()
    conn.close()

    delay_mins = schedule.get('delay_minutes', 0)
    calculated_stops = calculate_stop_times(schedule['departure_time'], delay_mins, stops)
    
    if calculated_stops:
        schedule['expected_arrival_time'] = calculated_stops[-1]['expected_time']
    else:
        schedule['expected_arrival_time'] = add_minutes_to_time(schedule['arrival_time'], delay_mins)

    schedule['stops'] = calculated_stops
    return schedule

def apply_schedule_delay(schedule_id, delay_minutes, reason="Traffic congestion"):
    """Smart Delay Management: Cascades delay to all subsequent stops."""
    conn = get_db()
    cursor = conn.cursor()

    delay_minutes = int(delay_minutes)
    status = 'Delayed' if delay_minutes > 0 else 'On Time'

    cursor.execute("SELECT departure_time, arrival_time FROM schedules WHERE schedule_id = ?", (schedule_id,))
    row = cursor.fetchone()
    if not row:
        conn.close()
        return False, "Schedule not found"

    cursor.execute("""
    UPDATE schedules 
    SET delay_minutes = ?, delay_reason = ?, status = ?
    WHERE schedule_id = ?
    """, (delay_minutes, reason, status, schedule_id))

    cursor.execute("""
    INSERT INTO delays (schedule_id, delay_minutes, reason)
    VALUES (?, ?, ?)
    """, (schedule_id, delay_minutes, reason))

    conn.commit()
    conn.close()
    return True, get_schedule_details(schedule_id)

def update_bus_occupancy(schedule_id, occupancy):
    """Updates real-time passenger crowd level: Low, Medium, High, Full."""
    if occupancy not in ['Low', 'Medium', 'High', 'Full']:
        return False, "Invalid occupancy state"

    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("UPDATE schedules SET occupancy = ? WHERE schedule_id = ?", (occupancy, schedule_id))
    conn.commit()
    conn.close()
    return True, f"Occupancy updated to {occupancy}"

# ---------------------------------------------------------
# INTERACTIVE 2x2 BUS SEAT SELECTION & MOST WANTED SEATS
# ---------------------------------------------------------
def get_seat_layout(schedule_id, travel_date=None):
    """
    Generates an authentic 40-seat coach layout (10 rows of 4 seats: A, B [aisle] C, D)
    Features:
    - 'Most Wanted' tags on prime front window seats (1A, 1D, 2A, 2D, 3A, 3D)
    - Dynamically queries existing bookings for that travel_date
    """
    if not travel_date:
        travel_date = date.today().isoformat()

    conn = get_db()
    cursor = conn.cursor()

    # Get schedule fare and the actual bus capacity.
    cursor.execute("SELECT s.fare, b.bus_number, b.bus_type, b.capacity FROM schedules s JOIN buses b ON s.bus_id = b.bus_id WHERE s.schedule_id = ?", (schedule_id,))
    sched_info = cursor.fetchone()
    base_fare = sched_info['fare'] if sched_info else 120.0
    capacity = min(sched_info['capacity'], 40) if sched_info else 40

    # Get all booked seat numbers for this schedule on this date
    cursor.execute("""
    SELECT seat_number FROM bookings 
    WHERE schedule_id = ? AND travel_date = ? AND status != 'Cancelled'
    """, (schedule_id, travel_date))
    booked_seats = {row['seat_number'] for row in cursor.fetchall()}
    conn.close()

    most_wanted_seats = {'1A', '1D', '2A', '2D', '3A', '3D', '4A', '4D'}

    rows = []
    row_count = (capacity + 3) // 4
    for r in range(1, row_count + 1):
        row_seats = []
        for col in ['A', 'B', 'C', 'D']:
            seat_code = f"{r}{col}"
            if len(rows) * 4 + len(row_seats) >= capacity:
                continue
            is_booked = seat_code in booked_seats
            is_window = col in ['A', 'D']
            is_most_wanted = seat_code in most_wanted_seats

            # Most wanted seats have premium comfort pricing (+ ₹20)
            seat_fare = base_fare + 20.0 if is_most_wanted else base_fare

            row_seats.append({
                'seat_code': seat_code,
                'row': r,
                'column': col,
                'is_window': is_window,
                'is_booked': is_booked,
                'is_most_wanted': is_most_wanted,
                'fare': round(seat_fare, 2)
            })
        rows.append({'row_number': r, 'seats': row_seats})

    return {
        'schedule_id': schedule_id,
        'travel_date': travel_date,
        'base_fare': base_fare,
        'total_seats': capacity,
        'booked_count': len(booked_seats),
        'available_count': 40 - len(booked_seats),
        'layout': rows
    }

# ---------------------------------------------------------
# DRIVER WORKING HOURS & SHIFT TRACKER
# ---------------------------------------------------------
def get_driver_duty_metrics(driver_id):
    """Calculates logged working hours, active shift status, and weekly totals."""
    conn = get_db()
    cursor = conn.cursor()

    today_str = date.today().isoformat()
    week_ago_str = (date.today() - timedelta(days=7)).isoformat()

    # Active shift today
    cursor.execute("""
    SELECT * FROM driver_shifts 
    WHERE driver_id = ? AND shift_date = ? AND status = 'Active'
    ORDER BY shift_id DESC LIMIT 1
    """, (driver_id, today_str))
    active_shift = cursor.fetchone()

    # Total completed hours today
    cursor.execute("""
    SELECT SUM(hours_worked) AS total_today FROM driver_shifts
    WHERE driver_id = ? AND shift_date = ?
    """, (driver_id, today_str))
    today_res = cursor.fetchone()
    today_hours = today_res['total_today'] or 0.0

    # Total hours this week
    cursor.execute("""
    SELECT SUM(hours_worked) AS total_week FROM driver_shifts
    WHERE driver_id = ? AND shift_date >= ?
    """, (driver_id, week_ago_str))
    week_res = cursor.fetchone()
    week_hours = week_res['total_week'] or 0.0

    conn.close()

    is_on_duty = active_shift is not None
    current_shift_elapsed = 0.0

    if active_shift:
        try:
            start_dt = datetime.strptime(f"{today_str} {active_shift['start_time']}", "%Y-%m-%d %H:%M")
            now_dt = datetime.now()
            if now_dt > start_dt:
                current_shift_elapsed = round((now_dt - start_dt).total_seconds() / 3600.0, 1)
        except Exception:
            current_shift_elapsed = active_shift.get('hours_worked', 6.5)

    return {
        'driver_id': driver_id,
        'is_on_duty': is_on_duty,
        'today_hours': round(today_hours + (current_shift_elapsed if is_on_duty else 0.0), 1),
        'week_hours': round(week_hours + (current_shift_elapsed if is_on_duty else 0.0), 1),
        'active_shift': active_shift,
        'current_shift_elapsed': current_shift_elapsed
    }

def toggle_driver_shift(driver_id):
    """Starts or stops driver duty shift and updates logged hours."""
    conn = get_db()
    cursor = conn.cursor()
    today_str = date.today().isoformat()
    now_time = datetime.now().strftime("%H:%M")

    cursor.execute("""
    SELECT * FROM driver_shifts 
    WHERE driver_id = ? AND status = 'Active'
    ORDER BY shift_id DESC LIMIT 1
    """, (driver_id,))
    active_shift = cursor.fetchone()

    if active_shift:
        # End active shift
        start_time = active_shift['start_time']
        try:
            t1 = datetime.strptime(start_time, "%H:%M")
            t2 = datetime.strptime(now_time, "%H:%M")
            diff_hours = max(0.5, round((t2 - t1).total_seconds() / 3600.0, 1))
        except Exception:
            diff_hours = 8.0

        cursor.execute("""
        UPDATE driver_shifts 
        SET end_time = ?, hours_worked = ?, status = 'Completed'
        WHERE shift_id = ?
        """, (now_time, diff_hours, active_shift['shift_id']))
        msg = f"Duty Shift Ended at {now_time}. Logged {diff_hours} hours."
        is_on_duty = False
    else:
        # Start new shift
        cursor.execute("""
        INSERT INTO driver_shifts (driver_id, shift_date, start_time, hours_worked, status)
        VALUES (?, ?, ?, 0.0, 'Active')
        """, (driver_id, today_str, now_time))
        msg = f"Duty Shift Started at {now_time}. Welcome on board!"
        is_on_duty = True

    conn.commit()
    conn.close()
    return True, msg, is_on_duty

# ---------------------------------------------------------
# TICKET QR CONFIRMATION & VERIFICATION SCANNER
# ---------------------------------------------------------
def verify_ticket_code(booking_code):
    """Verifies ticket by booking code and marks boarding status as 'Boarded'."""
    conn = get_db()
    cursor = conn.cursor()

    cursor.execute("""
    SELECT b.*, s.departure_time, s.arrival_time, s.status AS bus_status,
           bu.bus_number, bu.bus_type, r.route_name, r.source, r.destination,
           u.name AS driver_name
    FROM bookings b
    JOIN schedules s ON b.schedule_id = s.schedule_id
    JOIN buses bu ON s.bus_id = bu.bus_id
    JOIN routes r ON s.route_id = r.route_id
    LEFT JOIN users u ON s.driver_id = u.id
    WHERE UPPER(TRIM(b.booking_code)) = UPPER(TRIM(?))
    """, (booking_code,))
    ticket = cursor.fetchone()

    if not ticket:
        conn.close()
        return False, "Invalid ticket or booking code not found.", None

    if ticket['status'] == 'Confirmed':
        cursor.execute("UPDATE bookings SET status = 'Boarded' WHERE booking_id = ?", (ticket['booking_id'],))
        conn.commit()
        ticket['status'] = 'Boarded'
        msg = "Ticket Verified Successfully! Passenger Marked as BOARDED."
    elif ticket['status'] == 'Boarded':
        msg = "Notice: Passenger already checked-in / boarded."
    else:
        msg = f"Ticket status is {ticket['status']}."

    conn.close()
    return True, msg, ticket

# ---------------------------------------------------------
# MAP DESTINATION & "BEST WAY" ROUTE RECOMMENDER
# ---------------------------------------------------------
def get_best_way_route(source="Tumkur", destination="Bangalore"):
    """
    Recommends optimal route options for drivers and passengers:
    - Route 1: NH48 Highway Expressway (Fastest / Best Way)
    - Route 2: Old Highway / SH8 Bypass (Alternative)
    """
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("""
    SELECT r.*, COALESCE(MIN(s.offset_minutes), 0) AS start_offset,
           COALESCE(MAX(s.offset_minutes), r.distance_km * 1.5) AS travel_minutes
    FROM routes r
    LEFT JOIN stops s ON s.route_id = r.route_id
    WHERE LOWER(r.source) = LOWER(?) AND LOWER(r.destination) = LOWER(?)
    GROUP BY r.route_id
    ORDER BY r.distance_km ASC
    """, (source, destination))
    route = cursor.fetchone()
    coordinates = []
    if route:
        cursor.execute("""
        SELECT stop_name, latitude, longitude FROM stops
        WHERE route_id = ? AND latitude IS NOT NULL AND longitude IS NOT NULL
        ORDER BY sequence ASC
        """, (route['route_id'],))
        coordinates = [
            {'name': stop['stop_name'], 'lat': stop['latitude'], 'lng': stop['longitude']}
            for stop in cursor.fetchall()
        ]
    conn.close()

    distance = route['distance_km'] if route else 70
    duration_minutes = int(route['travel_minutes']) if route else round(distance * 1.2)
    route_label = route['route_name'] if route else f'{source} - {destination}'
    routes_comparison = [
        {
            'route_id': route['route_id'] if route else 0,
            'name': f'{route_label} (Recommended - Best Way)',
            'tag': 'Best Way 🚀',
            'is_recommended': True,
            'distance_km': distance,
            'estimated_time': f'{duration_minutes // 60}h {duration_minutes % 60:02d}m',
            'road_condition': '4-Lane Toll Expressway',
            'traffic_level': 'Light to Moderate',
            'toll_count': 2,
            'color': '#10B981', # Neon Green
            'highlights': f'Optimized for the {source} to {destination} corridor'
            , 'coordinates': coordinates
        },
        {
            'route_id': 2,
            'name': 'State Highway 8 / Old Tumkur Bypass',
            'tag': 'Scenic / Toll-Free',
            'is_recommended': False,
            'distance_km': distance + 6,
            'estimated_time': f'{(duration_minutes + 30) // 60}h {(duration_minutes + 30) % 60:02d}m',
            'road_condition': '2-Lane Highway with Signals',
            'traffic_level': 'Heavy near Nelamangala',
            'toll_count': 0,
            'color': '#F59E0B', # Amber
            'highlights': 'No toll fees but slower travel with market intersections'
            , 'coordinates': coordinates
        }
    ]
    return routes_comparison

def simulate_bus_unavailability(bus_id):
    """What-If Schedule Simulator: Simulates breakdown and suggests replacement."""
    conn = get_db()
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM buses WHERE bus_id = ?", (bus_id,))
    target_bus = cursor.fetchone()
    if not target_bus:
        conn.close()
        return None

    cursor.execute("""
    SELECT s.*, r.route_name, r.source, r.destination, r.distance_km,
           u.name AS driver_name, u.phone AS driver_phone
    FROM schedules s
    JOIN routes r ON s.route_id = r.route_id
    LEFT JOIN users u ON s.driver_id = u.id
    WHERE s.bus_id = ?
    ORDER BY s.departure_time ASC
    """, (bus_id,))
    affected_schedules = cursor.fetchall()

    cursor.execute("""
    SELECT b.* FROM buses b
    WHERE b.bus_id != ? AND b.status = 'Active'
    ORDER BY b.capacity DESC
    """, (bus_id,))
    all_active_buses = cursor.fetchall()

    conn.close()

    recommendations = []
    used_bus_ids = set()

    for sched in affected_schedules:
        candidate_bus = None
        for b in all_active_buses:
            if b['bus_id'] not in used_bus_ids and b['capacity'] >= (target_bus['capacity'] - 5):
                candidate_bus = b
                used_bus_ids.add(b['bus_id'])
                break
        if not candidate_bus and all_active_buses:
            candidate_bus = all_active_buses[0]

        recommendations.append({
            'schedule_id': sched['schedule_id'],
            'route_name': sched['route_name'],
            'departure_time': sched['departure_time'],
            'arrival_time': sched['arrival_time'],
            'original_bus': target_bus['bus_number'],
            'suggested_bus': candidate_bus['bus_number'] if candidate_bus else 'KA07ST5566 (Depot Standby)',
            'suggested_bus_type': candidate_bus['bus_type'] if candidate_bus else 'Volvo Semi-Deluxe',
            'suggested_capacity': candidate_bus['capacity'] if candidate_bus else 45,
            'driver': sched.get('driver_name') or 'Standby Driver',
            'action_summary': f"Reroute {candidate_bus['bus_number'] if candidate_bus else 'Standby'} to cover {sched['route_name']} at {sched['departure_time']}."
        })

    return {
        'simulated_bus': target_bus,
        'affected_schedules_count': len(affected_schedules),
        'estimated_passengers_impacted': len(affected_schedules) * int(target_bus['capacity'] * 0.75),
        'affected_schedules': affected_schedules,
        'recommendations': recommendations
    }

def search_routes(source, destination, travel_date=None):
    """Searches schedules with calculated stops and dynamic fares."""
    conn = get_db()
    cursor = conn.cursor()

    source = source.strip().lower()
    destination = destination.strip().lower()

    cursor.execute("""
    SELECT s.*, 
           b.bus_number, b.bus_type, b.capacity,
           r.route_name, r.source, r.destination, r.distance_km, r.base_fare,
           u.name AS driver_name
    FROM schedules s
    JOIN buses b ON s.bus_id = b.bus_id
    JOIN routes r ON s.route_id = r.route_id
    LEFT JOIN users u ON s.driver_id = u.id
    WHERE (LOWER(r.source) LIKE ? AND LOWER(r.destination) LIKE ?)
       OR (LOWER(r.route_name) LIKE ? AND LOWER(r.route_name) LIKE ?)
    ORDER BY s.departure_time ASC
    """, (f"%{source}%", f"%{destination}%", f"%{source}%", f"%{destination}%"))
    
    schedules = cursor.fetchall()
    results = []

    for sched in schedules:
        cursor.execute("SELECT * FROM stops WHERE route_id = ? ORDER BY sequence ASC", (sched['route_id'],))
        stops = cursor.fetchall()
        delay_mins = sched.get('delay_minutes', 0)
        calc_stops = calculate_stop_times(sched['departure_time'], delay_mins, stops)
        
        sched['stops'] = calc_stops
        sched['expected_departure'] = calc_stops[0]['expected_time'] if calc_stops else sched['departure_time']
        sched['expected_arrival'] = calc_stops[-1]['expected_time'] if calc_stops else sched['arrival_time']
        sched['travel_date'] = travel_date or date.today().isoformat()
        results.append(sched)

    conn.close()
    return results

def get_analytics_metrics():
    """Generates analytics data with safe dict keys."""
    conn = get_db()
    cursor = conn.cursor()

    cursor.execute("SELECT status, COUNT(*) AS count FROM schedules GROUP BY status")
    status_counts_raw = cursor.fetchall()
    status_map = {'On Time': 0, 'Delayed': 0, 'Cancelled': 0, 'Not Started': 0}
    for row in status_counts_raw:
        if row['status'] in status_map:
            status_map[row['status']] = row['count']

    cursor.execute("SELECT COUNT(*) AS count FROM buses")
    total_buses = cursor.fetchone()['count']

    cursor.execute("SELECT COUNT(*) AS count FROM routes")
    total_routes = cursor.fetchone()['count']

    cursor.execute("SELECT COUNT(*) AS count FROM users WHERE role = 'driver'")
    total_drivers = cursor.fetchone()['count']

    cursor.execute("SELECT COUNT(*) AS count FROM schedules")
    total_schedules = cursor.fetchone()['count']

    most_used_routes = [
        {'route_name': 'Tumkur - Bangalore', 'percentage': 32},
        {'route_name': 'Tumkur - Nagasandra', 'percentage': 22},
        {'route_name': 'Tumkur - Doddaballapur', 'percentage': 18},
        {'route_name': 'Tumkur - Nelamangala', 'percentage': 16},
        {'route_name': 'Tumkur - Mysore', 'percentage': 12},
    ]

    utilization = {
        'labels': ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun'],
        'rates': [68, 74, 82, 79, 91, 95, 88]
    }

    delay_reasons = {
        'labels': ['Traffic', 'Weather', 'Technical', 'Road Work'],
        'percentages': [40, 20, 18, 22]
    }

    cancellations = {
        'total': 3,
        'this_month': 2,
        'last_month': 1
    }

    conn.close()

    return {
        'total_buses': total_buses,
        'total_routes': total_routes,
        'total_drivers': total_drivers,
        'total_schedules': total_schedules,
        'status_breakdown': status_map,
        'most_used_routes': most_used_routes,
        'utilization': utilization,
        'delay_reasons': delay_reasons,
        'cancellations': cancellations
    }
