package ru.yandex.autotests.metrika.tests.ft.management.delegates;

import org.junit.Before;
import org.junit.Test;
import ru.yandex.autotests.irt.testutils.allure.TestSteps;
import ru.yandex.autotests.metrika.Requirements;
import ru.yandex.autotests.metrika.data.common.users.User;
import ru.yandex.autotests.metrika.steps.UserSteps;
import ru.yandex.qatools.allure.annotations.Features;
import ru.yandex.qatools.allure.annotations.Stories;
import ru.yandex.qatools.allure.annotations.Title;

import static ru.yandex.autotests.irt.testutils.beandiffer.BeanDifferMatcher.beanEquivalent;
import static ru.yandex.autotests.metrika.data.common.users.Users.SIMPLE_USER_ONLY_FOR_QUOTAS;

@Features(Requirements.Feature.MANAGEMENT)
@Stories(Requirements.Story.Management.DELEGATE)
@Title("Проверка размера множителя квот на представителей юзера")
public class DelegateQuotaMultiplierTest {

    private static final User OWNER = SIMPLE_USER_ONLY_FOR_QUOTAS;

    private UserSteps owner;

    @Before
    public void setup() {
        owner = new UserSteps().withUser(OWNER);
    }

    @Test
    public void check() {
        double actualMultiplier = owner.onManagementSteps().onQuotaMultiplierSteps().getDelegateQuotaMultiplier();

        System.out.println(actualMultiplier);

        TestSteps.assertThat(
                "у владелца " + OWNER + ", размер множителя на представителей должно равняться к 0",
                actualMultiplier,
                beanEquivalent(0.0)
        );
    }
}
