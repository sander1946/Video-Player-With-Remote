DROP TABLE IF EXISTS videos;

CREATE TABLE ip_data (
    id      INTEGER    NOT NULL    PRIMARY KEY AUTOINCREMENT,
    code    INTEGER    NOT NULL,
    naam    TEXT,
    vid     TEXT       UNSIGNED    DEFAULT "no video",
    img     TEXT       UNSIGNED    DEFAULT "no image"
);