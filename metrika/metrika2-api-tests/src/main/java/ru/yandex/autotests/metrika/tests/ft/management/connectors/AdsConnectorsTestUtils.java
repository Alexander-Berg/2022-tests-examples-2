package ru.yandex.autotests.metrika.tests.ft.management.connectors;

import ru.yandex.metrika.api.management.client.connectors.AdsCabinet;
import ru.yandex.metrika.api.management.client.connectors.AdsConnector;
import ru.yandex.metrika.api.management.client.connectors.AdsPlatform;

import java.text.SimpleDateFormat;
import java.util.Collections;
import java.util.Date;
import java.util.concurrent.ThreadLocalRandom;
import java.util.stream.Collectors;
import java.util.stream.Stream;

public final class AdsConnectorsTestUtils {

    private static final ThreadLocalRandom RND = ThreadLocalRandom.current();

    private AdsConnectorsTestUtils() {
    }

    public static AdsConnector buildDefaultConnector(long connectorId, AdsPlatform platform) {
        AdsConnector connector = new AdsConnector();
        connector.setConnectorId(connectorId);
        connector.setName("test_ads_connector_" + new SimpleDateFormat("yyyyMMddHHmmssSSS").format(new Date()));
        connector.setPlatform(platform);
        connector.setCabinets(Collections.singletonList(buildDefaultCabinet()));
        return connector;
    }

    public static AdsConnector deepCopyConnector(AdsConnector connector) {
        AdsConnector c = new AdsConnector();
        c.setConnectorId(connector.getConnectorId());
        c.setAuthorized(connector.getAuthorized());
        c.setLogin(connector.getLogin());
        c.setName(connector.getName());
        c.setPlatform(connector.getPlatform());
        c.setCabinets(connector.getCabinets().stream().map(AdsConnectorsTestUtils::deepCopyCabinet).collect(Collectors.toList()));
        c.setUid(connector.getUid());
        return c;
    }

    public static AdsCabinet deepCopyCabinet(AdsCabinet cabinet) {
        AdsCabinet c = new AdsCabinet();
        c.setAuthorized(cabinet.getAuthorized());
        c.setCustomerAccountCurrency(cabinet.getCustomerAccountCurrency());
        c.setCustomerAccountId(cabinet.getCustomerAccountId());
        c.setCustomerAccountName(cabinet.getCustomerAccountName());
        c.setCustomerAccountTimezone(cabinet.getCustomerAccountTimezone());
        c.setManagedBy(cabinet.getManagedBy());
        return c;
    }

    public static AdsCabinet buildDefaultCabinet() {
        return new AdsCabinet()
                .withCustomerAccountId(RND.nextLong(2L, 1_000_000L))
                .withCustomerAccountName("test_ads_cabinet_" + new SimpleDateFormat("yyyyMMddHHmmssSSS").format(new Date()))
                .withCustomerAccountTimezone("Asia/Krasnoyarsk")
                .withCustomerAccountCurrency("RUB");
    }
}
