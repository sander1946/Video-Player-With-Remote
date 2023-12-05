DROP TABLE IF EXISTS videos;

CREATE TABLE videos (
    id        INTEGER NOT NULL PRIMARY KEY AUTO_INCREMENT,
    code      INTEGER NOT NULL,
    naam      TEXT,
    img       TEXT  DEFAULT "no image",
	vid       TEXT DEFAULT "no video",
    start     INTEGER DEFAULT  2,
    duration  INTEGER DEFAULT  -1
    );