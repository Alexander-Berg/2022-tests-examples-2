package ru.yandex.autotests.advapi.api.tests.ft.management.placements;

import org.junit.Test;
import org.junit.runner.RunWith;
import org.junit.runners.Parameterized;
import ru.yandex.autotests.advapi.data.users.User;
import ru.yandex.autotests.advapi.steps.UserSteps;
import ru.yandex.autotests.irt.testutils.beandiffer2.comparestrategy.defaultcomparestrategy.DefaultCompareStrategy;
import ru.yandex.qatools.allure.annotations.Features;
import ru.yandex.qatools.allure.annotations.Title;

import java.util.Collection;

import static java.util.Arrays.asList;
import static java.util.Collections.singletonList;
import static ru.yandex.autotests.advapi.api.tests.ft.management.AdvApiFeatures.MANAGEMENT;
import static ru.yandex.autotests.advapi.api.tests.ft.management.ManagementTestUtils.PLACEMENT_268_BEAN;
import static ru.yandex.autotests.advapi.data.users.Users.*;
import static ru.yandex.autotests.irt.testutils.allure.TestSteps.assertThat;
import static ru.yandex.autotests.irt.testutils.beandiffer2.BeanDifferMatcher.beanDiffer;
import static ru.yandex.autotests.irt.testutils.beandiffer2.beanfield.BeanFieldPath.newPath;
import static ru.yandex.autotests.irt.testutils.beandiffer2.comparestrategy.defaultcomparestrategy.DefaultCompareStrategies.allFieldsExcept;

@Features(MANAGEMENT)
@Title("Получение размещений")
@RunWith(Parameterized.class)
public class GetPlacementsTest {

    private static final User OWNER = SIMPLE_USER_1;
    private static final long ADVERTISER_ID = 196L;
    private static final long CAMPAIGN_ID = 256L;
    private static final DefaultCompareStrategy STRATEGY = allFieldsExcept(newPath("0", "site", "siteType"));

    @Parameterized.Parameter()
    public User user;

    @Parameterized.Parameter(1)
    public String message;

    @Parameterized.Parameters(name = "{1}")
    public static Collection<Object[]> createParameters() {
        return asList(new Object[][]{
                {OWNER, "владелец может получить свое размещение"},
                {SUPER_USER, "суперпользователь может получить чужое размещение"},
                {SUPERVISOR, "суперсмотритель может получить чужое размещение"},
                {READ_GUEST, "пользователь с правами на чтение может получить размещение"},
                {WRITE_GUEST, "пользователь с правами на редактирование может получить размещение"}
        });
    }

    @Test
    public void getPlacements() {
        assertThat(message, UserSteps.withUser(user).onPlacementsSteps().getPlacementsAndExpectSuccess(ADVERTISER_ID, CAMPAIGN_ID).getPlacements(), beanDiffer(singletonList(PLACEMENT_268_BEAN)).useCompareStrategy(STRATEGY));
    }
}
