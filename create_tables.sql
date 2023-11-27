CREATE TYPE roleenum AS ENUM ('deactivated', 'user', 'moderator', 'administrator');
CREATE TABLE "user" (
        id SERIAL NOT NULL,
        name VARCHAR NOT NULL,
        password VARCHAR NOT NULL,
        role roleenum NOT NULL,
        PRIMARY KEY (id),
        UNIQUE (name)
);


CREATE TABLE place (
        id SERIAL NOT NULL,
        name VARCHAR NOT NULL,
        address VARCHAR NOT NULL,
        description VARCHAR,
        approved BOOLEAN NOT NULL,
        PRIMARY KEY (id),
        UNIQUE (address)
);


CREATE TABLE category (
        id SERIAL NOT NULL,
        name VARCHAR,
        description VARCHAR,
        approved BOOLEAN NOT NULL,
        parent_id INTEGER,
        PRIMARY KEY (id),
        UNIQUE (name),
        FOREIGN KEY(parent_id) REFERENCES category (id)
);


CREATE TABLE admission (
        id SERIAL NOT NULL,
        name VARCHAR,
        amount INTEGER NOT NULL,
        PRIMARY KEY (id)
);


CREATE TABLE event (
        id SERIAL NOT NULL,
        name VARCHAR NOT NULL,
        start_datetime TIMESTAMP WITHOUT TIME ZONE,
        end_datetime TIMESTAMP WITHOUT TIME ZONE,
        capacity INTEGER,
        description VARCHAR,
        image VARCHAR,
        approved BOOLEAN,
        owner_id INTEGER NOT NULL,
        place_id INTEGER NOT NULL,
        PRIMARY KEY (id),
        UNIQUE (name),
        FOREIGN KEY(owner_id) REFERENCES "user" (id),
        FOREIGN KEY(place_id) REFERENCES place (id)
);


CREATE TABLE event_category (
        event_id INTEGER NOT NULL,
        category_id INTEGER NOT NULL,
        PRIMARY KEY (event_id, category_id),
        FOREIGN KEY(event_id) REFERENCES event (id),
        FOREIGN KEY(category_id) REFERENCES category (id)
);


CREATE TABLE event_admission (
        event_id INTEGER NOT NULL,
        admission_id INTEGER NOT NULL,
        PRIMARY KEY (event_id, admission_id),
        FOREIGN KEY(event_id) REFERENCES event (id),
        FOREIGN KEY(admission_id) REFERENCES admission (id)
);


CREATE TABLE event_user (
        event_id INTEGER NOT NULL,
        user_id INTEGER NOT NULL,
        admission INTEGER,
        approved BOOLEAN NOT NULL,
        PRIMARY KEY (event_id, user_id),
        FOREIGN KEY(event_id) REFERENCES event (id),
        FOREIGN KEY(user_id) REFERENCES "user" (id)
);


CREATE TABLE review (
        id SERIAL NOT NULL,
        comment VARCHAR,
        rating INTEGER NOT NULL,
        user_id INTEGER NOT NULL,
        event_id INTEGER NOT NULL,
        PRIMARY KEY (id),
        FOREIGN KEY(user_id) REFERENCES "user" (id),
        FOREIGN KEY(event_id) REFERENCES event (id)
);