INSERT INTO eats_restapp_places.place_info (
    place_id,
    name,
    address,
    permalink,
    address_comment,
    full_address_comment,
    cc_data,
    cc_info_enabled
    )
VALUES
    (111,'111','a1',NULL,'comment111',NULL,'{}',false),
    (222,'222','a2','2222','comment222 этаж',NULL,'{}',false),
    (333,'333','a3','3333','comment333 этаж','comment333 этаж 3','{}',false),
    (444,'444','a4','4444','comment444','comment444_full','{}',false),
    (555,'555','a5','5555','comment555comment555comment555co' ||
                'mment555comment555comment555comm' ||
                'ent555comment555comment555commen' ||
                't555comment555comment555comment5' ||
                '55comment555comment555comment555' ||
                'comment555comment555comment555co' ||
                'mment555comment555comment555comm' ||
                'ent555comment555comme',NULL,'{}',false),
    (666,'666','a6','6666',' Со стороны Волги!!!',NULL,'{}',false),
    (777,'макдоналдс','a7',NULL,'comment777',NULL,'{}',false),
    (888,'888','a8','8888','comment888','comment888_full','{}',true),
    (999,'999','a9','9999','comment999','comment999_full','{"landmark":"со стороны фонтанки","mall":"коворкинг Практик","floor":"4 этаж","what_is_near":"ближайший вход к красному мосту","other":"из лифта пол пролёта вниз"}',true);

