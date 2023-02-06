package ru.yandex.autotests.mordabackend.actions;

import com.fasterxml.jackson.databind.JsonNode;
import ru.yandex.autotests.mordabackend.MordaClient;

import javax.ws.rs.client.Client;

/**
 * @author Ivan Nikolaev <ivannik@yandex-team.ru>
 */
public class OperaDataActions extends AbstractActions {
    public OperaDataActions(MordaClient mordaClient, Client client) {
        super(mordaClient, client);
    }

    public JsonNode getDataSamsungCombined(String geoId) {
        return client
                .target(mordaClient.getMordaHost())
                .path("/data/samsung/combined.js")
                .queryParam("geo", geoId)
                .request()
                .get(JsonNode.class);
    }
}
