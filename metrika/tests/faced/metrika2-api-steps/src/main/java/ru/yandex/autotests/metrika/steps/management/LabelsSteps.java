package ru.yandex.autotests.metrika.steps.management;

import org.apache.http.HttpEntity;
import org.hamcrest.Matcher;
import ru.yandex.autotests.metrika.beans.schemes.*;
import ru.yandex.autotests.metrika.commons.response.IExpectedError;
import ru.yandex.autotests.metrika.steps.MetrikaBaseSteps;
import ru.yandex.autotests.metrika.utils.EmptyHttpEntity;
import ru.yandex.metrika.api.management.client.counter.BadCounter;
import ru.yandex.metrika.api.management.client.external.CounterFull;
import ru.yandex.metrika.api.management.client.label.Label;
import ru.yandex.qatools.allure.annotations.Step;

import java.util.ArrayList;
import java.util.List;

import static ch.lambdaj.Lambda.on;
import static ch.lambdaj.collection.LambdaCollections.with;
import static ru.yandex.autotests.httpclient.lite.core.BackEndRequestBuilder.EMPTY_CONTEXT;
import static ru.yandex.autotests.irt.testutils.allure.TestSteps.assertThat;
import static ru.yandex.autotests.metrika.commons.response.ResponseMatchers.*;

/**
 * Created by proxeter on 28.07.2014.
 */
public class LabelsSteps extends MetrikaBaseSteps {

    @Step("Получение данных метки")
    public Label getLabelInfo(Long labelId) {
        ManagementV1LabelLabelIdGETSchema result = executeAsJson(
                getRequestBuilder(String.format("/management/v1/label/%s", labelId)).get())
                .readResponse(ManagementV1LabelLabelIdGETSchema.class);

        assertThat(SUCCESS_MESSAGE, result, expectSuccess());

        return result.getLabel();
    }

    @Step("Получение списка доступных меток")
    public List<Long> getLabels() {
        ManagementV1LabelsGETSchema result = executeAsJson(
                getRequestBuilder("/management/v1/labels").get())
                .readResponse(ManagementV1LabelsGETSchema.class);

        assertThat(SUCCESS_MESSAGE, result, expectSuccess());

        return with(result.getLabels()).extract(on(Label.class).getId());
    }

    @Step("Добавление метки")
    public Label addLabelAndExpectSuccess(Label label) {
        return addLabel(SUCCESS_MESSAGE, expectSuccess(), label).getLabel();
    }

    @Step("Добавление меток")
    public List<Long> addLabels(List<Label> labels) {
        if (labels.isEmpty()) {
            return null;
        }
        List<Long> labelIds = new ArrayList<>();
        labels.forEach(label -> labelIds.add(addLabelAndExpectSuccess(label).getId()));
        return labelIds;
    }

    @Step("Добавить метку и ожидать ошибку {0}")
    public void addLabelAndExpectError(IExpectedError error, Label label) {
        addLabel(ERROR_MESSAGE, expectError(error), label);
    }

    private ManagementV1LabelsPOSTSchema addLabel(String message, Matcher matcher,
                                                  Label label) {
        ManagementV1LabelsPOSTSchema result = executeAsJson(
                getRequestBuilder("/management/v1/labels").post(
                        new ManagementV1LabelsPOSTRequestSchema().withLabel(label)))
                .readResponse(ManagementV1LabelsPOSTSchema.class);

        assertThat(message, result, matcher);

        return result;
    }

    @Step("Удалить метку {0}")
    public Boolean deleteLabelAndExpectSuccess(Long labelId) {
        // Не надо удалять метку, если labelId == null
        if (labelId == null) {
            return null;
        }

        ManagementV1LabelLabelIdDELETESchema result = executeAsJson(
                getRequestBuilder(String.format("/management/v1/label/%s", labelId))
                        .delete(EMPTY_CONTEXT))
                .readResponse(ManagementV1LabelLabelIdDELETESchema.class);

        assertThat(SUCCESS_MESSAGE, result, expectSuccess());

        return result.getSuccess();
    }

    @Step("Удалить метку и ожидать ошибку {0}")
    public Boolean deleteLabelAndExpectError(IExpectedError error, Long labelId) {
        if (labelId == null) {
            return null;
        }

        ManagementV1LabelLabelIdDELETESchema result = executeAsJson(
                getRequestBuilder(String.format("/management/v1/label/%s", labelId))
                        .delete(EMPTY_CONTEXT))
                .readResponse(ManagementV1LabelLabelIdDELETESchema.class);

        assertThat(ERROR_MESSAGE, result, expectError(error));

        return result.getSuccess();
    }

    @Step("Удалить несколько меток")
    public void deleteLabels(List<Long> labelIds) {
        labelIds.forEach(this::deleteLabelAndExpectSuccess);
    }

    @Step("Изменение данных метки")
    public Label editLabelAndExpectSuccess(Long labelId, Label label) {
        return editLabel(SUCCESS_MESSAGE, expectSuccess(), labelId, label).getLabel();
    }

