package ru.yandex.autotests.metrika.appmetrica.data;

import java.util.Optional;
import java.util.stream.Stream;

/**
 * Created by konkov on 18.05.2016.
 */
public enum Tables implements Table {
    AUDIENCE("ym:a:"),
    CLIENT_EVENTS("ym:ce:"),
    SESSIONS("ym:s:"),
    INSTALLATIONS("ym:i:"),
    CLICKS("ym:c:"),
    MOBMET_EVENTS("ym:m:"),
    MOBMET_CAMPAIGNS("ym:mc:"),
    GENERIC_EVENTS("ym:ge:"),
    POSTBACKS("ym:pb:"),
    PUSH_CAMPAIGNS("ym:pc:"),
    USERS("ym:u:"),
    DEEPLINKS("ym:o:"),
    TRAFFIC_SOURCES("ym:ts:"),
    CLIENT_EVENTS_JOIN("ym:ce2:"),
    DEVICES("ym:d:"),
    PROFILES("ym:p:"),
    TECH_EVENTS("ym:t:"),
    CRASH_EVENTS("ym:cr:"),
    CRASH_EVENTS_JOIN("ym:cr2:"),
    ERROR_EVENTS("ym:er:"),
    ERROR_EVENTS_JOIN("ym:er2:"),
    ANR_EVENTS("ym:anr:"),
    ANR_EVENTS_JOIN("ym:anr2:"),
    REENGAGEMENTS("ym:re:"),
    REMARKETING_TRAFFIC_SOURCES("ym:rets:"),
    REVENUE_EVENTS("ym:r:"),
    REVENUE_EVENTS_JOIN("ym:r2:"),
    ECOMMERCE_EVENTS("ym:ec:"),
    ECOMMERCE_EVENTS_JOIN("ym:ec2:"),
    USER_FUNNELS_JOIN("ym:uf:"),
    SESSION_FUNNELS_JOIN("ym:sf:"),
    SKADNETWORK_POSTBACKS("ym:sk:");

    private final String namespace;

    Tables(String namespace) {
        this.namespace = namespace;
    }

    public static Table fromNamespace(String attribute) {
        Optional<Tables> table = Stream.of(values()).filter(t -> attribute.startsWith(t.getNamespace())).findFirst();
        if (table.isPresent()) {
            return table.get();
        } else {
            throw new IllegalArgumentException(attribute);
        }
    }

    public static String removeNamespace(String attribute) {
        Optional<Tables> table = Stream.of(values()).filter(t -> attribute.startsWith(t.getNamespace())).findFirst();
        if (table.isPresent()) {
            return attribute.substring(table.get().namespace.length());
        } else {
            throw new IllegalArgumentException(attribute);
        }
    }

    @Override
    public String getNamespace() {
        return namespace;
    }

    @Override
    public String getName() {
        return name().toLowerCase();
    }

    @Override
    public String toString() {
        return getName();
    }
}
