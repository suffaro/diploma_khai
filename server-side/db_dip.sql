
-- create database diploma_khai;
use diploma_khai;
SET FOREIGN_KEY_CHECKS=0;

-- Create Users table
CREATE TABLE Users (
    username VARCHAR(50) PRIMARY KEY,
    password VARCHAR(256)
);

-- Create Payment table
CREATE TABLE Payments (
    paymentID INT PRIMARY KEY,
    username VARCHAR(50),
    paymentDate DATE,
    promotion_id INT,
    FOREIGN KEY (username) REFERENCES Users(username),
    FOREIGN KEY (promotion_id) REFERENCES Promotions(promotion_id)
);

INSERT INTO Payments (paymentID, username, paymentDate, promotion_id) 
VALUES 
    (1, 'roflix@gmail.com', '2024-05-01', 5);

-- Create Subscriptions table
CREATE TABLE Subscribers(
    username VARCHAR(50) PRIMARY KEY,
    end_date DATE,
    FOREIGN KEY (username) REFERENCES Users(username)
);


CREATE TABLE Credits(
	username VARCHAR(50) PRIMARY KEY,
	credits INT DEFAULT 5,
    FOREIGN KEY (username) REFERENCES Users(username)
);


-- Create Requests table
CREATE TABLE Requests ( 
    requestID INT AUTO_INCREMENT PRIMARY KEY,
    username VARCHAR(50),
    requestText TEXT,
    FOREIGN KEY (username) REFERENCES Users(username)
);


CREATE TABLE auth_tokens (
    id INT AUTO_INCREMENT PRIMARY KEY,
    token VARCHAR(255) NOT NULL,
    start_date DATE NOT NULL,
    end_date DATE NOT NULL,
    username VARCHAR(50),
    FOREIGN KEY (username) REFERENCES Users(username)
);

CREATE TABLE confirmation_codes (
    id INT AUTO_INCREMENT PRIMARY KEY,
    username VARCHAR(50),
    code varchar(6) NOT NULL,
    expiration_date DATETIME NOT NULL,
    UNIQUE KEY unique_code (code)
);

CREATE TABLE promotions (
    promotion_id INT AUTO_INCREMENT PRIMARY KEY,
    subscription_length ENUM('1 month', '3 months', '6 months', '12 months') NOT NULL,
    cost DECIMAL(10, 2) NOT NULL,
    description TEXT,
    subscription_length_ua ENUM('1 місяць', '3 місяці', '6 місяців', '12 місяців') NOT NULL,
    description_ua TEXT
);

   

INSERT INTO promotions (subscription_length, cost, description, subscription_length_ua, description_ua)
VALUES 
('1 month', 10.00, 'Basic subscription for 1 month', '1 місяць', 'Базова підписка на 1 місяць'),
('3 months', 25.00, 'Standard subscription for 3 months', '3 місяці', 'Стандартна підписка на 3 місяці'),
('6 months', 45.00, 'Premium subscription for 6 months with discount', '6 місяців', 'Преміум підписка на 6 місяців зі знижкою');
INSERT INTO promotions (subscription_length, cost, description, subscription_length_ua, description_ua)
VALUES ('12 months', 85.00, 'Premium subscription for 12 months with discount', '12 місяців', 'Преміум підписка на 12 місяців зі знижкою');


CREATE TABLE models (
	model_name VARCHAR(50),
    description TEXT,
    premium Boolean
);

-- Insert data with descriptions into the models table
INSERT INTO models (model_name, description, premium) 
VALUES 
    ('ViT-L-14/openai', 'Vision Transformer (ViT) model trained on the openAI dataset, optimized for various vision tasks including image classification, object detection, and segmentation.', FALSE),
    ('ViT-H-14/laion2b_s32b_b79k', 'High-capacity Vision Transformer (ViT) model trained on the laion2b dataset, designed for complex visual tasks requiring fine-grained feature extraction and understanding.', FALSE),
    ('ViT-g-14/laion2b_s34b_b88k', 'General-purpose Vision Transformer (ViT) model trained on the laion2b dataset, suitable for a wide range of computer vision tasks with moderate computational requirements.', FALSE),
    ('EVA02-L-14/merged2b_s4b_b131k', 'Large-scale Vision Transformer (ViT) model with merged data from various sources and high batch size, ideal for handling extensive datasets and achieving state-of-the-art performance in vision tasks.', TRUE),
    ('ViT-L-14/datacomp_xl_s13b_b90k', 'Vision Transformer (ViT) model trained on the datacomp_xl dataset with a large batch size, tailored for handling extremely large-scale datasets and achieving superior performance in vision applications.', TRUE);


DELIMITER $$

CREATE EVENT delete_expired_hashes
ON SCHEDULE
    EVERY 1 DAY
COMMENT 'Delete expired hash records from the hash_dates table'
DO
BEGIN
    DELETE FROM auth_tokens
    WHERE CURRENT_DATE() NOT BETWEEN start_date AND end_date;
END$$

DELIMITER $$

DELIMITER ;

CREATE EVENT delete_expired_codes
ON SCHEDULE EVERY 1 MINUTE
DO
  DELETE FROM confirmation_codes WHERE expiration_date < NOW();
  

SET GLOBAL event_scheduler = ON;


DELIMITER ;
