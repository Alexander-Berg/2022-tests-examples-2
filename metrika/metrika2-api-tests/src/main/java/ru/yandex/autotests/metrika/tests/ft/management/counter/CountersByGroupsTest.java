package ru.yandex.autotests.metrika.tests.ft.management.counter;

import org.junit.Before;
import org.junit.Test;
import ru.yandex.autotests.httpclient.lite.core.IFormParameters;
import ru.yandex.autotests.metrika.Requirements;
import ru.yandex.autotests.metrika.data.parameters.management.v1.AvailableCountersParameters;
import ru.yandex.autotests.metrika.steps.UserSteps;
import ru.yandex.metrika.api.management.client.counter.SpecialLabels;
import ru.yandex.qatools.allure.annotations.Features;
import ru.yandex.qatools.allure.annotations.Stories;
import ru.yandex.qatools.allure.annotations.Title;

import static ru.yandex.autotests.irt.testutils.allure.TestSteps.assertThat;
import static ru.yandex.autotests.irt.testutils.beandiffer.BeanDifferMatcher.beanEquivalent;
import static ru.yandex.autotests.metrika.data.common.users.Users.SIMPLE_USER_GROUP_COUNTERS;
import static ru.yandex.autotests.metrika.data.management.v1.counters.enums.CounterStatusEnum.DELETED;
import static ru.yandex.autotests.metrika.data.management.v1.counters.enums.CounterTypeEnum.PARTNER;
import static ru.yandex.autotests.metrika.data.management.v1.counters.enums.CounterTypeEnum.SIMPLE;
import static ru.yandex.autotests.metrika.utils.AllureUtils.assumeThat;

/**
 * Created by vananos on 18.08.16.
 *
 * Тест ожидает, что у пользователя SIMPLE_USER_GROUP_COUNTERS есть 3 своих счетчика, 1 из которых добавлен в избранное.
 * 1 счетчик пользователя находится в удаленных. Пользователь имеет гостевой доступ к счетчику пользователя USER_GRANTOR
 *
 * Для обеспечения правильности выполнения тестов, перед выполнением теста делается предположение о том, что фактическое
 * количество различных счетчиков пользователя равно эталонному.
 *
 * Все счетчики используемые в тесте, были созданы через UI и не имеют представления в Counters.
 */
@Features(Requirements.Feature.MANAGEMENT)
@Stories(Requirements.Story.Management.COUNTERS)
@Title("Проверка количества счетчиков по группам")
public class CountersByGroupsTest {

    private UserSteps user = new UserSteps().withUser(SIMPLE_USER_GROUP_COUNTERS);
    private SpecialLabels actualCountersAmount;
    private SpecialLabels expectedCountersAmount = new SpecialLabels().withOwn(2L)
            .withFavorite(1L)
            .withDeleted(0L)
            .withGuest(2L)
            .withPartner(0L);

    @Before
    public void setup() {
        SpecialLabels currentCountersAmount = new SpecialLabels()
                .withFavorite(getCountersAmount(new AvailableCountersParameters().withFavorite(true)))
                .withGuest(getCountersAmount(new AvailableCountersParameters().withPermission("view,edit")))
                .withDeleted(getCountersAmount(
                        new AvailableCountersParameters().withStatus(DELETED).withField("labels")))
                .withPartner(getCountersAmount(
                        new AvailableCountersParameters().withType(PARTNER)))
                .withOwn(getCountersAmount(new AvailableCountersParameters().withPermission("own").withType(SIMPLE)));

        assumeThat("количество счетчиков по группам равно эталонному количеству", currentCountersAmount,
                beanEquivalent(expectedCountersAmount));

        actualCountersAmount = user.onManagementSteps().onCountersSteps()
                .getCountersByGroupsAndExpectSuccess();
    }

    private long getCountersAmount(IFormParameters... params) {
        return user.onManagementSteps().onCountersSteps().getCountersAmountAndExceptSuccess(params);
    }

    @Test
    @Title("Количество счетчиков по группам должно совпадать с ожидаемым")
    public void countersAmountByGroupShouldBeAsExpected() {
        assertThat("количество счетчиков совпадает с ожидаемым", actualCountersAmount,
                beanEquivalent(expectedCountersAmount));
    }
}
