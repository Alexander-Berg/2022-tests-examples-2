package ru.yandex.autotests.internalapid.tests;

import java.util.Arrays;
import java.util.List;

import com.google.common.collect.Lists;
import org.junit.After;
import org.junit.Before;
import org.junit.BeforeClass;
import org.junit.Test;

import ru.yandex.autotests.internalapid.beans.data.User;
import ru.yandex.autotests.internalapid.beans.data.Users;
import ru.yandex.autotests.internalapid.beans.schemes.YandexservicesAddCounterPOSTSchema;
import ru.yandex.autotests.internalapid.util.DataUtil;
import ru.yandex.metrika.api.Feature;
import ru.yandex.metrika.api.management.client.counter.CounterEdit;
import ru.yandex.metrika.api.management.client.external.CodeOptionsE;
import ru.yandex.metrika.api.management.client.external.CounterBrief;
import ru.yandex.metrika.api.management.client.external.CounterFull;
import ru.yandex.metrika.api.management.client.external.CounterSource;
import ru.yandex.metrika.api.management.client.external.GrantE;
import ru.yandex.metrika.api.management.client.external.GrantType;
import ru.yandex.metrika.api.management.client.external.goals.DepthGoal;
import ru.yandex.metrika.api.management.client.external.goals.GoalE;
import ru.yandex.metrika.api.management.client.external.goals.GoalType;
import ru.yandex.qatools.allure.annotations.Title;

import static java.util.Arrays.asList;
import static org.apache.tika.metadata.MSOffice.MANAGER;
import static org.hamcrest.MatcherAssert.assertThat;
import static org.hamcrest.Matchers.allOf;
import static org.hamcrest.Matchers.empty;
import static org.hamcrest.Matchers.equalTo;
import static org.hamcrest.Matchers.everyItem;
import static org.hamcrest.Matchers.hasItem;
import static org.hamcrest.Matchers.hasProperty;
import static org.hamcrest.Matchers.is;
import static org.hamcrest.Matchers.iterableWithSize;
import static org.hamcrest.Matchers.not;
import static org.hamcrest.Matchers.notNullValue;
import static org.hamcrest.Matchers.nullValue;
import static ru.yandex.autotests.irt.testutils.allure.TestSteps.assumeThat;

@Title("Тест апи для сервисов яндекса")
public class YandexServicesTest extends InternalApidTest {
    public static final String SITE = "test.ru";
    public static final String GOAL_NAME = "goal name";
    public static final List<GoalE> GOALS = asList(new DepthGoal().withName(GOAL_NAME).withType(GoalType.NUMBER).withDepth(100L));
    private static CounterFull COUNTER;
    private final static String userGranteeLogin = Users.METRIKA_INTAPI_GRANTEE.get(User.LOGIN);
    private static String COUNTER_NAME;


    @BeforeClass
    public static void init() {
        COUNTER_NAME = DataUtil.getRandomCounterName();
        COUNTER = userSteps.onInternalApidSteps().createCounter(
                new CounterFull()
                        .withName(COUNTER_NAME)
                        .withSite(SITE)
                        .withSource(CounterSource.SPRAV)
                        .withGoals(GOALS)
        );
    }

    @Test
    public void createCounterWithNotEnabledFeature() {
        YandexservicesAddCounterPOSTSchema counter = userSteps.onInternalApidSteps().tryCreateCounter(
                new CounterFull()
                        .withName(DataUtil.getRandomCounterName())
                        .withSite(SITE)
                        .withFeatures(asList(Feature.ADFOX))
        );
        assertThat("Счетчик не был создан", counter.getCounter(), nullValue());
        assertThat("вернулся код 400", counter.getCode(), is(400L));
    }

    @Test
    public void createCounterWithEnabledFeature() {
        YandexservicesAddCounterPOSTSchema counter = userSteps.onInternalApidSteps().tryCreateCounter(
                new CounterFull()
                        .withName(DataUtil.getRandomCounterName())
                        .withSite(SITE)
                        .withFeatures(asList(Feature.VACUUM))
        );
        assertThat("Счетчик был создан", counter.getCounter(), notNullValue());
        assertThat("фича проставлена", counter.getCounter().getFeatures(), hasItem(Feature.VACUUM));
    }

