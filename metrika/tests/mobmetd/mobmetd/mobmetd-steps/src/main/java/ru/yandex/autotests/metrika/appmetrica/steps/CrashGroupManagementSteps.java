package ru.yandex.autotests.metrika.appmetrica.steps;

import ru.yandex.autotests.httpclientlite.HttpClientLite;
import ru.yandex.autotests.metrika.appmetrica.beans.schemes.*;
import ru.yandex.autotests.metrika.appmetrica.parameters.crash.ReportGroupPlural;
import ru.yandex.autotests.metrika.appmetrica.steps.parallel.ParallelExecution;
import ru.yandex.metrika.segments.apps.misc.crashes.CrashGroup;
import ru.yandex.metrika.segments.apps.misc.crashes.CrashGroupStatus;
import ru.yandex.qatools.allure.annotations.Step;

import java.net.URL;

import static java.lang.String.format;
import static org.hamcrest.MatcherAssert.assertThat;
import static ru.yandex.autotests.metrika.appmetrica.steps.parallel.ParallelExecution.Permission.ALLOW;
import static ru.yandex.autotests.metrika.commons.response.ResponseMatchers.SUCCESS_MESSAGE;
import static ru.yandex.autotests.metrika.commons.response.ResponseMatchers.expectSuccess;

public class CrashGroupManagementSteps extends AppMetricaBaseSteps {

    public CrashGroupManagementSteps(URL baseUrl, HttpClientLite client) {
        super(baseUrl, client);
    }

    @Step("({0}) Загрузить группу крэшей {2} приложения {1}")
    @ParallelExecution(ALLOW)
    public CrashGroup getCrashGroup(ReportGroupPlural report, long appId, String crashGroupId) {
        return doGetCrashGroup(report, appId, crashGroupId);
    }

    @Step("({0}) Добавить комментарий для группы крэшей {2} приложения {1}")
    @ParallelExecution(ALLOW)
    public void setCrashGroupComment(ReportGroupPlural report, long appId, String crashGroupId, String comment) {
        doSetCrashGroupComment(report, appId, crashGroupId, comment);
    }

    @Step("({0}) Удалить комментарий для группы крэшей {2} приложения {1}")
    @ParallelExecution(ALLOW)
    public void deleteCrashGroupComment(ReportGroupPlural report, long appId, String crashGroupId) {
        doDeleteCrashGroupComment(report, appId, crashGroupId);
    }

    @Step("({0}) Установить статус {3} для группы крэшей {2} приложения {1}")
    @ParallelExecution(ALLOW)
    public void setCrashGroupStatus(ReportGroupPlural report, long appId, String crashGroupId, CrashGroupStatus status) {
        doSetCrashGroupStatus(report, appId, crashGroupId, status);
    }

    private CrashGroup doGetCrashGroup(ReportGroupPlural report, long appId, String crashGroupId) {
        ManagementV1ApplicationApiKeyTypeCrashesErrorsAnrsCrashGroupIdGETSchema result = get(
                ManagementV1ApplicationApiKeyTypeCrashesErrorsAnrsCrashGroupIdGETSchema.class,
                format("/management/v1/application/%s/%s/%s", appId, report, crashGroupId));

        assertThat(SUCCESS_MESSAGE, result, expectSuccess());

        return result.getResponse();
    }

    private void doSetCrashGroupComment(ReportGroupPlural report, long appId, String crashGroupId, String comment) {
        ManagementV1ApplicationApiKeyTypeCrashesErrorsAnrsCrashGroupIdCommentPOSTSchema result = post(
                ManagementV1ApplicationApiKeyTypeCrashesErrorsAnrsCrashGroupIdCommentPOSTSchema.class,
                format("/management/v1/application/%s/%s/%s/comment", appId, report, crashGroupId),
                new ManagementV1ApplicationApiKeyTypeCrashesErrorsAnrsCrashGroupIdCommentPOSTRequestSchema()
                        .withValue(comment));

        assertThat(SUCCESS_MESSAGE, result, expectSuccess());
    }

    private void doDeleteCrashGroupComment(ReportGroupPlural report, long appId, String crashGroupId) {
        ManagementV1ApplicationApiKeyTypeCrashesErrorsAnrsCrashGroupIdCommentDELETESchema result = delete(
                ManagementV1ApplicationApiKeyTypeCrashesErrorsAnrsCrashGroupIdCommentDELETESchema.class,
                format("/management/v1/application/%s/%s/%s/comment", appId, report, crashGroupId));

        assertThat(SUCCESS_MESSAGE, result, expectSuccess());
    }

    private void doSetCrashGroupStatus(ReportGroupPlural report, long appId, String crashGroupId, CrashGroupStatus status) {
        ManagementV1ApplicationApiKeyTypeCrashesErrorsAnrsCrashGroupIdStatusPOSTSchema result = post(
                ManagementV1ApplicationApiKeyTypeCrashesErrorsAnrsCrashGroupIdStatusPOSTSchema.class,
                format("/management/v1/application/%s/%s/%s/status", appId, report, crashGroupId),
                new ManagementV1ApplicationApiKeyTypeCrashesErrorsAnrsCrashGroupIdStatusPOSTRequestSchema()
                        .withValue(status));

        assertThat(SUCCESS_MESSAGE, result, expectSuccess());
    }

}
