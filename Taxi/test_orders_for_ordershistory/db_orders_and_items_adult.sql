INSERT INTO eats_retail_order_history.order_history (id, order_nr, original_cost_for_customer,
                                                     final_cost_for_customer, delivery_cost_for_customer,
                                                     picking_cost_for_customer, created_at, updated_at,
                                                     status_updated_at, diff)
VALUES (1, '121-121', 123, 234, 100, 50, now(), now(), now(),
        jsonb('{"add":[],"remove":[],"update":[],"replace":[' ||
'{"from_item":{"id":"214663","name":"Салат со шпинатом без сулугуни","count":1,"images":[],"cost_for_customer":"1"},' ||
'"to_item":{"id":"214664","name":"Салат со шпинатом и сыром сулугуни","count":1,"images":[{"url":"","resized_url_pattern":"214664_image_url_1"},{"url":"","resized_url_pattern":"214664_image_url_2"}],"cost_for_customer":"1"}},' ||
'{"from_item":{"id":"214662","name":"Салат без шпината и без сулугуни","count":1,"images":[],"cost_for_customer":"1"},' ||
'"to_item":{"id":"214664","name":"Салат со шпинатом и сыром сулугуни","count":1,"images":[{"url":"","resized_url_pattern":"214664_image_url_1"},{"url":"","resized_url_pattern":"214664_image_url_2"}],"cost_for_customer":"1"}}],' ||
'"no_changes":[{"id":"214665","name":"Греческий салат","count":2,"images":[{"url":"","resized_url_pattern":"214665_image_url_1"},{"url":"","resized_url_pattern":"214665_image_url_2"}],"cost_for_customer":"1600","adult":true}],"soft-delete":[],"picked_items":[]}'));
