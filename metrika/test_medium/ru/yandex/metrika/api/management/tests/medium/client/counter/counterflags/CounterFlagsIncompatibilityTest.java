package ru.yandex.metrika.api.management.tests.medium.client.counter.counterflags;

import org.junit.Assert;
import org.junit.Test;
import org.junit.runner.RunWith;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.context.annotation.Configuration;
import org.springframework.context.annotation.Import;
import org.springframework.test.context.ContextConfiguration;
import org.springframework.test.context.junit4.SpringJUnit4ClassRunner;

import ru.yandex.metrika.api.management.client.counter.CounterFlags;
import ru.yandex.metrika.api.management.client.counter.CountersService;
import ru.yandex.metrika.api.management.client.external.CounterFull;
import ru.yandex.metrika.api.management.config.CountersServiceConfig;

import static ru.yandex.metrika.CommonTestsHelper.FAKE_USER;
import static ru.yandex.metrika.api.management.tests.medium.client.counter.counterflags.AbstractCounterFlagsCountersServiceTest.fields;
import static ru.yandex.metrika.api.management.tests.medium.client.counter.counterflags.AbstractCounterFlagsCountersServiceTest.setBasicDataToCounter;

@RunWith(SpringJUnit4ClassRunner.class)
@ContextConfiguration
public class CounterFlagsIncompatibilityTest {

    @Autowired
    private CountersService countersService;

    @Test
    public void createCounterGDPRWithCollectFirstPartyData() {
        var counter = setBasicDataToCounter(new CounterFull());
        counter.setGdprAgreementAccepted(true);
        var counterFlags = new CounterFlags(null,
                false,
                false,
                CounterFlags.Incognito.disabled,
                true,
                false,
                false,
                false
        );
        counter.setCounterFlags(counterFlags);
        var counterSaved = countersService.save(FAKE_USER, FAKE_USER, counter, fields, false);
        Assert.assertEquals( false, counterSaved.getCounterFlags().collectFirstPartyData());
    }

    @Configuration
    @Import({CountersServiceConfig.class})
    public static class Config {}
}
