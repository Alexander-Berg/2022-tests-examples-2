INSERT INTO chatterbox.startrack_sip_calls(call_id,
                                           user_id,
                                           num_from,
                                           num_to,
                                           direction,
                                           status_completed,
                                           record_urls,
                                           is_synced)
VALUES ('my_call',
        'support',
        '+7990',
        '+7999',
        'direction',
        'status_completed',
        ARRAY[
            'https://chatterbox.orivet.ru/telphin/storage/record-id_0',
            'https://chatterbox.orivet.ru/telphin/storage/record-id_1'
        ],
        true)
