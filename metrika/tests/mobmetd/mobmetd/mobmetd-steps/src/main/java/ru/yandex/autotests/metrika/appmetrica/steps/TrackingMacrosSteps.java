package ru.yandex.autotests.metrika.appmetrica.steps;

import java.net.URL;
import java.util.List;

import org.hamcrest.Matcher;
import ru.yandex.autotests.httpclientlite.HttpClientLite;
import ru.yandex.autotests.metrika.appmetrica.beans.schemes.InternalMacrosIdDELETESchema;
import ru.yandex.autotests.metrika.appmetrica.beans.schemes.InternalMacrosPOSTRequestSchema;
import ru.yandex.autotests.metrika.appmetrica.beans.schemes.InternalMacrosPOSTSchema;
import ru.yandex.autotests.metrika.appmetrica.beans.schemes.ManagementV1TrackingPartnerIdMacrosGETSchema;
import ru.yandex.autotests.metrika.appmetrica.steps.parallel.ParallelExecution;
import ru.yandex.autotests.metrika.commons.response.IExpectedError;
import ru.yandex.metrika.mobmet.model.redirect.TrackingPartnerMacros;
import ru.yandex.qatools.allure.annotations.Step;

import static ru.yandex.autotests.irt.testutils.allure.TestSteps.assertThat;
import static ru.yandex.autotests.metrika.appmetrica.steps.parallel.ParallelExecution.Permission.ALLOW;
import static ru.yandex.autotests.metrika.commons.response.ResponseMatchers.ANYTHING_MESSAGE;
import static ru.yandex.autotests.metrika.commons.response.ResponseMatchers.ERROR_MESSAGE;
import static ru.yandex.autotests.metrika.commons.response.ResponseMatchers.SUCCESS_MESSAGE;
import static ru.yandex.autotests.metrika.commons.response.ResponseMatchers.expectAnything;
import static ru.yandex.autotests.metrika.commons.response.ResponseMatchers.expectError;
import static ru.yandex.autotests.metrika.commons.response.ResponseMatchers.expectSuccess;

public class TrackingMacrosSteps extends AppMetricaBaseSteps {
    public TrackingMacrosSteps(URL baseUrl, HttpClientLite client) {
        super(baseUrl, client);
    }

    @Step("Создать шаблон постбека {0}")
    @ParallelExecution(ALLOW)
    public TrackingPartnerMacros createTrackingMacros(TrackingPartnerMacros macros) {
        return createMacros(SUCCESS_MESSAGE, expectSuccess(), macros).getMacros();
    }

    @Step("Создать шаблон постбека {0}")
    @ParallelExecution(ALLOW)
    public TrackingPartnerMacros createTrackingMacrosAndExpectError(TrackingPartnerMacros macros, IExpectedError error) {
        return createMacros(ERROR_MESSAGE, expectError(error), macros).getMacros();
    }

    @Step("Создать шаблон постбека {0}")
    @ParallelExecution(ALLOW)
    public List<TrackingPartnerMacros> getTrackingMacrosList(Long partnerId) {
        return getTrackingMacrosList(SUCCESS_MESSAGE, expectSuccess(), partnerId).getMacros();
    }

    @Step("Создать шаблон постбека {0}")
    @ParallelExecution(ALLOW)
    public void deleteMacrosIgnoringResult(Long macrosId) {
        deleteMacros(ANYTHING_MESSAGE, expectAnything(), macrosId);
    }

    private InternalMacrosPOSTSchema createMacros(String message, Matcher matcher, TrackingPartnerMacros macros) {
        InternalMacrosPOSTSchema result = post(
                InternalMacrosPOSTSchema.class,
                "/internal/macros",
                new InternalMacrosPOSTRequestSchema().withMacros(macros));

        assertThat(message, result, matcher);

        return result;
    }

    private ManagementV1TrackingPartnerIdMacrosGETSchema getTrackingMacrosList(String message, Matcher matcher, Long partnerId) {
        ManagementV1TrackingPartnerIdMacrosGETSchema result = get(
                ManagementV1TrackingPartnerIdMacrosGETSchema.class,
                String.format("/management/v1/tracking/partner/%s/macros", partnerId));

        assertThat(message, result, matcher);

        return result;
    }

    private void deleteMacros(String message, Matcher matcher, Long macrosId) {
        InternalMacrosIdDELETESchema result = delete(
                InternalMacrosIdDELETESchema.class,
                String.format("/internal/macros/%s", macrosId));

        assertThat(message, result, matcher);
    }
}
