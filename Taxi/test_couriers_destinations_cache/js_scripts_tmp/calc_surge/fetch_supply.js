let supply_params = [];
for (let i in places) {
  let place = places[i];
  let params = places_settings[place.place_id][place.zone_id];
  supply_params.push({
    place_id: place.place_id,
    zone_id: place.zone_id,
    region_id: params.region_id,
    radius: params.settings.max_distance,
    time_quants: params.settings.time_quants
  });
}
return {eda_supply: supply_params};
