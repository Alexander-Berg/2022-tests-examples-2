package ru.yandex.autotests.metrika.tests.ft.management.counter;

import org.junit.Before;
import org.junit.Test;
import ru.yandex.autotests.metrika.Requirements;
import ru.yandex.autotests.metrika.steps.UserSteps;
import ru.yandex.metrika.api.management.client.external.CounterBrief;
import ru.yandex.metrika.api.management.client.external.CounterFull;
import ru.yandex.metrika.api.management.client.external.CounterSource;
import ru.yandex.qatools.allure.annotations.Features;
import ru.yandex.qatools.allure.annotations.Stories;
import ru.yandex.qatools.allure.annotations.Title;

import java.util.List;

import static org.hamcrest.core.IsCollectionContaining.hasItem;
import static org.junit.Assert.assertEquals;
import static ru.yandex.autotests.irt.testutils.beans.BeanHelper.copyProperties;
import static ru.yandex.autotests.metrika.data.common.users.Users.SUPER_USER;
import static ru.yandex.autotests.metrika.data.parameters.management.v1.Fields.all;
import static ru.yandex.autotests.metrika.errors.ManagementError.PARTNER_DELETE_ERROR;
import static ru.yandex.autotests.metrika.matchers.CounterMatchers.beanEquivalentIgnoringFeatures;
import static ru.yandex.autotests.metrika.tests.ft.management.ManagementTestData.getPartnerCounter;
import static ru.yandex.autotests.metrika.utils.AllureUtils.assertThat;

@Features(Requirements.Feature.MANAGEMENT)
@Stories(Requirements.Story.Management.COUNTERS)
@Title("Счетчик: проверка добавления счетчика РСЯ")
public class AddPartnerCounterTest {

    private UserSteps user;
    private Long counterId;
    private CounterFull counter;
    private CounterFull addedCounter;

    @Before
    public void setup() {
        user = new UserSteps().withUser(SUPER_USER);

        counter = getPartnerCounter();
        addedCounter = user.onManagementSteps().onCountersSteps()
                .addCounterAndExpectSuccess(counter, all());

        counterId = addedCounter.getId();
    }

    @Test
    public void checkAddedCounter() {
        assertThat("добавленный счетчик должен быть эквивалентен добавляемому", addedCounter,
                beanEquivalentIgnoringFeatures(counter));

        assertEquals(addedCounter.getAutogoalsEnabled(), false);
        assertEquals(addedCounter.getSource(), CounterSource.PARTNER);
    }

    @Test
    public void checkCounterInfo() {
        CounterFull actualCounter = user.onManagementSteps().onCountersSteps()
                .getCounterInfo(counterId, all());

        assertThat("информация о счетчике должна быть эквивалентна добавляемому счетчику", actualCounter,
                beanEquivalentIgnoringFeatures(counter));

        assertEquals(actualCounter.getAutogoalsEnabled(), false);
        assertEquals(actualCounter.getSource(), CounterSource.PARTNER);
    }

    @Test
    public void counterShouldBeInCountersList() {
        List<CounterBrief> counters = user.onManagementSteps().onCountersSteps().getAvailableCountersAndExpectSuccess();

        CounterBrief expectedCounterBrief = new CounterBrief();
        copyProperties(counter, expectedCounterBrief);

        assertThat("список должен содержать добавленный счетчик", counters,
                hasItem(beanEquivalentIgnoringFeatures(expectedCounterBrief)));
    }

    @Test
    @Title("РСЯ счетчик не должен удаляться")
    public void counterCannotBeDeleted() {
        user.onManagementSteps().onCountersSteps().deleteCounterAndExpeсtError(counterId, PARTNER_DELETE_ERROR);
    }
}
