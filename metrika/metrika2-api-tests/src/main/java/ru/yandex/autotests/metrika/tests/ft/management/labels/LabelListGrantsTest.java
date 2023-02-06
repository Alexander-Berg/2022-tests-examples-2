package ru.yandex.autotests.metrika.tests.ft.management.labels;

import org.junit.After;
import org.junit.Before;
import org.junit.Test;
import ru.yandex.autotests.metrika.Requirements;
import ru.yandex.autotests.metrika.data.common.users.User;
import ru.yandex.autotests.metrika.data.common.users.Users;
import ru.yandex.autotests.metrika.steps.UserSteps;
import ru.yandex.metrika.api.management.client.counter.BadCounter;
import ru.yandex.metrika.api.management.client.external.CounterFull;
import ru.yandex.metrika.api.management.client.external.GrantE;
import ru.yandex.metrika.api.management.client.label.Label;
import ru.yandex.qatools.allure.annotations.Features;
import ru.yandex.qatools.allure.annotations.Issue;
import ru.yandex.qatools.allure.annotations.Stories;
import ru.yandex.qatools.allure.annotations.Title;

import java.util.ArrayList;
import java.util.List;

import static org.hamcrest.Matchers.hasItem;
import static org.hamcrest.core.IsNot.not;
import static ru.yandex.autotests.irt.testutils.beandiffer.BeanDifferMatcher.beanEquivalent;
import static ru.yandex.autotests.metrika.matchers.CounterMatchers.beanEquivalentIgnoringFeatures;
import static ru.yandex.autotests.metrika.data.common.users.User.LOGIN;
import static ru.yandex.autotests.metrika.data.common.users.Users.SIMPLE_USER2;
import static ru.yandex.autotests.metrika.data.parameters.management.v1.Field.GRANTS;
import static ru.yandex.autotests.metrika.tests.ft.management.ManagementTestData.getDefaultCounter;
import static ru.yandex.autotests.metrika.tests.ft.management.ManagementTestData.getDefaultLabel;
import static ru.yandex.autotests.metrika.utils.AllureUtils.assertThat;
import static ru.yandex.metrika.api.management.client.counter.Cause.ACCESS_DENIED;
import static ru.yandex.metrika.api.management.client.external.GrantType.VIEW;

/**
 * Created by proxeter on 24.07.2014.
 */
@Features(Requirements.Feature.MANAGEMENT)
@Stories(Requirements.Story.Management.LABELS)
@Title("Проверка прав на счётчики из списка")
public class LabelListGrantsTest {

    private UserSteps user;
    private Long labelId;
    private Long counterId;
    private Label label;
    private CounterFull counter;
    private Label addedLabel;
    private CounterFull addedCounter;

    private static final User OWNER = SIMPLE_USER2;
    private static final User GRANTEE = Users.SIMPLE_USER;

    @Before
    public void before() {
        user = new UserSteps().withUser(OWNER);
        counter = getDefaultCounter();
        user.onManagementSteps().onCountersSteps().deleteAllCountersWithName(counter.getName());

        addedCounter = user.onManagementSteps().onCountersSteps()
                .addCounterAndExpectSuccess(counter, GRANTS);
        counterId = addedCounter.getId();

        GrantE grant = new GrantE()
                .withUserLogin(GRANTEE.get(LOGIN))
                .withPerm(VIEW)
                .withComment("");
        counter.getGrants().add(grant);
        user.onManagementSteps().onCountersSteps().editCounter(counterId, counter, GRANTS);
        label = getDefaultLabel();
        addedLabel = user.withUser(GRANTEE).onManagementSteps().onLabelsSteps().addLabelAndExpectSuccess(label);
        labelId = addedLabel.getId();

        user.onManagementSteps().onLabelsSteps().joinCounterToLabelAndExpectSuccess(counterId, labelId);
    }

    @Test
    @Title("Метка: есть права на счётчик")
    public void joinCounterToLabelPermTest() {
        List<CounterFull> countersByLabel = user.onManagementSteps().onLabelsSteps()
                .getCountersByLabelAndExpectSuccess(labelId);
        CounterFull expectedCounter = new CounterFull()
                .withId(counterId)
                .withName(counter.getName())
                .withSite(counter.getSite());

        assertThat("Привязанный счетчик присутствует в списке счетчиков метки", countersByLabel,
                hasItem(beanEquivalentIgnoringFeatures(expectedCounter)));
    }

    @Test
    @Title("Метка: нет прав на счётчик")
    @Issue("METR-18163")
    public void joinCounterToLabelNoPermTest() {
        //при отзыве доступа на счетчик он удаляется из метого того, чей доступ был отозван
        //https://st.yandex-team.ru/METR-18163#1443113579000
        counter.setGrants(new ArrayList<>());
        user.withUser(OWNER).onManagementSteps().onCountersSteps().editCounter(counterId, counter, GRANTS);

        List<CounterFull> countersByLabel = user.withUser(GRANTEE).onManagementSteps().onLabelsSteps()
                .getCountersByLabelAndExpectSuccess(labelId);
        BadCounter expectedCounter = new BadCounter()
                .withId(counterId)
                .withName(counter.getName())
                .withSite(counter.getSite())
                .withCause(ACCESS_DENIED);

        assertThat("привязанный счетчик отсутствует в списке счетчиков метки",
                countersByLabel, not(hasItem(beanEquivalent(expectedCounter))));
    }

    @After
    public void after() {
        user.withUser(OWNER).onManagementSteps().onCountersSteps().deleteCounterAndExpectSuccess(counterId);
        user.withUser(GRANTEE).onManagementSteps().onLabelsSteps().deleteLabelAndExpectSuccess(labelId);
    }

}
