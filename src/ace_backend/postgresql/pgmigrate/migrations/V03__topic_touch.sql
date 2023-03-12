CREATE TABLE ace.topic
(
    id                   BIGSERIAL PRIMARY KEY,

    created_at           TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    text                 VARCHAR NOT NULL
);

CREATE TABLE ace.touch
(
    id                   BIGSERIAL PRIMARY KEY,

    last_seen_at         TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    ace_session_id       VARCHAR NOT NULL,

    UNIQUE(ace_session_id)
);
