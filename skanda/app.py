"""
CatchIt: Smart Bus Schedule & Transportation Management System
Flask Backend Application, REST APIs, and Role-Based Route Controllers
"""

import os
import random
import sqlite3
from datetime import datetime, date
from functools import wraps
from flask import Flask, render_template, request, redirect, url_for, session, flash, jsonify, send_file
from werkzeug.security import check_password_hash, generate_password_hash

from models import init_db, seed_data, get_db, DB_PATH, using_mysql
import engine

app = Flask(__name__)
app.secret_key = os.environ.get('SECRET_KEY', 'catchit-super-secret-key-2026-bca')

# Auto-initialize and seed DB on startup
with app.app_context():
    init_db()
    seed_data()

# ---------------------------------------------------------
# ACCESS CONTROL HELPERS
# ---------------------------------------------------------

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            flash('Please log in to access this page.', 'warning')
            return redirect(url_for('login', next=request.url))
        return f(*args, **kwargs)
    return decorated_function

def role_required(*allowed_roles):
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if 'user_id' not in session:
                flash('Please log in first.', 'warning')
                return redirect(url_for('login'))
            if session.get('role') not in allowed_roles:
                flash('Access denied: Unauthorized role.', 'danger')
                if session.get('role') == 'admin':
                    return redirect(url_for('admin_dashboard'))
                elif session.get('role') == 'driver':
                    return redirect(url_for('driver_dashboard'))
                else:
                    return redirect(url_for('passenger_dashboard'))
            return f(*args, **kwargs)
        return decorated_function
    return decorator

@app.context_processor
def inject_user():
    return {
        'current_user': {
            'id': session.get('user_id'),
            'name': session.get('name', 'Guest'),
            'email': session.get('email'),
            'role': session.get('role'),
            'license_number': session.get('license_number')
        },
        'today_date': datetime.now().strftime("%d %b %Y"),
        'today_iso': date.today().isoformat()
    }

# ---------------------------------------------------------
# PUBLIC & AUTH ROUTES
# ---------------------------------------------------------

@app.route('/')
def index():
    """Public Landing Page matching mockup Home Page with CatchIt branding."""
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("""
    SELECT s.*, b.bus_number, b.bus_type, r.route_name, r.source, r.destination, r.distance_km, r.base_fare
    FROM schedules s
    JOIN buses b ON s.bus_id = b.bus_id
    JOIN routes r ON s.route_id = r.route_id
    ORDER BY s.departure_time ASC
    LIMIT 6
    """)
    featured = cursor.fetchall()
    conn.close()
    return render_template('index.html', featured=featured)

@app.route('/login', methods=['GET', 'POST'])
def login():
    """Login page with 1-click Demo accounts."""
    if request.method == 'POST':
        identifier = request.form.get('identifier', '').strip()
        password = request.form.get('password', '').strip()
        session.clear()

        conn = get_db()
        cursor = conn.cursor()
        cursor.execute("""
        SELECT * FROM users 
        WHERE (LOWER(email) = LOWER(?) OR phone = ?)
        """, (identifier, identifier))
        user = cursor.fetchone()
        conn.close()

        if user and check_password_hash(user['password_hash'], password):
            session['user_id'] = user['id']
            session['name'] = user['name']
            session['email'] = user['email']
            session['role'] = user['role']
            session['license_number'] = user.get('license_number')

            flash(f"Welcome back, {user['name']}!", 'success')
            if user['role'] == 'admin':
                return redirect(url_for('admin_dashboard'))
            elif user['role'] == 'driver':
                return redirect(url_for('driver_dashboard'))
            else:
                return redirect(url_for('passenger_dashboard'))
        else:
            flash('Invalid email/phone or password.', 'danger')

    return render_template('login.html')

