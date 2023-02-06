package ru.yandex.autotests.metrika.steps.management;

import ru.yandex.autotests.httpclient.lite.core.IFormParameters;
import ru.yandex.autotests.irt.testutils.allure.TestSteps;
import ru.yandex.autotests.metrika.beans.schemes.ManagementV1ClientsGETSchema;
import ru.yandex.autotests.metrika.steps.MetrikaBaseSteps;
import ru.yandex.metrika.api.management.client.external.Client;
import ru.yandex.qatools.allure.annotations.Step;

import java.util.List;
import java.util.stream.Collectors;

import static org.hamcrest.Matchers.empty;
import static org.hamcrest.Matchers.not;
import static ru.yandex.autotests.metrika.commons.response.ResponseMatchers.*;

/**
 * Created by konkov on 19.06.2015.
 */
public class ClientSteps extends MetrikaBaseSteps {

    @Step("Получить список клиентов Директа")
    private List<Client> getClients(IFormParameters... parameters) {
        ManagementV1ClientsGETSchema result = executeAsJson(
                getRequestBuilder("/management/v1/clients").get(parameters))
                .readResponse(ManagementV1ClientsGETSchema.class);

        TestSteps.assertThat(SUCCESS_MESSAGE, result, expectSuccess());

        return result.getClients();
    }

    @Step("Получить список идентификаторов клиентов Директа")
    public List<Long> getClientIds(IFormParameters... parameters) {

        List<Client> clients = getClients(parameters);

        TestSteps.assumeThat("для теста доступен список клиентов Директа", clients, not(empty()));

        return clients.stream().map(Client::getId).collect(Collectors.toList());
    }

    @Step("Получить список логинов клиентов Директа")
    public List<String> getClientLogins(IFormParameters... parameters) {
        List<Client> clients = getClients(parameters);

        TestSteps.assumeThat("для тестов доступен список клиентов Директа", clients, not(empty()));

        return clients.stream().map(Client::getChiefLogin).collect(Collectors.toList());
    }
}
