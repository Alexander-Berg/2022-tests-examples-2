package ru.yandex.metrika.cdp.scheduler.bitrix.validation;

import java.util.Arrays;
import java.util.List;

import org.jetbrains.annotations.NotNull;
import org.junit.Assert;
import org.junit.Before;
import org.junit.Test;

import ru.yandex.metrika.cdp.scheduler.bitrix.BitrixTestUtils;
import ru.yandex.metrika.cdp.scheduler.bitrix.dto.BitrixLeadYt;

public class BitrixLeadValidatorTest {
    private BitrixLeadValidator validator;
    private long entityCounter;

    @NotNull
    private BitrixLeadYt buildValidLead() {
        BitrixLeadYt lead = new BitrixLeadYt();
        lead.setCounterId(123);
        lead.setEntityId(nextEntityId());
        lead.setCreateDateTime("2022-02-22 11:42:19");
        lead.setUpdateDateTime("2022-02-22 23:33:28");
        lead.setOrderStatus("NEW");
        lead.setContactId(1L);
        return lead;
    }

    private long nextEntityId() {
        return ++entityCounter;
    }

    @Before
    public void setUp() {
        validator = new BitrixLeadValidator(
                BitrixTestUtils.connectorsCache, true,
                BitrixTestUtils.activeCountersCache, true
        );
        entityCounter = 0;
    }

    @Test
    public void validLead() {
        Assert.assertTrue(validator.isValid(buildValidLead()));
        BitrixTestUtils.assertValidatorErrorsSize(validator, 1, 0);
    }

    @Test
    public void invalidCounterIds() {
        List<Integer> invalidCounterIds = Arrays.asList(
                null, -53, 0,
                BitrixTestUtils.NOT_ACTIVE_COUNTER_ID,
                BitrixTestUtils.COUNTER_ID_WITHOUT_CONNECTOR,
                BitrixTestUtils.COUNTER_ID_WITH_DISABLED_LEADS
        );
        for (Integer counterId : invalidCounterIds) {
            BitrixLeadYt lead = buildValidLead();
            lead.setCounterId(counterId);
            Assert.assertFalse(validator.isValid(lead));
        }
        BitrixTestUtils.assertValidatorErrorsSize(validator, invalidCounterIds.size(), 1);
    }

    @Test
    public void invalidEntityIds() {
        List<Long> invalidEntityIds = Arrays.asList(null, -1L, 0L);
        for (Long entityId : invalidEntityIds) {
            BitrixLeadYt lead = buildValidLead();
            lead.setEntityId(entityId);
            Assert.assertFalse(validator.isValid(lead));
        }
        BitrixTestUtils.assertValidatorErrorsSize(validator, invalidEntityIds.size(), 1);
    }

    @Test
    public void invalidDateTime() {
        List<String> invalidDateTime = Arrays.asList("2022-22-02 11:42:19", "2022022211:42:19", null, "", "  ", "2022-02-22 42:42:19");
        for (String dateTime : invalidDateTime) {
            BitrixLeadYt lead = buildValidLead();
            lead.setCreateDateTime(dateTime);
            lead.setUpdateDateTime(dateTime);
            Assert.assertFalse(validator.isValid(lead));
        }
        BitrixTestUtils.assertValidatorErrorsSize(validator, invalidDateTime.size(), 2);
    }

    @Test
    public void validUserFields() {
        List<String> validUserFieldsJson = Arrays.asList(
                "{\"metrikaclientids\":[\"102\"]}",
                "{\"metrika_client_id\":[102]}",
                "{\"metrika-client-id\":102}",
                "{\"metrica_client_id\":\"102\"}",
                """
                        {
                            "metrika_client_id":[15, 79],
                            "metrikaclientid":[],
                            "metrika-client-id":null,
                            "metrica_client_id":["112","111"],
                            "metricaclientid":54,
                            "metrica-client-id":"102"
                        }
                        """
        );

        for (String json : validUserFieldsJson) {
            BitrixLeadYt lead = buildValidLead();
            lead.setUserFields(json);
            Assert.assertTrue(validator.isValid(lead));
        }
        BitrixTestUtils.assertValidatorErrorsSize(validator, validUserFieldsJson.size(), 0);
    }

    @Test
    public void invalidUserFields() {
        List<String> invalidUserFieldsJson = Arrays.asList(
                "\"metrikaclientids\":[\"102\"]}",
                "{\"metrika_client_id\":}",
                "{\"metrika-client-id\":102",
                "{\"metrica_client_id:102\"}"
        );

        for (String json : invalidUserFieldsJson) {
            BitrixLeadYt lead = buildValidLead();
            lead.setUserFields(json);
            Assert.assertFalse(validator.isValid(lead));
        }
        BitrixTestUtils.assertValidatorErrorsSize(validator, invalidUserFieldsJson.size(), 1);
    }

    @Test
    public void invalidOpportunity() {
        List<String> invalidOpportunity = Arrays.asList("-1", "string", "-.43", "34o9");
        for (String opportunity : invalidOpportunity) {
            BitrixLeadYt lead = buildValidLead();
            lead.setOpportunity(opportunity);
            Assert.assertFalse(validator.isValid(lead));
        }
        BitrixTestUtils.assertValidatorErrorsSize(validator, invalidOpportunity.size(), 1);
    }

    @Test
    public void invalidStatus() {
        List<String> invalidStatus = Arrays.asList("", null, "   ");
        for (String status : invalidStatus) {
            BitrixLeadYt lead = buildValidLead();
            lead.setOrderStatus(status);
            Assert.assertFalse(validator.isValid(lead));
        }
        BitrixTestUtils.assertValidatorErrorsSize(validator, invalidStatus.size(), 1);
    }

