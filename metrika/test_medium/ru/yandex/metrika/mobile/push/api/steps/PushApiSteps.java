package ru.yandex.metrika.mobile.push.api.steps;

import org.awaitility.Duration;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.stereotype.Component;
import org.springframework.test.web.servlet.MockMvc;

import ru.yandex.qatools.allure.annotations.Step;

import static org.awaitility.Awaitility.await;
import static org.hamcrest.Matchers.equalTo;
import static org.springframework.test.web.servlet.request.MockMvcRequestBuilders.get;
import static org.springframework.test.web.servlet.result.MockMvcResultMatchers.jsonPath;
import static org.springframework.test.web.servlet.result.MockMvcResultMatchers.status;
import static ru.yandex.metrika.mobmet.push.common.model.PushTransferStatus.PENDING;

@Component
public class PushApiSteps {

    @Autowired
    private ApplicationsSteps applications;

    @Autowired
    private CredentialsSteps credentials;

    @Autowired
    private GroupsSteps groups;

    @Autowired
    private SendSteps send;

    @Autowired
    private StatusSteps status;

    @Autowired
    private LogsSteps logs;

    public ApplicationsSteps onApplications() {
        return applications;
    }

    public CredentialsSteps onCredentials() {
        return credentials;
    }

    public GroupsSteps onGroups() {
        return groups;
    }

    public SendSteps onSend() {
        return send;
    }

    public StatusSteps onStatus() {
        return status;
    }

    public LogsSteps onLogs() {
        return logs;
    }

    @Step("Подготовка")
    public void prepare() {
    }

    public void assertGetSuccess(MockMvc mockMvc, String handle) throws Exception {
        mockMvc.perform(get(handle))
                .andExpect(status().isOk())
                .andExpect(jsonPath("success", equalTo(true)));
    }

    /**
     * Часть проверок происходят уже на push-dispatcher.
     * В этом случае в тестах у трансфера будет статус
     * {@link ru.yandex.metrika.mobmet.push.common.model.PushTransferStatus#PENDING}
     */
    public void waitUntilFastValidationComplete(MockMvc mockMvc, long transferId) {
        await()
                .atMost(Duration.TEN_SECONDS)
                .pollInterval(Duration.ONE_SECOND)
                .ignoreExceptions()
                .alias("transferId=" + transferId + " waiting")
                .until(() -> validationCompleted(mockMvc, transferId));
    }

    private boolean validationCompleted(MockMvc mockMvc, long transferId) {
        try {
            return status.receive(mockMvc, transferId).getStatus() != PENDING;
        } catch (Exception exception) {
            throw new RuntimeException("transferId" + transferId + " status fetching is failed", exception);
        }
    }

}
