INSERT INTO supportai.contexts_meta (id, project_id, chat_id, created_at, last_sure_topic, chat_mark)
VALUES
(1, 'demo_dialog', '123', '2021-03-01 09:00:00', 'help', 'critical'),
(2, 'demo_dialog', '1234', '2021-03-15 18:06:48.891541', 'help', NULL),
(3, 'demo_dialog', '12345', '2021-04-01 10:00:00', 'not_help', 'not_ok');

ALTER SEQUENCE supportai.contexts_meta_id_seq RESTART WITH 4;

INSERT INTO supportai.contexts (id, meta_id, created_at, mark, mark_comment, sure_topic, context) VALUES
(1, 1, '2021-03-01 09:00:00', 'ok', NULL, 'hi',
$$
{
    "request": {
        "chat_id": "123",
        "dialog": {
            "messages": [
                {
                    "text": "hi",
                    "author": "user"
                }
            ]
        },
        "features": []
    },
    "response": {
        "reply": {
            "text": "hello",
            "texts": ["hello"]
        },
        "features": {
            "most_probable_topic": "hi",
            "sure_topic": "hi",
            "probabilities": []
        }
    }
}
$$
),
(2, 1, '2021-03-01 10:00:00', 'critical', 'Very not ok!', 'help',
$$
{
    "request": {
        "chat_id": "123",
        "dialog": {
            "messages": [
                {
                    "text": "help help help",
                    "author": "user"
                }
            ]
        },
        "features": []
    },
    "response": {
        "reply": {
            "text": "Im on my way",
            "texts": ["Im on my way"]
        },
        "features": {
            "most_probable_topic": "help",
            "sure_topic": "help",
            "probabilities": []
        }
    }
}
$$
),
(3, 2, '2021-03-15 10:00:00', NULL, NULL, 'help',
$$
{
    "request": {
        "chat_id": "1234",
        "dialog": {
            "messages": [
                {
                    "text": "help help help",
                    "author": "user"
                }
            ]
        },
        "features": []
    },
    "response": {
        "features": {
            "most_probable_topic": "help",
            "sure_topic": "help",
            "probabilities": []
        }
    }
}
$$
),
(4, 3, '2021-04-01 10:00:00', 'not_ok', NULL, NULL,
$$
{
    "request": {
        "chat_id": "12345",
        "dialog": {
            "messages": [
                {
                    "text": "not_help not_help not_help",
                    "author": "user"
                }
            ]
        },
        "features": []
    },
    "response": {
        "reply": {
            "text": "OKAY:(",
            "texts": ["OKAY:("]
        },
        "features": {
            "most_probable_topic": "not_help",
            "probabilities": []
        }
    }
}
$$
);

ALTER SEQUENCE supportai.contexts_id_seq RESTART WITH 5;


INSERT INTO supportai.samplings (slug, name, project_id, quantity, percent, marked_percent, marked) VALUES
('demo_sampling', 'test', 'demo_dialog', 3, 0, 0, false);