    @Test
    public void invalidContactId() {
        List<Long> invalidContactId = Arrays.asList(-2L, null, 0L);
        for (Long contactId : invalidContactId) {
            BitrixLeadYt lead = buildValidLead();
            lead.setContactId(contactId);
            Assert.assertFalse(validator.isValid(lead));
        }
        BitrixTestUtils.assertValidatorErrorsSize(validator, invalidContactId.size(), 1);
    }

    @Test
    public void invalidEmail() {
        List<String> invalidEmailsJson = Arrays.asList(
                """
                        [
                            {"ID":"51",
                            "VALUE_TYPE":"WORK",
                            "TYPE_ID":"EMAIL"}
                        ]
                        """,
                """
                        [
                            {"ID":"51",
                            "VALUE_TYPE":"WORK",
                            "VAE":"test@test.ru",
                            "TYPE_ID":"EMAIL"}
                        ]
                        """,
                """
                        [
                            "ID":"51",
                            "VALUE_TYPE":"WORK",
                            "VALUE":"test@test.ru",
                            "TYPE_ID":"EMAIL"
                        ]
                        """,
                """
                        {"ID":"51",
                        "VALUE_TYPE":"WORK",
                        "VALUE":"test@test.ru",
                        "TYPE_ID":"EMAIL"}
                        """,
                """
                        [
                            {"VALUE":"test@.ru"}
                        ]
                        """,
                """
                        [
                            {"VALUE":"test.ru"}
                        ]
                        """,
                """
                        [
                            {"VALUE":"test@test."}
                        ]
                        """,
                """
                        [
                            {"VALUE":"test@test"}
                        ]
                        """,
                """
                        [
                            {"VALUE":"@test.ru"}
                        ]
                        """,
                """
                        [
                            {"ID":"51",
                            "VALUE_TYPE":"WORK",
                            "VALUE":"test@test.ru",
                            "TYPE_ID":"EMAIL"},

                            {"ID":"52",
                            "VALUE_TYPE":"WORK",
                            "TYPE_ID":"EMAIL"}
                        ]
                        """,
                """
                        {"ID":"51",
                        "VALUE_TYPE":"WORK",
                        "VALUE":"test@test.ru",
                        "TYPE_ID":"EMAIL"},

                        {"ID":"52",
                        "VALUE_TYPE":"WORK",
                        "VALUE":"test@test.com",
                        "TYPE_ID":"EMAIL"}
                        """
        );
        for (String json : invalidEmailsJson) {
            BitrixLeadYt lead = buildValidLead();
            lead.setEmailsJson(json);
            Assert.assertFalse(validator.isValid(lead));
        }
        BitrixTestUtils.assertValidatorErrorsSize(validator, invalidEmailsJson.size(), 1);
    }

    @Test
    public void validEmails() {
        List<String> validEmailsJson = Arrays.asList(
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
        for (String json : validEmailsJson) {
            BitrixLeadYt lead = buildValidLead();
            lead.setEmailsJson(json);
            Assert.assertTrue(validator.isValid(lead));
        }
        BitrixTestUtils.assertValidatorErrorsSize(validator, validEmailsJson.size(), 0);
    }

    @Test
    public void invalidPhones() {
        List<String> invalidPhonesJson = Arrays.asList(
                """
                        [
                            {"ID":"51",
                            "VALUE_TYPE":"WORK",
                            "TYPE_ID":"PHONE"}
                        ]
                        """,
                """
                        [
                            {"ID":"51",
                            "VALUE_TYPE":"WORK",
                            "VAE":"79991234568",
                            "TYPE_ID":"PHONE"}
                        ]
                        """,
                """
                        [
                            "ID":"51",
                            "VALUE_TYPE":"WORK",
                            "VALUE":"79991234568",
                            "TYPE_ID":"PHONE"
                        ]
                        """,
                """
                        {"ID":"51",
                        "VALUE_TYPE":"WORK",
                        "VALUE":"79991234568",
                        "TYPE_ID":"PHONE"}
                        """,
                """
                        [
                            {"ID":"51",
                            "VALUE_TYPE":"WORK",
                            "VALUE":"79991234568",
                            "TYPE_ID":"PHONE"},

                            {"ID":"52",
                            "VALUE_TYPE":"WORK",
                            "TYPE_ID":"PHONE"}
                        ]
                        """,
                """
                        {"ID":"51",
                        "VALUE_TYPE":"WORK",
                        "VALUE":"79991234568",
                        "TYPE_ID":"PHONE"},

                        {"ID":"52",
                        "VALUE_TYPE":"WORK",
                        "VALUE":"79990123456",
                        "TYPE_ID":"PHONE"}
                        """
        );
        for (String json : invalidPhonesJson) {
            BitrixLeadYt lead = buildValidLead();
            lead.setPhonesJson(json);
            Assert.assertFalse(validator.isValid(lead));
        }
        BitrixTestUtils.assertValidatorErrorsSize(validator, invalidPhonesJson.size(), 1);
    }

    @Test
    public void validPhones() {
        List<String> validPhonesJson = Arrays.asList(
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
        for (String json : validPhonesJson) {
            BitrixLeadYt lead = buildValidLead();
            lead.setPhonesJson(json);
            Assert.assertTrue(validator.isValid(lead));
        }
        BitrixTestUtils.assertValidatorErrorsSize(validator, validPhonesJson.size(), 0);
    }
}
