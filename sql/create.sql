-- Table: apartments
CREATE TABLE apartments (
    id int NOT NULL AUTO_INCREMENT,
    url varchar(255) NOT NULL UNIQUE,
    title varchar(64) NOT NULL,
    address varchar(64) NOT NULL,
    metro varchar(64) NOT NULL,
    metro_distance varchar(64) NOT NULL,
    price int NOT NULL,
    fee int NOT NULL,
    pos_l float NOT NULL,
    pos_w float NOT NULL,
    date TIMESTAMP NOT NULL,
    CONSTRAINT apartments_pk PRIMARY KEY (id)
) COMMENT 'Список объявлений';

-- Table: user
CREATE TABLE users (
    id int NOT NULL AUTO_INCREMENT,
    ean varchar(255) NOT NULL,
    name varchar(255) NOT NULL UNIQUE,
    password varchar(64) NOT NULL,
    token varchar(64) NOT NULL,
    timestamp TIMESTAMP NOT NULL,
    CONSTRAINT user_pk PRIMARY KEY (id)
) COMMENT 'Список пользователей';
