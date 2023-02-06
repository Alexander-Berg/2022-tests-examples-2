package ru.yandex.autotests.metrika.appmetrica.steps;

import org.hamcrest.Matcher;
import ru.yandex.autotests.httpclient.lite.core.IFormParameters;
import ru.yandex.autotests.httpclientlite.HttpClientLite;
import ru.yandex.autotests.metrika.appmetrica.beans.schemes.V1TrafficSourcesEventsGETSchema;
import ru.yandex.autotests.metrika.appmetrica.beans.schemes.V2UserAcquisitionGETSchema;
import ru.yandex.autotests.metrika.appmetrica.steps.parallel.ParallelExecution;
import ru.yandex.metrika.mobmet.model.events.EventsResponse;

import java.net.URL;

import static org.hamcrest.MatcherAssert.assertThat;
import static ru.yandex.autotests.metrika.appmetrica.steps.parallel.ParallelExecution.Permission.RESTRICT;
import static ru.yandex.autotests.metrika.commons.response.ResponseMatchers.SUCCESS_MESSAGE;
import static ru.yandex.autotests.metrika.commons.response.ResponseMatchers.expectSuccess;

/**
 * Created by graev on 30/03/2017.
 */
public class TrafficSourcesSteps extends AppMetricaBaseSteps {

    public TrafficSourcesSteps(URL baseUrl, HttpClientLite client) {
        super(baseUrl, client);
    }

    @ParallelExecution(RESTRICT)
    public V2UserAcquisitionGETSchema getReport(IFormParameters... parameters) {
        return getReport(SUCCESS_MESSAGE, expectSuccess(), parameters);
    }

    @ParallelExecution(RESTRICT)
    public EventsResponse getEvents(IFormParameters... parameters) {
        return getEvents(SUCCESS_MESSAGE, expectSuccess(), parameters).getEventsInfo();
    }

    private V2UserAcquisitionGETSchema getReport(String message, Matcher matcher, IFormParameters... parameters) {
        V2UserAcquisitionGETSchema result = get(
                V2UserAcquisitionGETSchema.class,
                "/v2/user/acquisition",
                parameters
        );

        assertThat(message, result, matcher);

        return result;
    }

    private V1TrafficSourcesEventsGETSchema getEvents(String message, Matcher matcher, IFormParameters... parameters) {
        final V1TrafficSourcesEventsGETSchema result = get(
                V1TrafficSourcesEventsGETSchema.class,
                "/v1/traffic/sources/events",
                parameters
        );

        assertThat(message, result, matcher);

        return result;
    }

}
