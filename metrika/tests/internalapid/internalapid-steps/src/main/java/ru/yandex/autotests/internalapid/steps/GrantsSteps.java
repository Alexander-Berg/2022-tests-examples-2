package ru.yandex.autotests.internalapid.steps;

import java.net.URL;
import java.util.ArrayList;
import java.util.List;

import com.fasterxml.jackson.annotation.JsonProperty;

import ru.yandex.autotests.httpclientlite.HttpClientLite;
import ru.yandex.autotests.internalapid.beans.schemes.GrantsV1UserUidGrantAccessRequestsStatusPOSTSchema;
import ru.yandex.autotests.metrika.commons.clients.http.HttpClientLiteFacade;
import ru.yandex.qatools.allure.annotations.Step;

public class GrantsSteps extends HttpClientLiteFacade {

    protected GrantsSteps(URL baseUrl, HttpClientLite client) {
        super(baseUrl, client);
    }

    @Step("Запросить с неверными полями в JSON'е статусы по запросам на доступы ")
    public GrantsV1UserUidGrantAccessRequestsStatusPOSTSchema tryGetGrantAccessRequestStatusWithoutCountersList(Long uid) {
        return post(GrantsV1UserUidGrantAccessRequestsStatusPOSTSchema.class,
                "/grants/v1/user/" + uid + "/grant_access_requests_status",
                new HelperForIncorrectJsonRequestWithFakedList().setCounterIdList(123L)
        );
    }


    public static class HelperForIncorrectJsonRequestWithFakedList {
        @JsonProperty("wrongNamedCounterList")
        private List<Long> someList = new ArrayList<>();

        public List<Long> getSomeList() {
            return someList;
        }

        public HelperForIncorrectJsonRequestWithFakedList setCounterIdList(Long id) {
            List<Long> some = new ArrayList<>();
            some.add(id);
            this.someList = some;
            return this;
        }
    }
}
