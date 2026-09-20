/**
 * CatchIt: Smart Bus Schedule & Transportation Management System
 * Core Client Controller: Theme Toggle, Interactive 2x2 Bus Seat Selector,
 * QR Ticket Scanner, Live Telemetry Map, and Driver Shift Duty Tracker
 */

// ---------------------------------------------------------
// DARK / LIGHT MODE SWITCHER
// ---------------------------------------------------------
function initTheme() {
    const saved = localStorage.getItem('catchit_theme') || 'dark';
    document.documentElement.setAttribute('data-theme', saved);
    updateThemeToggleIcon(saved);
}

function toggleTheme() {
    const current = document.documentElement.getAttribute('data-theme') || 'dark';
    const next = current === 'dark' ? 'light' : 'dark';
    document.documentElement.setAttribute('data-theme', next);
    localStorage.setItem('catchit_theme', next);
    updateThemeToggleIcon(next);
}

function updateThemeToggleIcon(theme) {
    const btn = document.getElementById('theme_toggle_btn');
    if (btn) {
        btn.innerHTML = theme === 'dark' ? '<i class="bi bi-sun-fill" style="color:#F59E0B;"></i>' : '<i class="bi bi-moon-stars-fill" style="color:#2563EB;"></i>';
    }
}

document.addEventListener('DOMContentLoaded', initTheme);

// ---------------------------------------------------------
// MODAL MANAGEMENT & TOASTS
// ---------------------------------------------------------
function openModal(modalId) {
    const el = document.getElementById(modalId);
    if (el) {
        el.classList.add('active');
        document.body.style.overflow = 'hidden';
    }
}

function closeModal(modalId) {
    const el = document.getElementById(modalId);
    if (el) {
        el.classList.remove('active');
        document.body.style.overflow = '';
    }
}

window.addEventListener('click', (e) => {
    if (e.target.classList.contains('modal-overlay')) {
        e.target.classList.remove('active');
        document.body.style.overflow = '';
    }
});

function showToast(message, type = 'success') {
    const toast = document.createElement('div');
    toast.className = `alert alert-${type}`;
    toast.style.position = 'fixed';
    toast.style.bottom = '24px';
    toast.style.right = '24px';
    toast.style.zIndex = '99999';
    toast.style.boxShadow = '0 10px 30px rgba(0,0,0,0.4)';
    toast.style.minWidth = '280px';
    toast.innerHTML = `<i class="bi bi-info-circle-fill"></i> <div>${message}</div>`;
    document.body.appendChild(toast);
    setTimeout(() => {
        toast.style.transition = 'opacity 0.4s';
        toast.style.opacity = '0';
        setTimeout(() => toast.remove(), 400);
    }, 3500);
}

// ---------------------------------------------------------
// INTERACTIVE 2x2 BUS SEAT SELECTOR & MOST WANTED SEATS
// ---------------------------------------------------------
let currentSelectedSchedule = null;
let currentSelectedSeat = null;
let currentSelectedFare = 0;
let currentSelectedDate = null;

