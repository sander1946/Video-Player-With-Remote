DROP TABLE if EXISTS url_data;
DROP TABLE if EXISTS mail_data;
DROP TABLE if EXISTS ip_data;

CREATE TABLE url_data (
     id              integer     NOT NULL PRIMARY KEY auto_increment,
     url_id          text        NOT NULL,
     created         timestamp   NOT NULL DEFAULT CURRENT_TIMESTAMP,
     made_by 		 text		 NOT NULL,
     original_url    text        DEFAULT NULL,
     clicks          integer     NOT NULL DEFAULT 0 
     );
     
CREATE TABLE mail_data (
     id              integer     NOT NULL PRIMARY KEY auto_increment,
     mail_id         text        NOT NULL,
     created         timestamp   NOT NULL DEFAULT CURRENT_TIMESTAMP,
     made_by 		 text		 NOT NULL,
     times_opened    integer     NOT NULL DEFAULT 0,
     mail_address    text  		 DEFAULT NULL 
     );

CREATE TABLE ip_data (
     id              integer 	NOT NULL 	PRIMARY KEY auto_increment,
     url_id          text 		DEFAULT 	NULL,
     mail_id         text 		DEFAULT 	NULL,
     track_date      timestamp 	NOT NULL 	DEFAULT 	CURRENT_TIMESTAMP ,
     made_by 		 integer	NOT NULL,
     ip              char(20) 	DEFAULT 	'0.0.0.0',
     hostname        char(20) 	DEFAULT 	'0.0.0.0',
     referrer        text 		DEFAULT 	NULL,
     user_agent      text 		DEFAULT 	NULL 
     );
