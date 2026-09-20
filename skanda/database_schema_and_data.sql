-- CatchIt MySQL Database Dump
SET FOREIGN_KEY_CHECKS=0;

DROP TABLE IF EXISTS `bookings`;
CREATE TABLE `bookings` (
  `booking_id` int(11) NOT NULL AUTO_INCREMENT,
  `user_id` int(11) NOT NULL,
  `schedule_id` int(11) NOT NULL,
  `passenger_name` text NOT NULL,
  `seat_number` text NOT NULL,
  `travel_date` text NOT NULL,
  `fare_paid` double NOT NULL DEFAULT 120,
  `booking_code` text NOT NULL,
  `status` text NOT NULL DEFAULT 'Confirmed' CHECK (`status` in ('Confirmed','Boarded','Cancelled','Completed')),
  `created_at` timestamp NOT NULL DEFAULT current_timestamp(),
  PRIMARY KEY (`booking_id`),
  UNIQUE KEY `booking_code` (`booking_code`) USING HASH,
  KEY `user_id` (`user_id`),
  KEY `schedule_id` (`schedule_id`),
  CONSTRAINT `bookings_ibfk_1` FOREIGN KEY (`user_id`) REFERENCES `users` (`id`),
  CONSTRAINT `bookings_ibfk_2` FOREIGN KEY (`schedule_id`) REFERENCES `schedules` (`schedule_id`)
) ENGINE=InnoDB AUTO_INCREMENT=7 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
INSERT INTO `bookings` (`booking_id`, `user_id`, `schedule_id`, `passenger_name`, `seat_number`, `travel_date`, `fare_paid`, `booking_code`, `status`, `created_at`) VALUES ('1', '3', '1', 'Skanda Bharadwaj', '1A', '2026-09-19', '140.0', 'CI-2026-TKBLR-01', 'Confirmed', '2026-09-19 23:28:36');
INSERT INTO `bookings` (`booking_id`, `user_id`, `schedule_id`, `passenger_name`, `seat_number`, `travel_date`, `fare_paid`, `booking_code`, `status`, `created_at`) VALUES ('2', '3', '3', 'Skanda Bharadwaj', '2D', '2026-09-19', '95.0', 'CI-2026-TKDBP-02', 'Confirmed', '2026-09-19 23:28:36');
INSERT INTO `bookings` (`booking_id`, `user_id`, `schedule_id`, `passenger_name`, `seat_number`, `travel_date`, `fare_paid`, `booking_code`, `status`, `created_at`) VALUES ('3', '3', '1', 'Skanda Bharadwaj', '1D', '2026-09-18', '140.0', 'CI-2026-TKBLR-99', 'Boarded', '2026-09-19 23:28:36');
INSERT INTO `bookings` (`booking_id`, `user_id`, `schedule_id`, `passenger_name`, `seat_number`, `travel_date`, `fare_paid`, `booking_code`, `status`, `created_at`) VALUES ('4', '3', '5', 'Skanda Bharadwaj', '3A', '2026-09-14', '220.0', 'CI-2026-TKMYS-44', 'Completed', '2026-09-19 23:28:36');
INSERT INTO `bookings` (`booking_id`, `user_id`, `schedule_id`, `passenger_name`, `seat_number`, `travel_date`, `fare_paid`, `booking_code`, `status`, `created_at`) VALUES ('5', '20', '1', 'Ananya Sharma', '2A', '2026-09-19', '140.0', 'CI-2026-TKBLR-03', 'Confirmed', '2026-09-19 23:28:36');
INSERT INTO `bookings` (`booking_id`, `user_id`, `schedule_id`, `passenger_name`, `seat_number`, `travel_date`, `fare_paid`, `booking_code`, `status`, `created_at`) VALUES ('6', '21', '2', 'Karthik Varma', '4B', '2026-09-19', '85.0', 'CI-2026-TKNGS-04', 'Confirmed', '2026-09-19 23:28:36');

DROP TABLE IF EXISTS `buses`;
CREATE TABLE `buses` (
  `bus_id` int(11) NOT NULL AUTO_INCREMENT,
  `bus_number` text NOT NULL,
  `bus_type` text NOT NULL,
  `capacity` int(11) NOT NULL,
  `status` text NOT NULL DEFAULT 'Active' CHECK (`status` in ('Active','Maintenance','Out of Service')),
  PRIMARY KEY (`bus_id`),
  UNIQUE KEY `bus_number` (`bus_number`) USING HASH
) ENGINE=InnoDB AUTO_INCREMENT=26 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
INSERT INTO `buses` (`bus_id`, `bus_number`, `bus_type`, `capacity`, `status`) VALUES ('1', 'KA01AB1234', 'AC Sleeper', '40', 'Active');
INSERT INTO `buses` (`bus_id`, `bus_number`, `bus_type`, `capacity`, `status`) VALUES ('2', 'KA05CD5678', 'Non-AC', '45', 'Active');
INSERT INTO `buses` (`bus_id`, `bus_number`, `bus_type`, `capacity`, `status`) VALUES ('3', 'KA09EF9012', 'Non-AC', '45', 'Active');
INSERT INTO `buses` (`bus_id`, `bus_number`, `bus_type`, `capacity`, `status`) VALUES ('4', 'KA11GH3456', 'Volvo', '50', 'Maintenance');
INSERT INTO `buses` (`bus_id`, `bus_number`, `bus_type`, `capacity`, `status`) VALUES ('5', 'KA13IJ7890', 'AC', '42', 'Active');
INSERT INTO `buses` (`bus_id`, `bus_number`, `bus_type`, `capacity`, `status`) VALUES ('6', 'KA04KL2345', 'Volvo Multi-Axle', '48', 'Active');
INSERT INTO `buses` (`bus_id`, `bus_number`, `bus_type`, `capacity`, `status`) VALUES ('7', 'KA06MN6789', 'AC Sleeper', '36', 'Active');
INSERT INTO `buses` (`bus_id`, `bus_number`, `bus_type`, `capacity`, `status`) VALUES ('8', 'KA02OP1122', 'Non-AC Deluxe', '52', 'Active');
INSERT INTO `buses` (`bus_id`, `bus_number`, `bus_type`, `capacity`, `status`) VALUES ('9', 'KA03QR3344', 'Electric AC', '45', 'Active');
INSERT INTO `buses` (`bus_id`, `bus_number`, `bus_type`, `capacity`, `status`) VALUES ('10', 'KA07ST5566', 'Volvo', '50', 'Active');
INSERT INTO `buses` (`bus_id`, `bus_number`, `bus_type`, `capacity`, `status`) VALUES ('11', 'KA08UV7788', 'AC Seater', '44', 'Active');
INSERT INTO `buses` (`bus_id`, `bus_number`, `bus_type`, `capacity`, `status`) VALUES ('12', 'KA10WX9900', 'Non-AC', '55', 'Active');
INSERT INTO `buses` (`bus_id`, `bus_number`, `bus_type`, `capacity`, `status`) VALUES ('13', 'KA12YZ1234', 'AC Sleeper', '40', 'Active');
INSERT INTO `buses` (`bus_id`, `bus_number`, `bus_type`, `capacity`, `status`) VALUES ('14', 'KA14AA5678', 'Volvo', '52', 'Active');
INSERT INTO `buses` (`bus_id`, `bus_number`, `bus_type`, `capacity`, `status`) VALUES ('15', 'KA15BB9012', 'Electric AC', '46', 'Active');
INSERT INTO `buses` (`bus_id`, `bus_number`, `bus_type`, `capacity`, `status`) VALUES ('16', 'KA16CC3456', 'Non-AC Deluxe', '50', 'Active');
INSERT INTO `buses` (`bus_id`, `bus_number`, `bus_type`, `capacity`, `status`) VALUES ('17', 'KA17DD7890', 'AC Sleeper', '38', 'Active');
INSERT INTO `buses` (`bus_id`, `bus_number`, `bus_type`, `capacity`, `status`) VALUES ('18', 'KA18EE2345', 'Volvo Multi-Axle', '48', 'Active');
INSERT INTO `buses` (`bus_id`, `bus_number`, `bus_type`, `capacity`, `status`) VALUES ('19', 'KA19FF6789', 'AC Seater', '42', 'Active');
INSERT INTO `buses` (`bus_id`, `bus_number`, `bus_type`, `capacity`, `status`) VALUES ('20', 'KA20GG1122', 'Non-AC', '54', 'Active');
INSERT INTO `buses` (`bus_id`, `bus_number`, `bus_type`, `capacity`, `status`) VALUES ('21', 'KA21HH3344', 'Volvo', '50', 'Active');
INSERT INTO `buses` (`bus_id`, `bus_number`, `bus_type`, `capacity`, `status`) VALUES ('22', 'KA22II5566', 'Electric AC', '45', 'Active');
INSERT INTO `buses` (`bus_id`, `bus_number`, `bus_type`, `capacity`, `status`) VALUES ('23', 'KA23JJ7788', 'AC Sleeper', '40', 'Active');
INSERT INTO `buses` (`bus_id`, `bus_number`, `bus_type`, `capacity`, `status`) VALUES ('24', 'KA24KK9900', 'Non-AC', '52', 'Active');
INSERT INTO `buses` (`bus_id`, `bus_number`, `bus_type`, `capacity`, `status`) VALUES ('25', 'KA25LL1234', 'Volvo', '50', 'Active');

