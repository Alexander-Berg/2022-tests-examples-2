package ru.yandex.autotests.internalapid.tests;

import java.util.ArrayList;
import java.util.Arrays;
import java.util.Collections;
import java.util.Date;
import java.util.List;
import java.util.Optional;
import java.util.Random;

import com.google.common.collect.Lists;
import org.hamcrest.Matchers;
import org.joda.time.DateTime;
import org.junit.Assert;
import org.junit.BeforeClass;
import org.junit.Test;

import ru.yandex.autotests.internalapid.beans.data.Counters;
import ru.yandex.autotests.internalapid.beans.data.User;
import ru.yandex.autotests.internalapid.beans.data.Users;
import ru.yandex.autotests.internalapid.beans.responses.DirectUpdatedUserCountersNumResponse;
import ru.yandex.autotests.internalapid.beans.responses.DirectUserCountersNumExtendedResponse;
import ru.yandex.autotests.internalapid.beans.responses.DirectUserCountersNumResponse;
import ru.yandex.autotests.internalapid.beans.responses.DirectUsersCountersNumAdditionalResponse;
import ru.yandex.autotests.internalapid.beans.responses.ListResponse;
import ru.yandex.autotests.internalapid.util.DataUtil;
import ru.yandex.autotests.irt.testutils.beandiffer.BeanDifferMatcher;
import ru.yandex.autotests.metrika.commons.response.CustomError;
import ru.yandex.metrika.api.Feature;
import ru.yandex.metrika.api.management.client.AddGrantRequest;
import ru.yandex.metrika.api.management.client.AddGrantRequestInnerAddRequestType;
import ru.yandex.metrika.api.management.client.GrantRequestServiceInnerGrantRequestStatus;
import ru.yandex.metrika.api.management.client.GrantRequestServiceInnerGrantResult;
import ru.yandex.metrika.api.management.client.external.CounterFull;
import ru.yandex.metrika.api.management.client.external.CounterSource;
import ru.yandex.metrika.api.management.client.external.goals.GoalCondition;
import ru.yandex.metrika.api.management.client.external.goals.GoalConditionType;
import ru.yandex.metrika.api.management.client.external.goals.GoalE;
import ru.yandex.metrika.api.management.client.external.goals.GoalType;
import ru.yandex.metrika.api.management.client.external.goals.UrlGoal;
import ru.yandex.metrika.internalapid.common.ExistentCounter;
import ru.yandex.metrika.internalapid.direct.external.CounterGoal;
import ru.yandex.qatools.allure.annotations.Title;

import static org.hamcrest.Matchers.allOf;
import static org.hamcrest.Matchers.equalTo;
import static org.hamcrest.Matchers.everyItem;
import static org.hamcrest.Matchers.greaterThan;
import static org.hamcrest.Matchers.greaterThanOrEqualTo;
import static org.hamcrest.Matchers.hasItem;
import static org.hamcrest.Matchers.hasProperty;
import static org.hamcrest.Matchers.iterableWithSize;
import static org.hamcrest.Matchers.not;
import static org.hamcrest.Matchers.nullValue;
import static org.hamcrest.Matchers.startsWith;
import static ru.yandex.autotests.irt.testutils.allure.TestSteps.assertThat;
import static ru.yandex.autotests.irt.testutils.beandiffer.BeanDifferMatcher.beanEquivalent;
import static ru.yandex.autotests.irt.testutils.beandiffer.beanconstraint.BeanConstraints.only;

@Title("Тесты ручек директа")
public class DirectTest extends InternalApidTest {

    private static CounterFull COUNTER;
    private static CounterFull COUNTER_2;
    private static final Random rnd = new Random();

    @BeforeClass
    public static void init() {
        COUNTER = userSteps.onInternalApidSteps().createCounter(new CounterFull().withName(DataUtil.getRandomCounterName()).withSite("test.ru"));
        COUNTER_2 = userSteps.onInternalApidSteps().createCounter(new CounterFull().withName(DataUtil.getRandomCounterName()).withSite("test-2.ru"));
    }

    @Test
    @Title("Тест ручки /display/create_new_goal")
    public void testDisplayCreateNewGoal() {
        GoalE goal = makeSimpleGoal();
        final GoalE result = userSteps.onDirectSteps().addDisplayGoal(COUNTER.getId(), goal);
        assertThat("Создали цель", result, BeanDifferMatcher.beanEquivalent(goal).fields(only("name", "type")));
    }