async function openSeatSelector(scheduleId, busNum, routeName, baseFare, travelDate) {
    if (!travelDate) {
        travelDate = document.getElementById('search_date') ? document.getElementById('search_date').value : new Date().toISOString().split('T')[0];
    }

    currentSelectedSchedule = scheduleId;
    currentSelectedDate = travelDate;
    currentSelectedSeat = null;
    currentSelectedFare = parseFloat(baseFare);

    document.getElementById('seat_bus_num').innerText = busNum;
    document.getElementById('seat_route_name').innerText = routeName;
    document.getElementById('seat_travel_date').innerText = travelDate;
    document.getElementById('selected_seat_code').innerText = 'None';
    document.getElementById('selected_seat_fare').innerText = `₹${baseFare}`;

    const gridContainer = document.getElementById('bus_seat_grid_container');
    gridContainer.innerHTML = `<div style="text-align:center; padding:30px;"><p style="color:var(--text-muted);">Loading coach seat map...</p></div>`;

    openModal('seatModal');

    try {
        const resp = await fetch(`/api/schedules/${scheduleId}/seats?date=${encodeURIComponent(travelDate)}`);
        const res = await resp.json();

        if (!res.success) {
            gridContainer.innerHTML = `<div class="alert alert-danger">Error loading seats.</div>`;
            return;
        }

        const data = res.data;
        let html = `
        <div class="bus-coach">
            <div class="bus-front-cabin">
                <span><i class="bi bi-door-closed"></i> Passenger Entry</span>
                <span><i class="bi bi-circle"></i> Driver Steering Wheel <i class="bi bi-compass"></i></span>
            </div>
            <div class="bus-seat-grid">
        `;

        data.layout.forEach(r => {
            const seats = r.seats;
            html += `<div class="bus-seat-row">`;
            
            // Left pair: A, B
            html += `<div class="seat-pair">`;
            [seats[0], seats[1]].forEach(s => {
                const bookedClass = s.is_booked ? 'booked' : '';
                const wantedClass = s.is_most_wanted && !s.is_booked ? 'most-wanted' : '';
                const title = s.is_booked ? 'Booked' : (s.is_most_wanted ? '🔥 Most Wanted Front Window Seat' : 'Available');
                const onclick = s.is_booked ? '' : `onclick="selectSeat('${s.seat_code}', ${s.fare}, this)"`;
                html += `
                    <button type="button" class="seat-btn ${bookedClass} ${wantedClass}" ${onclick} title="${title}">
                        <span>${s.seat_code}</span>
                        <small style="font-size:9px; opacity:0.8;">₹${s.fare}</small>
                    </button>
                `;
            });
            html += `</div>`;

            // Aisle
            html += `<div class="seat-aisle-gap">AISLE</div>`;

            // Right pair: C, D
            html += `<div class="seat-pair">`;
            [seats[2], seats[3]].forEach(s => {
                const bookedClass = s.is_booked ? 'booked' : '';
                const wantedClass = s.is_most_wanted && !s.is_booked ? 'most-wanted' : '';
                const title = s.is_booked ? 'Booked' : (s.is_most_wanted ? '🔥 Most Wanted Window Seat' : 'Available');
                const onclick = s.is_booked ? '' : `onclick="selectSeat('${s.seat_code}', ${s.fare}, this)"`;
                html += `
                    <button type="button" class="seat-btn ${bookedClass} ${wantedClass}" ${onclick} title="${title}">
                        <span>${s.seat_code}</span>
                        <small style="font-size:9px; opacity:0.8;">₹${s.fare}</small>
                    </button>
                `;
            });
            html += `</div>`;

            html += `</div>`;
        });

        html += `
            </div>
            <div class="seat-legend">
                <div class="legend-item"><span class="legend-dot" style="border:2px solid var(--seat-available-border); background:var(--seat-available);"></span> Available</div>
                <div class="legend-item"><span class="legend-dot" style="border:2px solid #F59E0B; background:var(--seat-available);"></span> 🔥 Most Wanted</div>
                <div class="legend-item"><span class="legend-dot" style="background:var(--seat-booked);"></span> Booked</div>
                <div class="legend-item"><span class="legend-dot" style="background:#2563EB;"></span> Selected</div>
            </div>
        </div>
        `;

        gridContainer.innerHTML = html;
    } catch (err) {
        console.error(err);
        gridContainer.innerHTML = `<div class="alert alert-danger">Network error loading seat layout.</div>`;
    }
}

function selectSeat(seatCode, fare, btn) {
    document.querySelectorAll('.seat-btn.selected').forEach(b => b.classList.remove('selected'));
    btn.classList.add('selected');

    currentSelectedSeat = seatCode;
    currentSelectedFare = fare;

    document.getElementById('selected_seat_code').innerText = seatCode;
    document.getElementById('selected_seat_fare').innerText = `₹${fare}`;
}

async function confirmSeatBooking() {
    if (!currentSelectedSeat) {
        alert('Please click on an available seat to choose your seat number.');
        return;
    }

    const passengerName = document.getElementById('booking_passenger_name') ? document.getElementById('booking_passenger_name').value : 'Passenger';

    try {
        const resp = await fetch('/api/book-seat', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                schedule_id: currentSelectedSchedule,
                seat_number: currentSelectedSeat,
                travel_date: currentSelectedDate,
                fare: currentSelectedFare,
                passenger_name: passengerName
            })
        });
        const data = await resp.json();

        if (data.success) {
            closeModal('seatModal');
            showConfirmedPassModal(data.booking_code, data.seat_number, data.travel_date, data.fare_paid, passengerName);
        } else {
            alert(data.message);
        }
    } catch (err) {
        console.error(err);
        alert('Error completing reservation.');
    }
}