@app.route('/demo-login/<role>')
def demo_login(role):
    """1-Click quick login for viva demonstration."""
    conn = get_db()
    cursor = conn.cursor()
    if role == 'admin':
        cursor.execute("SELECT * FROM users WHERE email = 'admin@busflow.com'")
    elif role == 'driver':
        cursor.execute("SELECT * FROM users WHERE email = 'driver@busflow.com'")
    else:
        cursor.execute("SELECT * FROM users WHERE email = 'passenger@busflow.com'")
    user = cursor.fetchone()
    conn.close()

    if user:
        session['user_id'] = user['id']
        session['name'] = user['name']
        session['email'] = user['email']
        session['role'] = user['role']
        session['license_number'] = user.get('license_number')
        flash(f"Logged in automatically as {user['role'].title()} ({user['name']})", 'info')

        if role == 'admin':
            return redirect(url_for('admin_dashboard'))
        elif role == 'driver':
            return redirect(url_for('driver_dashboard'))
        else:
            return redirect(url_for('passenger_dashboard'))

    return redirect(url_for('login'))

@app.route('/register', methods=['GET', 'POST'])
def register():
    """Registration page."""
    if request.method == 'POST':
        name = request.form.get('name', '').strip()
        email = request.form.get('email', '').strip()
        phone = request.form.get('phone', '').strip()
        password = request.form.get('password', '').strip()
        confirm_password = request.form.get('confirm_password', '').strip()
        role = request.form.get('role', 'passenger').lower()
        if role not in {'passenger', 'driver'}:
            flash('Please choose Passenger or Driver. Admin accounts are managed by the transit administrator.', 'warning')
            return render_template('register.html')
        license_no = request.form.get('license_number', '').strip() if role == 'driver' else None

        if role == 'driver' and not license_no:
            flash('A commercial license number is required for driver registration.', 'warning')
            return render_template('register.html')

        if not name or not email or not password:
            flash('Please fill in all required fields.', 'warning')
            return render_template('register.html')

        if password != confirm_password:
            flash('Passwords do not match.', 'danger')
            return render_template('register.html')

        conn = get_db()
        cursor = conn.cursor()
        cursor.execute("SELECT id FROM users WHERE email = ?", (email,))
        if cursor.fetchone():
            conn.close()
            flash('Email already registered. Please log in.', 'warning')
            return redirect(url_for('login'))

        cursor.execute("""
        INSERT INTO users (name, email, phone, password_hash, role, license_number)
        VALUES (?, ?, ?, ?, ?, ?)
        """, (name, email, phone, generate_password_hash(password), role, license_no))
        conn.commit()
        conn.close()

        flash('Registration successful! You can now log in.', 'success')
        return redirect(url_for('login'))

    return render_template('register.html')

@app.route('/logout')
def logout():
    session.clear()
    flash('You have been logged out successfully.', 'info')
    return redirect(url_for('login'))

# ---------------------------------------------------------
# SQL EXPORT & DOWNLOAD ROUTE
# ---------------------------------------------------------

@app.route('/export/sql')
def export_sql():
    """Exports and downloads the complete database as an ANSI SQL file."""
    sql_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'database_schema_and_data.sql')
    if not using_mysql():
        conn = sqlite3.connect(DB_PATH)
        with open(sql_path, 'w', encoding='utf-8') as f:
            f.write('-- CatchIt Database Dump (ANSI SQL)\n\n')
            for line in conn.iterdump():
                f.write(f"{line}\n")
        conn.close()
    else:
        conn = get_db()
        cursor = conn.cursor()
        cursor.execute('SHOW TABLES')
        table_names = [next(iter(row.values())) for row in cursor.fetchall()]
        with open(sql_path, 'w', encoding='utf-8') as f:
            f.write('-- CatchIt MySQL Database Dump\nSET FOREIGN_KEY_CHECKS=0;\n\n')
            for table_name in table_names:
                cursor.execute(f'SHOW CREATE TABLE `{table_name}`')
                create_row = cursor.fetchone()
                create_sql = list(create_row.values())[1]
                f.write(f'DROP TABLE IF EXISTS `{table_name}`;\n{create_sql};\n')
                cursor.execute(f'SELECT * FROM `{table_name}`')
                columns = [column[0] for column in cursor.description]
                for row in cursor.fetchall():
                    values = ', '.join(
                        'NULL' if row[column] is None else "'" + str(row[column]).replace("'", "''") + "'"
                        for column in columns
                    )
                    f.write(f"INSERT INTO `{table_name}` (`{'`, `'.join(columns)}`) VALUES ({values});\n")
                f.write('\n')
            f.write('SET FOREIGN_KEY_CHECKS=1;\n')
        conn.close()
    return send_file(sql_path, as_attachment=True, download_name='catchit_database_schema_and_data.sql')