    @Test
    public void createCounterWithGrants() {
        YandexservicesAddCounterPOSTSchema counter = userSteps.onInternalApidSteps().tryCreateCounter(
                new CounterFull()
                        .withName(DataUtil.getRandomCounterName())
                        .withSite(SITE)
                        .withGrants(Arrays.asList(
                                new GrantE().withUserLogin(Users.MANAGER.get(User.LOGIN)).withPerm(GrantType.VIEW),
                                new GrantE().withUserLogin(Users.METRIKA_INTAPI_DELEGATE.get(User.LOGIN)).withPerm(GrantType.VIEW),
                                new GrantE().withUserLogin(Users.MANAGER_2.get(User.LOGIN)).withPerm(GrantType.EDIT),
                                new GrantE().withPerm(GrantType.PUBLIC_STAT)
                        )));
        assertThat("Счетчик был создан", counter.getCounter(), notNullValue());

        List<GrantE> counterGrants = userSteps.onInternalApidSteps().getGrants(counter.getCounter().getId());
        assertThat("Доступ есть", counterGrants, hasItem(hasProperty("userLogin", equalTo(Users.MANAGER.get(User.LOGIN)))));
    }

    @Test
    @Title("Изменение счетчика")
    public void editCounter() {
        String ecommerceObject = "edit ecommerce object";
        CounterFull editCounter = userSteps.onInternalApidSteps().editCounter(COUNTER.getId(),
                new CounterEdit()
                        .withCodeOptions(new CodeOptionsE().withEcommerceObject(ecommerceObject))
                        .withGoals(GOALS)
        );

        assertThat("Счетчик изменился", editCounter.getCodeOptions().getEcommerceObject(), is(ecommerceObject));
    }

    @Test
    @Title("Удаление счетчика")
    public void deleteCounter() {
        YandexservicesAddCounterPOSTSchema counter = userSteps.onInternalApidSteps().tryCreateCounter(
                new CounterFull()
                        .withName(DataUtil.getRandomCounterName())
                        .withSource(CounterSource.SPRAV)
                        .withSite(SITE)
        );
        userSteps.onInternalApidSteps().deleteCounter(counter.getCounter().getId());
    }

    @Test
    @Title("Поиск счетчика по айди")
    public void readCounter() {
        CounterFull counter = userSteps.onInternalApidSteps().сounter(COUNTER.getId());
        assertThat("Прочитал счетчик", counter.getSite(), is(SITE));
    }

    @Test
    @Title("Поиск счетчика по имени")
    public void findCounterByName() {
        List<CounterBrief> counters = userSteps.onInternalApidSteps().counters(COUNTER_NAME);
        assertThat("1 счетчик", counters.size(), is(1));
        assertThat("Site правильный", counters.get(0).getSite(), is(SITE));
    }

    @Test
    @Title("Поиск целей счетчика")
    public void findGoals() {
        List<GoalE> goals = userSteps.onInternalApidSteps().goals(COUNTER.getId());
        assertThat("1 цель", goals.size(), is(1));
        assertThat("Имя правильное", goals.get(0).getName(), is(GOAL_NAME));
    }

    @Test
    @Title("Доступ добавляется и удаляется")
    public void addAndDeleteGrant() {
        List<GrantE> counterGrants = userSteps.onInternalApidSteps().getGrants(COUNTER.getId());
        assumeThat("Доступов нет", counterGrants, empty());

        userSteps.onInternalApidSteps().addGrant(COUNTER.getId(), new GrantE().withUserLogin(userGranteeLogin).withPerm(GrantType.VIEW));
        counterGrants = userSteps.onInternalApidSteps().getGrants(COUNTER.getId());
        assertThat("Доступ есть", counterGrants, hasItem(hasProperty("userLogin", equalTo(userGranteeLogin))));

        userSteps.onInternalApidSteps().deleteGrant(COUNTER.getId(), userGranteeLogin);
        counterGrants = userSteps.onInternalApidSteps().getGrants(COUNTER.getId());
        assertThat("Доступа нет", counterGrants, not(hasItem(hasProperty("userLogin", equalTo(userGranteeLogin)))));
    }

    @Test
    @Title("Доступ добавляется и изменяется")
    public void addAndModifyGrant() {
        List<GrantE> counterGrants = userSteps.onInternalApidSteps().getGrants(COUNTER.getId());
        assumeThat("Доступов нет", counterGrants, empty());

        userSteps.onInternalApidSteps().addGrant(COUNTER.getId(), new GrantE().withUserLogin(userGranteeLogin).withPerm(GrantType.VIEW));
        counterGrants = userSteps.onInternalApidSteps().getGrants(COUNTER.getId());
        assertThat("Доступ на чтение есть", counterGrants, hasItem(allOf(
                hasProperty("userLogin", equalTo(userGranteeLogin)),
                hasProperty("perm", equalTo(GrantType.VIEW)))));

        userSteps.onInternalApidSteps().editGrant(COUNTER.getId(), new GrantE().withUserLogin(userGranteeLogin).withPerm(GrantType.EDIT));
        counterGrants = userSteps.onInternalApidSteps().getGrants(COUNTER.getId());
        assertThat("Доступ на запись есть", counterGrants, hasItem(allOf(
                hasProperty("userLogin", equalTo(userGranteeLogin)),
                hasProperty("perm", equalTo(GrantType.EDIT)))));
    }

