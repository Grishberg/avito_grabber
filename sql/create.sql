CREATE DATABASE apart
  DEFAULT CHARACTER SET utf8
  DEFAULT COLLATE utf8_general_ci;

USE apart;

-- Table: apartments
CREATE TABLE apartments (
    id int NOT NULL AUTO_INCREMENT,
    url varchar(255) NOT NULL UNIQUE,
    photo varchar(255),
    title varchar(255) NOT NULL,
    address varchar(255) NOT NULL,
    metro varchar(64) NOT NULL,
    metro_distance varchar(64) NOT NULL,
    price int NOT NULL,
    fee int NOT NULL,
    pos_l float,
    pos_w float,
    date TIMESTAMP NOT NULL,
    CONSTRAINT apartments_pk PRIMARY KEY (id)
) COMMENT 'Список объявлений';

-- Table: user
CREATE TABLE users (
    id int NOT NULL AUTO_INCREMENT,
    name varchar(255) NOT NULL UNIQUE,
    password varchar(64) NOT NULL,
    token varchar(64) NOT NULL,
    timestamp TIMESTAMP NOT NULL,
    CONSTRAINT user_pk PRIMARY KEY (id)
) COMMENT 'Список пользователей';

INSERT INTO users (name, password, token) VALUES ('admin', '', '');

-- Table: circuits
CREATE TABLE circuits (
    id int NOT NULL AUTO_INCREMENT,
    user_id int,
    CONSTRAINT circuits_pk PRIMARY KEY (id)
) COMMENT 'Список районов для поиска';

-- Table: circuits_points
CREATE TABLE points (
    id int NOT NULL AUTO_INCREMENT,
    circuits_id int NOT NULL,
    pos_l float NOT NULL,
    pos_w float NOT NULL,
    CONSTRAINT points_pk PRIMARY KEY (id)
) COMMENT 'Список пользователей';


-- foreign keys
ALTER TABLE circuits ADD CONSTRAINT circuits_user FOREIGN KEY circuits_user (user_id)
    REFERENCES users (id);

ALTER TABLE points ADD CONSTRAINT points_circuit FOREIGN KEY points_circuit (circuits_id)
    REFERENCES circuits (id);