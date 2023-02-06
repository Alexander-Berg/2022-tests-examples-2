package ru.yandex.autotests.audience.management.tests.delegates;

import com.google.common.collect.ImmutableList;
import org.junit.After;
import org.junit.Before;
import org.junit.Test;
import org.junit.runner.RunWith;
import org.junit.runners.Parameterized;
import org.junit.runners.Parameterized.Parameter;
import ru.yandex.autotests.audience.data.users.User;
import ru.yandex.autotests.audience.management.tests.Requirements;
import ru.yandex.autotests.audience.steps.UserSteps;
import ru.yandex.metrika.audience.pubapi.Delegate;
import ru.yandex.metrika.audience.pubapi.DelegateType;
import ru.yandex.qatools.allure.annotations.Features;
import ru.yandex.qatools.allure.annotations.Stories;
import ru.yandex.qatools.allure.annotations.Title;

import java.util.Collection;
import java.util.List;

import static org.apache.commons.lang3.ArrayUtils.toArray;
import static ru.yandex.autotests.audience.data.users.Users.*;
import static ru.yandex.autotests.audience.data.wrappers.DelegateWrapper.wrap;
import static ru.yandex.autotests.audience.management.tests.TestData.getDelegate;
import static ru.yandex.autotests.metrika.commons.beans.BeanDifferMatchers.hasBeanEquivalent;
import static ru.yandex.autotests.irt.testutils.allure.TestSteps.assertThat;
import static ru.yandex.metrika.audience.pubapi.DelegateType.EDIT;
import static ru.yandex.metrika.audience.pubapi.DelegateType.VIEW;

/**
 * Created by ava1on on 26.05.17.
 */
@Features(Requirements.Feature.MANAGEMENT)
@Stories({Requirements.Story.Management.GRANTS})
@Title("Представители: назначение представителя")
@RunWith(Parameterized.class)
public class AddDelegateTest {
    private final UserSteps user = UserSteps.withUser(USER_DELEGATOR_2);

    private Delegate delegate;

    @Parameter
    public DelegateType perm;

    @Parameter(1)
    public User userParam;

    @Parameterized.Parameters(name = "{0}")
    public static Collection<Object[]> createParameters() {
        return ImmutableList.of(
                toArray(VIEW, USER_WITH_PERM_VIEW),
                toArray(EDIT, USER_WITH_PERM_EDIT)
        );
    }

    @Before
    public void setup() {
        delegate = getDelegate(userParam.toString(), perm);

        user.onDelegatesSteps().createDelegate(wrap(delegate));
    }

    @Test
    public void checkAddDelegate() {
        List<Delegate> delegates = user.onDelegatesSteps().getDelegates();

        assertThat("представитель присутствует в списке", delegates,
                hasBeanEquivalent(Delegate.class, delegate));
    }

    @After
    public void tearDown() {
        user.onDelegatesSteps().deleteDelegate(delegate.getUserLogin());
    }
}
