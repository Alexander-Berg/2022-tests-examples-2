package ru.yandex.metrika.cdp.scheduler.bitrix.validation;

import java.util.ArrayList;
import java.util.Collection;
import java.util.List;

import org.junit.Assert;
import org.junit.Before;
import org.junit.Test;
import org.junit.runner.RunWith;
import org.junit.runners.Parameterized;
import org.junit.runners.Parameterized.Parameter;
import org.junit.runners.Parameterized.Parameters;

import ru.yandex.metrika.cdp.scheduler.bitrix.BitrixTestUtils;
import ru.yandex.metrika.cdp.scheduler.bitrix.dto.BitrixContactYt;

@RunWith(Parameterized.class)
public class BitrixContactValidatorTest {
    private BitrixContactValidator validator;

    @Parameter
    public String testName;

    @Parameter(value = 1)
    public BitrixContactYt contact;

    @Parameter(value = 2)
    public Integer errorsCount;

    @Before
    public void setUp() {
        validator = new BitrixContactValidator(
                BitrixTestUtils.connectorsCache, true,
                BitrixTestUtils.activeCountersCache, true
        );
    }


    @Parameters(name = "{0}")
    public static Collection<Object[]> parameters() {
        List<Object[]> parameters = new ArrayList<>();

        BitrixContactYt invalidContact = new BitrixContactYt();
        invalidContact.setCounterId(BitrixTestUtils.NOT_ACTIVE_COUNTER_ID);
        invalidContact.setEntityId(143L);
        invalidContact.setCreateDateTime(null);
        invalidContact.setUpdateDateTime("2022-02-24 05:00:00:00");
        invalidContact.setEmailsJson("[{\"VALUE\":\"not@a.correct@day\"}]");
        invalidContact.setPhonesJson("[{\"VUE\":\"79991234567\"}]");
        invalidContact.setUserFields("{\"metrica_client_id\":qwerty}");
        parameters.add(new Object[]{"Invalid contact", invalidContact, 6});

        BitrixContactYt validContact = new BitrixContactYt();
        validContact.setCounterId(512);
        validContact.setEntityId(783L);
        validContact.setCreateDateTime("2021-09-29 11:30:00");
        validContact.setUpdateDateTime("2022-01-01 00:00:00");
        validContact.setEmailsJson("[{\"VALUE\":\"much@better.day\"}, {\"VALUE\":\"new@year.day\"}]");
        validContact.setPhonesJson("[{\"VALUE\":\"79991234567\"}, {\"VALUE\":\"79998888888\"}]");
        validContact.setUserFields("" +
                "{\"metrica_client_id\":\"84\"," +
                "\"metrikaclientid\":93," +
                "\"metricaclientid\":[79, 145]}");
        parameters.add(new Object[]{"Valid contact", validContact, 0});

        BitrixContactYt validContact2 = new BitrixContactYt();
        validContact2.setCounterId(232);
        validContact2.setEntityId(444L);
        validContact2.setCreateDateTime("2020-12-29 11:30:00");
        validContact2.setUpdateDateTime("2022-02-02 00:00:00");
        parameters.add(new Object[]{"Valid contact 2", validContact2, 0});

        BitrixContactYt validContactWithoutConnector = new BitrixContactYt();
        validContactWithoutConnector.setCounterId(BitrixTestUtils.COUNTER_ID_WITHOUT_CONNECTOR);
        validContactWithoutConnector.setEntityId(444L);
        validContactWithoutConnector.setCreateDateTime("2020-12-29 11:30:00");
        validContactWithoutConnector.setUpdateDateTime("2022-02-02 00:00:00");
        parameters.add(new Object[]{"Valid contact without connector", validContactWithoutConnector, 1});

        return parameters;
    }

    @Test
    public void isValidTest() {
        if (errorsCount == 0) {
            Assert.assertTrue(validator.isValid(contact));
        } else {
            Assert.assertFalse(validator.isValid(contact));
        }
        BitrixTestUtils.assertValidatorErrorsSize(validator, errorsCount);
    }
}