DROP TABLE IF EXISTS `delays`;
CREATE TABLE `delays` (
  `delay_id` int(11) NOT NULL AUTO_INCREMENT,
  `schedule_id` int(11) NOT NULL,
  `delay_minutes` int(11) NOT NULL,
  `reason` text NOT NULL,
  `updated_at` timestamp NOT NULL DEFAULT current_timestamp(),
  PRIMARY KEY (`delay_id`),
  KEY `schedule_id` (`schedule_id`),
  CONSTRAINT `delays_ibfk_1` FOREIGN KEY (`schedule_id`) REFERENCES `schedules` (`schedule_id`) ON DELETE CASCADE
) ENGINE=InnoDB AUTO_INCREMENT=5 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
INSERT INTO `delays` (`delay_id`, `schedule_id`, `delay_minutes`, `reason`, `updated_at`) VALUES ('1', '2', '15', 'Heavy traffic near Dabaspet toll', '2026-09-19 23:28:36');
INSERT INTO `delays` (`delay_id`, `schedule_id`, `delay_minutes`, `reason`, `updated_at`) VALUES ('2', '8', '20', 'Rain & slow moving traffic on NH48', '2026-09-19 23:28:36');
INSERT INTO `delays` (`delay_id`, `schedule_id`, `delay_minutes`, `reason`, `updated_at`) VALUES ('3', '12', '10', 'Signal delay at Yeshwanthpur flyover', '2026-09-19 23:28:36');
INSERT INTO `delays` (`delay_id`, `schedule_id`, `delay_minutes`, `reason`, `updated_at`) VALUES ('4', '27', '25', 'Bridge maintenance diversion near Nelamangala', '2026-09-19 23:28:36');

