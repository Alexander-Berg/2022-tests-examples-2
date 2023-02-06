let prev = Math.min(2 * limit, old_arrival_time);
let curr = Math.min(2 * limit, new_arrival_time);
let load_level = 100 * (
  (weight * Math.min(prev, 2 * limit)) +
  ((1 - weight) * Math.min(curr, 2 * limit))
) / limit;

return {
  data: {
    place_id: place.place_id,
    zone_id: place.zone_id,
    result: {
      load_level: load_level
    }
  }
};
