package ru.yandex.autotests.mordabackend.actions;

import com.fasterxml.jackson.databind.JsonNode;
import ru.yandex.autotests.mordabackend.MordaClient;

import javax.ws.rs.client.Client;

/**
 * @author Ivan Nikolaev <ivannik@yandex-team.ru>
 */
public class GpsaveActions extends AbstractActions {

    public GpsaveActions(MordaClient mordaClient, Client client) {
        super(mordaClient, client);
    }

    public JsonNode gpsave(String lat, String lon, String precision, String sk) {
        return action("gpsave", lat, lon, precision, sk);
    }

    public JsonNode mgpsave(String lat, String lon, String precision, String sk) {
        return action("mgpsave", lat, lon, precision, sk);
    }

    private JsonNode action(String path, String lat, String lon, String precision, String sk) {
        return client
                .target(mordaClient.getMordaHost())
                .path(path)
                .queryParam("lat", lat)
                .queryParam("lon", lon)
                .queryParam("precision", precision)
                .queryParam("sk", sk)
                .request()
                .get(JsonNode.class);
    }
}