DROP TABLE IF EXISTS `driver_shifts`;
CREATE TABLE `driver_shifts` (
  `shift_id` int(11) NOT NULL AUTO_INCREMENT,
  `driver_id` int(11) NOT NULL,
  `shift_date` text NOT NULL,
  `start_time` text NOT NULL,
  `end_time` text DEFAULT NULL,
  `hours_worked` double NOT NULL DEFAULT 0,
  `status` text NOT NULL DEFAULT 'Active' CHECK (`status` in ('Active','Completed')),
  PRIMARY KEY (`shift_id`),
  KEY `driver_id` (`driver_id`),
  CONSTRAINT `driver_shifts_ibfk_1` FOREIGN KEY (`driver_id`) REFERENCES `users` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=8 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
INSERT INTO `driver_shifts` (`shift_id`, `driver_id`, `shift_date`, `start_time`, `end_time`, `hours_worked`, `status`) VALUES ('1', '2', '2026-09-19', '06:00', NULL, '6.5', 'Active');
INSERT INTO `driver_shifts` (`shift_id`, `driver_id`, `shift_date`, `start_time`, `end_time`, `hours_worked`, `status`) VALUES ('2', '2', '2026-09-18', '06:30', '14:30', '8.0', 'Completed');
INSERT INTO `driver_shifts` (`shift_id`, `driver_id`, `shift_date`, `start_time`, `end_time`, `hours_worked`, `status`) VALUES ('3', '2', '2026-09-17', '07:00', '15:30', '8.5', 'Completed');
INSERT INTO `driver_shifts` (`shift_id`, `driver_id`, `shift_date`, `start_time`, `end_time`, `hours_worked`, `status`) VALUES ('4', '2', '2026-09-16', '06:00', '14:00', '8.0', 'Completed');
INSERT INTO `driver_shifts` (`shift_id`, `driver_id`, `shift_date`, `start_time`, `end_time`, `hours_worked`, `status`) VALUES ('5', '2', '2026-09-15', '07:30', '14:30', '7.0', 'Completed');
INSERT INTO `driver_shifts` (`shift_id`, `driver_id`, `shift_date`, `start_time`, `end_time`, `hours_worked`, `status`) VALUES ('6', '4', '2026-09-19', '07:00', NULL, '5.5', 'Active');
INSERT INTO `driver_shifts` (`shift_id`, `driver_id`, `shift_date`, `start_time`, `end_time`, `hours_worked`, `status`) VALUES ('7', '5', '2026-09-19', '08:00', NULL, '4.5', 'Active');

DROP TABLE IF EXISTS `routes`;
CREATE TABLE `routes` (
  `route_id` int(11) NOT NULL AUTO_INCREMENT,
  `route_name` text NOT NULL,
  `source` text NOT NULL,
  `destination` text NOT NULL,
  `distance_km` int(11) NOT NULL,
  `base_fare` double NOT NULL DEFAULT 80,
  PRIMARY KEY (`route_id`)
) ENGINE=InnoDB AUTO_INCREMENT=13 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
INSERT INTO `routes` (`route_id`, `route_name`, `source`, `destination`, `distance_km`, `base_fare`) VALUES ('1', 'Tumkur - Bangalore', 'Tumkur', 'Bangalore', '70', '120.0');
INSERT INTO `routes` (`route_id`, `route_name`, `source`, `destination`, `distance_km`, `base_fare`) VALUES ('2', 'Tumkur - Nagasandra', 'Tumkur', 'Nagasandra', '45', '80.0');
INSERT INTO `routes` (`route_id`, `route_name`, `source`, `destination`, `distance_km`, `base_fare`) VALUES ('3', 'Tumkur - Doddaballapur', 'Tumkur', 'Doddaballapur', '60', '95.0');
INSERT INTO `routes` (`route_id`, `route_name`, `source`, `destination`, `distance_km`, `base_fare`) VALUES ('4', 'Tumkur - Nelamangala', 'Tumkur', 'Nelamangala', '35', '60.0');
INSERT INTO `routes` (`route_id`, `route_name`, `source`, `destination`, `distance_km`, `base_fare`) VALUES ('5', 'Tumkur - Mysore', 'Tumkur', 'Mysore', '150', '220.0');
INSERT INTO `routes` (`route_id`, `route_name`, `source`, `destination`, `distance_km`, `base_fare`) VALUES ('6', 'Bangalore - Tumkur', 'Bangalore', 'Tumkur', '70', '120.0');
INSERT INTO `routes` (`route_id`, `route_name`, `source`, `destination`, `distance_km`, `base_fare`) VALUES ('7', 'Bangalore - Mysore', 'Bangalore', 'Mysore', '145', '210.0');
INSERT INTO `routes` (`route_id`, `route_name`, `source`, `destination`, `distance_km`, `base_fare`) VALUES ('8', 'Tumkur - Sira', 'Tumkur', 'Sira', '55', '85.0');
INSERT INTO `routes` (`route_id`, `route_name`, `source`, `destination`, `distance_km`, `base_fare`) VALUES ('9', 'Tumkur - Gubbi', 'Tumkur', 'Gubbi', '22', '40.0');
INSERT INTO `routes` (`route_id`, `route_name`, `source`, `destination`, `distance_km`, `base_fare`) VALUES ('10', 'Tumkur - Hassan', 'Tumkur', 'Hassan', '128', '190.0');
INSERT INTO `routes` (`route_id`, `route_name`, `source`, `destination`, `distance_km`, `base_fare`) VALUES ('11', 'Bangalore - Doddaballapur', 'Bangalore', 'Doddaballapur', '40', '70.0');
INSERT INTO `routes` (`route_id`, `route_name`, `source`, `destination`, `distance_km`, `base_fare`) VALUES ('12', 'Tumkur - Tiptur', 'Tumkur', 'Tiptur', '74', '110.0');

DROP TABLE IF EXISTS `schedules`;
CREATE TABLE `schedules` (
  `schedule_id` int(11) NOT NULL AUTO_INCREMENT,
  `bus_id` int(11) NOT NULL,
  `route_id` int(11) NOT NULL,
  `driver_id` int(11) DEFAULT NULL,
  `departure_time` text NOT NULL,
  `arrival_time` text NOT NULL,
  `status` text NOT NULL DEFAULT 'On Time' CHECK (`status` in ('On Time','Delayed','Cancelled','Not Started')),
  `occupancy` text NOT NULL DEFAULT 'Low' CHECK (`occupancy` in ('Low','Medium','High','Full')),
  `delay_minutes` int(11) NOT NULL DEFAULT 0,
  `delay_reason` text DEFAULT NULL,
  `fare` double NOT NULL DEFAULT 120,
  PRIMARY KEY (`schedule_id`),
  KEY `bus_id` (`bus_id`),
  KEY `route_id` (`route_id`),
  KEY `driver_id` (`driver_id`),
  CONSTRAINT `schedules_ibfk_1` FOREIGN KEY (`bus_id`) REFERENCES `buses` (`bus_id`),
  CONSTRAINT `schedules_ibfk_2` FOREIGN KEY (`route_id`) REFERENCES `routes` (`route_id`),
  CONSTRAINT `schedules_ibfk_3` FOREIGN KEY (`driver_id`) REFERENCES `users` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=49 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
INSERT INTO `schedules` (`schedule_id`, `bus_id`, `route_id`, `driver_id`, `departure_time`, `arrival_time`, `status`, `occupancy`, `delay_minutes`, `delay_reason`, `fare`) VALUES ('1', '1', '1', '2', '08:00', '10:00', 'On Time', 'High', '0', NULL, '140.0');
INSERT INTO `schedules` (`schedule_id`, `bus_id`, `route_id`, `driver_id`, `departure_time`, `arrival_time`, `status`, `occupancy`, `delay_minutes`, `delay_reason`, `fare`) VALUES ('2', '2', '2', '4', '09:15', '10:20', 'Delayed', 'Medium', '15', 'Heavy traffic near Dabaspet toll', '85.0');
INSERT INTO `schedules` (`schedule_id`, `bus_id`, `route_id`, `driver_id`, `departure_time`, `arrival_time`, `status`, `occupancy`, `delay_minutes`, `delay_reason`, `fare`) VALUES ('3', '3', '3', '5', '10:30', '11:45', 'On Time', 'Low', '0', NULL, '95.0');
INSERT INTO `schedules` (`schedule_id`, `bus_id`, `route_id`, `driver_id`, `departure_time`, `arrival_time`, `status`, `occupancy`, `delay_minutes`, `delay_reason`, `fare`) VALUES ('4', '4', '4', '6', '11:45', '12:35', 'Cancelled', 'Low', '0', 'Technical maintenance', '60.0');
INSERT INTO `schedules` (`schedule_id`, `bus_id`, `route_id`, `driver_id`, `departure_time`, `arrival_time`, `status`, `occupancy`, `delay_minutes`, `delay_reason`, `fare`) VALUES ('5', '5', '5', '7', '07:30', '10:40', 'On Time', 'High', '0', NULL, '220.0');
INSERT INTO `schedules` (`schedule_id`, `bus_id`, `route_id`, `driver_id`, `departure_time`, `arrival_time`, `status`, `occupancy`, `delay_minutes`, `delay_reason`, `fare`) VALUES ('6', '1', '1', '2', '12:30', '14:30', 'Not Started', 'Low', '0', NULL, '140.0');
INSERT INTO `schedules` (`schedule_id`, `bus_id`, `route_id`, `driver_id`, `departure_time`, `arrival_time`, `status`, `occupancy`, `delay_minutes`, `delay_reason`, `fare`) VALUES ('7', '6', '6', '8', '08:30', '10:30', 'On Time', 'Full', '0', NULL, '160.0');
INSERT INTO `schedules` (`schedule_id`, `bus_id`, `route_id`, `driver_id`, `departure_time`, `arrival_time`, `status`, `occupancy`, `delay_minutes`, `delay_reason`, `fare`) VALUES ('8', '7', '2', '9', '09:45', '10:50', 'On Time', 'Medium', '0', NULL, '85.0');
INSERT INTO `schedules` (`schedule_id`, `bus_id`, `route_id`, `driver_id`, `departure_time`, `arrival_time`, `status`, `occupancy`, `delay_minutes`, `delay_reason`, `fare`) VALUES ('9', '8', '3', '10', '11:15', '12:30', 'Delayed', 'High', '20', 'Rain & slow moving traffic', '95.0');
INSERT INTO `schedules` (`schedule_id`, `bus_id`, `route_id`, `driver_id`, `departure_time`, `arrival_time`, `status`, `occupancy`, `delay_minutes`, `delay_reason`, `fare`) VALUES ('10', '9', '4', '11', '13:00', '13:50', 'On Time', 'Low', '0', NULL, '60.0');
INSERT INTO `schedules` (`schedule_id`, `bus_id`, `route_id`, `driver_id`, `departure_time`, `arrival_time`, `status`, `occupancy`, `delay_minutes`, `delay_reason`, `fare`) VALUES ('11', '10', '5', '12', '14:00', '17:10', 'On Time', 'Medium', '0', NULL, '220.0');
INSERT INTO `schedules` (`schedule_id`, `bus_id`, `route_id`, `driver_id`, `departure_time`, `arrival_time`, `status`, `occupancy`, `delay_minutes`, `delay_reason`, `fare`) VALUES ('12', '11', '1', '13', '15:30', '17:30', 'On Time', 'Full', '0', NULL, '140.0');
INSERT INTO `schedules` (`schedule_id`, `bus_id`, `route_id`, `driver_id`, `departure_time`, `arrival_time`, `status`, `occupancy`, `delay_minutes`, `delay_reason`, `fare`) VALUES ('13', '12', '6', '14', '16:15', '18:15', 'Delayed', 'Medium', '10', 'Signal delay at Yeshwanthpur', '160.0');
INSERT INTO `schedules` (`schedule_id`, `bus_id`, `route_id`, `driver_id`, `departure_time`, `arrival_time`, `status`, `occupancy`, `delay_minutes`, `delay_reason`, `fare`) VALUES ('14', '13', '2', '15', '17:00', '18:05', 'On Time', 'High', '0', NULL, '85.0');
INSERT INTO `schedules` (`schedule_id`, `bus_id`, `route_id`, `driver_id`, `departure_time`, `arrival_time`, `status`, `occupancy`, `delay_minutes`, `delay_reason`, `fare`) VALUES ('15', '14', '3', '16', '18:00', '19:15', 'On Time', 'Medium', '0', NULL, '95.0');
INSERT INTO `schedules` (`schedule_id`, `bus_id`, `route_id`, `driver_id`, `departure_time`, `arrival_time`, `status`, `occupancy`, `delay_minutes`, `delay_reason`, `fare`) VALUES ('16', '15', '7', '17', '06:00', '08:00', 'On Time', 'High', '0', NULL, '150.0');
INSERT INTO `schedules` (`schedule_id`, `bus_id`, `route_id`, `driver_id`, `departure_time`, `arrival_time`, `status`, `occupancy`, `delay_minutes`, `delay_reason`, `fare`) VALUES ('17', '16', '1', '18', '06:45', '08:45', 'On Time', 'Low', '0', NULL, '140.0');
INSERT INTO `schedules` (`schedule_id`, `bus_id`, `route_id`, `driver_id`, `departure_time`, `arrival_time`, `status`, `occupancy`, `delay_minutes`, `delay_reason`, `fare`) VALUES ('18', '17', '2', '19', '07:15', '08:20', 'On Time', 'Medium', '0', NULL, '85.0');
INSERT INTO `schedules` (`schedule_id`, `bus_id`, `route_id`, `driver_id`, `departure_time`, `arrival_time`, `status`, `occupancy`, `delay_minutes`, `delay_reason`, `fare`) VALUES ('19', '18', '5', '2', '08:45', '11:55', 'On Time', 'Full', '0', NULL, '220.0');
INSERT INTO `schedules` (`schedule_id`, `bus_id`, `route_id`, `driver_id`, `departure_time`, `arrival_time`, `status`, `occupancy`, `delay_minutes`, `delay_reason`, `fare`) VALUES ('20', '19', '1', '4', '09:30', '11:30', 'On Time', 'High', '0', NULL, '140.0');
INSERT INTO `schedules` (`schedule_id`, `bus_id`, `route_id`, `driver_id`, `departure_time`, `arrival_time`, `status`, `occupancy`, `delay_minutes`, `delay_reason`, `fare`) VALUES ('21', '20', '2', '5', '10:00', '11:05', 'On Time', 'Medium', '0', NULL, '85.0');
INSERT INTO `schedules` (`schedule_id`, `bus_id`, `route_id`, `driver_id`, `departure_time`, `arrival_time`, `status`, `occupancy`, `delay_minutes`, `delay_reason`, `fare`) VALUES ('22', '21', '3', '6', '10:45', '12:00', 'On Time', 'Low', '0', NULL, '95.0');
INSERT INTO `schedules` (`schedule_id`, `bus_id`, `route_id`, `driver_id`, `departure_time`, `arrival_time`, `status`, `occupancy`, `delay_minutes`, `delay_reason`, `fare`) VALUES ('23', '22', '4', '7', '12:15', '13:05', 'Not Started', 'Low', '0', NULL, '60.0');
INSERT INTO `schedules` (`schedule_id`, `bus_id`, `route_id`, `driver_id`, `departure_time`, `arrival_time`, `status`, `occupancy`, `delay_minutes`, `delay_reason`, `fare`) VALUES ('24', '23', '1', '8', '13:45', '15:45', 'On Time', 'High', '0', NULL, '140.0');
INSERT INTO `schedules` (`schedule_id`, `bus_id`, `route_id`, `driver_id`, `departure_time`, `arrival_time`, `status`, `occupancy`, `delay_minutes`, `delay_reason`, `fare`) VALUES ('25', '24', '6', '9', '14:30', '16:30', 'On Time', 'Medium', '0', NULL, '160.0');
INSERT INTO `schedules` (`schedule_id`, `bus_id`, `route_id`, `driver_id`, `departure_time`, `arrival_time`, `status`, `occupancy`, `delay_minutes`, `delay_reason`, `fare`) VALUES ('26', '25', '2', '10', '15:00', '16:05', 'On Time', 'High', '0', NULL, '85.0');
INSERT INTO `schedules` (`schedule_id`, `bus_id`, `route_id`, `driver_id`, `departure_time`, `arrival_time`, `status`, `occupancy`, `delay_minutes`, `delay_reason`, `fare`) VALUES ('27', '1', '1', '2', '16:30', '18:30', 'On Time', 'Full', '0', NULL, '140.0');
INSERT INTO `schedules` (`schedule_id`, `bus_id`, `route_id`, `driver_id`, `departure_time`, `arrival_time`, `status`, `occupancy`, `delay_minutes`, `delay_reason`, `fare`) VALUES ('28', '2', '2', '11', '17:30', '18:35', 'Delayed', 'Medium', '25', 'Bridge repair near Nelamangala', '85.0');
INSERT INTO `schedules` (`schedule_id`, `bus_id`, `route_id`, `driver_id`, `departure_time`, `arrival_time`, `status`, `occupancy`, `delay_minutes`, `delay_reason`, `fare`) VALUES ('29', '3', '3', '12', '18:30', '19:45', 'On Time', 'Low', '0', NULL, '95.0');
INSERT INTO `schedules` (`schedule_id`, `bus_id`, `route_id`, `driver_id`, `departure_time`, `arrival_time`, `status`, `occupancy`, `delay_minutes`, `delay_reason`, `fare`) VALUES ('30', '5', '4', '13', '19:00', '19:50', 'On Time', 'Medium', '0', NULL, '60.0');
INSERT INTO `schedules` (`schedule_id`, `bus_id`, `route_id`, `driver_id`, `departure_time`, `arrival_time`, `status`, `occupancy`, `delay_minutes`, `delay_reason`, `fare`) VALUES ('31', '6', '5', '14', '19:30', '22:40', 'On Time', 'High', '0', NULL, '220.0');
INSERT INTO `schedules` (`schedule_id`, `bus_id`, `route_id`, `driver_id`, `departure_time`, `arrival_time`, `status`, `occupancy`, `delay_minutes`, `delay_reason`, `fare`) VALUES ('32', '7', '1', '15', '20:15', '22:15', 'Not Started', 'Low', '0', NULL, '140.0');
INSERT INTO `schedules` (`schedule_id`, `bus_id`, `route_id`, `driver_id`, `departure_time`, `arrival_time`, `status`, `occupancy`, `delay_minutes`, `delay_reason`, `fare`) VALUES ('33', '8', '6', '16', '21:00', '23:00', 'On Time', 'Medium', '0', NULL, '160.0');
INSERT INTO `schedules` (`schedule_id`, `bus_id`, `route_id`, `driver_id`, `departure_time`, `arrival_time`, `status`, `occupancy`, `delay_minutes`, `delay_reason`, `fare`) VALUES ('34', '9', '2', '17', '05:30', '06:35', 'On Time', 'Low', '0', NULL, '85.0');
INSERT INTO `schedules` (`schedule_id`, `bus_id`, `route_id`, `driver_id`, `departure_time`, `arrival_time`, `status`, `occupancy`, `delay_minutes`, `delay_reason`, `fare`) VALUES ('35', '10', '3', '18', '06:30', '07:45', 'On Time', 'Medium', '0', NULL, '95.0');
INSERT INTO `schedules` (`schedule_id`, `bus_id`, `route_id`, `driver_id`, `departure_time`, `arrival_time`, `status`, `occupancy`, `delay_minutes`, `delay_reason`, `fare`) VALUES ('36', '11', '4', '19', '07:00', '07:50', 'On Time', 'Low', '0', NULL, '60.0');
INSERT INTO `schedules` (`schedule_id`, `bus_id`, `route_id`, `driver_id`, `departure_time`, `arrival_time`, `status`, `occupancy`, `delay_minutes`, `delay_reason`, `fare`) VALUES ('37', '12', '1', '2', '07:45', '09:45', 'On Time', 'High', '0', NULL, '140.0');
INSERT INTO `schedules` (`schedule_id`, `bus_id`, `route_id`, `driver_id`, `departure_time`, `arrival_time`, `status`, `occupancy`, `delay_minutes`, `delay_reason`, `fare`) VALUES ('38', '13', '6', '4', '08:15', '10:15', 'On Time', 'Full', '0', NULL, '160.0');
INSERT INTO `schedules` (`schedule_id`, `bus_id`, `route_id`, `driver_id`, `departure_time`, `arrival_time`, `status`, `occupancy`, `delay_minutes`, `delay_reason`, `fare`) VALUES ('39', '14', '2', '5', '08:45', '09:50', 'On Time', 'Medium', '0', NULL, '85.0');
INSERT INTO `schedules` (`schedule_id`, `bus_id`, `route_id`, `driver_id`, `departure_time`, `arrival_time`, `status`, `occupancy`, `delay_minutes`, `delay_reason`, `fare`) VALUES ('40', '15', '3', '6', '09:00', '10:15', 'On Time', 'Low', '0', NULL, '95.0');
INSERT INTO `schedules` (`schedule_id`, `bus_id`, `route_id`, `driver_id`, `departure_time`, `arrival_time`, `status`, `occupancy`, `delay_minutes`, `delay_reason`, `fare`) VALUES ('41', '16', '5', '7', '09:30', '12:40', 'On Time', 'High', '0', NULL, '220.0');
INSERT INTO `schedules` (`schedule_id`, `bus_id`, `route_id`, `driver_id`, `departure_time`, `arrival_time`, `status`, `occupancy`, `delay_minutes`, `delay_reason`, `fare`) VALUES ('42', '17', '1', '8', '10:15', '12:15', 'On Time', 'Medium', '0', NULL, '140.0');
INSERT INTO `schedules` (`schedule_id`, `bus_id`, `route_id`, `driver_id`, `departure_time`, `arrival_time`, `status`, `occupancy`, `delay_minutes`, `delay_reason`, `fare`) VALUES ('43', '18', '6', '9', '11:00', '13:00', 'On Time', 'High', '0', NULL, '160.0');
INSERT INTO `schedules` (`schedule_id`, `bus_id`, `route_id`, `driver_id`, `departure_time`, `arrival_time`, `status`, `occupancy`, `delay_minutes`, `delay_reason`, `fare`) VALUES ('44', '19', '2', '10', '11:30', '12:35', 'On Time', 'Low', '0', NULL, '85.0');
INSERT INTO `schedules` (`schedule_id`, `bus_id`, `route_id`, `driver_id`, `departure_time`, `arrival_time`, `status`, `occupancy`, `delay_minutes`, `delay_reason`, `fare`) VALUES ('45', '20', '3', '11', '12:00', '13:15', 'On Time', 'Medium', '0', NULL, '95.0');
INSERT INTO `schedules` (`schedule_id`, `bus_id`, `route_id`, `driver_id`, `departure_time`, `arrival_time`, `status`, `occupancy`, `delay_minutes`, `delay_reason`, `fare`) VALUES ('46', '21', '4', '12', '12:45', '13:35', 'On Time', 'Low', '0', NULL, '60.0');
INSERT INTO `schedules` (`schedule_id`, `bus_id`, `route_id`, `driver_id`, `departure_time`, `arrival_time`, `status`, `occupancy`, `delay_minutes`, `delay_reason`, `fare`) VALUES ('47', '22', '1', '13', '13:15', '15:15', 'On Time', 'High', '0', NULL, '140.0');
INSERT INTO `schedules` (`schedule_id`, `bus_id`, `route_id`, `driver_id`, `departure_time`, `arrival_time`, `status`, `occupancy`, `delay_minutes`, `delay_reason`, `fare`) VALUES ('48', '23', '6', '14', '14:15', '16:15', 'On Time', 'Medium', '0', NULL, '160.0');

DROP TABLE IF EXISTS `stops`;
CREATE TABLE `stops` (
  `stop_id` int(11) NOT NULL AUTO_INCREMENT,
  `route_id` int(11) NOT NULL,
  `stop_name` text NOT NULL,
  `sequence` int(11) NOT NULL,
  `offset_minutes` int(11) NOT NULL,
  `latitude` double DEFAULT NULL,
  `longitude` double DEFAULT NULL,
  PRIMARY KEY (`stop_id`),
  KEY `route_id` (`route_id`),
  CONSTRAINT `stops_ibfk_1` FOREIGN KEY (`route_id`) REFERENCES `routes` (`route_id`) ON DELETE CASCADE
) ENGINE=InnoDB AUTO_INCREMENT=34 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
INSERT INTO `stops` (`stop_id`, `route_id`, `stop_name`, `sequence`, `offset_minutes`, `latitude`, `longitude`) VALUES ('1', '1', 'Tumkur KSRTC Bus Stand', '1', '0', '13.3409', '77.101');
INSERT INTO `stops` (`stop_id`, `route_id`, `stop_name`, `sequence`, `offset_minutes`, `latitude`, `longitude`) VALUES ('2', '1', 'Kyathsandra Toll', '2', '15', '13.3157', '77.1592');
INSERT INTO `stops` (`stop_id`, `route_id`, `stop_name`, `sequence`, `offset_minutes`, `latitude`, `longitude`) VALUES ('3', '1', 'Dabaspet Junction', '3', '35', '13.2298', '77.2417');
INSERT INTO `stops` (`stop_id`, `route_id`, `stop_name`, `sequence`, `offset_minutes`, `latitude`, `longitude`) VALUES ('4', '1', 'Nelamangala Toll Gate', '4', '55', '13.0984', '77.3898');
INSERT INTO `stops` (`stop_id`, `route_id`, `stop_name`, `sequence`, `offset_minutes`, `latitude`, `longitude`) VALUES ('5', '1', 'Nagasandra Metro', '5', '65', '13.0475', '77.4988');
INSERT INTO `stops` (`stop_id`, `route_id`, `stop_name`, `sequence`, `offset_minutes`, `latitude`, `longitude`) VALUES ('6', '1', 'Yeshwanthpur TTMC', '6', '95', '13.0234', '77.5501');
INSERT INTO `stops` (`stop_id`, `route_id`, `stop_name`, `sequence`, `offset_minutes`, `latitude`, `longitude`) VALUES ('7', '1', 'Bangalore Majestic (KBS)', '7', '120', '12.9772', '77.5729');
INSERT INTO `stops` (`stop_id`, `route_id`, `stop_name`, `sequence`, `offset_minutes`, `latitude`, `longitude`) VALUES ('8', '2', 'Tumkur KSRTC Bus Stand', '1', '0', '13.3409', '77.101');
INSERT INTO `stops` (`stop_id`, `route_id`, `stop_name`, `sequence`, `offset_minutes`, `latitude`, `longitude`) VALUES ('9', '2', 'Kyathsandra Toll', '2', '15', '13.3157', '77.1592');
INSERT INTO `stops` (`stop_id`, `route_id`, `stop_name`, `sequence`, `offset_minutes`, `latitude`, `longitude`) VALUES ('10', '2', 'Hirehalli Industrial Area', '3', '25', '13.275', '77.198');
INSERT INTO `stops` (`stop_id`, `route_id`, `stop_name`, `sequence`, `offset_minutes`, `latitude`, `longitude`) VALUES ('11', '2', 'Dabaspet Junction', '4', '38', '13.2298', '77.2417');
INSERT INTO `stops` (`stop_id`, `route_id`, `stop_name`, `sequence`, `offset_minutes`, `latitude`, `longitude`) VALUES ('12', '2', 'Nelamangala Bypass', '5', '55', '13.0984', '77.3898');
INSERT INTO `stops` (`stop_id`, `route_id`, `stop_name`, `sequence`, `offset_minutes`, `latitude`, `longitude`) VALUES ('13', '2', 'Nagasandra Metro Terminal', '6', '65', '13.0475', '77.4988');
INSERT INTO `stops` (`stop_id`, `route_id`, `stop_name`, `sequence`, `offset_minutes`, `latitude`, `longitude`) VALUES ('14', '3', 'Tumkur KSRTC Bus Stand', '1', '0', '13.3409', '77.101');
INSERT INTO `stops` (`stop_id`, `route_id`, `stop_name`, `sequence`, `offset_minutes`, `latitude`, `longitude`) VALUES ('15', '3', 'Urdigere Cross', '2', '20', '13.312', '77.21');
INSERT INTO `stops` (`stop_id`, `route_id`, `stop_name`, `sequence`, `offset_minutes`, `latitude`, `longitude`) VALUES ('16', '3', 'Doddabelavangala', '3', '50', '13.298', '77.412');
INSERT INTO `stops` (`stop_id`, `route_id`, `stop_name`, `sequence`, `offset_minutes`, `latitude`, `longitude`) VALUES ('17', '3', 'Doddaballapur Bus Stand', '4', '75', '13.2925', '77.5432');
INSERT INTO `stops` (`stop_id`, `route_id`, `stop_name`, `sequence`, `offset_minutes`, `latitude`, `longitude`) VALUES ('18', '4', 'Tumkur KSRTC Bus Stand', '1', '0', '13.3409', '77.101');
INSERT INTO `stops` (`stop_id`, `route_id`, `stop_name`, `sequence`, `offset_minutes`, `latitude`, `longitude`) VALUES ('19', '4', 'Kyathsandra', '2', '15', '13.3157', '77.1592');
INSERT INTO `stops` (`stop_id`, `route_id`, `stop_name`, `sequence`, `offset_minutes`, `latitude`, `longitude`) VALUES ('20', '4', 'Dabaspet', '3', '35', '13.2298', '77.2417');
INSERT INTO `stops` (`stop_id`, `route_id`, `stop_name`, `sequence`, `offset_minutes`, `latitude`, `longitude`) VALUES ('21', '4', 'Nelamangala TTMC', '4', '50', '13.0984', '77.3898');
INSERT INTO `stops` (`stop_id`, `route_id`, `stop_name`, `sequence`, `offset_minutes`, `latitude`, `longitude`) VALUES ('22', '5', 'Tumkur Bus Stand', '1', '0', '13.3409', '77.101');
INSERT INTO `stops` (`stop_id`, `route_id`, `stop_name`, `sequence`, `offset_minutes`, `latitude`, `longitude`) VALUES ('23', '5', 'Kunigal Bypass', '2', '40', '13.0245', '77.027');
INSERT INTO `stops` (`stop_id`, `route_id`, `stop_name`, `sequence`, `offset_minutes`, `latitude`, `longitude`) VALUES ('24', '5', 'Maddur Circle', '3', '110', '12.584', '77.045');
INSERT INTO `stops` (`stop_id`, `route_id`, `stop_name`, `sequence`, `offset_minutes`, `latitude`, `longitude`) VALUES ('25', '5', 'Mandya KSRTC Bus Stand', '4', '140', '12.522', '76.898');
INSERT INTO `stops` (`stop_id`, `route_id`, `stop_name`, `sequence`, `offset_minutes`, `latitude`, `longitude`) VALUES ('26', '5', 'Mysore KSRTC Suburb Stand', '5', '190', '12.3118', '76.6529');
INSERT INTO `stops` (`stop_id`, `route_id`, `stop_name`, `sequence`, `offset_minutes`, `latitude`, `longitude`) VALUES ('27', '6', 'Bangalore Majestic (KBS)', '1', '0', '12.9772', '77.5729');
INSERT INTO `stops` (`stop_id`, `route_id`, `stop_name`, `sequence`, `offset_minutes`, `latitude`, `longitude`) VALUES ('28', '6', 'Yeshwanthpur TTMC', '2', '25', '13.0234', '77.5501');
INSERT INTO `stops` (`stop_id`, `route_id`, `stop_name`, `sequence`, `offset_minutes`, `latitude`, `longitude`) VALUES ('29', '6', 'Nagasandra Metro', '3', '45', '13.0475', '77.4988');
INSERT INTO `stops` (`stop_id`, `route_id`, `stop_name`, `sequence`, `offset_minutes`, `latitude`, `longitude`) VALUES ('30', '6', 'Nelamangala Toll Gate', '4', '65', '13.0984', '77.3898');
INSERT INTO `stops` (`stop_id`, `route_id`, `stop_name`, `sequence`, `offset_minutes`, `latitude`, `longitude`) VALUES ('31', '6', 'Dabaspet Junction', '5', '85', '13.2298', '77.2417');
INSERT INTO `stops` (`stop_id`, `route_id`, `stop_name`, `sequence`, `offset_minutes`, `latitude`, `longitude`) VALUES ('32', '6', 'Kyathsandra Toll', '6', '105', '13.3157', '77.1592');
INSERT INTO `stops` (`stop_id`, `route_id`, `stop_name`, `sequence`, `offset_minutes`, `latitude`, `longitude`) VALUES ('33', '6', 'Tumkur KSRTC Bus Stand', '7', '120', '13.3409', '77.101');

DROP TABLE IF EXISTS `users`;
CREATE TABLE `users` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `name` text NOT NULL,
  `email` text NOT NULL,
  `phone` text DEFAULT NULL,
  `password_hash` text NOT NULL,
  `role` text NOT NULL CHECK (`role` in ('admin','driver','passenger')),
  `license_number` text DEFAULT NULL,
  `created_at` timestamp NOT NULL DEFAULT current_timestamp(),
  PRIMARY KEY (`id`),
  UNIQUE KEY `email` (`email`) USING HASH
) ENGINE=InnoDB AUTO_INCREMENT=22 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
INSERT INTO `users` (`id`, `name`, `email`, `phone`, `password_hash`, `role`, `license_number`, `created_at`) VALUES ('1', 'Admin In-Charge', 'admin@busflow.com', '9845012345', 'scrypt:32768:8:1$kreuoQQ52os4nlNJ$87f724056bd4e13b4f5c3620898327e151afba385f73761ffffd6b45867ba09b2be0f39b615b7d861519e5f45c5e84c1b5649abf873eebf8736225447c5559b8', 'admin', NULL, '2026-09-19 23:28:36');
INSERT INTO `users` (`id`, `name`, `email`, `phone`, `password_hash`, `role`, `license_number`, `created_at`) VALUES ('2', 'Ravi Kumar', 'driver@busflow.com', '9876543210', 'scrypt:32768:8:1$Hdu9xk3exJEvqtC1$285170178ddd0001a09f66454fd83d03becb919b26e4e6da003a07627c8e7a7100cfb83dfdb6f13a104af7de4252bb28dce89f1580f787eea0f626dd6f90d66a', 'driver', 'KA-123456', '2026-09-19 23:28:36');
INSERT INTO `users` (`id`, `name`, `email`, `phone`, `password_hash`, `role`, `license_number`, `created_at`) VALUES ('3', 'Skanda Bharadwaj', 'passenger@busflow.com', '9123456780', 'scrypt:32768:8:1$w341O3pSmf5yv9Cn$f7aaaff23b2aaa074286d07c85c5a3d64cf9bd16116158644c1a054ba4417ade9fca6f0189083b439a10314fddee9239ac4a00b8a2fa6fce9671042b0bc520ea', 'passenger', NULL, '2026-09-19 23:28:36');
INSERT INTO `users` (`id`, `name`, `email`, `phone`, `password_hash`, `role`, `license_number`, `created_at`) VALUES ('4', 'Manjunath Gowda', 'manju@busflow.com', '9880112233', 'scrypt:32768:8:1$LS8iXIaW4VJRNE8f$bcd60ce4ad2c55a213e4bd73db428ae0ee38d6453adb8360bd1305062abc1290f4bbc3342e254ea4caa14625f4b3ec53b10b1678af036af92ec6e487ba07dcc0', 'driver', 'KA-234567', '2026-09-19 23:28:36');
INSERT INTO `users` (`id`, `name`, `email`, `phone`, `password_hash`, `role`, `license_number`, `created_at`) VALUES ('5', 'Suresh Nayak', 'suresh@busflow.com', '9880223344', 'scrypt:32768:8:1$zjkVPwhPZnu8oHgQ$1d628e30e1f6c254bfd64c19377c4e6a496ff50ca518a7d4cbb027f07646cfb71948a193820e661d857c40d61bb377a18cd8301a2482c26226d875e9c869f409', 'driver', 'KA-345678', '2026-09-19 23:28:36');
INSERT INTO `users` (`id`, `name`, `email`, `phone`, `password_hash`, `role`, `license_number`, `created_at`) VALUES ('6', 'Venkatesh Rao', 'venky@busflow.com', '9880334455', 'scrypt:32768:8:1$uCkBrBOg9bFitN7c$e828a1ba76db42955b3fa5e175c04098a3f47912763776a5342f055761f9fb66f8e258150fc5f1db33df0db38b04db9196de31c4f4280e57ef1d82b0476c9f35', 'driver', 'KA-456789', '2026-09-19 23:28:36');
INSERT INTO `users` (`id`, `name`, `email`, `phone`, `password_hash`, `role`, `license_number`, `created_at`) VALUES ('7', 'Anand Swamy', 'anand@busflow.com', '9880445566', 'scrypt:32768:8:1$EU1ljR8GpWEbVMmx$16b12e6156e4a41c59e7418b312e28efafff591e719e016c7cd1e7d76571b2349fafc566e050f4a6467e13b7cf419d2b3e6000e5a2cf88d383159d8a47e868d5', 'driver', 'KA-567890', '2026-09-19 23:28:36');
INSERT INTO `users` (`id`, `name`, `email`, `phone`, `password_hash`, `role`, `license_number`, `created_at`) VALUES ('8', 'Praveen Kumar', 'praveen@busflow.com', '9880556677', 'scrypt:32768:8:1$DENPpG6vmSSLTd6V$7da92713593412b31481977b391deb554831c67b42ff93989045938ccb9fc81c4fb994404929636ab978bb69d441d9170f265109573b5dcc9e14d478fac3e4c6', 'driver', 'KA-678901', '2026-09-19 23:28:36');
INSERT INTO `users` (`id`, `name`, `email`, `phone`, `password_hash`, `role`, `license_number`, `created_at`) VALUES ('9', 'Basavaraj Patil', 'basava@busflow.com', '9880667788', 'scrypt:32768:8:1$qX7MIuKqhobgzbM1$c73482e2f6462f0b87a796d1f6cd9d8ae4dd93aca4c009c9800f4894ac30bf90322af52b177278cbb4bd27bf86b4b0f19f3d6218b65461bb68f40c022b473444', 'driver', 'KA-789012', '2026-09-19 23:28:36');
INSERT INTO `users` (`id`, `name`, `email`, `phone`, `password_hash`, `role`, `license_number`, `created_at`) VALUES ('10', 'Raghavendra Bhat', 'raghu@busflow.com', '9880778899', 'scrypt:32768:8:1$oD7BjANxJ7lPiHiD$da23735d641a7ccbdcb0d4e90afd66f76f22b6e4c552dfd9b99930d5c8e7cef74e9682dd54567e8044de6e0ab740bf3e1612773900316486efc525529d4f21d6', 'driver', 'KA-890123', '2026-09-19 23:28:36');
INSERT INTO `users` (`id`, `name`, `email`, `phone`, `password_hash`, `role`, `license_number`, `created_at`) VALUES ('11', 'Channappa M', 'channa@busflow.com', '9880889900', 'scrypt:32768:8:1$o971F21mqnkCoptD$e2e6481bca6653b48e6cd0b070de255ba1d71d6b31817939f485c78a29cd1025da037d371a6dce1fd83c13a3447205633345523317951e35a2eb657ae9212588', 'driver', 'KA-901234', '2026-09-19 23:28:36');
INSERT INTO `users` (`id`, `name`, `email`, `phone`, `password_hash`, `role`, `license_number`, `created_at`) VALUES ('12', 'Girish Shetty', 'girish@busflow.com', '9880990011', 'scrypt:32768:8:1$LpcogprQGxrSVwKj$65b06de7a96f06ab84ca9e4af705943e289c911d7bfca4e117e97d93f26471e191be8f5cafe61eb66f20db76a81c6ba528e947cc7f1c176ffd259bc141f8559a', 'driver', 'KA-012345', '2026-09-19 23:28:36');
INSERT INTO `users` (`id`, `name`, `email`, `phone`, `password_hash`, `role`, `license_number`, `created_at`) VALUES ('13', 'Shashidhar K', 'shashi@busflow.com', '9881001122', 'scrypt:32768:8:1$ltohfRZUPZtsqmjl$37327dbc305eb8d3856612a620a2343cbc291e6698ed779b6c39e23302ac15f74ba0785ede084fcefa3a7a517a22779e4cea295fa5610088e792ad104967e7ae', 'driver', 'KA-112233', '2026-09-19 23:28:36');
INSERT INTO `users` (`id`, `name`, `email`, `phone`, `password_hash`, `role`, `license_number`, `created_at`) VALUES ('14', 'Kiran Prasad', 'kiran@busflow.com', '9881112233', 'scrypt:32768:8:1$lj4SCLJpGBAIrf3r$8ff21a3712dea4058d667c3b1e79e711417f91a4f76b02eec39bfe05302bd21f4a2f5e4fd10ff205bf94dc0cfce8fdd826855377f8da31350c36940616548a8a', 'driver', 'KA-223344', '2026-09-19 23:28:36');
INSERT INTO `users` (`id`, `name`, `email`, `phone`, `password_hash`, `role`, `license_number`, `created_at`) VALUES ('15', 'Mahesh Hegde', 'mahesh@busflow.com', '9881223344', 'scrypt:32768:8:1$KVXg68jy1JJObGds$f9671ad75c7fd1929362a7548b3a14373bf741be42bda5b74a3a892ccc75bc7bde034621e52f771677253ed2f7b63e5030b2868ca357a44f8a4d87ac87d74dad', 'driver', 'KA-334455', '2026-09-19 23:28:36');
INSERT INTO `users` (`id`, `name`, `email`, `phone`, `password_hash`, `role`, `license_number`, `created_at`) VALUES ('16', 'Nagaraj Reddy', 'nagaraj@busflow.com', '9881334455', 'scrypt:32768:8:1$ggwEDRDIFAHVT2Zw$6c7b52ef881395b3ec07b3735504c6660befd2e82dc6663a75d981548a956f5f57e1f9f236821eff57addaf63b89e7c6695defeac3b9c802a6b366eea6844303', 'driver', 'KA-445566', '2026-09-19 23:28:36');
INSERT INTO `users` (`id`, `name`, `email`, `phone`, `password_hash`, `role`, `license_number`, `created_at`) VALUES ('17', 'Shivakumar B', 'shiva@busflow.com', '9881445566', 'scrypt:32768:8:1$VVEjICZqEvS5irxa$263f62bdaeb0a2eb8226770083f0b584828db752c62d2117b2abe21c5a8d5db14becadc52bf74e8725fd7615c6a00f4e03940936ac84689f2f96d4f7e83d924b', 'driver', 'KA-556677', '2026-09-19 23:28:36');
INSERT INTO `users` (`id`, `name`, `email`, `phone`, `password_hash`, `role`, `license_number`, `created_at`) VALUES ('18', 'Ramesh Chandra', 'ramesh@busflow.com', '9881556677', 'scrypt:32768:8:1$7llZUTRepiJn2jet$0148680079644f8b88c93fadf03af8e0ba290a5ac90177ed3fa1cad0dcdd2906aa66099ec2d33cc8bebffb4c86d42595bda6c3e4f54f3951b4f49db2699a84c1', 'driver', 'KA-667788', '2026-09-19 23:28:36');
INSERT INTO `users` (`id`, `name`, `email`, `phone`, `password_hash`, `role`, `license_number`, `created_at`) VALUES ('19', 'Vijay Kumar', 'vijay@busflow.com', '9881667788', 'scrypt:32768:8:1$kADrm0RKjRlxan4l$78353665bc2ff205661481d18bb2ae447095f464b4acae132b697e9ec32c20dee865cc48f0d2943736782287d61805933c468ab9b067d2a010fd2423f51b9cb2', 'driver', 'KA-778899', '2026-09-19 23:28:36');
INSERT INTO `users` (`id`, `name`, `email`, `phone`, `password_hash`, `role`, `license_number`, `created_at`) VALUES ('20', 'Ananya Sharma', 'ananya@example.com', '9900112233', 'scrypt:32768:8:1$2zYqEkTkLvLt6qMP$b952d401c475d2e9dd4adb40b6e39502217031430d280031ad89a03afb46724a0b87a5afc06f36ae336191e8303bae2dc7c85f1ba598182609f1293bb9c16cee', 'passenger', NULL, '2026-09-19 23:28:36');
INSERT INTO `users` (`id`, `name`, `email`, `phone`, `password_hash`, `role`, `license_number`, `created_at`) VALUES ('21', 'Karthik Varma', 'karthik@example.com', '9900223344', 'scrypt:32768:8:1$YnHrYIjvKc6HVba7$4857c0c4d2c70ea39349f2d63d2d5fc2ad5e9152c913edf3fa67f86a7230b83f778ce132fd8be70c90cee72f814ca1febfaa67843821b4b30f22ba8794d60140', 'passenger', NULL, '2026-09-19 23:28:36');

SET FOREIGN_KEY_CHECKS=1;
