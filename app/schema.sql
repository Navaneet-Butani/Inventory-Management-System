DROP TABLE IF EXISTS records;

CREATE TABLE records (
    id INTEGER NOT NULL AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(100),
    category VARCHAR(100),
    expiry_time DATETIME,
    quantity INTEGER,
    manufacturing_time DATETIME,
    uploaded_image_name VARCHAR(200)
);
