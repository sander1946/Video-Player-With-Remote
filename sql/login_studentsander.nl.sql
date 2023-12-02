DROP TABLE if EXISTS login_data;

CREATE TABLE login_data (
     id              INTEGER     NOT NULL PRIMARY KEY auto_increment,
     name            TEXT        NOT NULL,
     email           TEXT        NOT NULL,
     password        TEXT        NOT NULL,
     creation_date   TIMESTAMP   NOT NULL DEFAULT CURRENT_TIMESTAMP 
     );