# ---------------------------------------------------------
# TICKET SCANNER & VERIFICATION PORTAL
# ---------------------------------------------------------

@app.route('/ticket-scanner')
@role_required('admin', 'driver')
def ticket_scanner():
    """Conductor & Driver ticket verification scanner."""
    return render_template('ticket_scanner.html')

# ---------------------------------------------------------
# ADMIN DASHBOARD & MANAGEMENT ROUTES
# ---------------------------------------------------------

@app.route('/admin')
@role_required('admin')
def admin_dashboard():
    """Transit Control Center Admin Dashboard."""
    conn = get_db()
    cursor = conn.cursor()

    cursor.execute("SELECT COUNT(*) AS c FROM buses")
    total_buses = cursor.fetchone()['c']

    cursor.execute("SELECT COUNT(*) AS c FROM routes")
    total_routes = cursor.fetchone()['c']

    cursor.execute("SELECT COUNT(*) AS c FROM users WHERE role = 'driver'")
    total_drivers = cursor.fetchone()['c']

    cursor.execute("SELECT COUNT(*) AS c FROM schedules")
    total_schedules = cursor.fetchone()['c']

    cursor.execute("""
    SELECT s.*, b.bus_number, b.bus_type, r.route_name
    FROM schedules s
    JOIN buses b ON s.bus_id = b.bus_id
    JOIN routes r ON s.route_id = r.route_id
    ORDER BY s.departure_time ASC
    LIMIT 6
    """)
    upcoming_departures = cursor.fetchall()

    cursor.execute("SELECT status, COUNT(*) AS count FROM schedules GROUP BY status")
    status_rows = cursor.fetchall()
    status_counts = {'On Time': 18, 'Delayed': 4, 'Cancelled': 1, 'Not Started': 2}
    for row in status_rows:
        if row['status'] in status_counts:
            status_counts[row['status']] = row['count']

    conn.close()

    return render_template('admin_dashboard.html',
                           total_buses=total_buses,
                           total_routes=total_routes,
                           total_drivers=total_drivers,
                           total_schedules=total_schedules,
                           upcoming_departures=upcoming_departures,
                           status_counts=status_counts)

@app.route('/admin/buses')
@role_required('admin')
def admin_buses():
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM buses ORDER BY bus_number ASC")
    buses = cursor.fetchall()
    conn.close()
    return render_template('admin_buses.html', buses=buses)

@app.route('/admin/routes')
@role_required('admin')
def admin_routes():
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("""
    SELECT r.*, COUNT(s.stop_id) AS stops_count
    FROM routes r
    LEFT JOIN stops s ON r.route_id = s.route_id
    GROUP BY r.route_id
    ORDER BY r.route_name ASC
    """)
    routes = cursor.fetchall()
    conn.close()
    return render_template('admin_routes.html', routes=routes)

@app.route('/admin/schedules')
@role_required('admin')
def admin_schedules():
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("""
    SELECT s.*, b.bus_number, b.bus_type, r.route_name, u.name AS driver_name
    FROM schedules s
    JOIN buses b ON s.bus_id = b.bus_id
    JOIN routes r ON s.route_id = r.route_id
    LEFT JOIN users u ON s.driver_id = u.id
    ORDER BY s.departure_time ASC
    """)
    schedules = cursor.fetchall()

    cursor.execute("SELECT * FROM buses WHERE status = 'Active'")
    buses = cursor.fetchall()

    cursor.execute("SELECT * FROM routes")
    routes = cursor.fetchall()

    cursor.execute("SELECT id, name FROM users WHERE role = 'driver'")
    drivers = cursor.fetchall()

    conn.close()
    return render_template('admin_schedules.html', schedules=schedules, buses=buses, routes=routes, drivers=drivers)

