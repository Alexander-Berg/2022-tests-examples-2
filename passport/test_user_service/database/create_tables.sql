CREATE TABLE user_table
(
    uid          bigint       NOT NULL,
    login        varchar(60)  NOT NULL,
    password     varchar(256) NOT NULL,
    locked_until timestamp,
    delete_at    timestamp,
    env          varchar(20)  NOT NULL,
    PRIMARY KEY (uid, env)
);

CREATE TABLE tag_table
(
    tag_id int GENERATED BY DEFAULT AS IDENTITY PRIMARY KEY,
    tag    varchar(120) UNIQUE NOT NULL
);

CREATE TABLE user_tags_table
(
    uid    bigint,
    tag_id int,
    env    varchar(20) NOT NULL,
    FOREIGN KEY (uid, env) REFERENCES user_table (uid, env) ON DELETE CASCADE,
    PRIMARY KEY (uid, tag_id, env)
);

CREATE TABLE "client_table"
(
    "login_id" int GENERATED BY DEFAULT AS IDENTITY PRIMARY KEY,
    "login"    varchar(60) NOT NULL UNIQUE
);

CREATE TABLE "consumer_table"
(
    "consumer_id"   int GENERATED BY DEFAULT AS IDENTITY PRIMARY KEY,
    "consumer_name" varchar(60) NOT NULL UNIQUE
);

CREATE TABLE "consumer_clients_table"
(
    "login"         varchar(60) REFERENCES "client_table" ("login") ON DELETE CASCADE,
    "consumer_name" varchar(60) REFERENCES "consumer_table" ("consumer_name"),
    "role"          varchar(60) NOT NULL,
    PRIMARY KEY (login, consumer_name, role)
);

CREATE TABLE "consumer_test_accounts_table"
(
    "uid"           bigint,
    "env"           varchar(20) NOT NULL,
    "consumer_name" varchar(60) REFERENCES "consumer_table" ("consumer_name"),
    FOREIGN KEY (uid, env) REFERENCES user_table (uid, env) ON DELETE CASCADE,
    PRIMARY KEY (uid, env, consumer_name)
);

CREATE INDEX tags_for_user_index ON user_tags_table (uid, env);
CREATE INDEX consumer_for_user_index ON consumer_test_accounts_table (consumer_name, env);
CREATE INDEX users_with_tag_index ON user_tags_table (tag_id);
