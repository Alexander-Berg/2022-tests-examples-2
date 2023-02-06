package ru.yandex.metrika.cdp.scheduler.bitrix.dto;

import java.util.Arrays;
import java.util.List;
import java.util.Set;

import org.junit.Assert;
import org.junit.Test;

import static ru.yandex.metrika.cdp.scheduler.bitrix.BitrixTestUtils.DEFAULT_CLIENT_ID_NAMES;

public class BitrixLeadYtTest {
    @Test
    public void parseClientIds() {
        List<String> userFieldsJson = Arrays.asList(
                "{\"metrika_client_id\":[\"102\"]}",
                "{\"metrikaclientid\":[102]}",
                "{\"metrika-client-id\":102}",
                "{\"metricaclientid\":\"102\"}",
                """
                        {
                            "metrika_client_id":[15, 79],
                            "metrikaclientid":[],
                            "metrika-client-id":null,
                            "metrica_client_id":["112","111"],
                            "metricaclientid":54,
                            "metrica-client-id":"102"
                        }
                        """,
                "{\"invalidFieldName\":[\"444\"]}"
        );

        List<Set<Long>> clientIds = Arrays.asList(
                Set.of(102L),
                Set.of(102L),
                Set.of(102L),
                Set.of(102L),
                Set.of(15L, 54L, 79L, 102L, 111L, 112L),
                Set.of()
        );
        Assert.assertEquals(clientIds.size(), userFieldsJson.size());

        for (int i = 0; i < userFieldsJson.size(); i++) {
            BitrixLeadYt lead = new BitrixLeadYt();
            lead.setUserFields(userFieldsJson.get(i));
            Assert.assertEquals(clientIds.get(i), lead.getClientIds(DEFAULT_CLIENT_ID_NAMES));
        }
    }

    @Test
    public void parseEmails() {
        List<String> emailsJson = Arrays.asList(
                """
                        [
                            {"ID":"51",
                            "VALUE_TYPE":"WORK",
                            "VALUE":"test@test.ru",
                            "TYPE_ID":"EMAIL"}
                        ]
                        """,
                """
                        [
                            {"VALUE":"test@test.ru"}
                        ]
                        """,
                """
                        [
                            {"VALUE":"test@test.ru",
                            "ID":"51",
                            "VALUE_TYPE":"WORK",
                            "TYPE_ID":"EMAIL"},

                            {"ID":"52",
                            "VALUE_TYPE":"WORK",
                            "TYPE_ID":"EMAIL",
                            "VALUE":"test@test.com"}
                        ]
                        """,
                "",
                null,
                "   "
        );

        List<Set<String>> emails = Arrays.asList(
                Set.of("test@test.ru"),
                Set.of("test@test.ru"),
                Set.of("test@test.ru", "test@test.com"),
                Set.of(),
                Set.of(),
                Set.of()
        );
        Assert.assertEquals(emails.size(), emailsJson.size());

        for (int i = 0; i < emailsJson.size(); i++) {
            BitrixLeadYt lead = new BitrixLeadYt();
            lead.setEmailsJson(emailsJson.get(i));
            Assert.assertEquals(emails.get(i), lead.getEmails());
        }
    }

    @Test
    public void parsePhones() {
        List<String> phonesJson = Arrays.asList(
                """
                        [
                            {"ID":"51",
                            "VALUE_TYPE":"WORK",
                            "VALUE":"79991234568",
                            "TYPE_ID":"PHONE"}
                        ]
                        """,
                """
                        [
                            {"VALUE":"79991234568"}
                        ]
                        """,
                """
                        [
                            {"VALUE":"79991234568",
                            "ID":"51",
                            "VALUE_TYPE":"WORK",
                            "TYPE_ID":"PHONE"},

                            {"ID":"52",
                            "VALUE_TYPE":"WORK",
                            "TYPE_ID":"PHONE",
                            "VALUE":"79990123456"}
                        ]
                        """,
                "",
                null,
                "   "
        );

        List<Set<String>> phones = Arrays.asList(
                Set.of("79991234568"),
                Set.of("79991234568"),
                Set.of("79991234568", "79990123456"),
                Set.of(),
                Set.of(),
                Set.of()
        );
        Assert.assertEquals(phones.size(), phonesJson.size());

        for (int i = 0; i < phonesJson.size(); i++) {
            BitrixLeadYt lead = new BitrixLeadYt();
            lead.setPhonesJson(phonesJson.get(i));
            Assert.assertEquals(phones.get(i), lead.getPhones());
        }
    }
}