@app.route('/admin/drivers')
@role_required('admin')
def admin_drivers():
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("""
    SELECT u.*, 
           (SELECT COUNT(*) FROM schedules s WHERE s.driver_id = u.id) AS assigned_schedules_count,
           (SELECT COALESCE(SUM(hours_worked), 0) FROM driver_shifts ds WHERE ds.driver_id = u.id) AS total_hours_worked
    FROM users u
    WHERE u.role = 'driver'
    ORDER BY u.name ASC
    """)
    drivers = cursor.fetchall()
    conn.close()
    return render_template('admin_drivers.html', drivers=drivers)

@app.route('/admin/live-tracking')
@role_required('admin', 'passenger', 'driver')
def admin_live_tracking():
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("""
    SELECT s.schedule_id, s.departure_time, s.arrival_time, s.status, s.occupancy, s.delay_minutes, s.fare,
           b.bus_number, b.bus_type, r.route_name, r.source, r.destination, r.distance_km,
           u.name AS driver_name
    FROM schedules s
    JOIN buses b ON s.bus_id = b.bus_id
    JOIN routes r ON s.route_id = r.route_id
    LEFT JOIN users u ON s.driver_id = u.id
    WHERE s.status IN ('On Time', 'Delayed')
    ORDER BY s.departure_time ASC
    """)
    active_buses = cursor.fetchall()
    conn.close()
    best_routes = engine.get_best_way_route()
    return render_template('admin_live_tracking.html', active_buses=active_buses, best_routes=best_routes)

@app.route('/admin/what-if')
@role_required('admin')
def admin_what_if():
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM buses ORDER BY bus_number ASC")
    buses = cursor.fetchall()
    conn.close()
    return render_template('admin_what_if.html', buses=buses)

@app.route('/admin/analytics')
@role_required('admin')
def admin_analytics():
    metrics = engine.get_analytics_metrics()
    return render_template('admin_analytics.html', metrics=metrics)

# ---------------------------------------------------------
# DRIVER CONSOLE & WORKING HOURS TRACKER
# ---------------------------------------------------------

@app.route('/driver')
@role_required('driver')
def driver_dashboard():
    user_id = session.get('user_id')
    conn = get_db()
    cursor = conn.cursor()

    cursor.execute("""
    SELECT s.*, b.bus_number, b.bus_type, b.capacity,
           r.route_name, r.source, r.destination, r.distance_km, r.base_fare
    FROM schedules s
    JOIN buses b ON s.bus_id = b.bus_id
    JOIN routes r ON s.route_id = r.route_id
    WHERE s.driver_id = ?
    ORDER BY s.departure_time ASC
    LIMIT 1
    """, (user_id,))
    schedule = cursor.fetchone()

    if not schedule:
        cursor.execute("""
        SELECT s.*, b.bus_number, b.bus_type, b.capacity,
               r.route_name, r.source, r.destination, r.distance_km, r.base_fare
        FROM schedules s
        JOIN buses b ON s.bus_id = b.bus_id
        JOIN routes r ON s.route_id = r.route_id
        WHERE s.schedule_id = 1
        """)
        schedule = cursor.fetchone()

    conn.close()

    enriched_schedule = None
    if schedule:
        enriched_schedule = engine.get_schedule_details(schedule['schedule_id'])

    # Get driver working hours & duty metrics
    duty_metrics = engine.get_driver_duty_metrics(user_id)
    best_way_routes = engine.get_best_way_route()

    return render_template('driver_dashboard.html',
                           schedule=enriched_schedule,
                           duty_metrics=duty_metrics,
                           best_way_routes=best_way_routes)

# ---------------------------------------------------------
# PASSENGER PORTAL & TRAVEL HISTORY
# ---------------------------------------------------------

