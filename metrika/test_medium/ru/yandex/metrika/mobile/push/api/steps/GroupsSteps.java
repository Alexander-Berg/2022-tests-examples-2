package ru.yandex.metrika.mobile.push.api.steps;

import java.util.List;
import java.util.Objects;

import org.springframework.stereotype.Component;
import org.springframework.test.web.servlet.MockMvc;

import ru.yandex.metrika.api.management.steps.MockMvcSteps;
import ru.yandex.metrika.mobmet.push.api.model.PushGroupAdapter;
import ru.yandex.metrika.mobmet.push.api.model.PushGroupAdapterWrapper;
import ru.yandex.metrika.mobmet.push.api.model.PushGroupsAdapter;
import ru.yandex.qatools.allure.annotations.Step;

import static java.lang.String.format;
import static org.springframework.test.web.servlet.request.MockMvcRequestBuilders.get;
import static org.springframework.test.web.servlet.request.MockMvcRequestBuilders.post;
import static org.springframework.test.web.servlet.request.MockMvcRequestBuilders.put;
import static ru.yandex.metrika.util.json.ObjectMappersFactory.getDefaultMapper;

@Component
public class GroupsSteps extends MockMvcSteps {

    @Step("Добавление группы")
    public PushGroupAdapter add(MockMvc mockMvc, PushGroupAdapter group) throws Exception {
        String content = getDefaultMapper().writeValueAsString(new PushGroupAdapterWrapper(group));
        return execute(mockMvc,
                post("/push/v1/management/groups").content(content),
                PushGroupAdapterWrapper.class)
                .getGroup();
    }

    @Step("Получение группы")
    public PushGroupAdapter recieve(MockMvc mockMvc, Long id) throws Exception {
        return execute(mockMvc, get(format("/push/v1/management/group/%s", id)), PushGroupAdapterWrapper.class)
                .getGroup();
    }

    @Step("Получение списка групп")
    public List<PushGroupAdapter> list(MockMvc mockMvc, int applicationId) throws Exception {
        return execute(mockMvc,
                get("/push/v1/management/groups").param("app_id", Objects.toString(applicationId)),
                PushGroupsAdapter.class)
                .getGroups();
    }

    @Step("Обновление группы")
    public PushGroupAdapter update(MockMvc mockMvc, PushGroupAdapter group) throws Exception {
        String content = getDefaultMapper().writeValueAsString(new PushGroupAdapterWrapper(group));
        return execute(mockMvc,
                put(format("/push/v1/management/group/%s", group.getId())).content(content),
                PushGroupAdapterWrapper.class)
                .getGroup();
    }

}
