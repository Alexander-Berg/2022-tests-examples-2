package ru.yandex.autotests.metrika.appmetrica.steps;

import java.net.URL;
import java.util.List;

import org.hamcrest.Matcher;
import ru.yandex.autotests.httpclientlite.HttpClientLite;
import ru.yandex.autotests.irt.testutils.allure.AssumptionException;
import ru.yandex.autotests.metrika.appmetrica.beans.schemes.InternalPartnerIdPUTRequestSchema;
import ru.yandex.autotests.metrika.appmetrica.beans.schemes.InternalPartnerIdPUTSchema;
import ru.yandex.autotests.metrika.appmetrica.beans.schemes.InternalPartnersPOSTSchema;
import ru.yandex.autotests.metrika.appmetrica.beans.schemes.ManagementV1TrackingPartnerIdDELETESchema;
import ru.yandex.autotests.metrika.appmetrica.beans.schemes.ManagementV1TrackingPartnerIdGETSchema;
import ru.yandex.autotests.metrika.appmetrica.beans.schemes.ManagementV1TrackingPartnerIdPUTRequestSchema;
import ru.yandex.autotests.metrika.appmetrica.beans.schemes.ManagementV1TrackingPartnerIdPUTSchema;
import ru.yandex.autotests.metrika.appmetrica.beans.schemes.ManagementV1TrackingPartnersGETSchema;
import ru.yandex.autotests.metrika.appmetrica.beans.schemes.ManagementV1TrackingPartnersPOSTRequestSchema;
import ru.yandex.autotests.metrika.appmetrica.beans.schemes.ManagementV1TrackingPartnersPOSTSchema;
import ru.yandex.autotests.metrika.appmetrica.core.AppMetricaCsvRawResponse;
import ru.yandex.autotests.metrika.appmetrica.core.AppMetricaCsvResponse;
import ru.yandex.autotests.metrika.appmetrica.info.csv.CsvPartner;
import ru.yandex.autotests.metrika.appmetrica.parameters.CommonReportParameters;
import ru.yandex.autotests.metrika.appmetrica.steps.parallel.ParallelExecution;
import ru.yandex.autotests.metrika.appmetrica.wrappers.PartnerWrapper;
import ru.yandex.autotests.metrika.commons.response.IExpectedError;
import ru.yandex.metrika.mobmet.model.redirect.TrackingPartner;
import ru.yandex.qatools.allure.annotations.Step;

import static java.lang.String.format;
import static ru.yandex.autotests.irt.testutils.allure.TestSteps.assertThat;
import static ru.yandex.autotests.metrika.appmetrica.parameters.FreeFormParameters.makeParameters;
import static ru.yandex.autotests.metrika.appmetrica.steps.parallel.ParallelExecution.Permission.ALLOW;
import static ru.yandex.autotests.metrika.commons.response.ResponseMatchers.ANYTHING_MESSAGE;
import static ru.yandex.autotests.metrika.commons.response.ResponseMatchers.ERROR_MESSAGE;
import static ru.yandex.autotests.metrika.commons.response.ResponseMatchers.SUCCESS_MESSAGE;
import static ru.yandex.autotests.metrika.commons.response.ResponseMatchers.expectAnything;
import static ru.yandex.autotests.metrika.commons.response.ResponseMatchers.expectError;
import static ru.yandex.autotests.metrika.commons.response.ResponseMatchers.expectSuccess;

/**
 * Created by graev on 22/12/2016.
 */
public class PartnerSteps extends AppMetricaBaseSteps {
    private static final int LIMIT_TO_FETCH_ALL_PARTNERS = 1_000_000;

    public PartnerSteps(URL baseUrl, HttpClientLite client) {
        super(baseUrl, client);
    }

    @Step("Создать партнера {0}")
    @ParallelExecution(ALLOW)
    public TrackingPartner createPartner(PartnerWrapper partner) {
        return createPartner(SUCCESS_MESSAGE, expectSuccess(), partner.getPartner()).getPartner();
    }