@app.route('/passenger')
@role_required('passenger')
def passenger_dashboard():
    user_id = session.get('user_id')
    conn = get_db()
    cursor = conn.cursor()

    # Complete passenger travel history
    cursor.execute("""
    SELECT b.*, s.departure_time, s.arrival_time, s.status AS bus_status, s.delay_minutes,
           bu.bus_number, bu.bus_type, r.route_name, r.source, r.destination, r.distance_km
    FROM bookings b
    JOIN schedules s ON b.schedule_id = s.schedule_id
    JOIN buses bu ON s.bus_id = bu.bus_id
    JOIN routes r ON s.route_id = r.route_id
    WHERE b.user_id = ?
    ORDER BY b.travel_date DESC, b.booking_id DESC
    """, (user_id,))
    bookings = cursor.fetchall()

    cursor.execute("SELECT DISTINCT source FROM routes UNION SELECT DISTINCT destination FROM routes")
    cities = [row['source'] for row in cursor.fetchall()]

    conn.close()

    favourite_routes = [
        {'route_name': 'Tumkur → Bangalore', 'source': 'Tumkur', 'destination': 'Bangalore', 'distance': '70 km', 'duration': '1h 25m', 'fare': '₹140', 'bus_count': 14},
        {'route_name': 'Tumkur → Nagasandra', 'source': 'Tumkur', 'destination': 'Nagasandra', 'distance': '45 km', 'duration': '1h 05m', 'fare': '₹85', 'bus_count': 8},
        {'route_name': 'Tumkur → Doddaballapur', 'source': 'Tumkur', 'destination': 'Doddaballapur', 'distance': '60 km', 'duration': '1h 45m', 'fare': '₹95', 'bus_count': 6},
    ]

    return render_template('passenger_dashboard.html',
                           bookings=bookings,
                           cities=cities,
                           favourite_routes=favourite_routes,
                           travel_history=bookings)

# ---------------------------------------------------------
# REST API ENDPOINTS
# ---------------------------------------------------------

@app.route('/api/schedules/search')
def api_search_schedules():
    source = request.args.get('source', '')
    destination = request.args.get('destination', '')
    travel_date = request.args.get('date', date.today().isoformat())
    if not source or not destination:
        return jsonify({'success': False, 'message': 'Source and destination required'}), 400
    results = engine.search_routes(source, destination, travel_date)
    return jsonify({'success': True, 'count': len(results), 'schedules': results, 'travel_date': travel_date})

@app.route('/api/schedules/<int:schedule_id>')
def api_get_schedule(schedule_id):
    sched = engine.get_schedule_details(schedule_id)
    if not sched:
        return jsonify({'success': False, 'message': 'Schedule not found'}), 404
    return jsonify({'success': True, 'schedule': sched})

@app.route('/api/schedules/<int:schedule_id>/seats')
def api_get_seats(schedule_id):
    """Returns 40-seat coach layout with booked seats and Most Wanted indicators."""
    travel_date = request.args.get('date', date.today().isoformat())
    seat_data = engine.get_seat_layout(schedule_id, travel_date)
    return jsonify({'success': True, 'data': seat_data})

@app.route('/api/schedules/<int:schedule_id>/delay', methods=['POST'])
def api_update_delay(schedule_id):
    data = request.get_json() or request.form
    delay_minutes = data.get('delay_minutes')
    reason = data.get('reason', 'Traffic delay')

    if delay_minutes is None:
        return jsonify({'success': False, 'message': 'delay_minutes is required'}), 400

    try:
        delay_minutes = int(delay_minutes)
    except ValueError:
        return jsonify({'success': False, 'message': 'Invalid delay_minutes format'}), 400

    success, result = engine.apply_schedule_delay(schedule_id, delay_minutes, reason)
    if not success:
        return jsonify({'success': False, 'message': result}), 400

    return jsonify({'success': True, 'message': f'Delay of {delay_minutes} min applied successfully', 'schedule': result})

@app.route('/api/schedules/<int:schedule_id>/occupancy', methods=['POST'])
def api_update_occupancy(schedule_id):
    data = request.get_json() or request.form
    occupancy = data.get('occupancy')
    success, msg = engine.update_bus_occupancy(schedule_id, occupancy)
    if not success:
        return jsonify({'success': False, 'message': msg}), 400
    return jsonify({'success': True, 'message': msg, 'occupancy': occupancy})

@app.route('/api/ticket/verify', methods=['POST'])
def api_verify_ticket():
    """Confirms passenger ticket & boarding status from QR Scanner."""
    data = request.get_json() or request.form
    booking_code = data.get('booking_code', '').strip()
    if not booking_code:
        return jsonify({'success': False, 'message': 'Booking code is required'}), 400

    success, msg, ticket = engine.verify_ticket_code(booking_code)
    return jsonify({'success': success, 'message': msg, 'ticket': ticket})

