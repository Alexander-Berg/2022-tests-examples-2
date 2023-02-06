package ru.yandex.autotests.metrika.tests.ft.management.counter.move;

import java.util.Collection;
import java.util.List;

import org.junit.After;
import org.junit.Before;
import org.junit.Test;
import org.junit.runner.RunWith;
import org.junit.runners.Parameterized;

import ru.yandex.autotests.irt.testutils.beandiffer.beanconstraint.BeanConstraint;
import ru.yandex.autotests.irt.testutils.beandiffer.beanconstraint.BeanConstraints;
import ru.yandex.autotests.irt.testutils.beandiffer.matchvariation.DefaultMatchVariation;
import ru.yandex.autotests.metrika.Requirements;
import ru.yandex.autotests.metrika.beans.schemes.CounterFullObjectWrapper;
import ru.yandex.autotests.metrika.data.common.users.User;
import ru.yandex.autotests.metrika.steps.UserSteps;
import ru.yandex.metrika.api.management.client.external.CounterBrief;
import ru.yandex.metrika.api.management.client.external.CounterFull;
import ru.yandex.metrika.api.management.client.external.GrantE;
import ru.yandex.qatools.allure.annotations.Features;
import ru.yandex.qatools.allure.annotations.Issue;
import ru.yandex.qatools.allure.annotations.Stories;
import ru.yandex.qatools.allure.annotations.Title;

import static ch.lambdaj.Lambda.having;
import static ch.lambdaj.Lambda.on;
import static ch.lambdaj.collection.LambdaCollections.with;
import static java.util.Arrays.asList;
import static org.hamcrest.Matchers.allOf;
import static org.hamcrest.Matchers.containsInAnyOrder;
import static org.hamcrest.Matchers.equalTo;
import static org.hamcrest.Matchers.hasItem;
import static org.hamcrest.Matchers.iterableWithSize;
import static org.hamcrest.Matchers.not;
import static org.junit.Assume.assumeThat;
import static org.junit.runners.Parameterized.Parameter;
import static org.junit.runners.Parameterized.Parameters;
import static ru.yandex.autotests.irt.testutils.beandiffer.BeanDifferMatcher.beanEquivalent;
import static ru.yandex.autotests.metrika.data.common.users.User.LOGIN;
import static ru.yandex.autotests.metrika.data.common.users.Users.SIMPLE_USER;
import static ru.yandex.autotests.metrika.data.common.users.Users.SIMPLE_USER2;
import static ru.yandex.autotests.metrika.data.common.users.Users.SIMPLE_USER_PDD;
import static ru.yandex.autotests.metrika.data.common.users.Users.SUPER_USER;
import static ru.yandex.autotests.metrika.data.common.users.Users.USER_WITH_PHONE_LOGIN;
import static ru.yandex.autotests.metrika.data.parameters.management.v1.Fields.all;
import static ru.yandex.autotests.metrika.tests.ft.management.ManagementTestData.createCounterMoveParam;
import static ru.yandex.autotests.metrika.tests.ft.management.ManagementTestData.getCounterWithBasicParameters;
import static ru.yandex.autotests.metrika.tests.ft.management.ManagementTestData.getDefaultCounterWithEditPermission;
import static ru.yandex.autotests.metrika.tests.ft.management.ManagementTestData.getDefaultCounterWithViewPermission;
import static ru.yandex.autotests.metrika.utils.AllureUtils.assertThat;

/**
 * Created by konkov on 08.06.2015.
 */
@Features(Requirements.Feature.MANAGEMENT)
@Stories(Requirements.Story.Management.COUNTERS)
@Title("Проверка переноса счетчика")
@Issue("METR-16688")
@RunWith(Parameterized.class)
public class CounterMovePositiveTest {

    private UserSteps userOwner;
    private UserSteps userRecipient;
    private UserSteps userMover;
    private UserSteps userCleaner;

    private Long counterId;
    private CounterBrief addedCounterBrief;
    private CounterFull addedCounter;

    private static final User OWNER = SIMPLE_USER;
    private static final User CLEANER = SUPER_USER;

    private static final BeanConstraint ignore = BeanConstraints.ignore("updateTime", "monitoring");

    @Parameter(0)
    public CounterFullObjectWrapper counterWrapper;

    @Parameter(1)
    public User mover;

    @Parameter(2)
    public User recipient;

    @Parameter(3)
    public String expectedOwnerLogin;

