DROP TABLE IF EXISTS videos;

CREATE TABLE videos (
    id        INTEGER NOT NULL PRIMARY KEY,
    code      INTEGER NOT NULL,
    naam      TEXT,
    vid       TEXT DEFAULT "no video",
    img       TEXT  DEFAULT "no image",
    start     INTEGER DEFAULT  0,
    duration  INTEGER DEFAULT  -1
    );