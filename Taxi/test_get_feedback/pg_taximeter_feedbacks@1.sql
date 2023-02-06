INSERT INTO feedbacks_0 
            (park_id, 
             id, 
             order_id,
             date, 
             feed_type, 
             status, 
             description, 
             score,
             predefined_comments) 
VALUES      ('park_id_1', -- park_id
             'id_0', -- id
             'order_id_0', -- order_id
             '2019-11-30 23:32:23.220000', -- date
             1, -- feed_type
             0, -- status
             'Best', -- description
             5, -- score
             'key5'), -- predefined_comments

             ('park_id_1', -- park_id
             'id_1', -- id
             'order_id_1', -- order_id
             '2019-12-24 11:22:23.240000', -- date
             3, -- feed_type
             0, -- status
             NULL, -- description
             1, -- score
             'key1;key2'); -- predefined_comments
