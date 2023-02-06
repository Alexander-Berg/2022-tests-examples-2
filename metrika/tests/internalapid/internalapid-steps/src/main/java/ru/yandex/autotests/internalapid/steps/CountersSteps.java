package ru.yandex.autotests.internalapid.steps;

import java.net.URL;
import java.util.List;

import ru.yandex.autotests.httpclientlite.HttpClientLite;
import ru.yandex.autotests.internalapid.beans.schemes.CountersV1CounterSettingsGETSchema;
import ru.yandex.autotests.internalapid.beans.schemes.CountersV1CountersForUidGETSchema;
import ru.yandex.autotests.internalapid.beans.schemes.CountersV1DescribeCountersGETSchema;
import ru.yandex.autotests.irt.testutils.allure.TestSteps;
import ru.yandex.autotests.metrika.commons.clients.http.FreeFormParameters;
import ru.yandex.autotests.metrika.commons.clients.http.HttpClientLiteFacade;
import ru.yandex.metrika.api.management.client.counter.CounterIdEnhanced;
import ru.yandex.metrika.internalapid.common.CounterSettings;
import ru.yandex.qatools.allure.annotations.Step;

import static ru.yandex.autotests.metrika.commons.response.ResponseMatchers.SUCCESS_MESSAGE;
import static ru.yandex.autotests.metrika.commons.response.ResponseMatchers.expectSuccess;

public class CountersSteps extends HttpClientLiteFacade {
    protected CountersSteps(URL baseUrl, HttpClientLite client) {
        super(baseUrl, client);
    }

    public void getCountersForUidSuccess(long uid) {
        final CountersV1CountersForUidGETSchema counters = get(CountersV1CountersForUidGETSchema.class, "/counters/v1/counters_for_uid",
                new FreeFormParameters().append("uid", uid));
        TestSteps.assumeThat(SUCCESS_MESSAGE, counters, expectSuccess());
    }

    @Step("Получить список счетчиков для uid {0}")
    public List<CounterIdEnhanced> getCountersForUid(long uid) {
        final CountersV1CountersForUidGETSchema counters = get(
                CountersV1CountersForUidGETSchema.class,
                "/counters/v1/counters_for_uid",
                new FreeFormParameters().append("uid", uid));
        TestSteps.assumeThat(SUCCESS_MESSAGE, counters, expectSuccess());
        return counters.getCounters();
    }

    @Step("Получить настройки счетчика {1}")
    public CounterSettings getCounterSettings(long counterId) {
        final CountersV1CounterSettingsGETSchema result = get(
                CountersV1CounterSettingsGETSchema.class,
                "counters/v1/counter_settings",
                new FreeFormParameters().append("counter_id", counterId)
        );

        TestSteps.assumeThat(SUCCESS_MESSAGE, result, expectSuccess());

        return new CounterSettings()
                .withCounterId(result.getCounterId())
                .withStatus(result.getStatus())
                .withAutoGoalsEnabled(result.getAutoGoalsEnabled())
                .withType(result.getType())
                .withGdprAgreementAccepted(result.getGdprAgreementAccepted());
    }

    @Step("Получить описание счетчика {0} от имени пользователя {1}")
    public List<CounterIdEnhanced> getCounterDescription(int counterId, long uid) {
        final CountersV1DescribeCountersGETSchema result = get(
                CountersV1DescribeCountersGETSchema.class,
                "counters/v1/describe/counters",
                new FreeFormParameters().append("ids", counterId)
                        .append("uid", uid)

        );

        TestSteps.assumeThat(SUCCESS_MESSAGE, result, expectSuccess());

        return result.getCounters();
    }


}
