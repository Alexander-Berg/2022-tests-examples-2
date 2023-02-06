package ru.yandex.metrika.mobile.push.api.steps;

import org.springframework.stereotype.Component;
import org.springframework.test.web.servlet.MockMvc;
import org.springframework.test.web.servlet.ResultMatcher;

import ru.yandex.metrika.api.management.steps.MockMvcSteps;
import ru.yandex.metrika.mobmet.push.api.model.PushTransferWrapper;
import ru.yandex.metrika.mobmet.push.common.transfers.model.PushTransfer;
import ru.yandex.qatools.allure.annotations.Step;

import static java.lang.String.format;
import static org.springframework.test.web.servlet.request.MockMvcRequestBuilders.get;

@Component
public class StatusSteps extends MockMvcSteps {

    @Step("Получить статус рассылки {1}")
    public PushTransfer receive(MockMvc mockMvc, long transferId) throws Exception {
        return execute(mockMvc, get(format("/push/v1/status/%d", transferId)), PushTransferWrapper.class)
                .getTransfer();
    }

    @Step("Получить статус рассылки {2} в группе {1}")
    public PushTransfer receive(MockMvc mockMvc, long groupId, long clientTransferId) throws Exception {
        return execute(mockMvc,
                get(format("/push/v1/status/%d/%d", groupId, clientTransferId)),
                PushTransferWrapper.class)
                .getTransfer();
    }

    @Step("Получить статус рассылки {2} в группе {1} и ожидать ошибку {3}")
    public void receiveWithError(MockMvc mockMvc,
                                 long groupId,
                                 long clientTransferId,
                                 ResultMatcher matcher) throws Exception {
        execute(mockMvc, get(format("/push/v1/status/%d/%d", groupId, clientTransferId)), matcher);
    }

}
