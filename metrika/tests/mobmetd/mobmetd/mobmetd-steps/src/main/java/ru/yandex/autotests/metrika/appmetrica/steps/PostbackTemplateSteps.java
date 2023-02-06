package ru.yandex.autotests.metrika.appmetrica.steps;

import java.net.URL;
import java.util.List;

import org.hamcrest.Matcher;
import ru.yandex.autotests.httpclientlite.HttpClientLite;
import ru.yandex.autotests.metrika.appmetrica.beans.schemes.ManagementV1TrackingPartnerPartnerIdPostbacksGETSchema;
import ru.yandex.autotests.metrika.appmetrica.beans.schemes.ManagementV1TrackingPostbackIdDELETESchema;
import ru.yandex.autotests.metrika.appmetrica.beans.schemes.ManagementV1TrackingPostbackIdGETSchema;
import ru.yandex.autotests.metrika.appmetrica.beans.schemes.ManagementV1TrackingPostbackIdPUTRequestSchema;
import ru.yandex.autotests.metrika.appmetrica.beans.schemes.ManagementV1TrackingPostbackIdPUTSchema;
import ru.yandex.autotests.metrika.appmetrica.beans.schemes.ManagementV1TrackingPostbacksPOSTRequestSchema;
import ru.yandex.autotests.metrika.appmetrica.beans.schemes.ManagementV1TrackingPostbacksPOSTSchema;
import ru.yandex.autotests.metrika.appmetrica.steps.parallel.ParallelExecution;
import ru.yandex.autotests.metrika.appmetrica.wrappers.PostbackTemplateWrapper;
import ru.yandex.autotests.metrika.commons.response.IExpectedError;
import ru.yandex.metrika.mobmet.model.redirect.PostbackTemplate;
import ru.yandex.qatools.allure.annotations.Step;

import static ru.yandex.autotests.irt.testutils.allure.TestSteps.assertThat;
import static ru.yandex.autotests.metrika.appmetrica.steps.parallel.ParallelExecution.Permission.ALLOW;
import static ru.yandex.autotests.metrika.commons.response.ResponseMatchers.ANYTHING_MESSAGE;
import static ru.yandex.autotests.metrika.commons.response.ResponseMatchers.ERROR_MESSAGE;
import static ru.yandex.autotests.metrika.commons.response.ResponseMatchers.SUCCESS_MESSAGE;
import static ru.yandex.autotests.metrika.commons.response.ResponseMatchers.expectAnything;
import static ru.yandex.autotests.metrika.commons.response.ResponseMatchers.expectError;
import static ru.yandex.autotests.metrika.commons.response.ResponseMatchers.expectSuccess;

/**
 * Created by graev on 23/12/2016.
 */
public class PostbackTemplateSteps extends AppMetricaBaseSteps {
    public PostbackTemplateSteps(URL baseUrl, HttpClientLite client) {
        super(baseUrl, client);
    }

    @Step("Создать шаблон постбека {0}")
    @ParallelExecution(ALLOW)
    public PostbackTemplate createTemplate(PostbackTemplateWrapper template) {
        return createTemplate(SUCCESS_MESSAGE, expectSuccess(), template.getTemplate()).getPostbackTemplate();
    }

    @Step("Создать шаблон постбека {0} и ожидать ошибку {1}")
    @ParallelExecution(ALLOW)
    public PostbackTemplate createTemplateAndExpectError(PostbackTemplateWrapper template, IExpectedError error) {
        return createTemplate(ERROR_MESSAGE, expectError(error), template.getTemplate()).getPostbackTemplate();
    }

    @Step("Получить шаблон постбека {0}")
    @ParallelExecution(ALLOW)
    public PostbackTemplate getPostbackTemplate(Long templateId) {
        return getPostbackTemplate(SUCCESS_MESSAGE, expectSuccess(), templateId).getPostbackTemplate();
    }

    @Step("Получить шаблон постбека {0} и ожидать ошибку {1}")
    @ParallelExecution(ALLOW)
    public PostbackTemplate getPostbackTemplateAndExpectError(Long templateId, IExpectedError error) {
        return getPostbackTemplate(ERROR_MESSAGE, expectError(error), templateId).getPostbackTemplate();
    }

