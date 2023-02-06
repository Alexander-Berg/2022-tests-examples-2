return {
    data: {
        place_id: place_id,
        zone_id: zone_id,
        result: {total: 1, extra: {supply: result || 'undefined', location: location || 'undefined'}}
    }
};
