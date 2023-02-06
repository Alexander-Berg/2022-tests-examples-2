package ru.yandex.autotests.audience.management.tests.delegates;

import org.junit.Before;
import org.junit.Test;
import ru.yandex.autotests.audience.management.tests.Requirements;
import ru.yandex.autotests.audience.steps.UserSteps;
import ru.yandex.metrika.audience.pubapi.Delegate;
import ru.yandex.metrika.audience.pubapi.DelegateType;
import ru.yandex.qatools.allure.annotations.Features;
import ru.yandex.qatools.allure.annotations.Stories;
import ru.yandex.qatools.allure.annotations.Title;

import java.util.List;

import static org.hamcrest.Matchers.not;
import static ru.yandex.autotests.audience.data.users.Users.SIMPLE_USER;
import static ru.yandex.autotests.audience.data.users.Users.USER_GRANTEE;
import static ru.yandex.autotests.audience.data.wrappers.DelegateWrapper.wrap;
import static ru.yandex.autotests.audience.management.tests.TestData.getDelegate;
import static ru.yandex.autotests.irt.testutils.allure.TestSteps.assertThat;
import static ru.yandex.autotests.metrika.commons.beans.BeanDifferMatchers.hasBeanEquivalent;

/**
 * Created by ava1on on 26.05.17.
 */
@Features(Requirements.Feature.MANAGEMENT)
@Stories({Requirements.Story.Management.GRANTS})
@Title("Представители: удаление представителя")
public class DeleteDelegateTest {
    private final UserSteps user = UserSteps.withUser(SIMPLE_USER);

    private Delegate delegate;

    @Before
    public void setup() {
        delegate = getDelegate(USER_GRANTEE, DelegateType.VIEW);
        user.onDelegatesSteps().createDelegate(wrap(delegate));

        user.onDelegatesSteps().deleteDelegate(delegate.getUserLogin());
    }

    @Test
    public void checkDeleteDelegate() {
        List<Delegate> delegates = user.onDelegatesSteps().getDelegates();

        assertThat("представитель отсутствует в списке", delegates,
                not(hasBeanEquivalent(Delegate.class, delegate)));
    }
}
