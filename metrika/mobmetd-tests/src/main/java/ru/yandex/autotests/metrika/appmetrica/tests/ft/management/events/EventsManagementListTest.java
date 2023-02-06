package ru.yandex.autotests.metrika.appmetrica.tests.ft.management.events;

import org.junit.Test;
import ru.yandex.autotests.metrika.appmetrica.data.Application;
import ru.yandex.autotests.metrika.appmetrica.data.Applications;
import ru.yandex.autotests.metrika.appmetrica.parameters.events.management.EventsManagementListParameters;
import ru.yandex.autotests.metrika.appmetrica.steps.UserSteps;
import ru.yandex.autotests.metrika.appmetrica.tests.Requirements;
import ru.yandex.metrika.mobmet.management.events.model.EventManagementRow;
import ru.yandex.metrika.mobmet.management.events.response.EventsManagementList;
import ru.yandex.qatools.allure.annotations.Features;
import ru.yandex.qatools.allure.annotations.Stories;
import ru.yandex.qatools.allure.annotations.Title;

import java.util.List;

import static java.util.stream.Collectors.toList;
import static org.hamcrest.Matchers.*;
import static ru.yandex.autotests.irt.testutils.allure.TestSteps.assertThat;
import static ru.yandex.autotests.irt.testutils.allure.TestSteps.assumeThat;
import static ru.yandex.autotests.metrika.appmetrica.data.Users.SUPER_LIMITED;

@Features(Requirements.Feature.Management.Application.EVENTS)
@Stories({
        Requirements.Story.Application.EventsManagement.LIST
})
@Title("Получение списка событий (управление)")
public class EventsManagementListTest {

    private static final UserSteps user = UserSteps.onTesting(SUPER_LIMITED);

    private static final Long APP_ID = Applications.PUSH_SAMPLE.get(Application.ID);

    @Test
    public void checkEventsManagementList() {
        // ищем Send push
        String mask = "end p";

        EventsManagementList list = user.onEventsManagementSteps().getEventsManagementList(
                APP_ID,
                new EventsManagementListParameters()
                        .withMask(mask)
        );

        List<String> eventNames = list.getRows().stream()
                .map(EventManagementRow::getEvent)
                .collect(toList());

        assumeThat("Список событий не пустой", eventNames, not(empty()));
        assumeThat("Totals событий не нулевой", list.getTotals(), greaterThan(0L));
        assertThat("Имена событий содержат подстроку фильтра", eventNames, everyItem(containsString(mask)));
    }

}
