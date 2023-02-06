package ru.yandex.autotests.metrika.tests.ft.management.counter.grants;

import org.junit.After;
import org.junit.Before;
import org.junit.Test;
import org.junit.runner.RunWith;
import org.junit.runners.Parameterized;
import ru.yandex.autotests.metrika.Requirements;
import ru.yandex.autotests.metrika.data.parameters.management.v1.Field;
import ru.yandex.autotests.metrika.steps.UserSteps;
import ru.yandex.autotests.metrika.tests.ft.management.ManagementTestData;
import ru.yandex.metrika.api.management.client.external.CounterFull;
import ru.yandex.metrika.api.management.client.external.GrantE;
import ru.yandex.metrika.api.management.client.external.GrantType;
import ru.yandex.qatools.allure.annotations.Features;
import ru.yandex.qatools.allure.annotations.Stories;
import ru.yandex.qatools.allure.annotations.Title;

import java.util.Collection;

import static java.util.Arrays.asList;
import static org.hamcrest.Matchers.notNullValue;
import static org.junit.runners.Parameterized.Parameter;
import static org.junit.runners.Parameterized.Parameters;
import static ru.yandex.autotests.irt.testutils.beandiffer.BeanDifferMatcher.beanEquivalent;
import static ru.yandex.autotests.metrika.utils.AllureUtils.assertThat;

/**
 * Created by proxeter on 01.08.2014.
 */
@Features(Requirements.Feature.MANAGEMENT)
@Stories(Requirements.Story.Management.COUNTERS)
@Title("Проверка редактирования прав доступа счетчика")
@RunWith(Parameterized.class)
public class EditCounterGrantsTest {

    private UserSteps user = new UserSteps();

    private Long counterId;
    private CounterFull counter;

    private GrantE resultGrant;

    @Parameter(0)
    public GrantE inputGrant;
    @Parameter(1)
    public GrantE expectedGrant;

    @Before
    public void setup() {
        counter = new CounterFull()
                .withName(ManagementTestData.getCounterName())
                .withSite(ManagementTestData.getCounterSite())
                .withGrants(
                        asList(new GrantE()
                                .withUserLogin("vzlomvk7")
                                .withPerm(GrantType.VIEW)
                                .withComment("Доступ к сайту президента России"))
                );

        counterId = user.onManagementSteps().onCountersSteps().addCounterAndExpectSuccess(counter, Field.GRANTS).getId();

        counter.setGrants(asList(inputGrant));

        CounterFull editedCounter = user.onManagementSteps().onCountersSteps()
                .editCounter(counterId, counter, Field.GRANTS);

        resultGrant = editedCounter.getGrants().get(0);
    }

    @Parameters(name = "Новый доступ: {0}")
    public static Collection<Object[]> createParameters() {
        return asList(
                new Object[]{
                        new GrantE()
                                .withUserLogin("sibvk01")
                                .withPerm(GrantType.EDIT)
                                .withComment("Доступ для пользователя sibvk01"),
                        new GrantE()
                                .withUserLogin("sibvk01")
                                .withPerm(GrantType.EDIT)
                                .withComment("Доступ для пользователя sibvk01"),
                },
                new Object[]{
                        new GrantE()
                                .withUserLogin("vzlomvk7")
                                .withPerm(GrantType.VIEW)
                                .withComment("редактируем комментарий"),
                        new GrantE()
                                .withUserLogin("vzlomvk7")
                                .withPerm(GrantType.VIEW)
                                .withComment("редактируем комментарий"),
                },
                new Object[]{
                        new GrantE()
                                .withUserLogin("Vzlomvk7")
                                .withPerm(GrantType.VIEW)
                                .withComment("Доступ к сайту президента России"),
                        new GrantE()
                                .withUserLogin("vzlomvk7")
                                .withPerm(GrantType.VIEW)
                                .withComment("Доступ к сайту президента России"),
                }
        );
    }

    @Test
    @Title("Права доступа: доступ совпадает с ожидаемым")
    public void grantShouldBeAsExpected() {
        assertThat("доступ совпадает с ожидаемым", resultGrant, beanEquivalent(expectedGrant));
    }

    @Test
    @Title("Права досупа: доступ содержит не нулевую дату создания ")
    public void grantShouldHaveNotNullCreationDate() {
        assertThat("дата создания не пустая", resultGrant.getCreatedAt(), notNullValue());
    }

    @After
    public void tearDown() {
        user.onManagementSteps().onCountersSteps().deleteCounterAndExpectSuccess(counterId);
    }
}
