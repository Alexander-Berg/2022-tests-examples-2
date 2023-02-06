package ru.yandex.metrika.api.management.tests.medium.client.counter.counterflags;


import org.junit.Test;
import org.junit.runner.RunWith;
import org.junit.runners.Parameterized;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.context.annotation.Configuration;
import org.springframework.context.annotation.Import;
import org.springframework.test.context.ContextConfiguration;

import ru.yandex.metrika.api.Feature;
import ru.yandex.metrika.api.constructor.contr.FeatureService;
import ru.yandex.metrika.api.management.client.counter.CounterFlags;
import ru.yandex.metrika.api.management.config.CountersServiceConfig;

import static org.junit.Assert.assertEquals;
import static ru.yandex.metrika.CommonTestsHelper.FAKE_USER;

@RunWith(Parameterized.class)
@ContextConfiguration
public class CounterFlagsCountersServiceEditCounterTest extends AbstractCounterFlagsCountersServiceTest{

    @Autowired
    private FeatureService featureService;

    @Test
    public void testCounterUpdateWithCounterFlags() {
        var created = createCounterWithFlags(null);
        int counterId = created.getId();
        setPredefinedFlags(counterId);

        var counterEdit = getCounterEdit();
        counterEdit.setCounterFlags(counterFlags);
        countersService.merge(FAKE_USER, FAKE_USER, counterId, counterEdit, fields, false);
        var edited = countersService.getById(FAKE_USER, FAKE_USER, counterId, fields);
        assertEquals(new CounterFlags(counterId,
                        expected.useInBenchmarks(),
                        expected.directAllowUseGoalsWithoutAccess(),
                        expected.incognito(),
                        expected.collectFirstPartyData(),
                        expected.statisticsOverSite(),
                        expected.newsEnabledByUser(),
                        expected.newsEnabledByClassifier()
                ), //to set right counter_id
                edited.getCounterFlags());
    }

    private void setPredefinedFlags(Integer counterId) {
        if (Boolean.TRUE.equals(counterFlags.newsEnabledByClassifier())) {
            featureService.addFeature(counterId, Feature.news_enabled_by_classifier);
        }
    }

    @Configuration
    @Import({CountersServiceConfig.class})
    public static class Config {}
}