    @Step("Создать интегрированного партнера {0}")
    @ParallelExecution(ALLOW)
    public TrackingPartner createIntegratedPartner(PartnerWrapper partner) {
        return createIntegratedPartner(SUCCESS_MESSAGE, expectSuccess(), partner.getPartner()).getPartner();
    }

    @Step("Создать интегрированного партнера {0} и ожидать ошибку {1}")
    @ParallelExecution(ALLOW)
    public TrackingPartner createIntegratedPartnerAndExpectError(PartnerWrapper partner, IExpectedError error) {
        return createIntegratedPartner(SUCCESS_MESSAGE, expectError(error), partner.getPartner()).getPartner();
    }

    @Step("Получить партнера {0}")
    @ParallelExecution(ALLOW)
    public TrackingPartner getPartner(Long partnerId) {
        return getPartner(SUCCESS_MESSAGE, expectSuccess(), partnerId).getPartner();
    }

    @Step("Получить партнера {0} и ожидать ошибку {1}")
    @ParallelExecution(ALLOW)
    public TrackingPartner getPartnerExpectingError(Long partnerId, IExpectedError error) {
        return getPartner(ERROR_MESSAGE, expectError(error), partnerId).getPartner();
    }

    @Step("Получить партнера {0} из списка")
    @ParallelExecution(ALLOW)
    public TrackingPartner getPartnerFromList(Long partnerId) {
        return getPartnersList(SUCCESS_MESSAGE, expectSuccess()).getPartners().getPartners()
                .stream()
                .filter(p -> p.getId().equals(partnerId))
                .findFirst()
                .orElseThrow(() -> new AssumptionException(format("Партнер %s присутствует в списке", partnerId)));
    }

    @Step("Получить список партнеров для текущего пользователя")
    @ParallelExecution(ALLOW)
    public List<TrackingPartner> getPartnersList() {
        return getPartnersList(SUCCESS_MESSAGE, expectSuccess()).getPartners().getPartners();
    }

    @Step("Редактировать партнера {0}")
    @ParallelExecution(ALLOW)
    public TrackingPartner editPartner(PartnerWrapper newPartner) {
        return editPartner(SUCCESS_MESSAGE, expectSuccess(), newPartner.getPartner()).getPartner();
    }

    @Step("Редактировать партнера {0} и ожидать ошибку {1}")
    @ParallelExecution(ALLOW)
    public TrackingPartner editPartnerAndExpectError(PartnerWrapper newPartner, IExpectedError error) {
        return editPartner(ERROR_MESSAGE, expectError(error), newPartner.getPartner()).getPartner();
    }

    @Step("Редактировать интегрированного партнера {0}")
    @ParallelExecution(ALLOW)
    public TrackingPartner editIntegratedPartner(PartnerWrapper newPartner) {
        return editIntegratedPartner(SUCCESS_MESSAGE, expectSuccess(), newPartner.getPartner()).getPartner();
    }

    @Step("Редактировать интегрированного партнера {0} и ожидать ошибку {1}")
    @ParallelExecution(ALLOW)
    public TrackingPartner editIntegratedPartnerAndExpectError(PartnerWrapper newPartner, IExpectedError error) {
        return editIntegratedPartner(SUCCESS_MESSAGE,expectError(error), newPartner.getPartner()).getPartner();
    }

    @Step("Удалить партнера {0}")
    @ParallelExecution(ALLOW)
    public void deletePartner(Long partnerId) {
        deletePartner(SUCCESS_MESSAGE, expectSuccess(), partnerId);
    }

    @Step("Удалить партнера {0} и ожидать ошибку")
    @ParallelExecution(ALLOW)
    public void deletePartnerAndExpectError(Long partnerId, IExpectedError error) {
        deletePartner(ERROR_MESSAGE, expectError(error), partnerId);
    }

    @Step("Удалить интегрированного партнера {0} и игнорировать результат")
    @ParallelExecution(ALLOW)
    public void deleteIntegratedPartnerIgnoringResult(Long partnerId) {
        deleteIntegratedPartner(ANYTHING_MESSAGE, expectAnything(), partnerId);
    }

