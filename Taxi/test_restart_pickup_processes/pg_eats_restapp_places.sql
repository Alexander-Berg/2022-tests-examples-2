INSERT INTO eats_restapp_places.pickup_status (
    place_id,
    place_delivery_zone_id,
    place_delivery_zone_enabled,
    place_commission_value,
    pickup_started,
    pickup_enabled,
    pickup_mode,
    in_process,
    updated_at)
VALUES
       (111,NULL,false,15.2,NULL,true,'self_allowed'::eats_restapp_places.pickup_mode, true, now() - interval '8 minute'),
       (222,NULL,false,15.2,NULL,false,'self_allowed'::eats_restapp_places.pickup_mode, true, now() - interval '6 minute'),
       (333,NULL,false,15.2,NULL,false,'self_allowed'::eats_restapp_places.pickup_mode, true, now() - interval '3 minute')
