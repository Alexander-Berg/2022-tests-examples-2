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

import static ru.yandex.metrika.cdp.scheduler.bitrix.BitrixTestUtils.DEFAULT_CLIENT_ID_NAMES;

@RunWith(Parameterized.class)
public class BitrixContactYtTest {

    @Parameter
    public BitrixContactYt contact;

    @Parameter(value = 1)
    public Client client;

    @Parameter(value = 2)
    public Client clientSmall;

    @Parameters
    public static Collection<Object[]> parameters() {
        List<Object[]> parameters = new ArrayList<>();

        BitrixContactYt contact1 = new BitrixContactYt();
        contact1.setCounterId(512);
        contact1.setEntityId(783L);
        contact1.setCreateDateTime("2021-09-29 11:30:00");
        contact1.setUpdateDateTime("2022-01-01 00:00:00");
        contact1.setEmailsJson("[{\"VALUE\":\"much@better.day\"}, {\"VALUE\":\"new@year.day\"}]");
        contact1.setPhonesJson("[{\"VALUE\":\"79991234567\"}, {\"VALUE\":\"79998888888\"}]");
        contact1.setUserFields("" +
                "{\"metrica_client_id\":\"84\"," +
                "\"metrikaclientid\":93," +
                "\"metricaclientid\":[79, 145]}");

        Client client1 = new Client(
                CdpIdUtil.buildContactCdpUid("783"),
                512,
                "783",
                EntityStatus.ACTIVE,
                ClientType.CONTACT
        );
        client1.setCreateDateTime(Instant.parse("2021-09-29T08:30:00.00Z"));
        client1.setUpdateDateTime(Instant.parse("2021-12-31T21:00:00.00Z"));
        client1.setEmails(Set.of("much@better.day", "new@year.day"));
        client1.setPhones(Set.of("79991234567", "79998888888"));
        client1.setClientUserIds(Collections.emptySet());
        client1.setEmailsMd5(Collections.emptySet());
        client1.setPhonesMd5(Collections.emptySet());
        client1.setAttributes(Collections.emptyMap());

        Client clientSmall1 = new Client(
                CdpIdUtil.buildContactCdpUid("783"),
                512,
                "783",
                EntityStatus.ACTIVE,
                ClientType.CONTACT,
                Set.of(79L, 84L, 93L, 145L)
        );

        parameters.add(new Object[]{contact1, client1, clientSmall1});


        BitrixContactYt contact2 = new BitrixContactYt();
        contact2.setCounterId(232);
        contact2.setEntityId(444L);
        contact2.setCreateDateTime("2020-12-29 11:30:00");
        contact2.setUpdateDateTime("2022-02-02 00:00:00");

        Client client2 = new Client(
                CdpIdUtil.buildContactCdpUid("444"),
                232,
                "444",
                EntityStatus.ACTIVE,
                ClientType.CONTACT
        );
        client2.setCreateDateTime(Instant.parse("2020-12-29T08:30:00.00Z"));
        client2.setUpdateDateTime(Instant.parse("2022-02-01T21:00:00.00Z"));
        client2.setEmails(Collections.emptySet());
        client2.setPhones(Collections.emptySet());
        client2.setClientUserIds(Collections.emptySet());
        client2.setEmailsMd5(Collections.emptySet());
        client2.setPhonesMd5(Collections.emptySet());
        client2.setAttributes(Collections.emptyMap());

        Client clientSmall2 = new Client(
                CdpIdUtil.buildContactCdpUid("444"),
                232,
                "444",
                EntityStatus.ACTIVE,
                ClientType.CONTACT,
                Set.of()
        );

        parameters.add(new Object[]{contact2, client2, clientSmall2});

        return parameters;
    }

    @Test
    public void toEntityTest() {
        Client toEntityClient = contact.toEntity();
        Client toEntityClientSmall = contact.getClientSmall(DEFAULT_CLIENT_ID_NAMES).toEntity();

        Assert.assertEquals(client, toEntityClient);
        Assert.assertEquals(clientSmall, toEntityClientSmall);
    }
}