    @Step("Удалить интегрированного партнера {0} и ожидать ошибку {1}")
    @ParallelExecution(ALLOW)
    public void deleteIntegratedPartnerAndExpectError(Long partnerId, IExpectedError error) {
        deleteIntegratedPartner(ERROR_MESSAGE, expectError(error), partnerId);
    }

    @Step("Удалить партнера {0} и игнорировать результат")
    @ParallelExecution(ALLOW)
    public void deletePartnerIgnoringResult(Long partnerId) {
        deletePartner(ANYTHING_MESSAGE, expectAnything(), partnerId);
    }

    @Step("Получить данные из csv с локалью {0}")
    @ParallelExecution(ALLOW)
    public AppMetricaCsvResponse<CsvPartner> getPartnerCsv(String locale) {
        return get(AppMetricaCsvRawResponse.class,
                "management/v1/tracking/partners.csv",
                new CommonReportParameters().withLang(locale))
                .withMapper(CsvPartner::new);
    }

    private ManagementV1TrackingPartnersPOSTSchema createPartner(String message, Matcher matcher, TrackingPartner partner) {
        ManagementV1TrackingPartnersPOSTSchema result = post(
                ManagementV1TrackingPartnersPOSTSchema.class,
                "/management/v1/tracking/partners",
                new ManagementV1TrackingPartnersPOSTRequestSchema().withPartner(partner));

        assertThat(message, result, matcher);

        return result;
    }

    private InternalPartnersPOSTSchema createIntegratedPartner(String message, Matcher matcher, TrackingPartner partner) {
        InternalPartnersPOSTSchema result = post(
                InternalPartnersPOSTSchema.class,
                "/internal/partners",
                new InternalPartnersPOSTSchema().withPartner(partner));

        assertThat(message, result, matcher);

        return result;
    }

    private ManagementV1TrackingPartnerIdGETSchema getPartner(String message, Matcher matcher, Long partnerId) {
        ManagementV1TrackingPartnerIdGETSchema result = get(
                ManagementV1TrackingPartnerIdGETSchema.class,
                format("/management/v1/tracking/partner/%s", partnerId));

        assertThat(message, result, matcher);

        return result;
    }

    private ManagementV1TrackingPartnersGETSchema getPartnersList(String message, Matcher matcher) {
        ManagementV1TrackingPartnersGETSchema result = get(
                ManagementV1TrackingPartnersGETSchema.class,
                "/management/v1/tracking/partners",
                makeParameters("limit", LIMIT_TO_FETCH_ALL_PARTNERS));

        assertThat(message, result, matcher);

        return result;
    }

    private ManagementV1TrackingPartnerIdPUTSchema editPartner(String message, Matcher matcher, TrackingPartner newPartner) {
        ManagementV1TrackingPartnerIdPUTSchema result = put(
                ManagementV1TrackingPartnerIdPUTSchema.class,
                format("/management/v1/tracking/partner/%s", newPartner.getId()),
                new ManagementV1TrackingPartnerIdPUTRequestSchema().withPartner(newPartner));

        assertThat(message, result, matcher);

        return result;
    }

    private InternalPartnerIdPUTSchema editIntegratedPartner(String message, Matcher matcher, TrackingPartner newPartner) {
        InternalPartnerIdPUTSchema result = put(
                InternalPartnerIdPUTSchema.class,
                format("/internal/partner/%s", newPartner.getId()),
                new InternalPartnerIdPUTRequestSchema().withPartner(newPartner));

        assertThat(message, result, matcher);

        return result;
    }

    private void deletePartner(String message, Matcher matcher, Long partnerId) {
        ManagementV1TrackingPartnerIdDELETESchema result = delete(
                ManagementV1TrackingPartnerIdDELETESchema.class,
                format("/management/v1/tracking/partner/%s", partnerId));

        assertThat(message, result, matcher);
    }

    private void deleteIntegratedPartner(String message, Matcher matcher, Long partnerId) {
        ManagementV1TrackingPartnerIdDELETESchema result = delete(
                ManagementV1TrackingPartnerIdDELETESchema.class,
                format("/internal/partner/%s", partnerId));

        assertThat(message, result, matcher);
    }
}