    @Test
    @Title("Тест ручки /direct/changed_goals")
    public void testChangedGoals() {
        DateTime current = DateTime.now();
        GoalE goal = makeSimpleGoal();
        final GoalE newGoal = userSteps.onDirectSteps().addDisplayGoal(COUNTER.getId(), goal);
        final List<Integer> changedGoalsIds = userSteps.onDirectSteps().getChangedGoalsIds(current.minusSeconds(5));
        assertThat("Новая цель есть в списке измененных", changedGoalsIds, hasItem(newGoal.getId().intValue()));
    }

    @Test
    @Title("Тест ручки /direct/counter_goals")
    public void testCounterGoalsDirect() {
        GoalE goal = makeSimpleGoal();
        userSteps.onDirectSteps().addDisplayGoal(COUNTER.getId(), goal);
        final List<CounterGoal> counterGoals = userSteps.onDirectSteps().getCounterGoalsDirect(Lists.newArrayList(COUNTER.getId(), Counters.METRIKA.getId()));
        assertThat("Список целей больше 1 и содержит новую цель",
                counterGoals,
                allOf(
                        iterableWithSize(Matchers.greaterThan(1)),
                        hasItem(
                                allOf(
                                        hasProperty("counterId", equalTo(COUNTER.getId())),
                                        hasProperty("goal", hasProperty("name", equalTo(goal.getName())))
                                )
                        )
                )
        );
    }

    @Test
    @Title("Тест ручки /goals/v1/counter_goals")
    public void testCounterGoals() {
        GoalE goal = makeSimpleGoal();
        userSteps.onDirectSteps().addDisplayGoal(COUNTER.getId(), goal);
        final List<CounterGoal> counterGoals = userSteps.onDirectSteps().getCounterGoals(Lists.newArrayList(COUNTER.getId(), Counters.METRIKA.getId()));
        assertThat("Список целей больше 1 и содержит новую цель",
                counterGoals,
                allOf(
                        iterableWithSize(Matchers.greaterThan(1)),
                        hasItem(
                                allOf(
                                        hasProperty("counterId", equalTo(COUNTER.getId())),
                                        hasProperty("goal", hasProperty("name", equalTo(goal.getName())))
                                )
                        )
                )
        );
    }

    @Test
    @Title("Тест ручки /internal/grant_requests")
    public void testGrantRequests() {
        final AddGrantRequest grantRequest = new AddGrantRequest()
                .withObjectType(AddGrantRequestInnerAddRequestType.COUNTER)
                .withObjectId(COUNTER.getId().toString())
                .withPermission("RW")
                .withRequestorLogin(Users.METRIKA_INTAPI_GRANTEE.get(User.LOGIN))
                .withOwnerLogin(Users.METRIKA_INTAPI_AUTO.get(User.LOGIN));
        final List<GrantRequestServiceInnerGrantResult> results = userSteps.onDirectSteps().addGrants(Lists.newArrayList(grantRequest));

        assertThat("Запрошенные права должны обработаться правильно", results,
                allOf(
                        iterableWithSize(1),
                        hasItem(
                                allOf(
                                        hasProperty("objectId", equalTo(grantRequest.getObjectId())),
                                        hasProperty("result", equalTo("ok"))
                                ))
                )
        );
    }

    @Test
    @Title("Тест ручки /internal/grant_requests (с фейковым owner_login)")
    public void testGrantRequestsWithFakeOwnerLogin() {
        final AddGrantRequest grantRequest = new AddGrantRequest()
                .withObjectType(AddGrantRequestInnerAddRequestType.COUNTER)
                .withObjectId(COUNTER.getId().toString())
                .withPermission("RW")
                .withRequestorLogin(Users.METRIKA_INTAPI_GRANTEE.get(User.LOGIN))
                .withOwnerLogin("blablabla");
        final List<GrantRequestServiceInnerGrantResult> results = userSteps.onDirectSteps().addGrants(Lists.newArrayList(grantRequest));

        assertThat("Запрошенные права должны обработаться правильно", results,
                allOf(
                        iterableWithSize(1),
                        hasItem(
                                allOf(
                                        hasProperty("objectId", equalTo(grantRequest.getObjectId())),
                                        hasProperty("result", equalTo("error"))
                                ))
                )
        );
    }

