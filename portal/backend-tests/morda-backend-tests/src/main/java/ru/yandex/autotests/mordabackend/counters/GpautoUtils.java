package ru.yandex.autotests.mordabackend.counters;

import com.fasterxml.jackson.databind.JsonNode;
import com.fasterxml.jackson.databind.node.MissingNode;

/**
 * @author Ivan Nikolaev <ivannik@yandex-team.ru>
 */
public class GpautoUtils {

    public static JsonNode getExpNode(JsonNode node, String exp) {
        for (JsonNode n : node.get("blocks")) {
            if (n.has("exp")) {
                return n.path("exp").path(exp);
            }
        }
        return MissingNode.getInstance();
    }

    public static String getGpautoWithCoords(String lat, String lon, String acc, long timestamp) {
        long validUntil = timestamp + 864000;
        return String.format("%s.gpauto.%s:%s:%s:0:%s", validUntil, lat, lon, acc, timestamp);
    }
}