    @Step("Изменить данные метки и ожидать ошибку {0}")
    public void editLabelAndExpectError(IExpectedError error, Long labelId, Label label) {
        editLabel(ERROR_MESSAGE, expectError(error), labelId, label);
    }

    private ManagementV1LabelLabelIdPUTSchema editLabel(String message, Matcher matcher,
                                                        Long labelId, Label label) {

        ManagementV1LabelLabelIdPUTSchema result = executeAsJson(
                getRequestBuilder(String.format("/management/v1/label/%s", labelId)).put(
                        new ManagementV1LabelsPOSTRequestSchema().withLabel(label)))
                .readResponse(ManagementV1LabelLabelIdPUTSchema.class);

        assertThat(message, result, matcher);

        return result;
    }

    @Step("Изменение порядка меток")
    public void changeLabelsOrder(List<Long> labelIds) {
        ManagementV1LabelsOrderPUTSchema result = executeAsJson(
                getRequestBuilder("/management/v1/labels/order")
                        .put(new ManagementV1LabelsOrderPUTRequestSchema().withLabels(labelIds)))
                .readResponse(ManagementV1LabelsOrderPUTSchema.class);

        assertThat(SUCCESS_MESSAGE, result, expectSuccess());
    }

    @Step("Привязать счетчик {0} к метке {1}")
    public Boolean joinCounterToLabelAndExpectSuccess(
            Long counterId, Long labelId) {
        return joinCounterToLabel(SUCCESS_MESSAGE, expectSuccess(), counterId, labelId).getSuccess();
    }

    @Step("Привязать счетчики к метке {1}")
    public void joinCountersToLabel(List<Long> counterIds, Long labelId) {
        for (Long counterId : counterIds) {
            joinCounterToLabelAndExpectSuccess(counterId, labelId);
        }
    }

    @Step("Привязать счетчик {1} к метке {2} и ожидать ошибку {0}")
    public Boolean joinCounterToLabelAndExpectError(
            IExpectedError error, Long counterId, Long labelId) {
        return joinCounterToLabel(ERROR_MESSAGE, expectError(error), counterId, labelId).getSuccess();
    }

    private ManagementV1CounterCounterIdLabelLabelIdPOSTSchema joinCounterToLabel(
            String message, Matcher matcher,
            Long counterId, Long labelId) {
        ManagementV1CounterCounterIdLabelLabelIdPOSTSchema result =
                executeAsJson(getRequestBuilder(
                        String.format("/management/v1/counter/%s/label/%s", counterId, labelId))
                        .post(new EmptyHttpEntity(), EMPTY_CONTEXT))
                        .readResponse(ManagementV1CounterCounterIdLabelLabelIdPOSTSchema.class);

        assertThat(message, result, matcher);

        return result;
    }

    @Step("Отменить привязку счетчика {0} к метке {1}")
    public ManagementV1CounterCounterIdLabelLabelIdDELETESchema cancelJoinCounterToLabelAndExpectSuccess(
            Long counterId, Long labelId) {
        ManagementV1CounterCounterIdLabelLabelIdDELETESchema result = executeAsJson(
                getRequestBuilder(
                        String.format("/management/v1/counter/%s/label/%s", counterId, labelId))
                        .delete(EMPTY_CONTEXT))
                .readResponse(ManagementV1CounterCounterIdLabelLabelIdDELETESchema.class);

        assertThat(SUCCESS_MESSAGE, result, expectSuccess());

        return result;
    }

    @Step("Отменить привязку счетчика {1} к метке {2} и ожидать ошибку {0}")
    public ManagementV1CounterCounterIdLabelLabelIdDELETESchema cancelJoinCounterToLabelAndExpectError(
            IExpectedError error, Long counterId, Long labelId) {
        ManagementV1CounterCounterIdLabelLabelIdDELETESchema result = executeAsJson(
                getRequestBuilder(
                        String.format("/management/v1/counter/%s/label/%s", counterId, labelId))
                        .delete(EMPTY_CONTEXT))
                .readResponse(ManagementV1CounterCounterIdLabelLabelIdDELETESchema.class);

        assertThat(ERROR_MESSAGE, result, expectError(error));

        return result;
    }

    @Step("Получение списка счетчиков, привязанных к метке {0}")
    public List<CounterFull> getCountersByLabelAndExpectSuccess(Long labelId) {
        return getCountersByLabel(SUCCESS_MESSAGE, expectSuccess(), labelId).getCounters();
    }

    @Step("Получение списка недоступных счетчиков, привязанных к метке {0}")
    public List<BadCounter> getBadCountersByLabelAndExpectSuccess(Long labelId) {
        return getCountersByLabel(SUCCESS_MESSAGE, expectSuccess(), labelId).getBadCounters();
    }

    private ManagementV1CountersLabelIdGETSchema getCountersByLabel(String message, Matcher matcher, long labelId) {
        ManagementV1CountersLabelIdGETSchema result = executeAsJson(
                getRequestBuilder(String.format("/management/v1/counters/%s", labelId)).get())
                .readResponse(ManagementV1CountersLabelIdGETSchema.class);

        assertThat(message, result, matcher);

        return result;
    }
}