    @Step("Получить список шаблонов постбеков для партнера {0}")
    @ParallelExecution(ALLOW)
    public List<PostbackTemplate> getPostbackTemplateList(Long partnerId) {
        return getPostbackTemplateList(SUCCESS_MESSAGE, expectSuccess(), partnerId).getPostbacks();
    }

    @Step("Отредактировать шаблон постбека на {0}")
    @ParallelExecution(ALLOW)
    public PostbackTemplate editPostbackTemplate(PostbackTemplateWrapper template) {
        return editPostbackTemplate(SUCCESS_MESSAGE, expectSuccess(), template.getTemplate()).getPostbackTemplate();
    }

    @Step("Отредактировать шаблон постбека на {0} и ожидать ошибку {1}")
    @ParallelExecution(ALLOW)
    public PostbackTemplate editPostbackTemplateAndExpectError(PostbackTemplateWrapper template, IExpectedError error) {
        return editPostbackTemplate(ERROR_MESSAGE, expectError(error), template.getTemplate()).getPostbackTemplate();
    }

    @Step("Удалить шаблон постбека {0}")
    @ParallelExecution(ALLOW)
    public void deleteTemplate(Long templateId) {
        deleteTemplate(SUCCESS_MESSAGE, expectSuccess(), templateId);
    }

    @Step("Удалить шаблон постбека {0} и ожидать ошибку {1}")
    @ParallelExecution(ALLOW)
    public void deleteTemplateAndExpectError(Long templateId, IExpectedError error) {
        deleteTemplate(ERROR_MESSAGE, expectError(error), templateId);
    }

    @Step("Удалить шаблон постбека и игнорировать результат")
    @ParallelExecution(ALLOW)
    public void deleteTemplateIgnoringResult(PostbackTemplate template) {
        if (template != null) {
            deleteTemplate(ANYTHING_MESSAGE, expectAnything(), template.getId());
        }
    }

    @Step("Удалить шаблон постбека {0} и игнорировать результат")
    @ParallelExecution(ALLOW)
    public void deleteTemplateIgnoringResult(Long templateId) {
        deleteTemplate(ANYTHING_MESSAGE, expectAnything(), templateId);
    }

    private ManagementV1TrackingPostbacksPOSTSchema createTemplate(String message, Matcher matcher, PostbackTemplate template) {
        ManagementV1TrackingPostbacksPOSTSchema result = post(
                ManagementV1TrackingPostbacksPOSTSchema.class,
                "/management/v1/tracking/postbacks",
                new ManagementV1TrackingPostbacksPOSTRequestSchema().withPostbackTemplate(template));

        assertThat(message, result, matcher);

        return result;
    }

    private ManagementV1TrackingPartnerPartnerIdPostbacksGETSchema getPostbackTemplateList(String message, Matcher matcher, Long partnerId) {
        ManagementV1TrackingPartnerPartnerIdPostbacksGETSchema result = get(
                ManagementV1TrackingPartnerPartnerIdPostbacksGETSchema.class,
                String.format("/management/v1/tracking/partner/%s/postbacks", partnerId));

        assertThat(message, result, matcher);

        return result;
    }

    private ManagementV1TrackingPostbackIdGETSchema getPostbackTemplate(String message, Matcher matcher, Long templateId) {
        ManagementV1TrackingPostbackIdGETSchema result = get(
                ManagementV1TrackingPostbackIdGETSchema.class,
                String.format("/management/v1/tracking/postback/%s", templateId));

        assertThat(message, result, matcher);

        return result;
    }

    private ManagementV1TrackingPostbackIdPUTSchema editPostbackTemplate(String message, Matcher matcher, PostbackTemplate template) {
        ManagementV1TrackingPostbackIdPUTSchema result = put(
                ManagementV1TrackingPostbackIdPUTSchema.class,
                String.format("/management/v1/tracking/postback/%s", template.getId()),
                new ManagementV1TrackingPostbackIdPUTRequestSchema().withPostbackTemplate(template));

        assertThat(message, result, matcher);

        return result;
    }

    private void deleteTemplate(String message, Matcher matcher, Long templateId) {
        ManagementV1TrackingPostbackIdDELETESchema result = delete(
                ManagementV1TrackingPostbackIdDELETESchema.class,
                String.format("/management/v1/tracking/postback/%s", templateId));

        assertThat(message, result, matcher);
    }
}