function showConfirmedPassModal(code, seat, date, fare, name) {
    const modal = document.getElementById('ticketPassModal');
    if (!modal) {
        alert(`🎉 Booking Confirmed!\nBooking Code: ${code}\nSeat: #${seat}\nFare: ₹${fare}`);
        window.location.reload();
        return;
    }

    document.getElementById('pass_code').innerText = code;
    document.getElementById('pass_seat').innerText = `#${seat}`;
    document.getElementById('pass_date').innerText = date;
    document.getElementById('pass_fare').innerText = `₹${fare}`;
    document.getElementById('pass_name').innerText = name;

    const qrUrl = `https://api.qrserver.com/v1/create-qr-code/?size=140x140&data=${encodeURIComponent(code)}`;
    document.getElementById('pass_qr_img').src = qrUrl;

    openModal('ticketPassModal');
}

// ---------------------------------------------------------
// TICKET VERIFICATION & QR SCANNER (Conductor / Driver Tool)
// ---------------------------------------------------------
async function verifyTicketCode(code) {
    if (!code) {
        code = document.getElementById('scanner_code_input').value.trim();
    }
    if (!code) {
        alert('Please enter or scan a booking code.');
        return;
    }

    const resultBox = document.getElementById('scanner_result_box');
    resultBox.innerHTML = `<div style="text-align:center; padding:20px;"><p style="color:var(--text-muted);">Validating ticket with transit registry...</p></div>`;

    try {
        const resp = await fetch('/api/ticket/verify', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ booking_code: code })
        });
        const data = await resp.json();

        if (!data.success) {
            resultBox.innerHTML = `
                <div class="alert alert-danger" style="margin-top:16px;">
                    <i class="bi bi-x-circle-fill"></i> ${data.message}
                </div>
            `;
            return;
        }

        const t = data.ticket;
        resultBox.innerHTML = `
            <div class="panel" style="border-left: 4px solid var(--status-ontime); margin-top:16px; background:var(--bg-card);">
                <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:12px;">
                    <span class="badge badge-ontime"><i class="bi bi-check-circle-fill"></i> ${data.message}</span>
                    <strong style="color:var(--accent-cyan); font-family:monospace; font-size:16px;">${t.booking_code}</strong>
                </div>
                <div style="display:grid; grid-template-columns:1fr 1fr; gap:12px; font-size:14px;">
                    <div><span style="color:var(--text-muted);">Passenger:</span> <strong>${t.passenger_name}</strong></div>
                    <div><span style="color:var(--text-muted);">Seat Number:</span> <strong style="color:#F59E0B; font-size:16px;">${t.seat_number}</strong></div>
                    <div><span style="color:var(--text-muted);">Bus Number:</span> <strong>${t.bus_number}</strong></div>
                    <div><span style="color:var(--text-muted);">Route:</span> <strong>${t.route_name}</strong></div>
                    <div><span style="color:var(--text-muted);">Travel Date:</span> <strong>${t.travel_date}</strong></div>
                    <div><span style="color:var(--text-muted);">Fare Paid:</span> <strong>₹${t.fare_paid}</strong></div>
                </div>
            </div>
        `;
    } catch (err) {
        console.error(err);
        resultBox.innerHTML = `<div class="alert alert-danger">Error verifying ticket.</div>`;
    }
}

// ---------------------------------------------------------
// DRIVER WORKING HOURS & DUTY TOGGLE
// ---------------------------------------------------------
async function toggleDriverDuty() {
    try {
        const resp = await fetch('/api/driver/shift/toggle', { method: 'POST' });
        const data = await resp.json();
        if (data.success) {
            showToast(data.message, data.is_on_duty ? 'success' : 'info');
            setTimeout(() => window.location.reload(), 900);
        }
    } catch (err) {
        console.error(err);
    }
}

