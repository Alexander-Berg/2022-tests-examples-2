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
VALUES      ('park_id_0', -- park_id
             'id_0', -- id
             'order_id_0', -- order_id
             '2019-12-23 12:21:23.000000', -- date
             1, -- feed_type
             0, -- status
             'Ok', -- description
             3, -- score
             NULL), -- predefined_comments

             ('park_id_0', -- park_id
             'id_1', -- id
             'order_id_0', -- order_id
             '2019-12-23 12:21:24.000000', -- date
             2, -- feed_type
             0, -- status
             'Good', -- description
             4, -- score
             NULL),

             ('park_id_0', -- park_id
             'id_2', -- id
             'order_id_0', -- order_id
             '2019-12-23 12:21:25.000000', -- date
             3, -- feed_type
             0, -- status
             'Best', -- description
             5, -- score
             NULL); -- predefined_comments
