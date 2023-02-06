package ru.yandex.metrika.mobile.push.api.steps;

import org.springframework.stereotype.Component;
import org.springframework.test.web.servlet.MockMvc;
import org.springframework.test.web.servlet.ResultMatcher;

import ru.yandex.metrika.api.management.steps.MockMvcSteps;
import ru.yandex.metrika.mobmet.push.api.model.PushApiResponse;
import ru.yandex.metrika.mobmet.push.api.model.PushApiResponseWrapper;
import ru.yandex.metrika.mobmet.push.api.model.send.PushApiBatchRequestAdapter;
import ru.yandex.metrika.mobmet.push.api.model.send.PushApiBatchRequestAdapterWrapper;
import ru.yandex.qatools.allure.annotations.Step;

import static org.springframework.test.web.servlet.request.MockMvcRequestBuilders.post;
import static ru.yandex.metrika.util.json.ObjectMappersFactory.getDefaultMapper;

@Component
public class SendSteps extends MockMvcSteps {

    @Step("Разослать batch сообщения")
    public PushApiResponse batch(MockMvc mockMvc, PushApiBatchRequestAdapter batch) throws Exception {
        String content = getDefaultMapper().writeValueAsString(new PushApiBatchRequestAdapterWrapper(batch));
        return execute(mockMvc, post("/push/v1/send-batch").content(content), PushApiResponseWrapper.class)
                .getResponse();
    }

    @Step("Разослать batch сообщения и ожидать ошибку {1}: {2}")
    public void batchWithMessage(MockMvc mockMvc,
                                 PushApiBatchRequestAdapter batch,
                                 ResultMatcher matcher,
                                 String message) throws Exception {
        String content = getDefaultMapper().writeValueAsString(new PushApiBatchRequestAdapterWrapper(batch));
        execute(mockMvc, post("/push/v1/send-batch").content(content), matcher, message);
    }

}
