DROP TABLE IF EXISTS ip_data;
DROP TABLE IF EXISTS url_data;
DROP TABLE IF EXISTS mail_data;

CREATE TABLE ip_data (
    id              INTEGER     NOT NULL PRIMARY KEY AUTOINCREMENT,
    url_id          TEXT,
    mail_id         TEXT,
    track_date      TIMESTAMP   NOT NULL DEFAULT CURRENT_TIMESTAMP,
    ip              INTEGER     UNSIGNED DEFAULT "0.0.0.0",
    hostname        INTEGER     UNSIGNED DEFAULT "0.0.0.0",
    referrer        TEXT        UNSIGNED,
    user_agent      TEXT        UNSIGNED
);

CREATE TABLE url_data (
    id              INTEGER     NOT NULL PRIMARY KEY AUTOINCREMENT,
    url_id          TEXT        NOT NULL,
    created         TIMESTAMP   NOT NULL DEFAULT CURRENT_TIMESTAMP,
    last_click_date TIMESTAMP   NOT NULL DEFAULT CURRENT_TIMESTAMP,
    original_url    TEXT        UNSIGNED,
    clicks          INTEGER     NOT NULL DEFAULT 0
);

CREATE TABLE mail_data (
    id              INTEGER     NOT NULL PRIMARY KEY AUTOINCREMENT,
    mail_id         TEXT        NOT NULL,
    created         TIMESTAMP   NOT NULL DEFAULT CURRENT_TIMESTAMP,
    last_open_date  TIMESTAMP   NOT NULL DEFAULT CURRENT_TIMESTAMP,
    times_opened    INTEGER     NOT NULL DEFAULT 0,
    mail_address    TEXT        UNSIGNED
);

CREATE TABLE Login_data (
    id              INTEGER     NOT NULL PRIMARY KEY AUTOINCREMENT,
    name            TEXT        NOT NULL,
    email           TEXT         NOT NULL,
    password        TEXT         NOT NULL,
    creation_date   TIMESTAMP   NOT NULL DEFAULT CURRENT_TIMESTAMP
);