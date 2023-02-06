package ru.yandex.autotests.mordabackend.actions;

import com.fasterxml.jackson.databind.JsonNode;
import ru.yandex.autotests.mordabackend.MordaClient;

import javax.ws.rs.client.Client;

/**
 * @author Ivan Nikolaev <ivannik@yandex-team.ru>
 */
public class LogsActions extends AbstractActions {
    public LogsActions(MordaClient mordaClient, Client client) {
        super(mordaClient, client);
    }

    public JsonNode getBlockDisplay(String requestId) {
        return client
                .target(mordaClient.getMordaHost())
                .path("/test/blockdisplay/")
                .queryParam("Requestid", requestId)
                .queryParam("v", "2")
                .request()
                .get(JsonNode.class);
    }
}