    @Test
    @Title("Добавляется батч доступов")
    public void batchAddGrants() {
        List<GrantE> counterGrants = userSteps.onInternalApidSteps().getGrants(COUNTER.getId());
        assumeThat("Доступов нет", counterGrants, empty());

        userSteps.onInternalApidSteps().addGrants(COUNTER.getId(),
                Lists.newArrayList(
                        new GrantE().withUserLogin(userGranteeLogin).withPerm(GrantType.VIEW),
                        new GrantE().withUserLogin(Users.METRIKA_INTAPI_DELEGATE.get(User.LOGIN)).withPerm(GrantType.VIEW)
                ));
        counterGrants = userSteps.onInternalApidSteps().getGrants(COUNTER.getId());
        assertThat("Доступы есть", counterGrants, iterableWithSize(2));
    }

    @Test
    @Title("Изменяется батч доступов")
    public void batchEditGrants() {
        List<GrantE> counterGrants = userSteps.onInternalApidSteps().getGrants(COUNTER.getId());
        assumeThat("Доступов нет", counterGrants, empty());

        userSteps.onInternalApidSteps().addGrants(COUNTER.getId(),
                Lists.newArrayList(
                        new GrantE().withUserLogin(userGranteeLogin).withPerm(GrantType.VIEW),
                        new GrantE().withUserLogin(Users.METRIKA_INTAPI_DELEGATE.get(User.LOGIN)).withPerm(GrantType.VIEW)
                ));
        counterGrants = userSteps.onInternalApidSteps().getGrants(COUNTER.getId());
        assumeThat("Доступы есть", counterGrants, iterableWithSize(2));

        userSteps.onInternalApidSteps().editGrants(COUNTER.getId(),
                Lists.newArrayList(
                        new GrantE().withUserLogin(userGranteeLogin).withPerm(GrantType.EDIT),
                        new GrantE().withUserLogin(Users.METRIKA_INTAPI_DELEGATE.get(User.LOGIN)).withPerm(GrantType.EDIT)
                ));
        counterGrants = userSteps.onInternalApidSteps().getGrants(COUNTER.getId());
        assertThat("Доступы теперь на редактирование", counterGrants, allOf(iterableWithSize(2), everyItem(hasProperty("perm", equalTo(GrantType.EDIT)))));
    }

    @Test
    @Title("Удаляется батч доступов")
    public void batchDeleteGrants() {
        List<GrantE> counterGrants = userSteps.onInternalApidSteps().getGrants(COUNTER.getId());
        assumeThat("Доступов нет", counterGrants, empty());

        userSteps.onInternalApidSteps().addGrants(COUNTER.getId(),
                Lists.newArrayList(
                        new GrantE().withUserLogin(userGranteeLogin).withPerm(GrantType.VIEW),
                        new GrantE().withUserLogin(Users.METRIKA_INTAPI_DELEGATE.get(User.LOGIN)).withPerm(GrantType.VIEW)
                ));
        counterGrants = userSteps.onInternalApidSteps().getGrants(COUNTER.getId());
        assumeThat("Доступы есть", counterGrants, iterableWithSize(2));

        userSteps.onInternalApidSteps().deleteGrants(COUNTER.getId(), Lists.newArrayList(Users.METRIKA_INTAPI_DELEGATE.get(User.LOGIN), userGranteeLogin));

        counterGrants = userSteps.onInternalApidSteps().getGrants(COUNTER.getId());
        assumeThat("Доступов нет", counterGrants, empty());
    }

    @Before
    @After
    public void clean() {
        userSteps.onInternalApidSteps().deleteGrant(COUNTER.getId(), Users.METRIKA_INTAPI_GRANTEE.get(User.LOGIN));
        userSteps.onInternalApidSteps().deleteGrant(COUNTER.getId(), Users.METRIKA_INTAPI_DELEGATE.get(User.LOGIN));
    }
}
