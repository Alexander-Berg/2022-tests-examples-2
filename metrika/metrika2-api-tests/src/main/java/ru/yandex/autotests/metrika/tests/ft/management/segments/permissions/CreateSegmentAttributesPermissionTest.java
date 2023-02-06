package ru.yandex.autotests.metrika.tests.ft.management.segments.permissions;

import org.junit.After;
import org.junit.Before;
import org.junit.BeforeClass;
import org.junit.Test;
import org.junit.runner.RunWith;
import org.junit.runners.Parameterized;
import ru.yandex.autotests.metrika.Requirements;
import ru.yandex.autotests.metrika.beans.schemes.CounterFullObjectWrapper;
import ru.yandex.autotests.metrika.data.common.users.User;
import ru.yandex.autotests.metrika.data.common.users.Users;
import ru.yandex.autotests.metrika.steps.UserSteps;
import ru.yandex.qatools.allure.annotations.Features;
import ru.yandex.qatools.allure.annotations.Issue;
import ru.yandex.qatools.allure.annotations.Stories;
import ru.yandex.qatools.allure.annotations.Title;

import java.util.Collection;

import static java.util.Arrays.asList;
import static org.junit.runners.Parameterized.Parameter;
import static org.junit.runners.Parameterized.Parameters;
import static ru.yandex.autotests.metrika.data.common.users.Users.SIMPLE_USER;
import static ru.yandex.autotests.metrika.errors.ManagementError.ACCESS_DENIED;
import static ru.yandex.autotests.metrika.errors.ManagementError.WRONG_ATTRIBUTE;
import static ru.yandex.autotests.metrika.tests.ft.management.ManagementTestData.*;

/**
 * Created by konkov on 26.02.2015.
 */
@Features(Requirements.Feature.MANAGEMENT)
@Stories(Requirements.Story.Management.SEGMENTS)
@Title("Создание сегмента с private и internal атрибутами для не публичного и публичного счетчиков")
@RunWith(Parameterized.class)
@Issue("METRIKASUPP-4702")
public class CreateSegmentAttributesPermissionTest {

    private final static User OWNER = SIMPLE_USER;
    private final static User ANONYMOUS = Users.SIMPLE_USER2;
    private final static User SUPPORT = Users.SUPPORT;

    protected static UserSteps userSupport;
    protected static UserSteps userOwner;
    protected static UserSteps userAnonymous;

    protected Long counterId;

    @Parameter()
    public CounterFullObjectWrapper counter;

    @Parameters(name = "{0}")
    public static Collection createParameters() {
        return asList(new Object[][]{
                {getNonPublicCounter()},
                {getPublicCounter()}
        });
    }

    @BeforeClass
    public static void init() {
        userSupport = new UserSteps().withUser(SUPPORT);
        userOwner = new UserSteps().withUser(OWNER);
        userAnonymous = new UserSteps().withUser(ANONYMOUS);
    }

    @Before
    public void setup() {
        counterId = userOwner.onManagementSteps().onCountersSteps().addCounterAndExpectSuccess(counter.get()).getId();
    }

    @Test
    public void supportPrivateAllowed() {
        userSupport.onManagementSteps().onSegmentsSteps()
                .createSegmentAndExpectSuccess(counterId, getSegmentWithPrivateAttribute());
    }

    @Test
    public void ownerPrivateAllowed() {
        userOwner.onManagementSteps().onSegmentsSteps()
                .createSegmentAndExpectSuccess(counterId, getSegmentWithPrivateAttribute());
    }

    @Test
    public void anonymousPrivateDisallowed() {
        userAnonymous.onManagementSteps().onSegmentsSteps()
                .createSegmentAndExpectError(ACCESS_DENIED, counterId, getSegmentWithPrivateAttribute());
    }

    @Test
    public void supportInternalAllowed() {
        userSupport.onManagementSteps().onSegmentsSteps()
                .createSegmentAndExpectSuccess(counterId, getSegmentWithInternalAttribute());
    }

    @Test
    public void ownerInternalDisallowed() {
        userOwner.onManagementSteps().onSegmentsSteps()
                .createSegmentAndExpectError(WRONG_ATTRIBUTE, counterId, getSegmentWithInternalAttribute());
    }

    @Test
    public void anonymousInternalDisallowed() {
        userAnonymous.onManagementSteps().onSegmentsSteps()
                .createSegmentAndExpectError(ACCESS_DENIED, counterId, getSegmentWithInternalAttribute());
    }

    @After
    public void teardown() {
        userOwner.onManagementSteps().onCountersSteps().deleteCounterAndExpectSuccess(counterId);
    }

    private static CounterFullObjectWrapper getNonPublicCounter() {
        return new CounterFullObjectWrapper(
                getDefaultCounter().withName(getCounterName("не публичный счетчик ")));
    }

    private static CounterFullObjectWrapper getPublicCounter() {
        return new CounterFullObjectWrapper(
                getDefaultCounterWithPublicStatPermission().withName(getCounterName("публичный счетчик ")));
    }
}