    @Test
    @Title("Тест ручки /internal/grant_requests (без параметра owner_login)")
    public void testGrantRequestsWithoutOwnerLoginParameter() {
        final AddGrantRequest grantRequest = new AddGrantRequest()
                .withObjectType(AddGrantRequestInnerAddRequestType.COUNTER)
                .withObjectId(COUNTER.getId().toString())
                .withPermission("RW")
                .withRequestorLogin(Users.METRIKA_INTAPI_DELEGATE.get(User.LOGIN));
        final List<GrantRequestServiceInnerGrantResult> results = userSteps.onDirectSteps().addGrants(Lists.newArrayList(grantRequest));

        assertThat("Запрошенные права должны обработаться правильно", results,
                allOf(
                        iterableWithSize(1),
                        hasItem(
                                allOf(
                                        hasProperty("objectId", equalTo(grantRequest.getObjectId())),
                                        hasProperty("result", equalTo("ok"))
                                ))
                )
        );
    }

    @Test
    @Title("Тест ручки /internal/user/{uid}/grant_access_requests_status")
    public void testGrantAccessRequestsStatus() {
        Long counterId = COUNTER.getId();
        Long counter2Id = COUNTER_2.getId();

        final AddGrantRequest grantRequest = new AddGrantRequest()
                .withObjectType(AddGrantRequestInnerAddRequestType.COUNTER)
                .withObjectId(counterId.toString())
                .withPermission("RW")
                .withRequestorLogin(Users.METRIKA_INTAPI_GRANTEE.get(User.LOGIN))
                .withOwnerLogin(Users.METRIKA_INTAPI_AUTO.get(User.LOGIN));

        final AddGrantRequest grantRequest2 = new AddGrantRequest()
                .withObjectType(AddGrantRequestInnerAddRequestType.COUNTER)
                .withObjectId(counter2Id.toString())
                .withPermission("RO")
                .withRequestorLogin(Users.METRIKA_INTAPI_GRANTEE.get(User.LOGIN))
                .withOwnerLogin(Users.METRIKA_INTAPI_AUTO.get(User.LOGIN));

        userSteps.onDirectSteps().addGrants(
                Lists.newArrayList(grantRequest, grantRequest2)
        );

        long uid = Users.METRIKA_INTAPI_GRANTEE.get(User.UID);

        List<Long> counterIdList = Arrays.asList(counterId, 234432L, counter2Id, 232222L, 1232L);

        final List<GrantRequestServiceInnerGrantRequestStatus> results = userSteps.onDirectSteps().postGrantAccessRequestsStatusAndExpectSuccess(uid, counterIdList);

        for (GrantRequestServiceInnerGrantRequestStatus grantRequestStatus : results) {
            boolean expectedAccessRequested = Arrays.asList(counterId, counter2Id).contains(grantRequestStatus.getCounterId());

            assertThat(
                    String.format("для счетчика %s, access requested должно равняться к expected access requested", grantRequestStatus.getCounterId()),
                    grantRequestStatus.getAccessRequested(),
                    beanEquivalent(expectedAccessRequested)
            );
        }
    }

    @Test
    @Title("Тест ручки /internal/existent_counters")
    public void testExistentCounters() {
        long simpleCounterId = Counters.SIMPLE_COUNTER.getId();
        long metrikaCounterId = Counters.METRIKA.getId();
        long withSourceCounterId = Counters.COUNTER_WITH_SOURCE.getId();

        List<Long> counterIdList = Arrays.asList(
                101L, simpleCounterId,
                202L, metrikaCounterId,
                303L, withSourceCounterId
        );

        List<ExistentCounter> existentCounters = userSteps.onDirectSteps().getExistentCountersAndExpectSuccess(counterIdList);

        assertThat("Список существующих счетчиков должно равняться ожидаемому списку счетчиков",
                existentCounters,
                allOf(
                        iterableWithSize(3),
                        hasItem(allOf(
                                hasProperty("counterId", equalTo(simpleCounterId)),
                                hasProperty("directAllowUseGoalsWithoutAccess", equalTo(true)),
                                hasProperty("ecommerce", equalTo(false))
                        )),
                        hasItem(allOf(
                                hasProperty("counterId", equalTo(metrikaCounterId)),
                                hasProperty("directAllowUseGoalsWithoutAccess", equalTo(false)),
                                hasProperty("ecommerce", equalTo(true))
                        )),
                        hasItem(allOf(
                                hasProperty("counterSource", equalTo(CounterSource.TURBODIRECT)),
                                hasProperty("counterId", equalTo(withSourceCounterId)),
                                hasProperty("directAllowUseGoalsWithoutAccess", equalTo(true)),
                                hasProperty("ecommerce", equalTo(true))
                        ))
                )
        );
    }