// ---------------------------------------------------------
// ROUTE SEARCH WITH DATE & FARE
// ---------------------------------------------------------
async function searchBuses(sourceId, destId, resultsContainerId) {
    const source = document.getElementById(sourceId).value;
    const dest = document.getElementById(destId).value;
    const dateInput = document.getElementById('search_date');
    const travelDate = dateInput ? dateInput.value : new Date().toISOString().split('T')[0];
    const container = document.getElementById(resultsContainerId);

    if (!source || !dest) {
        alert('Please select origin and destination.');
        return;
    }

    container.innerHTML = `<div style="text-align:center; padding:30px;"><p style="color:var(--text-muted);">Searching available buses for ${travelDate}...</p></div>`;

    try {
        const resp = await fetch(`/api/schedules/search?source=${encodeURIComponent(source)}&destination=${encodeURIComponent(dest)}&date=${encodeURIComponent(travelDate)}`);
        const data = await resp.json();

        if (!data.success || data.schedules.length === 0) {
            container.innerHTML = `
                <div class="panel" style="text-align:center; padding:32px;">
                    <i class="bi bi-bus-front" style="font-size:36px; color:var(--text-dim); margin-bottom:12px; display:block;"></i>
                    <h4>No Direct Schedules Found</h4>
                    <p style="color:var(--text-muted); font-size:14px; margin-top:6px;">Try searching popular corridors like <strong>Tumkur → Bangalore</strong>.</p>
                </div>
            `;
            return;
        }

        let html = `<div style="display:flex; flex-direction:column; gap:16px;">`;
        data.schedules.forEach(s => {
            const statusClass = s.status === 'On Time' ? 'badge-ontime' : (s.status === 'Delayed' ? 'badge-delayed' : 'badge-cancelled');
            const occClass = `badge-occupancy-${s.occupancy.toLowerCase()}`;
            const delayNotice = s.delay_minutes > 0 ? `<span style="color:#F59E0B; font-weight:700; font-size:12px;"><i class="bi bi-clock-history"></i> +${s.delay_minutes} min delayed</span>` : `<span style="color:#10B981; font-weight:600; font-size:12px;"><i class="bi bi-check-circle"></i> On Schedule</span>`;

            html += `
            <div class="panel" style="margin-bottom:0; border-left: 4px solid ${s.status === 'On Time' ? '#10B981' : '#F59E0B'};">
                <div style="display:flex; justify-content:space-between; align-items:flex-start; flex-wrap:wrap; gap:12px;">
                    <div>
                        <div style="display:flex; align-items:center; gap:10px; margin-bottom:6px;">
                            <span class="bus-vehicle-badge"><i class="bi bi-bus-front-fill"></i> ${s.bus_number}</span>
                            <span class="badge ${statusClass}"><span class="badge-dot"></span> ${s.status}</span>
                            <span class="badge ${occClass}"><i class="bi bi-people-fill"></i> ${s.occupancy} Crowd</span>
                        </div>
                        <div style="font-size:13px; color:var(--text-muted);">${s.bus_type} • ${s.distance_km} km • <strong style="color:var(--accent-gold); font-size:15px;">₹${s.fare}</strong> / seat</div>
                    </div>
                    <div style="text-align:right;">
                        <div style="font-size:20px; font-weight:800; color:var(--text-main);">
                            ${s.expected_departure} <span style="font-size:14px; color:var(--text-dim);">➔</span> ${s.expected_arrival}
                        </div>
                        <div>${delayNotice}</div>
                    </div>
                </div>

                <div style="margin-top:16px; padding-top:14px; border-top:1px solid var(--border-light); display:flex; justify-content:space-between; align-items:center; flex-wrap:wrap; gap:10px;">
                    <div style="font-size:13px; color:var(--text-muted);">
                        <i class="bi bi-geo-alt"></i> <strong>Stops:</strong> ${s.stops.map(st => st.stop_name.split(' ')[0]).join(' ➔ ')}
                    </div>
                    <button class="btn btn-primary btn-sm" onclick="openSeatSelector(${s.schedule_id}, '${s.bus_number}', '${s.route_name}', ${s.fare}, '${travelDate}')">
                        <i class="bi bi-grid-3x3-gap-fill"></i> Select Seats & Book
                    </button>
                </div>
            </div>
            `;
        });
        html += `</div>`;
        container.innerHTML = html;
    } catch (err) {
        console.error(err);
        container.innerHTML = `<div class="alert alert-danger">Error loading buses.</div>`;
    }
}

