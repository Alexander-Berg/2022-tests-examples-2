package ru.yandex.autotests.metrika.appmetrica.steps;

import org.hamcrest.Matcher;
import ru.yandex.autotests.httpclientlite.HttpClientLite;
import ru.yandex.autotests.metrika.appmetrica.beans.schemes.ManagementV1LabelLabelIdDELETESchema;
import ru.yandex.autotests.metrika.appmetrica.beans.schemes.ManagementV1LabelLabelIdLinkApikeyPOSTSchema;
import ru.yandex.autotests.metrika.appmetrica.beans.schemes.ManagementV1LabelsPOSTRequestSchema;
import ru.yandex.autotests.metrika.appmetrica.beans.schemes.ManagementV1LabelsPOSTSchema;
import ru.yandex.autotests.metrika.appmetrica.steps.parallel.ParallelExecution;
import ru.yandex.metrika.mobmet.model.AppLabel;
import ru.yandex.qatools.allure.annotations.Step;

import java.net.URL;

import static java.lang.String.format;
import static ru.yandex.autotests.irt.testutils.allure.TestSteps.assertThat;
import static ru.yandex.autotests.metrika.commons.response.ResponseMatchers.*;

public class LabelSteps extends AppMetricaBaseSteps {

    public LabelSteps(URL baseUrl, HttpClientLite client) {
        super(baseUrl, client);
    }

    @Step("Добавить папку")
    @ParallelExecution(ParallelExecution.Permission.ALLOW)
    public Long addLabel(AppLabel label) {
        // в контроллере нет wrapper-ов, а в тестах пока нужен только id
        return addLabel(SUCCESS_MESSAGE, expectSuccess(), label).getId();
    }

    @Step("Добавить приложение {0} в папку {1}")
    @ParallelExecution(ParallelExecution.Permission.ALLOW)
    public void linkApplicationToLabel(Long applicationId, Long labelId) {
        link(SUCCESS_MESSAGE, expectSuccess(), applicationId, labelId);
    }

    @Step("Удалить папку {0}")
    @ParallelExecution(ParallelExecution.Permission.ALLOW)
    public Boolean deleteLabel(Long id) {
        return deleteLabel(SUCCESS_MESSAGE, expectSuccess(), id).getSuccess();
    }

    @Step("Удалить папку {0} и игнорировать результат")
    @ParallelExecution(ParallelExecution.Permission.ALLOW)
    public Boolean deleteLabelAndIgnoreResult(Long id) {
        return deleteLabel(ANYTHING_MESSAGE, expectAnything(), id).getSuccess();
    }

    private ManagementV1LabelLabelIdDELETESchema deleteLabel(String message, Matcher matcher, Long id) {
        ManagementV1LabelLabelIdDELETESchema result = delete(ManagementV1LabelLabelIdDELETESchema.class,
                format("/management/v1/label/%s", id));

        assertThat(message, result, matcher);

        return result;
    }

    private ManagementV1LabelsPOSTSchema addLabel(String message, Matcher matcher, AppLabel label) {
        ManagementV1LabelsPOSTSchema result = post(ManagementV1LabelsPOSTSchema.class,
                "/management/v1/labels",
                new ManagementV1LabelsPOSTRequestSchema().withLabel(label));

        assertThat(message, result, matcher);

        return result;
    }

    private ManagementV1LabelLabelIdLinkApikeyPOSTSchema link(String message, Matcher matcher, Long applicationId, Long labelId) {
        ManagementV1LabelLabelIdLinkApikeyPOSTSchema result = post(ManagementV1LabelLabelIdLinkApikeyPOSTSchema.class,
                format("/management/v1/label/%s/link/%s", labelId, applicationId),
                null);

        assertThat(message, result, matcher);

        return result;
    }
}