    @Test
    @Title("Тест ручки /internal/existent_counters (проверяем counter id list на лимит)")
    public void testExistentCountersCounterIdListLimit() {
        List<Long> counterIdList = new ArrayList<>();
        for (long i = 1000; i < 2000; ++i)
            counterIdList.add(i);

        userSteps.onDirectSteps().getExistentCountersAndExpectSuccess(counterIdList);
    }

    @Test
    @Title("Тест ручки /internal/existent_counters (негативный тест, проверяем counter id list на лимит)")
    public void testExistentCountersCounterIdListLimitNegativeTest() {
        List<Long> counterIdList = new ArrayList<>();
        for (long i = 1000; i < 2001; ++i)
            counterIdList.add(i);

        userSteps.onDirectSteps().getExistentCountersAndExpectError(
                counterIdList,
                new CustomError(400L, startsWith("размер должен быть между 0 и 1000"))
        );
    }

    @Test
    @Title("Тест ручки /direct/user_counters_num")
    public void testUserCountersNum() {
        final ListResponse<DirectUserCountersNumResponse> directUserCountersNum = userSteps.onDirectSteps().getDirectUserCountersNum(
                Lists.newArrayList(
                        Users.METRIKA_INTAPI_AUTO.get(User.UID),
                        Users.METRIKA_INTAPI_DELEGATE.get(User.UID),
                        Users.METRIKA_INTAPI_GRANTEE.get(User.UID)
                )
        );

        assertThat("Ответ user_counters_num ожидаемый", directUserCountersNum.getResult(),
                allOf(
                        iterableWithSize(3),
                        hasItem(
                                allOf(
                                        hasProperty("owner", equalTo(Users.METRIKA_INTAPI_AUTO.get(User.UID))),
                                        hasProperty("counters", iterableWithSize(greaterThan(1)))
                                )
                        ),
                        hasItem(
                                allOf(
                                        hasProperty("owner", equalTo(Users.METRIKA_INTAPI_DELEGATE.get(User.UID))),
                                        hasProperty("counters", iterableWithSize(greaterThan(1)))
                                )
                        ),
                        hasItem(
                                allOf(
                                        hasProperty("owner", equalTo(Users.METRIKA_INTAPI_GRANTEE.get(User.UID))),
                                        hasProperty("counters", iterableWithSize(greaterThanOrEqualTo(1))) // гонка с тестом YandexServicesTest, так временно может быть дан грант на счетчик созданный в том тесте
                                )
                        ),
                        Matchers.everyItem(
                                hasProperty("counters", hasItem(equalTo((int) Counters.SIMPLE_COUNTER.getId())))
                        )
                )
        );

    }

    @Test
    @Title("Тест ручки /direct/user_counters_num2 на лимиты")
    public void testUserCountersNum2_limit() {
        final DirectUsersCountersNumAdditionalResponse response = userSteps.onDirectSteps().getDirectUserCountersNum2(
                Lists.newArrayList(
                        Users.METRIKA_INTAPI_AUTO.get(User.UID)
                ), Optional.of(2), "", Collections.emptyList()
        );
        assertThat("Ответ user_counters_num2 ожидаемый для флажка", response.isHasMoreCounters(), Matchers.is(true));

        assertThat("Ответ user_counters_num2 ожидаемый", response.getUsers(),
                allOf(
                        iterableWithSize(1),
                        hasItem(
                                allOf(
                                        hasProperty("owner", equalTo(Users.METRIKA_INTAPI_AUTO.get(User.UID))),
                                        hasProperty("counters", iterableWithSize(equalTo(2)))
                                )
                        )
                )
        );
    }

    @Test
    @Title("Тест ручки /direct/user_counters_num2 фильтр на префикс имен счетчиков")
    public void testUserCountersNum2_prefix() {
        final DirectUsersCountersNumAdditionalResponse response = userSteps.onDirectSteps().getDirectUserCountersNum2(
                Lists.newArrayList(
                        Users.METRIKA_INTAPI_AUTO.get(User.UID)
                ), Optional.empty(), "Тестов", Collections.emptyList()
        );
        assertThat("Ответ user_counters_num2 ожидаемый для флажка", response.isHasMoreCounters(), Matchers.is(false));

        assertThat("Ответ user_counters_num ожидаемый", response.getUsers(),
                allOf(
                        iterableWithSize(1),
                        hasItem(
                                allOf(
                                        hasProperty("owner", equalTo(Users.METRIKA_INTAPI_AUTO.get(User.UID))),
                                        hasProperty("counters", iterableWithSize(greaterThan(3)))
                                )
                        )
                )
        );
    }