    @Parameters(name = "{0}, {1}, {2}")
    public static Collection<Object[]> createParameters() {
        return asList(
                createCounterMoveParam(getCounterWithBasicParameters(),
                        OWNER, SIMPLE_USER2),
                createCounterMoveParam(getCounterWithBasicParameters(),
                        OWNER, SIMPLE_USER_PDD),
                createCounterMoveParam(getCounterWithBasicParameters(),
                        SUPER_USER, SIMPLE_USER2),
                createCounterMoveParam(getDefaultCounterWithViewPermission(SIMPLE_USER2),
                        OWNER, SIMPLE_USER2),
                createCounterMoveParam(getDefaultCounterWithEditPermission(SIMPLE_USER2),
                        OWNER, SIMPLE_USER2),
                createCounterMoveParam(getCounterWithBasicParameters(),
                        OWNER, USER_WITH_PHONE_LOGIN, "yandex-team-at-metr-8")
        );
    }

    @Before
    public void before() {
        userCleaner = new UserSteps().withUser(CLEANER);
        userOwner = new UserSteps().withUser(OWNER);
        userMover = new UserSteps().withUser(mover);
        userRecipient = new UserSteps().withUser(recipient);

        addedCounter = userOwner.onManagementSteps().onCountersSteps()
                .addCounterAndExpectSuccess(counterWrapper.get());

        counterId = addedCounter.getId();

        addedCounterBrief = with(userOwner.onManagementSteps().onCountersSteps()
                .getAvailableCountersAndExpectSuccess(all()))
                .first(having(on(CounterBrief.class).getId(), equalTo(counterId)));

        userMover.onManagementSteps().onCountersSteps().moveCounter(counterId, recipient.get(LOGIN));

        //изменяем значения атрибутов на ожидаемые
        addedCounter.setOwnerLogin(expectedOwnerLogin);
        addedCounterBrief.setOwnerLogin(expectedOwnerLogin);

        List<GrantE> expectedGrants = with(addedCounter.getGrants())
                .remove(having(on(GrantE.class).getUserLogin(), equalTo(recipient.get(LOGIN))));
        addedCounter.setGrants(expectedGrants);
        addedCounterBrief.setGrants(expectedGrants);
    }

    @Test
    public void ownerShouldNotHaveCounter() {

        assumeThat("При переносе от владельца к владельцу счетчик никуда не переносится",
                recipient, not(equalTo(OWNER)));

        List<CounterBrief> counters = userOwner.onManagementSteps().onCountersSteps()
                .getAvailableCountersAndExpectSuccess(all());

        assertThat("бывший владелец не имеет перенесенного счетчика", counters,
                not(hasItem(beanEquivalent(addedCounterBrief).fields(ignore))));
    }

    @Test
    public void recipientShouldHaveCounter() {
        List<CounterBrief> counters = userRecipient.onManagementSteps().onCountersSteps()
                .getAvailableCountersAndExpectSuccess(all());

        assertThat("новый владелец имеет перенесенный счетчик", counters,
                hasItem(beanEquivalent(addedCounterBrief).fields(ignore)));
    }

    @Test
    public void recipientShouldHaveOnlyOneCounter() {
        List<CounterBrief> counters = userRecipient.onManagementSteps().onCountersSteps()
                .getAvailableCountersAndExpectSuccess(all());

        int numCounters = with(counters).retain(having(on(CounterBrief.class).getId(), equalTo(counterId))).size();

        assertThat("новый владелец имеет перенесенный счетчик в одном экземпляре", numCounters, equalTo(1));
    }

    @Test
    public void recipientsCounterShouldHaveSameCounterInfo() {
        CounterFull counterInfo = userRecipient.onManagementSteps().onCountersSteps()
                .getCounterInfo(counterId, all());

        assertThat("данные счетчика у нового владельца совпадают с данными счетчика до переноса", counterInfo,
                beanEquivalent(addedCounter)
                        .fields(ignore)
                        .withVariation(new DefaultMatchVariation()
                                .forFields("features")
                                .useMatcher(allOf(
                                        iterableWithSize(addedCounter.getFeatures().size()),
                                        containsInAnyOrder(addedCounter.getFeatures().toArray())
                                ))));

    }

    @After
    public void after() {
        userCleaner.onManagementSteps().onCountersSteps().deleteCounterAndExpectSuccess(counterId);
    }
}
