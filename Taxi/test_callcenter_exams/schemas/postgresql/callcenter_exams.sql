CREATE SCHEMA callcenter_exams;

CREATE TABLE callcenter_exams.exam_questions
(
    question_id     TEXT           PRIMARY KEY,
    audio_link      TEXT           NOT NULL,
    answer          JSONB          NOT NULL
);

CREATE TABLE callcenter_exams.exams_pass
(
    exam_id         TEXT           PRIMARY KEY,
    variant_id      TEXT           NOT NULL,
    user_id         TEXT           NOT NULL,
    cur_question_id TEXT           ,
    start_time      TIMESTAMPTZ    NOT NULL DEFAULT NOW(),
    end_time        TIMESTAMPTZ    ,
    score           INTEGER        check ( score >= 0 ) DEFAULT 0,
    user_name       TEXT           ,
    group_name      TEXT           ,
    ticket_id       TEXT
);

CREATE TABLE callcenter_exams.questions_pass
(
    exam_id         TEXT           NOT NULL,
    question_id     TEXT           NOT NULL,
    result          BOOLEAN        NOT NULL DEFAULT FALSE,
    question_stat   JSONB          NOT NULL DEFAULT '{}'::jsonb,
    correct_answer  JSONB          DEFAULT NULL,
    PRIMARY KEY (exam_id, question_id)
);

CREATE TABLE callcenter_exams.exam_variants
(
    variant_id      TEXT           PRIMARY KEY,
    questions       TEXT[]         NOT NULL check ( array_length(questions, 1) > 0 )
);

CREATE TABLE callcenter_exams.mock_responses
(
    question_id     TEXT           NOT NULL,
    handler         TEXT           NOT NULL,
    answer          JSONB          ,
    is_default      BOOLEAN        NOT NULL DEFAULT FALSE,
    PRIMARY KEY (question_id, handler)
);

CREATE INDEX ON callcenter_exams.exams_pass (user_id);
CREATE INDEX ON callcenter_exams.questions_pass (exam_id);
CREATE INDEX ON callcenter_exams.questions_pass (question_id);
CREATE INDEX ON callcenter_exams.mock_responses (question_id);
