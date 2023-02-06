INSERT INTO eats_restapp_places.place_info (
    place_id,
    name,
    address,
    courier_entrance,
    use_courier_entrance,
    permalink)
VALUES
    (111,'name111','address111', POINT(55.44553, 38.23963), true, '222'),
    (222,'name222','address222', POINT(55.43899, 38.23885), false, '222');
