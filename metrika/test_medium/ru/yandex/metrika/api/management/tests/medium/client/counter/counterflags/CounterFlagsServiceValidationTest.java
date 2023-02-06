package ru.yandex.metrika.api.management.tests.medium.client.counter.counterflags;

import org.junit.BeforeClass;
import org.junit.Test;
import org.junit.runner.RunWith;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.context.annotation.Configuration;
import org.springframework.context.annotation.Import;
import org.springframework.test.context.ContextConfiguration;
import org.springframework.test.context.junit4.SpringRunner;

import ru.yandex.metrika.api.ApiException;
import ru.yandex.metrika.api.management.client.counter.CounterFlags;
import ru.yandex.metrika.api.management.client.counter.CounterFlagsService;
import ru.yandex.metrika.api.management.client.external.CounterSource;
import ru.yandex.metrika.api.management.config.CounterFlagsServiceConfig;
import ru.yandex.metrika.dbclients.MySqlTestSetup;
import ru.yandex.metrika.rbac.metrika.OwnerOfInternalObjects;

@RunWith(SpringRunner.class)
@ContextConfiguration
public class CounterFlagsServiceValidationTest {

    @Autowired
    private CounterFlagsService counterFlagsService;

    @BeforeClass
    public static void beforeClass() throws Exception {
        MySqlTestSetup.globalSetup();
    }

    @Test(expected = ApiException.class)
    public void testDirectAllowUseGoalsWithoutAccessYaMetrika() {
        CounterFlags counterFlags = getCounterFlagsWithOnlyDirectField(true);
        counterFlagsService.validate(counterFlags, OwnerOfInternalObjects.YA_METRIKA.getUid(), null);
    }

    @Test(expected = ApiException.class)
    public void testDirectAllowUseGoalsWithoutAccessAdInside() {
        CounterFlags counterFlags = getCounterFlagsWithOnlyDirectField(true);
        counterFlagsService.validate(counterFlags, OwnerOfInternalObjects.AD_INSIDE.getUid(), null);
    }

    @Test(expected = ApiException.class)
    public void testDirectAllowUseGoalsWithoutAccessPartner() {
        CounterFlags counterFlags = getCounterFlagsWithOnlyDirectField(true);
        counterFlagsService.validate(counterFlags, 42, CounterSource.partner);
    }

    @Test(expected = ApiException.class)
    public void testDirectAllowUseGoalsWithoutAccessSystem() {
        CounterFlags counterFlags = getCounterFlagsWithOnlyDirectField(true);
        counterFlagsService.validate(counterFlags, 42, CounterSource.system);
    }

    @Test
    public void testDirectAllowUseGoalsWithoutAccessOk() {
        CounterFlags counterFlags = getCounterFlagsWithOnlyDirectField(true);
        counterFlagsService.validate(counterFlags, 42, null);
    }

    private static CounterFlags getCounterFlagsWithOnlyDirectField(Boolean directAllowUseGoalsWithoutAccess) {
        return new CounterFlags(null, null, directAllowUseGoalsWithoutAccess, null,
                null, null, null, null);
    }


    @Configuration
    @Import(CounterFlagsServiceConfig.class)
    public static class Config {}
}
