package ru.yandex.autotests.metrika.appmetrica.steps;

import org.hamcrest.Matcher;
import ru.yandex.autotests.httpclient.lite.core.IFormParameters;
import ru.yandex.autotests.httpclientlite.HttpClientLite;
import ru.yandex.autotests.metrika.appmetrica.beans.schemes.InternalManagementV1ApplicationAppIdEventListGETSchema;
import ru.yandex.autotests.metrika.appmetrica.beans.schemes.InternalManagementV1ApplicationAppIdEventPOSTSchema;
import ru.yandex.autotests.metrika.appmetrica.parameters.FreeFormParameters;
import ru.yandex.autotests.metrika.appmetrica.steps.parallel.ParallelExecution;
import ru.yandex.autotests.metrika.commons.response.IExpectedError;
import ru.yandex.metrika.mobmet.management.events.model.EventManagementMetadata;
import ru.yandex.metrika.mobmet.management.events.response.EventsManagementList;
import ru.yandex.qatools.allure.annotations.Step;

import java.net.URL;

import static java.lang.String.format;
import static ru.yandex.autotests.irt.testutils.allure.TestSteps.assertThat;
import static ru.yandex.autotests.metrika.appmetrica.steps.parallel.ParallelExecution.Permission.RESTRICT;
import static ru.yandex.autotests.metrika.appmetrica.utils.Utils.aggregate;
import static ru.yandex.autotests.metrika.commons.response.ResponseMatchers.*;

public class EventsManagementSteps extends AppMetricaBaseSteps {

    public EventsManagementSteps(URL baseUrl, HttpClientLite client) {
        super(baseUrl, client);
    }

    @Step("Получить список событий")
    @ParallelExecution(RESTRICT)
    public EventsManagementList getEventsManagementList(Long appId, IFormParameters... parameters) {
        return getEventsManagementList(appId, SUCCESS_MESSAGE, expectSuccess(), parameters).getResponse();
    }

    @Step("Обновить фильтр события и ожидать ошибку")
    @ParallelExecution(RESTRICT)
    public void updateEventFiltersAndExpectError(Long appId, String eventName, EventManagementMetadata form, IExpectedError error) {
        updateEventFilters(appId, eventName, ERROR_MESSAGE, expectError(error), form);
    }

    private InternalManagementV1ApplicationAppIdEventListGETSchema getEventsManagementList(Long appId,
                                                                                           String message,
                                                                                           Matcher matcher,
                                                                                           IFormParameters... parameters) {
        InternalManagementV1ApplicationAppIdEventListGETSchema result = get(InternalManagementV1ApplicationAppIdEventListGETSchema.class,
                format("internal/management/v1/application/%s/event/list", appId),
                aggregate(parameters));

        assertThat(message, result, matcher);

        return result;
    }

    private void updateEventFilters(Long appId, String eventName, String message, Matcher matcher, EventManagementMetadata form) {
        InternalManagementV1ApplicationAppIdEventPOSTSchema result = post(InternalManagementV1ApplicationAppIdEventPOSTSchema.class,
                format("internal/management/v1/application/%s/event", appId),
                form,
                new FreeFormParameters().append("name", eventName));

        assertThat(message, result, matcher);
    }

}
