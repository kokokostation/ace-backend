CREATE SCHEMA ace;

CREATE TABLE ace.message
(
    id                   BIGSERIAL PRIMARY KEY,

    created_at           TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    ace_session_id       VARCHAR NOT NULL,
    text                 VARCHAR NOT NULL
);
