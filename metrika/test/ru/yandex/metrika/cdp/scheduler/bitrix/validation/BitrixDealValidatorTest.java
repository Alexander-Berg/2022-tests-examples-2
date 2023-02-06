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
import ru.yandex.metrika.cdp.scheduler.bitrix.dto.BitrixDealYt;

@RunWith(Parameterized.class)
public class BitrixDealValidatorTest {
    private BitrixDealValidator validator;

    @Parameter
    public String testName;

    @Parameter(value = 1)
    public BitrixDealYt deal;

    @Parameter(value = 2)
    public Integer errorsCount;

    @Before
    public void setUp() {
        validator = new BitrixDealValidator(
                BitrixTestUtils.connectorsCache, true,
                BitrixTestUtils.activeCountersCache, true
        );
    }


    @Parameters(name = "{0}")
    public static Collection<Object[]> parameters() {
        List<Object[]> parameters = new ArrayList<>();

        BitrixDealYt invalidDeal = new BitrixDealYt();
        invalidDeal.setCounterId(BitrixTestUtils.NOT_ACTIVE_COUNTER_ID);
        invalidDeal.setEntityId(143L);
        invalidDeal.setCreateDateTime(null);
        invalidDeal.setUpdateDateTime("2022-02-24 05:00:00:00");
        invalidDeal.setOpportunity("-67.86");
        invalidDeal.setOrderStatus("   ");
        invalidDeal.setUserFields("{\"metrica_client_id\":qwerty}");
        invalidDeal.setContactId(-43L);
        parameters.add(new Object[]{"Invalid deal", invalidDeal, 7});

        BitrixDealYt validDeal = new BitrixDealYt();
        validDeal.setCounterId(512);
        validDeal.setEntityId(783L);
        validDeal.setCreateDateTime("2021-09-29 11:30:00");
        validDeal.setUpdateDateTime("2022-01-01 00:00:00");
        validDeal.setOpportunity("56.32");
        validDeal.setOrderStatus("NEW");
        validDeal.setContactId(12L);
        validDeal.setUserFields("" +
                "{\"metrica_client_id\":\"84\"," +
                "\"metrikaclientid\":93," +
                "\"metricaclientid\":[79, 145]}");
        parameters.add(new Object[]{"Valid deal", validDeal, 0});

        BitrixDealYt validDeal2 = new BitrixDealYt();
        validDeal2.setCounterId(232);
        validDeal2.setEntityId(444L);
        validDeal2.setCreateDateTime("2020-12-29 11:30:00");
        validDeal2.setUpdateDateTime("2022-02-02 00:00:00");
        validDeal2.setContactId(256L);
        validDeal2.setOrderStatus("NEW");
        parameters.add(new Object[]{"Valid deal 2", validDeal2, 0});

        return parameters;
    }

    @Test
    public void isValidTest() {
        if (errorsCount == 0) {
            Assert.assertTrue(validator.isValid(deal));
        } else {
            Assert.assertFalse(validator.isValid(deal));
        }
        BitrixTestUtils.assertValidatorErrorsSize(validator, errorsCount);
    }
}