    @Test
    @Title("Тест ручки /direct/user_counters_num2 фильтр на список счетчиков")
    public void testUserCountersNum2_counterIds() {
        final DirectUsersCountersNumAdditionalResponse response = userSteps.onDirectSteps().getDirectUserCountersNum2(
                Lists.newArrayList(
                        Users.METRIKA_INTAPI_AUTO.get(User.UID)
                ), Optional.empty(), "", Arrays.asList(56850799)
        );
        assertThat("Ответ user_counters_num2 ожидаемый для флажка", response.isHasMoreCounters(), Matchers.is(false));

        assertThat("Ответ user_counters_num ожидаемый", response.getUsers(),
                allOf(
                        iterableWithSize(1),
                        hasItem(
                                allOf(
                                        hasProperty("owner", equalTo(Users.METRIKA_INTAPI_AUTO.get(User.UID))),
                                        hasProperty("counters", iterableWithSize(equalTo(1)))
                                )
                        )
                )
        );
    }

    @Test
    @Title("Тест ручки /direct/user_counters_num_extended")
    public void testUserCountersNumExtended() {
        final ListResponse<DirectUserCountersNumExtendedResponse> directUserCountersNum = userSteps.onDirectSteps().getDirectUserCountersNumExtended(
                Lists.newArrayList(
                        Users.METRIKA_INTAPI_AUTO.get(User.UID),
                        Users.METRIKA_INTAPI_DELEGATE.get(User.UID),
                        Users.METRIKA_INTAPI_GRANTEE.get(User.UID)
                )
        );

        assertThat("Ответ user_counters_num ожидаемый", directUserCountersNum.getResult(),
                allOf(
                        iterableWithSize(3),
                        hasItem(
                                allOf(
                                        hasProperty("owner", equalTo(Users.METRIKA_INTAPI_AUTO.get(User.UID))),
                                        hasProperty("counters", iterableWithSize(greaterThan(1)))
                                )
                        ),
                        hasItem(
                                allOf(
                                        hasProperty("owner", equalTo(Users.METRIKA_INTAPI_DELEGATE.get(User.UID))),
                                        hasProperty("counters", iterableWithSize(greaterThan(1)))
                                )
                        ),
                        hasItem(
                                allOf(
                                        hasProperty("owner", equalTo(Users.METRIKA_INTAPI_GRANTEE.get(User.UID))),
                                        hasProperty("counters", iterableWithSize(1))
                                )
                        ),
                        Matchers.everyItem(
                                hasProperty("counters",
                                        allOf(
                                                hasItem(hasProperty("id", equalTo((int) Counters.SIMPLE_COUNTER.getId()))),
                                                everyItem(allOf(
                                                        hasProperty("name", not(nullValue())),
                                                        hasProperty("sitePath", not(nullValue())),
                                                        hasProperty("counterPermission", not(nullValue()))
                                                ))
                                        )
                                )
                        )
                )
        );

    }


    @Test
    @Title("Тест ручки /direct/updated_user_counters_num")
    public void testUpdatedUserCountersNum() {
        final Date createTime = COUNTER.getCreateTime();
        DateTime createDateTime = new DateTime(createTime.getTime());
        final ListResponse<DirectUpdatedUserCountersNumResponse> directUpdatedUserCountersNum = userSteps.onDirectSteps().getDirectUpdatedUserCountersNum(createDateTime.toLocalDateTime().minusSeconds(5));
        assertThat("В списке есть владелец созданного счетчика счетчик",
                directUpdatedUserCountersNum.getResult(),
                hasItem(hasProperty("owner", equalTo(Users.METRIKA_INTAPI_AUTO.get(User.UID))))
        );
    }

    @Test
    @Title("Тест ручки /direct/turn_on_call_tracking")
    public void testTurnOnCallTracking() {
        GoalE callGoal = userSteps.onDirectSteps().turnOnCallTracking(COUNTER.getId());
        Assert.assertNotNull("Цель создалась", callGoal);
        assertThat("Тип цели звонок", callGoal.getType(), equalTo(GoalType.CALL));
        CounterFull counter = userSteps.onInternalApidSteps().сounter(COUNTER.getId());
        assertThat("Фича offline_calls включена", counter.getFeatures(), hasItem(Feature.OFFLINE_CALLS));
    }

    private GoalE makeSimpleGoal() {
        return new UrlGoal()
                .withName("моя цель " + rnd.nextInt()).withType(GoalType.URL)
                .withConditions(Lists.newArrayList(new GoalCondition().withType(GoalConditionType.EXACT).withUrl("http://my.url.com")));
    }

}
