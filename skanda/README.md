# 🚌 BusFlow: Smart Bus Schedule & Transportation Management System

> **BCA Final Year Major Project**  
> Modern Transportation Control Center with Real-Time Smart Delay Cascading, Interactive Corridor Tracking, Fleet Management, and "What-If" Contingency Scheduling.

---

## 🌟 Overview & Standout Features

BusFlow transforms a traditional CRUD college project into an **intelligent transportation control system**. Designed to mirror the uploaded design board mockup with a dark transit control room aesthetic, BusFlow includes:

1. **Smart Schedule Engine (Python)**:
   - When a bus experiences a delay (e.g. $+20\text{ min}$), the Python engine dynamically recalculates the exact arrival time at every single intermediate stop along the route ($T_i' = T_0 + \Delta t_i + D$).
   - Immediately shifts status to `🟡 Delayed` and broadcasts updates across driver and passenger portals.
2. **"What-If Schedule" Simulator**:
   - Allows dispatch controllers to test: *"What happens if Bus KA01AB1234 breaks down?"*
   - Analyzes all affected schedules, estimates passenger impact, and recommends standby buses and idle drivers.
3. **Interactive Live Bus Tracking**:
   - Built with **Leaflet.js** and **OpenStreetMap** (zero API key needed).
   - Real-time bus icons with route corridor polylines (Tumkur — NH-48 — Bangalore) and interactive telemetry inspection.
4. **Live Bus Occupancy Indicator**:
   - Drivers update crowd density (`Low`, `Medium`, `High`, `Full`) so passengers can make informed travel choices.
5. **Role-Based Dedicated Portals**:
   - **Admin Control Center**: Fleet KPIs (25 Buses, 12 Routes, 18 Drivers, 48 Schedules), live bus status Donut chart, full CRUD, What-If simulator, and analytics.
   - **Driver Console**: Assigned bus & route badge, stop-by-stop schedule with real-time ETAs, 1-click delay reporter, and occupancy updater.
   - **Passenger Portal**: Interactive Route Planner (Origin $\rightarrow$ Destination), favourite route quick cards, downloadable/printable schedule, and seat pass reservation.

---

## 🔑 Pre-Configured Demo Accounts (1-Click Viva Demonstration)

The login screen features 1-click instant login buttons for effortless viva demonstrations:

| Role | Email | Password | Representative Persona |
| :--- | :--- | :--- | :--- |
| **Admin** | `admin@busflow.com` | `admin123` | Control Center Dispatch Admin |
| **Driver** | `driver@busflow.com` | `driver123` | Ravi Kumar (Bus `KA01AB1234`) |
| **Passenger** | `passenger@busflow.com` | `passenger123` | Skanda Bharadwaj |

---

## 🚀 How to Run the Project

### Option A: Double-Click Launcher (Windows)
Double-click `run.bat` in the project root. The server will start automatically at `http://127.0.0.1:5000`.

### Option B: Terminal / Command Prompt
```bash
# 1. Install dependencies (if not already installed)
pip install -r requirements.txt

# 2. Run the application
python app.py
```
Open your browser and navigate to: **`http://127.0.0.1:5000`**

### Running Verification Tests
```bash
python test_system.py
```
All 17 automated tests validate the REST APIs, database, role access, and schedule algorithms.

---

## 🏗️ Architecture & Technology Stack

- **Backend**: Python 3.11, Flask, Werkzeug
- **Database**: SQLite by default, or XAMPP MySQL with relational integrity and auto-seeding
- **Frontend**: HTML5, CSS3 (Custom Dark Transportation Theme), JavaScript (ES6+)
- **Data Visualizations**: Chart.js 4 (Donut status chart, Utilization bar chart, Delay root-cause pie chart)
- **Mapping**: Leaflet.js + OpenStreetMap (No Google Maps API keys required)
- **Icons**: Bootstrap Icons

---

## 🗄️ Relational Database Schema

- `users`: id, name, email, phone, password_hash, role (`admin`, `driver`, `passenger`), license_number
- `buses`: bus_id, bus_number, bus_type, capacity, status (`Active`, `Maintenance`)
- `routes`: route_id, route_name, source, destination, distance_km
- `stops`: stop_id, route_id, stop_name, sequence, offset_minutes, latitude, longitude
- `schedules`: schedule_id, bus_id, route_id, driver_id, departure_time, arrival_time, status, occupancy, delay_minutes, delay_reason
- `delays`: delay_id, schedule_id, delay_minutes, reason, updated_at
- `bookings`: booking_id, user_id, schedule_id, passenger_name, seat_number, travel_date, booking_code, status

## XAMPP MySQL Setup

1. Start **Apache** and **MySQL** in the XAMPP Control Panel.
2. Install dependencies with `pip install -r requirements.txt`.
3. Set these Windows environment variables before starting Flask:

```powershell
$env:CATCHIT_DB = "mysql"
$env:MYSQL_HOST = "127.0.0.1"
$env:MYSQL_PORT = "3306"
$env:MYSQL_USER = "root"
$env:MYSQL_PASSWORD = ""
$env:MYSQL_DATABASE = "catchit"
python app.py
```

CatchIt creates the `catchit` database and all tables automatically, then seeds demo data when the database is empty. To keep using SQLite, omit `CATCHIT_DB` or set it to `sqlite`.