@app.route('/api/driver/shift/toggle', methods=['POST'])
@login_required
def api_toggle_shift():
    """Starts or ends duty shift for logged in driver."""
    user_id = session.get('user_id')
    success, msg, is_on_duty = engine.toggle_driver_shift(user_id)
    duty_metrics = engine.get_driver_duty_metrics(user_id)
    return jsonify({'success': success, 'message': msg, 'is_on_duty': is_on_duty, 'metrics': duty_metrics})

@app.route('/api/routes/best-way')
def api_best_way():
    routes = engine.get_best_way_route(
        request.args.get('source', 'Tumkur'),
        request.args.get('destination', 'Bangalore')
    )
    return jsonify({'success': True, 'routes': routes})

@app.route('/api/what-if')
def api_what_if():
    bus_id = request.args.get('bus_id')
    if not bus_id:
        return jsonify({'success': False, 'message': 'bus_id is required'}), 400
    res = engine.simulate_bus_unavailability(int(bus_id))
    if not res:
        return jsonify({'success': False, 'message': 'Bus not found'}), 404
    return jsonify({'success': True, 'simulation': res})

@app.route('/api/live-tracking')
def api_live_tracking():
    """Live tracking telemetry with GPS coordinates."""
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("""
    SELECT s.schedule_id, s.departure_time, s.arrival_time, s.status, s.occupancy, s.delay_minutes, s.fare,
           b.bus_number, b.bus_type, r.route_id, r.route_name, r.source, r.destination,
           u.name AS driver_name, u.phone AS driver_phone
    FROM schedules s
    JOIN buses b ON s.bus_id = b.bus_id
    JOIN routes r ON s.route_id = r.route_id
    LEFT JOIN users u ON s.driver_id = u.id
    WHERE s.status IN ('On Time', 'Delayed')
    LIMIT 8
    """)
    schedules = cursor.fetchall()

    live_fleet = []
    route_coords = [
        {'name': 'Tumkur KSRTC Bus Stand', 'lat': 13.3409, 'lng': 77.1010},
        {'name': 'Kyathsandra Toll', 'lat': 13.3157, 'lng': 77.1592},
        {'name': 'Hirehalli', 'lat': 13.2750, 'lng': 77.1980},
        {'name': 'Dabaspet Junction', 'lat': 13.2298, 'lng': 77.2417},
        {'name': 'Nelamangala Toll Gate', 'lat': 13.0984, 'lng': 77.3898},
        {'name': 'Nagasandra Metro', 'lat': 13.0475, 'lng': 77.4988},
        {'name': 'Yeshwanthpur TTMC', 'lat': 13.0234, 'lng': 77.5501},
        {'name': 'Bangalore Majestic', 'lat': 12.9772, 'lng': 77.5729},
    ]

    for idx, s in enumerate(schedules):
        pos_idx = (idx * 2 + 1) % len(route_coords)
        curr_stop = route_coords[pos_idx]
        next_stop = route_coords[min(pos_idx + 1, len(route_coords) - 1)]

        lat = curr_stop['lat'] + (random.uniform(-0.005, 0.005))
        lng = curr_stop['lng'] + (random.uniform(-0.005, 0.005))

        delay_mins = s.get('delay_minutes', 0)
        expected_next_time = engine.add_minutes_to_time(s['departure_time'], (pos_idx + 1) * 20 + delay_mins)

        live_fleet.append({
            'schedule_id': s['schedule_id'],
            'bus_number': s['bus_number'],
            'bus_type': s['bus_type'],
            'route_name': s['route_name'],
            'status': s['status'],
            'occupancy': s['occupancy'],
            'delay_minutes': delay_mins,
            'fare': s['fare'],
            'driver_name': s['driver_name'] or 'On-duty Driver',
            'latitude': round(lat, 4),
            'longitude': round(lng, 4),
            'current_stop': curr_stop['name'],
            'next_stop': next_stop['name'],
            'next_stop_eta': expected_next_time,
            'speed_kmh': random.randint(45, 62) if s['status'] != 'Cancelled' else 0
        })

    conn.close()
    return jsonify({'success': True, 'fleet': live_fleet, 'route_polyline': route_coords})

