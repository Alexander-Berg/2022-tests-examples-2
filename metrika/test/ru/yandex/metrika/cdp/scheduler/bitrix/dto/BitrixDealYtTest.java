package ru.yandex.metrika.cdp.scheduler.bitrix.dto;

import java.time.Instant;
import java.util.ArrayList;
import java.util.Collection;
import java.util.Collections;
import java.util.List;
import java.util.Set;

import org.junit.Assert;
import org.junit.Test;
import org.junit.runner.RunWith;
import org.junit.runners.Parameterized;
import org.junit.runners.Parameterized.Parameter;
import org.junit.runners.Parameterized.Parameters;

import ru.yandex.metrika.cdp.common.CdpIdUtil;
import ru.yandex.metrika.cdp.dto.core.Client;
import ru.yandex.metrika.cdp.dto.core.ClientType;
import ru.yandex.metrika.cdp.dto.core.EntityStatus;
import ru.yandex.metrika.cdp.dto.core.Order;

import static ru.yandex.metrika.cdp.scheduler.bitrix.BitrixTestUtils.DEFAULT_CLIENT_ID_NAMES;

@RunWith(Parameterized.class)
public class BitrixDealYtTest {

    @Parameter
    public BitrixDealYt deal;

    @Parameter(value = 1)
    public Order order;

    @Parameter(value = 2)
    public Client clientSmall;

    @Parameters
    public static Collection<Object[]> parameters() {
        List<Object[]> parameters = new ArrayList<>();

        BitrixDealYt deal1 = new BitrixDealYt();
        deal1.setCounterId(512);
        deal1.setEntityId(783L);
        deal1.setCreateDateTime("2021-09-29 11:30:00");
        deal1.setUpdateDateTime("2022-01-01 00:00:00");
        deal1.setOpportunity("56.32");
        deal1.setOrderStatus("NEW");
        deal1.setContactId(12L);
        deal1.setUserFields("" +
                "{\"metrica_client_id\":\"84\"," +
                "\"metrikaclientid\":93," +
                "\"metricaclientid\":[79, 145]}");

        Order order1 = new Order(
                CdpIdUtil.buildContactCdpUid("12"),
                512,
                CdpIdUtil.buildOrderId("783"),
                "783",
                EntityStatus.ACTIVE,
                "NEW"
        );
        order1.setCreateDateTime(Instant.parse("2021-09-29T08:30:00.00Z"));
        order1.setUpdateDateTime(Instant.parse("2021-12-31T21:00:00.00Z"));
        order1.setRevenue(56_320_000L);
        order1.setCost(0L);
        order1.setProducts(Collections.emptyMap());
        order1.setAttributes(Collections.emptyMap());

        Client clientSmall1 = new Client(
                CdpIdUtil.buildContactCdpUid("12"),
                512,
                "12",
                EntityStatus.ACTIVE,
                ClientType.CONTACT,
                Set.of(79L, 84L, 93L, 145L)
        );

        parameters.add(new Object[]{deal1, order1, clientSmall1});


        BitrixDealYt deal2 = new BitrixDealYt();
        deal2.setCounterId(232);
        deal2.setEntityId(444L);
        deal2.setCreateDateTime("2020-12-29 11:30:00");
        deal2.setUpdateDateTime("2022-02-02 00:00:00");
        deal2.setContactId(256L);
        deal2.setOrderStatus("NEW");

        Order order2 = new Order(
                CdpIdUtil.buildContactCdpUid("256"),
                232,
                CdpIdUtil.buildOrderId("444"),
                "444",
                EntityStatus.ACTIVE,
                "NEW"
        );
        order2.setCreateDateTime(Instant.parse("2020-12-29T08:30:00.00Z"));
        order2.setUpdateDateTime(Instant.parse("2022-02-01T21:00:00.00Z"));
        order2.setRevenue(0L);
        order2.setCost(0L);
        order2.setProducts(Collections.emptyMap());
        order2.setAttributes(Collections.emptyMap());

        Client clientSmall2 = new Client(
                CdpIdUtil.buildContactCdpUid("256"),
                232,
                "256",
                EntityStatus.ACTIVE,
                ClientType.CONTACT,
                Set.of()
        );

        parameters.add(new Object[]{deal2, order2, clientSmall2});

        return parameters;
    }

    @Test
    public void toEntityTest() {
        Order toEntityOrder = deal.toEntity();
        Client toEntityClientSmall = deal.getClientSmall(DEFAULT_CLIENT_ID_NAMES).toEntity();

        Assert.assertEquals(order, toEntityOrder);
        Assert.assertEquals(clientSmall, toEntityClientSmall);
    }
}
