package ru.yandex.autotests.metrika.tests.ft.management.counter.grants;

import org.junit.After;
import org.junit.Before;
import org.junit.BeforeClass;
import org.junit.Test;
import org.junit.runner.RunWith;
import org.junit.runners.Parameterized;
import ru.yandex.autotests.httpclient.lite.core.IFormParameters;
import ru.yandex.autotests.metrika.Requirements;
import ru.yandex.autotests.metrika.beans.schemes.AddGrantRequestObjectWrapper;
import ru.yandex.autotests.metrika.data.common.users.User;
import ru.yandex.autotests.metrika.steps.UserSteps;
import ru.yandex.metrika.api.management.client.external.CounterGrantRequest;
import ru.yandex.metrika.api.management.client.external.GrantE;
import ru.yandex.qatools.allure.annotations.Features;
import ru.yandex.qatools.allure.annotations.Stories;
import ru.yandex.qatools.allure.annotations.Title;

import java.util.Collection;
import java.util.List;
import java.util.Objects;

import static java.util.Arrays.asList;
import static org.hamcrest.Matchers.hasItem;
import static org.hamcrest.Matchers.not;
import static org.junit.runners.Parameterized.Parameter;
import static org.junit.runners.Parameterized.Parameters;
import static ru.yandex.autotests.irt.testutils.beandiffer.BeanDifferMatcher.beanEquivalent;
import static ru.yandex.autotests.metrika.data.common.users.User.LOGIN;
import static ru.yandex.autotests.metrika.data.common.users.Users.*;
import static ru.yandex.autotests.metrika.data.parameters.management.v1.DelegateParameters.ulogin;
import static ru.yandex.autotests.metrika.tests.ft.management.ManagementTestData.createGrantRequestParam;
import static ru.yandex.autotests.metrika.tests.ft.management.ManagementTestData.getDefaultCounter;
import static ru.yandex.autotests.metrika.utils.AllureUtils.assertThat;
import static ru.yandex.autotests.metrika.utils.AllureUtils.assumeThat;
import static ru.yandex.metrika.api.management.client.external.GrantType.EDIT;
import static ru.yandex.metrika.api.management.client.external.GrantType.fromValue;

/**
 * Created by konkov on 08.12.2015.
 */
@Features(Requirements.Feature.MANAGEMENT)
@Stories({
        Requirements.Story.Management.COUNTERS,
        Requirements.Story.Management.GRANTS
})
@Title("Проверка запросов на доступы")
@RunWith(Parameterized.class)
public class GrantRequestTest {

    private static UserSteps user;
    private static UserSteps userOwner;
    private UserSteps userDecider;

    private static final User OWNER = USER_DELEGATOR;
    private static final User DELEGATE = USER_DELEGATE_PERMANENT;
    private static final User GRANTED_USER = SIMPLE_USER3;

    @Parameter(0)
    public AddGrantRequestObjectWrapper grantRequest;

    @Parameter(1)
    public CounterGrantRequest expectedGrantRequest;

    @Parameter(2)
    public User decider;

    @Parameter(3)
    public IFormParameters ulogin;

    private Long counterId;

    @Parameters(name = "Запрос: {0}, кто обрабатывает {2}")
    public static Collection<Object[]> createParameters() {
        return asList(
                createParam(SIMPLE_USER2, "RO", OWNER),
                createParam(SIMPLE_USER2, "RW", OWNER),
                createParam(SIMPLE_USER2_EMAIL, "RW", SIMPLE_USER2.get(LOGIN), OWNER),
                createParam(SIMPLE_USER_PDD, "RW", OWNER),
                createParam(USER_WITH_PHONE_LOGIN, "RW", "yandex-team-at-metr-8", OWNER),
                createParam(USER_WITH_PHONE_ONLY_LOGIN, "RW", "yandex-team-at-metr-8", OWNER),
                createParam(SIMPLE_USER2, "RW", SUPPORT),
                createParam(SIMPLE_USER2, "RW", DELEGATE, ulogin(OWNER)),
                createParam(SIMPLE_USER2, "RW", GRANTED_USER)
        );
    }

