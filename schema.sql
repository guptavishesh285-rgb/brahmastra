-- SurakshaYatra — MySQL schema
-- Run this once against your MySQL database before starting the app
-- in MySQL mode (i.e. once MYSQL_HOST etc. are set).
--
-- Example:
--   mysql -h <host> -u <user> -p <db_name> < schema.sql

CREATE TABLE IF NOT EXISTS locations (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(100) UNIQUE NOT NULL,
    safety_score INT NOT NULL,
    hygiene_index INT NOT NULL,
    route_title VARCHAR(255),
    route_meta VARCHAR(255),
    safety_note VARCHAR(255)
) ENGINE=InnoDB;

CREATE TABLE IF NOT EXISTS guides (
    id INT AUTO_INCREMENT PRIMARY KEY,
    location_id INT NOT NULL,
    name VARCHAR(150) NOT NULL,
    specialty VARCHAR(150),
    rating DECIMAL(2,1),
    price_per_tour INT,
    verified TINYINT(1) DEFAULT 1,
    govt_id_ref VARCHAR(50),
    FOREIGN KEY (location_id) REFERENCES locations(id)
) ENGINE=InnoDB;

CREATE TABLE IF NOT EXISTS emergency_contacts (
    id INT AUTO_INCREMENT PRIMARY KEY,
    location_id INT NOT NULL,
    authority_name VARCHAR(150),
    whatsapp_number VARCHAR(20),
    phone_number VARCHAR(20),
    FOREIGN KEY (location_id) REFERENCES locations(id)
) ENGINE=InnoDB;

CREATE TABLE IF NOT EXISTS sos_logs (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id VARCHAR(100),
    latitude DOUBLE,
    longitude DOUBLE,
    emergency_type VARCHAR(50),
    channel VARCHAR(20),
    status VARCHAR(20),
    created_at DATETIME
) ENGINE=InnoDB;

-- Seed data (same as the SQLite mock, so behavior is identical)

INSERT INTO locations (name, safety_score, hygiene_index, route_title, route_meta, safety_note) VALUES
('Delhi', 92, 88, 'Red Fort → Chandni Chowk', '1.8 km • 24 min • Well-lit • High footfall', 'Excellent for travel'),
('Jaipur', 89, 90, 'Hawa Mahal → Johari Bazaar', '1.2 km • 16 min • Well-lit • High footfall', 'Very safe, minor crowding at markets'),
('Goa', 84, 79, "Baga Beach → Tito's Lane", '2.4 km • 30 min • Moderately lit • Busy at night', 'Generally safe, avoid isolated beach stretches after dark');

INSERT INTO guides (location_id, name, specialty, rating, price_per_tour, verified, govt_id_ref) VALUES
((SELECT id FROM locations WHERE name='Delhi'), 'Arjun Mehta', 'Heritage & Street Food', 4.9, 600, 1, 'GOVID-DL-1042'),
((SELECT id FROM locations WHERE name='Delhi'), 'Meera Sharma', 'Culture & Local Life', 4.8, 750, 1, 'GOVID-DL-1178'),
((SELECT id FROM locations WHERE name='Delhi'), 'Rohan Khan', 'Markets & Night Walks', 4.9, 500, 1, 'GOVID-DL-1290'),
((SELECT id FROM locations WHERE name='Jaipur'), 'Priya Rathore', 'Forts & Heritage', 4.9, 550, 1, 'GOVID-RJ-2041'),
((SELECT id FROM locations WHERE name='Jaipur'), 'Vikram Singh', 'Markets & Handicrafts', 4.7, 480, 1, 'GOVID-RJ-2077'),
((SELECT id FROM locations WHERE name='Goa'), "Leah D'Souza", 'Beaches & Nightlife', 4.8, 700, 1, 'GOVID-GA-3011'),
((SELECT id FROM locations WHERE name='Goa'), 'Aditya Naik', 'Water Sports & Food', 4.6, 620, 1, 'GOVID-GA-3055');

INSERT INTO emergency_contacts (location_id, authority_name, whatsapp_number, phone_number) VALUES
((SELECT id FROM locations WHERE name='Delhi'), 'Delhi Police Tourist Cell', '+919999900001', '+911123456780'),
((SELECT id FROM locations WHERE name='Jaipur'), 'Jaipur Tourist Police', '+919999900002', '+911412345680'),
((SELECT id FROM locations WHERE name='Goa'), 'Goa Tourist Police', '+919999900003', '+918322345680');
