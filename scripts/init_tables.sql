CREATE DATABASE IF NOT EXISTS fly;
USE fly;

CREATE TABLE IF NOT EXISTS users (
    id         int AUTO_INCREMENT,
    username   varchar(255) UNIQUE,
    LastName   text,
    FirstName  text,
    Roles      json DEFAULT NULL,
    sis        text,
    is_active  bool DEFAULT 1,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    update_at  TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    data       json DEFAULT NULL,
    PRIMARY KEY (id)
);

INSERT IGNORE INTO users
    SET id=1001, username="kic", LastName="kic", FirstName="admin",
        is_active=1, Roles='["admin","owner"]', sis='Zmx5MTIz';

CREATE TABLE IF NOT EXISTS gen (
    id         int AUTO_INCREMENT,
    key1       varchar(255),
    val1       varchar(255),
    is_active  bool DEFAULT 1,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    update_at  TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    data       json DEFAULT NULL,
    PRIMARY KEY (id)
);

CREATE TABLE IF NOT EXISTS ses (
    id         varchar(255) UNIQUE,
    user_id    int,
    is_active  bool DEFAULT 1,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    update_at  TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    data       json DEFAULT NULL,
    PRIMARY KEY (id)
);

INSERT IGNORE INTO gen SET id=31, key1="pages", val1=0, data='{"dashboard":{"name":"Dashboard","icon":"dashboard","roles":[],"order":1},"users":{"name":"Users","icon":"users","roles":["admin","owner"],"order":2},"sys_admin":{"name":"Admin","icon":"settings","roles":["admin","owner"],"order":3},"sys_plugins":{"name":"Plugins","icon":"plug","roles":["admin","owner"],"order":4}}';

CREATE USER IF NOT EXISTS 'fly'@'%' IDENTIFIED BY '1964';
GRANT ALL PRIVILEGES ON *.* TO 'fly'@'%' WITH GRANT OPTION;
FLUSH PRIVILEGES;




CREATE TABLE IF NOT EXISTS plugins (
    id         int AUTO_INCREMENT, 
    plugin_code text,
    is_active  bool DEFAULT 1,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    update_at  TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    data       json DEFAULT NULL,
    PRIMARY KEY (id)
);




