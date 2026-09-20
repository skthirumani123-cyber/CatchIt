# 📘 Project Report & Viva Voce Presentation Guide
## BusFlow: Smart Bus Schedule, Route & Fleet Management System

**Degree:** Bachelor of Computer Applications (BCA) / B.Tech Computer Science  
**Project Category:** Web Application / Intelligent Transit Information Systems  
**Authors:** Student Project Submission  

---

## 1. Introduction & Problem Statement

### 1.1 Existing System Limitations
Traditional bus transport websites operate as static or basic CRUD repositories. They suffer from critical shortcomings:
- **No Dynamic Delay Propagation:** When a bus gets stuck in traffic or breakdowns, static timetables fail to recalculate intermediate stop arrival times, leaving passengers stranded at enroute stops without updates.
- **Absence of Contingency Planning:** Fleet controllers lack automated tools to calculate the ripple effect of vehicle breakdowns ("What-If" scenarios), resulting in manual phone calls and ad-hoc reassignments.
- **Lack of Crowd Density Awareness:** Commuters board overcrowded buses without prior knowledge of seat availability.

### 1.2 Proposed System: BusFlow
BusFlow introduces an **Intelligent Transit Control Center** combining:
1. An algorithmic **Smart Schedule Engine** in Python that dynamically cascades delays down every subsequent stop along a route.
2. A **"What-If" Contingency Simulator** for fleet managers to model vehicle failures and receive immediate standby fleet/driver recommendations.
3. Multi-role responsive portals for **Dispatch Admins**, **Drivers**, and **Commuters/Passengers**.
4. Interactive GPS corridor tracking using OpenStreetMap and Leaflet.js without external paid API dependencies.

---

## 2. Software Requirements Specification (SRS)

### 2.1 Hardware Requirements
- **Processor:** Dual Core Intel/AMD @ 2.0 GHz or higher
- **RAM:** Minimum 4 GB (8 GB recommended)
- **Hard Disk:** 500 MB free space

### 2.2 Software Requirements
- **Operating System:** Windows 10/11, Linux, or macOS
- **Programming Language:** Python 3.10+
- **Web Framework:** Flask 3.x
- **Database Engine:** SQLite 3 (native relational database)
- **Frontend Stack:** HTML5, CSS3 (Custom Dark Control Center Theme), JavaScript (Vanilla ES6)
- **Libraries & APIs:** Leaflet.js (OpenStreetMap), Chart.js (Analytics), Bootstrap Icons

---

## 3. Mathematical Model: Smart Schedule Delay Engine

Let route $R$ consist of ordered stops $S = \{s_1, s_2, \dots, s_n\}$ with scheduled departure time $T_0$ from the origin stop $s_1$.

Each stop $s_i$ is associated with a pre-calibrated temporal offset $\Delta t_i$ from origin departure:
$$\text{Scheduled Arrival at Stop } s_i: \quad T(s_i) = T_0 + \Delta t_i$$

When a driver or dispatcher reports a delay of $D$ minutes at or before stop $s_k$ ($1 \le k \le n$):
$$\text{Expected Arrival at Stop } s_i: \quad T'(s_i) = T_0 + \Delta t_i + D \quad (\forall i \ge k)$$

### Algorithm in Python:
```python
def calculate_stop_times(departure_time_str, delay_minutes, stops):
    results = []
    for stop in stops:
        offset = stop.get('offset_minutes', 0)
        scheduled = add_minutes_to_time(departure_time_str, offset)
        expected = add_minutes_to_time(departure_time_str, offset + delay_minutes)
        results.append({
            'stop_name': stop['stop_name'],
            'scheduled_time': scheduled,
            'expected_time': expected,
            'is_delayed': delay_minutes > 0
        })
    return results
```

---

## 4. Entity Relationship (ER) Data Dictionary

```
+----------------+       +-------------------+       +-----------------+
|     USERS      |       |     SCHEDULES     |       |      BUSES      |
+----------------+       +-------------------+       +-----------------+
| id (PK)        |<----->| schedule_id (PK)  |<----->| bus_id (PK)     |
| name           |   1:N | bus_id (FK)       |  N:1  | bus_number (UQ) |
| email (UQ)     |       | route_id (FK)     |       | bus_type        |
| phone          |       | driver_id (FK)    |       | capacity        |
| password_hash  |       | departure_time    |       | status          |
| role           |       | arrival_time      |       +-----------------+
+----------------+       | status            |
                         | occupancy         |
                         | delay_minutes     |
                         +-------------------+
                                   |
                                   | 1:N
                                   v
                         +-------------------+
                         |      DELAYS       |
                         +-------------------+
                         | delay_id (PK)     |
                         | schedule_id (FK)  |
                         | delay_minutes     |
                         | reason            |
                         | updated_at        |
                         +-------------------+
```

---

## 5. Viva Voce Q&A Preparation (Examiner Guide)

### Q1: What makes BusFlow distinct from standard college bus management systems?
> **Answer:** Standard projects are simple CRUD operations (Create, Read, Update, Delete) storing static records. BusFlow is an **operational management system** with:
> 1. A dynamic Python calculation engine that recalculates stop arrival times upon delay entries.
> 2. An algorithmic "What-If" contingency simulator that calculates replacement buses and drivers in real-time during breakdowns.
> 3. Real-time crowd occupancy tracking (Low, Medium, High, Full) updated directly by drivers.

### Q2: Why did you select SQLite instead of MySQL?
> **Answer:** SQLite provides full relational ACID compliance, foreign key constraint enforcement, and zero-configuration portability, making the project run effortlessly on any evaluation machine without database server setup. However, the system's modular SQL abstraction can be re-targeted to MySQL or PostgreSQL by changing a single connection URI.

### Q3: How is password security implemented?
> **Answer:** Passwords are never stored in plain text. We utilize `werkzeug.security.generate_password_hash` with SHA-256 and salted hashing to protect user authentication against dictionary and rainbow table attacks.

### Q4: How does the "What-If Schedule" Simulator work?
> **Answer:** When an admin flags a bus as unavailable, the simulator:
> 1. Extracts all schedules assigned to that bus for the day.
> 2. Identifies active buses not committed to conflicting time windows with comparable capacity ($\ge \text{target capacity} - 5$).
> 3. Matches standby drivers to formulate an actionable rerouting order.
