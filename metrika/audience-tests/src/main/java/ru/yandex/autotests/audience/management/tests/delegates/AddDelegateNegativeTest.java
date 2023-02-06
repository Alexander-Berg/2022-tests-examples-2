package ru.yandex.autotests.audience.management.tests.delegates;

import com.google.common.collect.ImmutableList;
import org.apache.commons.lang3.StringUtils;
import org.junit.Test;
import org.junit.runner.RunWith;
import org.junit.runners.Parameterized;
import org.junit.runners.Parameterized.Parameter;
import ru.yandex.autotests.audience.data.wrappers.DelegateWrapper;
import ru.yandex.autotests.audience.management.tests.Requirements;
import ru.yandex.autotests.audience.steps.UserSteps;
import ru.yandex.autotests.irt.testutils.RandomUtils;
import ru.yandex.autotests.metrika.commons.response.IExpectedError;
import ru.yandex.qatools.allure.annotations.Features;
import ru.yandex.qatools.allure.annotations.Stories;
import ru.yandex.qatools.allure.annotations.Title;

import java.util.Collection;

import static ru.yandex.autotests.audience.data.users.Users.SIMPLE_USER;
import static ru.yandex.autotests.audience.errors.ManagementError.LOGIN_NOT_NULL;
import static ru.yandex.autotests.audience.errors.ManagementError.USER_NOT_FOUND;
import static ru.yandex.autotests.audience.management.tests.TestData.createDelegateNegativeParam;
import static ru.yandex.metrika.audience.pubapi.DelegateType.EDIT;
import static ru.yandex.metrika.audience.pubapi.DelegateType.VIEW;

/**
 * Created by ava1on on 26.05.17.
 */
@Features(Requirements.Feature.MANAGEMENT)
@Stories({Requirements.Story.Management.GRANTS})
@Title("Представители: назначение представителя (негативные тесты)")
@RunWith(Parameterized.class)
public class AddDelegateNegativeTest {
    private final UserSteps user = UserSteps.withUser(SIMPLE_USER);

    @Parameter()
    public String description;

    @Parameter(1)
    public DelegateWrapper delegateWrapper;

    @Parameter(2)
    public IExpectedError error;

    @Parameterized.Parameters(name = "{0}")
    public static Collection<Object[]> createParameters() {
        return ImmutableList.of(
                createDelegateNegativeParam("отсутствует userLogin", null, VIEW, LOGIN_NOT_NULL),
                createDelegateNegativeParam("пустой userLogin", StringUtils.EMPTY, EDIT, LOGIN_NOT_NULL),
                createDelegateNegativeParam("несуществуюший аккаунт", RandomUtils.getString(14), VIEW,
                        USER_NOT_FOUND)
        );
    }

    @Test
    public void checkTryAddDelegate() {
        user.onDelegatesSteps().createDelegateAndExpectError(error, delegateWrapper);
    }
}