# --- BUS CRUD ---
@app.route('/api/buses', methods=['POST'])
@role_required('admin')
def api_add_bus():
    data = request.get_json() or request.form
    bus_number = data.get('bus_number', '').strip().upper()
    bus_type = data.get('bus_type', 'AC Seater')
    capacity = int(data.get('capacity', 40))
    status = data.get('status', 'Active')

    conn = get_db()
    cursor = conn.cursor()
    try:
        cursor.execute("INSERT INTO buses (bus_number, bus_type, capacity, status) VALUES (?, ?, ?, ?)",
                       (bus_number, bus_type, capacity, status))
        conn.commit()
        bus_id = cursor.lastrowid
        conn.close()
        return jsonify({'success': True, 'message': 'Bus added successfully', 'bus_id': bus_id})
    except Exception as e:
        conn.close()
        return jsonify({'success': False, 'message': str(e)}), 400

@app.route('/api/buses/<int:bus_id>/status', methods=['POST'])
@role_required('admin')
def api_toggle_bus_status(bus_id):
    data = request.get_json() or request.form
    new_status = data.get('status', 'Active')
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("UPDATE buses SET status = ? WHERE bus_id = ?", (new_status, bus_id))
    conn.commit()
    conn.close()
    return jsonify({'success': True, 'message': f'Bus status changed to {new_status}'})

@app.route('/api/buses/<int:bus_id>', methods=['DELETE'])
@role_required('admin')
def api_delete_bus(bus_id):
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM buses WHERE bus_id = ?", (bus_id,))
    conn.commit()
    conn.close()
    return jsonify({'success': True, 'message': 'Bus deleted successfully'})

# --- ROUTE CRUD ---
@app.route('/api/routes', methods=['POST'])
@role_required('admin')
def api_add_route():
    data = request.get_json() or request.form
    route_name = data.get('route_name', '').strip()
    source = data.get('source', '').strip()
    destination = data.get('destination', '').strip()
    distance_km = int(data.get('distance_km', 50))
    base_fare = float(data.get('base_fare', round(distance_km * 1.6, 2)))

    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("INSERT INTO routes (route_name, source, destination, distance_km, base_fare) VALUES (?, ?, ?, ?, ?)",
                   (route_name, source, destination, distance_km, base_fare))
    conn.commit()
    route_id = cursor.lastrowid

    cursor.execute("INSERT INTO stops (route_id, stop_name, sequence, offset_minutes) VALUES (?, ?, 1, 0)",
                   (route_id, f"{source} Bus Stand"))
    cursor.execute("INSERT INTO stops (route_id, stop_name, sequence, offset_minutes) VALUES (?, ?, 2, ?)",
                   (route_id, f"{destination} Bus Stand", int(distance_km * 1.5)))
    conn.commit()
    conn.close()
    return jsonify({'success': True, 'message': 'Route created successfully', 'route_id': route_id})

@app.route('/api/routes/<int:route_id>', methods=['DELETE'])
@role_required('admin')
def api_delete_route(route_id):
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM routes WHERE route_id = ?", (route_id,))
    conn.commit()
    conn.close()
    return jsonify({'success': True, 'message': 'Route deleted successfully'})

# --- SCHEDULE CRUD ---
@app.route('/api/schedules', methods=['POST'])
@role_required('admin')
def api_add_schedule():
    data = request.get_json() or request.form
    bus_id = int(data.get('bus_id'))
    route_id = int(data.get('route_id'))
    driver_id = int(data.get('driver_id')) if data.get('driver_id') else None
    departure_time = data.get('departure_time', '09:00').strip()
    arrival_time = data.get('arrival_time', '11:00').strip()
    fare = float(data.get('fare', 120.0))
    status = data.get('status', 'On Time')

    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("""
    INSERT INTO schedules (bus_id, route_id, driver_id, departure_time, arrival_time, fare, status)
    VALUES (?, ?, ?, ?, ?, ?, ?)
    """, (bus_id, route_id, driver_id, departure_time, arrival_time, fare, status))
    conn.commit()
    sched_id = cursor.lastrowid
    conn.close()
    return jsonify({'success': True, 'message': 'Schedule created successfully', 'schedule_id': sched_id})