    @BeforeClass
    public static void init() {
        user = new UserSteps();
        userOwner = new UserSteps().withUser(OWNER);
    }

    @Before
    public void setup() {
        userDecider = new UserSteps().withUser(decider);

        counterId = userOwner.onManagementSteps().onCountersSteps()
                .addCounterAndExpectSuccess(getDefaultCounter()).getId();

        //выдать гостевой доступ
        userOwner.onManagementSteps().onGrantsSteps().setGrantAndExpectSuccess(counterId,
                new GrantE()
                        .withUserLogin(GRANTED_USER.get(LOGIN))
                        .withPerm(EDIT));

        user.onManagementSteps().onGrantRequestsSteps()
                .requestGrantAndExpectSuccess(grantRequest.getClone().withObjectId(Objects.toString(counterId)));

        List<CounterGrantRequest> grantRequests = userDecider.onManagementSteps().onGrantRequestsSteps()
                .getGrantRequestsAndExpectSuccess(counterId, ulogin);

        assumeThat("запрос на доступ присутствует в списке", grantRequests,
                hasItem(beanEquivalent(expectedGrantRequest)));
    }

    @Test
    public void accept() {
        userDecider.onManagementSteps().onGrantRequestsSteps()
                .acceptGrantRequestAndExpectSuccess(counterId, expectedGrantRequest, ulogin);

        List<CounterGrantRequest> grantRequests = userDecider.onManagementSteps().onGrantRequestsSteps()
                .getGrantRequestsAndExpectSuccess(counterId);

        assumeThat("запрос на доступ не присутствует в списке", grantRequests,
                not(hasItem(beanEquivalent(expectedGrantRequest))));

        List<GrantE> grants = userOwner.onManagementSteps().onGrantsSteps()
                .getGrantsAndExpectSuccess(counterId);

        assertThat("доступ принятого запроса присутствует в списке доступов счетчика", grants,
                hasItem(beanEquivalent(getExpectedGrant(expectedGrantRequest))));
    }

    @Test
    public void reject() {
        userDecider.onManagementSteps().onGrantRequestsSteps()
                .rejectGrantRequestAndExpectSuccess(counterId, expectedGrantRequest, ulogin);

        List<CounterGrantRequest> grantRequests = userDecider.onManagementSteps().onGrantRequestsSteps()
                .getGrantRequestsAndExpectSuccess(counterId);

        assumeThat("запрос на доступ не присутствует в списке", grantRequests,
                not(hasItem(beanEquivalent(expectedGrantRequest))));

        List<GrantE> grants = userOwner.onManagementSteps().onGrantsSteps()
                .getGrantsAndExpectSuccess(counterId);

        assertThat("доступ отклоненного запроса не присутствует в списке доступов счетчика", grants,
                not(hasItem(beanEquivalent(getExpectedGrant(expectedGrantRequest)))));
    }

    @After
    public void teardown() {
        userOwner.onManagementSteps().onGrantsSteps().deleteGrantAndExpectSuccess(counterId, GRANTED_USER.get(LOGIN));
        userOwner.onManagementSteps().onCountersSteps().deleteCounterAndExpectSuccess(counterId);
    }

    private GrantE getExpectedGrant(CounterGrantRequest expectedGrantRequest) {
        return new GrantE()
                .withUserLogin(expectedGrantRequest.getUserLogin())
                .withPerm(fromValue(expectedGrantRequest.getPerm().toString()))
                .withComment(expectedGrantRequest.getComment());
    }

    private static Object[] createParam(User requestor, String permission, User decider,
                                        IFormParameters parameters) {
        return createGrantRequestParam(OWNER, requestor, permission, requestor.get(LOGIN), decider, parameters);
    }

    private static Object[] createParam(User requestor, String permission, User decider) {
        return createGrantRequestParam(OWNER, requestor, permission, requestor.get(LOGIN), decider);
    }

    private static Object[] createParam(User requestor, String permission, String userLogin, User decider) {
        return createGrantRequestParam(OWNER, requestor, permission, userLogin, decider);
    }
}
