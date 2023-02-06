package ru.yandex.autotests.metrika.tests.ft.management.counter;

import org.junit.After;
import org.junit.Test;

import ru.yandex.autotests.metrika.Requirements;
import ru.yandex.autotests.metrika.steps.UserSteps;
import ru.yandex.metrika.api.management.client.external.CounterFull;
import ru.yandex.metrika.api.management.client.external.CounterMirrorE;
import ru.yandex.qatools.allure.annotations.Features;
import ru.yandex.qatools.allure.annotations.Stories;
import ru.yandex.qatools.allure.annotations.Title;

import static java.util.Collections.singletonList;
import static ru.yandex.autotests.metrika.data.common.users.Users.USER_FOR_SITE_PATH_DUPLICATES_VALIDATION;
import static ru.yandex.autotests.metrika.errors.ManagementError.COUNTER_ALREADY_EXISTS;
import static ru.yandex.autotests.metrika.tests.ft.management.ManagementTestData.getCounterWithBasicParameters;

@Features(Requirements.Feature.MANAGEMENT)
@Stories(Requirements.Story.Management.COUNTERS)
@Title("Счетчик: проверка валидации дубликатов по адресу сайта")
public class CounterSitePathDuplicatesValidationTest {

    public static final String COUNTER_NAME = "Дом Котлов на Маркете";
    public static final String SITE_WITH_PATH_1 = "market.yandex.ru/business/1044273";
    public static final String SITE_WITH_PATH_2 = "market.yandex.ru/business/853340";
    public static final String SITE_DOMAIN_ONLY = "market.yandex.ru";

    private static final UserSteps user = new UserSteps().withUser(USER_FOR_SITE_PATH_DUPLICATES_VALIDATION);

    @Test
    @Title("Добавление счетчика с адресом содержащим только домен")
    public void testAdd() {
        // Должна быть возможность добавить счетчик с адресом содержащим только домен,
        // когда у пользователя уже есть другой счетчик с таким же названием и с адресом содержащим этот домен и непустой путь
        user.onManagementSteps().onCountersSteps()
                .addCounterAndExpectSuccess(getCounterWithBasicParameters()
                        .withName(COUNTER_NAME)
                        .withSite2(mirror(SITE_WITH_PATH_1))
                );

        user.onManagementSteps().onCountersSteps()
                .addCounterAndExpectSuccess(getCounterWithBasicParameters()
                        .withName(COUNTER_NAME)
                        .withSite2(mirror(SITE_DOMAIN_ONLY))
                );
    }

    @Test
    @Title("Изменение адреса на домен")
    public void testEdit() {
        // Должна быть возможность поменять адрес на домен,
        // когда у пользователя уже есть другой счетчик с таким же названием и с адресом содержащим этот домен и непустой путь
        user.onManagementSteps().onCountersSteps()
                .addCounterAndExpectSuccess(getCounterWithBasicParameters()
                        .withName(COUNTER_NAME)
                        .withSite2(mirror(SITE_WITH_PATH_1))
                );

        CounterFull counter = user.onManagementSteps().onCountersSteps()
                .addCounterAndExpectSuccess(getCounterWithBasicParameters()
                        .withName(COUNTER_NAME)
                        .withSite2(mirror(SITE_WITH_PATH_2))
                );

        user.onManagementSteps().onCountersSteps()
                .editCounter(counter.getId(), counter.withSite2(mirror(SITE_DOMAIN_ONLY)));
    }

    @Test
    @Title("Добавление зеркала с адресом содержащим только домен")
    public void testAddMirror() {
        // Должна быть возможность добавить зеркало с адресом содержащим только домен,
        // когда у пользователя уже есть другой счетчик с таким же названием и с адресом содержащим этот домен и непустой путь
        user.onManagementSteps().onCountersSteps()
                .addCounterAndExpectSuccess(getCounterWithBasicParameters()
                        .withName(COUNTER_NAME)
                        .withSite2(mirror(SITE_WITH_PATH_1))
                );

        CounterFull counter = user.onManagementSteps().onCountersSteps()
                .addCounterAndExpectSuccess(getCounterWithBasicParameters()
                        .withName(COUNTER_NAME)
                        .withSite2(mirror(SITE_WITH_PATH_2))
                );

        user.onManagementSteps().onCountersSteps()
                .editCounter(counter.getId(), counter.withMirrors2(singletonList(mirror(SITE_DOMAIN_ONLY))));
    }

    @Test
    @Title("Добавление счетчика с уже существующим адресом")
    public void testAddNegative() {
        // Не должно быть возможности добавить счетчик с адресом,
        // когда у пользователя уже есть другой счетчик с таким же названием и адресом
        user.onManagementSteps().onCountersSteps()
                .addCounterAndExpectSuccess(getCounterWithBasicParameters()
                        .withName(COUNTER_NAME)
                        .withSite2(mirror(SITE_WITH_PATH_1))
                );

        user.onManagementSteps().onCountersSteps()
                .addCounterAndExpectError(COUNTER_ALREADY_EXISTS, getCounterWithBasicParameters()
                        .withName(COUNTER_NAME)
                        .withSite2(mirror(SITE_WITH_PATH_1))
                );
    }

    @Test
    @Title("Изменение адреса на уже существующий")
    public void testEditNegative() {
        // Не должно быть возможности поменять адрес,
        // когда у пользователя уже есть другой счетчик с таким же названием и адресом
        user.onManagementSteps().onCountersSteps()
                .addCounterAndExpectSuccess(getCounterWithBasicParameters()
                        .withName(COUNTER_NAME)
                        .withSite2(mirror(SITE_WITH_PATH_1))
                );

        CounterFull counter = user.onManagementSteps().onCountersSteps()
                .addCounterAndExpectSuccess(getCounterWithBasicParameters()
                        .withName(COUNTER_NAME)
                        .withSite2(mirror(SITE_WITH_PATH_2))
                );

        user.onManagementSteps().onCountersSteps()
                .editCounterAndExpectError(COUNTER_ALREADY_EXISTS, counter.getId(),
                        counter.withSite2(mirror(SITE_WITH_PATH_1))
                );
    }

    @Test
    @Title("Добавление зеркала с уже существующим адресом")
    public void testAddMirrorNegative() {
        // Не должно быть возможности добавить зеркало с адресом,
        // когда у пользователя уже есть другой счетчик с таким же названием и адресом
        user.onManagementSteps().onCountersSteps()
                .addCounterAndExpectSuccess(getCounterWithBasicParameters()
                        .withName(COUNTER_NAME)
                        .withSite2(mirror(SITE_WITH_PATH_1))
                );

        CounterFull counter = user.onManagementSteps().onCountersSteps()
                .addCounterAndExpectSuccess(getCounterWithBasicParameters()
                        .withName(COUNTER_NAME)
                        .withSite2(mirror(SITE_WITH_PATH_2))
                );

        user.onManagementSteps().onCountersSteps()
                .editCounterAndExpectError(COUNTER_ALREADY_EXISTS, counter.getId(),
                        counter.withMirrors2(singletonList(mirror(SITE_WITH_PATH_1)))
                );
    }

    @After
    public void teardown() {
        user.onManagementSteps().onCountersSteps().deleteAllCounters();
    }

    private CounterMirrorE mirror(String site) {
        return new CounterMirrorE().withSite(site);
    }
}