// ---------------------------------------------------------
// DELAY & OCCUPANCY HELPERS
// ---------------------------------------------------------
async function submitDelayUpdate(scheduleId) {
    const delayMins = document.getElementById('delay_minutes').value;
    const reason = document.getElementById('delay_reason').value;

    const resp = await fetch(`/api/schedules/${scheduleId}/delay`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ delay_minutes: parseInt(delayMins), reason: reason })
    });
    const data = await resp.json();
    if (data.success) {
        closeModal('delayModal');
        showToast(`Smart Schedule updated! ${delayMins}m delay cascaded.`, 'warning');
        setTimeout(() => window.location.reload(), 900);
    }
}

async function updateOccupancy(scheduleId, level) {
    const resp = await fetch(`/api/schedules/${scheduleId}/occupancy`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ occupancy: level })
    });
    const data = await resp.json();
    if (data.success) {
        showToast(`Occupancy updated to ${level}!`, 'info');
        setTimeout(() => window.location.reload(), 800);
    }
}

// Print Current Document
function printCurrentSchedule() {
    window.print();
}

// Leaflet map shared by passenger route planning and live tracking.
async function initLiveTrackingMap(mapId) {
    const mapElement = document.getElementById(mapId);
    if (!mapElement || typeof L === 'undefined') return;

    const map = L.map(mapElement).setView([13.18, 77.34], 10);
    L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
        attribution: '&copy; OpenStreetMap contributors'
    }).addTo(map);

    try {
        const response = await fetch('/api/live-tracking');
        const data = await response.json();
        const points = (data.route_polyline || []).map(point => [point.lat, point.lng]);
        if (points.length) {
            L.polyline(points, { color: '#06B6D4', weight: 5, opacity: 0.8 }).addTo(map);
            map.fitBounds(points, { padding: [24, 24] });
        }
        (data.fleet || []).forEach(bus => {
            const marker = L.marker([bus.latitude, bus.longitude]).addTo(map);
            marker.bindPopup(`<strong>${bus.bus_number}</strong><br>${bus.route_name}<br>${bus.speed_kmh} km/h`);
            marker.on('click', () => {
                const details = document.getElementById('selected_bus_details');
                if (details) {
                    details.innerHTML = `<div class="telemetry-detail"><strong>${bus.bus_number}</strong><span>${bus.current_stop} to ${bus.next_stop}</span><span>${bus.speed_kmh} km/h · ${bus.occupancy} occupancy</span></div>`;
                }
            });
        });
    } catch (error) {
        mapElement.innerHTML = '<div class="map-empty-state">Live map is temporarily unavailable.</div>';
    }
}

async function showPlannerRoute(sourceId, destinationId, mapId, summaryId) {
    const source = document.getElementById(sourceId)?.value;
    const destination = document.getElementById(destinationId)?.value;
    const mapElement = document.getElementById(mapId);
    const summary = document.getElementById(summaryId);
    if (!source || !destination || !mapElement || typeof L === 'undefined') return;

    if (window.plannerMap) window.plannerMap.remove();
    window.plannerMap = L.map(mapElement).setView([13.18, 77.34], 10);
    L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
        attribution: '&copy; OpenStreetMap contributors'
    }).addTo(window.plannerMap);

    const response = await fetch(`/api/routes/best-way?source=${encodeURIComponent(source)}&destination=${encodeURIComponent(destination)}`);
    const data = await response.json();
    const route = (data.routes || [])[0];
    const points = (route?.coordinates || []).map(point => [point.lat, point.lng]);
    if (points.length) {
        L.polyline(points, { color: '#10B981', weight: 6 }).addTo(window.plannerMap);
        points.forEach((point, index) => L.marker(point).addTo(window.plannerMap).bindTooltip(index === 0 ? source : destination));
        window.plannerMap.fitBounds(points, { padding: [24, 24] });
    }
    if (summary && route) summary.innerHTML = `<strong>${route.name}</strong><br>${route.distance_km} km · ${route.estimated_time} · ${route.highlights}`;
}
