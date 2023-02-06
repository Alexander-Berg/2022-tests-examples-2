let supply_params = [];
for (let i in places) {
  let place = places[i];
  let params = places_settings[place.place_id][place.zone_id];
  supply_params.push({
    place_id: place.place_id,
    region_id: params.region_id,
    time_quants: 1
  });
}
return {eda_supply: supply_params};