@app.route('/api/schedules/<int:schedule_id>', methods=['DELETE'])
@role_required('admin')
def api_delete_schedule(schedule_id):
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM schedules WHERE schedule_id = ?", (schedule_id,))
    conn.commit()
    conn.close()
    return jsonify({'success': True, 'message': 'Schedule deleted successfully'})

# --- BOOKING API ---
@app.route('/api/book-seat', methods=['POST'])
@login_required
def api_book_seat():
    data = request.get_json() or request.form
    try:
        schedule_id = int(data.get('schedule_id'))
    except (TypeError, ValueError):
        return jsonify({'success': False, 'message': 'A valid schedule is required.'}), 400
    seat_number = str(data.get('seat_number', '1A')).strip().upper()
    if seat_number.isdigit():
        seat_index = int(seat_number)
        if 1 <= seat_index <= 40:
            seat_number = f'{(seat_index - 1) // 4 + 1}{"ABCD"[(seat_index - 1) % 4]}'
    passenger_name = data.get('passenger_name', session.get('name', 'Passenger'))
    travel_date = data.get('travel_date', date.today().isoformat())
    user_id = session.get('user_id')

    try:
        requested_date = date.fromisoformat(travel_date)
    except (TypeError, ValueError):
        return jsonify({'success': False, 'message': 'Travel date must be YYYY-MM-DD.'}), 400
    if requested_date < date.today():
        return jsonify({'success': False, 'message': 'Travel date cannot be in the past.'}), 400

    # Ensure seat isn't already booked
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("""
    SELECT s.fare, b.capacity, s.status
    FROM schedules s
    JOIN buses b ON s.bus_id = b.bus_id
    WHERE s.schedule_id = ?
    """, (schedule_id,))
    schedule = cursor.fetchone()
    if not schedule:
        conn.close()
        return jsonify({'success': False, 'message': 'Schedule not found.'}), 404
    if schedule['status'] == 'Cancelled':
        conn.close()
        return jsonify({'success': False, 'message': 'This schedule is cancelled.'}), 400

    capacity = min(schedule['capacity'], 40)
    valid_seats = {f'{row}{column}' for row in range(1, (capacity + 3) // 4 + 1) for column in 'ABCD'}
    if seat_number not in valid_seats:
        conn.close()
        return jsonify({'success': False, 'message': f'Seat {seat_number} is not available on this bus.'}), 400

    cursor.execute("""
    SELECT booking_id FROM bookings 
    WHERE schedule_id = ? AND travel_date = ? AND seat_number = ? AND status != 'Cancelled'
    """, (schedule_id, travel_date, seat_number))
    existing = cursor.fetchone()
    if existing:
        conn.close()
        return jsonify({'success': False, 'message': f'Seat {seat_number} has already been reserved for this date. Please choose another seat.'}), 400

    cursor.execute("""
    SELECT COUNT(*) AS booked_count FROM bookings
    WHERE schedule_id = ? AND travel_date = ? AND status != 'Cancelled'
    """, (schedule_id, travel_date))
    if cursor.fetchone()['booked_count'] >= capacity:
        conn.close()
        return jsonify({'success': False, 'message': 'This bus is full for the selected date.'}), 400

    most_wanted = {'1A', '1D', '2A', '2D', '3A', '3D', '4A', '4D'}
    fare = float(schedule['fare']) + (20.0 if seat_number in most_wanted else 0.0)

    booking_code = f"CI-{random.randint(1000, 9999)}-{seat_number}"

    cursor.execute("""
    INSERT INTO bookings (user_id, schedule_id, passenger_name, seat_number, travel_date, fare_paid, booking_code, status)
    VALUES (?, ?, ?, ?, ?, ?, ?, 'Confirmed')
    """, (user_id, schedule_id, passenger_name, seat_number, travel_date, fare, booking_code))
    conn.commit()
    conn.close()

    return jsonify({
        'success': True,
        'message': f'🎉 Ticket Confirmed! Seat {seat_number} reserved.',
        'booking_code': booking_code,
        'seat_number': seat_number,
        'travel_date': travel_date,
        'fare_paid': fare
    })

if __name__ == '__main__':
    app.run(host='127.0.0.1', port=5000, debug=True)
