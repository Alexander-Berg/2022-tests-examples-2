INSERT INTO supportai.contexts_meta (id, project_id, chat_id, created_at, last_sure_topic)
VALUES
(1, 'demo', 'new_chat', '2021-02-01 20:00:00', 'help'),
(2, 'demo', 'old_chat', '2021-01-01 02:00:00', 'help'),
(3, 'configured', 'new_chat', '2021-02-01 20:00:00', 'help'),
(4, 'configured', 'old_chat', '2021-01-15 02:00:00', 'help');

INSERT INTO supportai.contexts (meta_id, created_at, context) VALUES
(1, '2021-02-01 20:00:00'::timestamptz,
$$
{
    "request": {
        "dialog": {
            "messages": []
        },
        "features": []
    },
    "response": {

    }
}
$$
),
(2, '2021-01-01 02:00:00'::timestamptz,
$$
{
    "request": {
        "dialog": {
            "messages": []
        },
        "features": []
    },
    "response": {

    }
}
$$
),
(3, '2021-02-01 20:00:00'::timestamptz,
$$
{
    "request": {
        "dialog": {
            "messages": []
        },
        "features": []
    },
    "response": {

    }
}
$$
),
(4, '2021-01-15 02:00:00'::timestamptz,
$$
{
    "request": {
        "dialog": {
            "messages": []
        },
        "features": []
    },
    "response": {

    }
}
$$
)

