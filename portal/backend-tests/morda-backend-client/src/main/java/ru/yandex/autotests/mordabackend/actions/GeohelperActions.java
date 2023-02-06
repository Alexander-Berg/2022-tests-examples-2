package ru.yandex.autotests.mordabackend.actions;

import ru.yandex.autotests.mordabackend.MordaClient;
import ru.yandex.autotests.mordabackend.beans.geohelper.GeohelperResponse;
import ru.yandex.autotests.mordabackend.beans.poi_groups.PoiGroupsItem;

import javax.ws.rs.client.Client;
import javax.ws.rs.client.Entity;
import javax.ws.rs.core.MediaType;
import java.util.HashMap;
import java.util.List;
import java.util.Map;

/**
 * @author Ivan Nikolaev <ivannik@yandex-team.ru>
 */
public class GeohelperActions extends AbstractActions {

    public GeohelperActions(MordaClient mordaClient, Client client) {
        super(mordaClient, client);
    }

    public GeohelperResponse getGeohelperResponse(String lat, String lon, String geoid, List<PoiGroupsItem> poiGroups) {
        Map<String, List<PoiGroupsItem>> postPoiData = new HashMap<>();
        postPoiData.put("poi", poiGroups);

        String mordaHost = mordaClient.getMordaHost().toString().replaceAll("(?<=//).+(?=\\.yandex)","l7test");

        return client
                .target(mordaHost)
                .path("/geohelper/get")
                .queryParam("lat", lat)
                .queryParam("lon", lon)
                .queryParam("geoid", geoid)
                .request()
                .post(Entity.entity(postPoiData, MediaType.APPLICATION_JSON_TYPE), GeohelperResponse.class);
    }
}
