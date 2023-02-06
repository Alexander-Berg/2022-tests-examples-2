package ru.yandex.autotests.tuneapitests.steps;

import org.glassfish.jersey.apache.connector.ApacheConnectorProvider;
import org.glassfish.jersey.client.ClientResponse;
import ru.yandex.autotests.tuneapitests.utils.Authorized;
import ru.yandex.autotests.tuneapitests.utils.Domain;
import ru.yandex.autotests.tuneclient.TuneResponse;
import ru.yandex.junitextensions.rules.passportrule.PassportRule;
import ru.yandex.qatools.allure.annotations.Step;

import javax.ws.rs.client.Client;
import javax.ws.rs.core.Response;
import java.lang.reflect.Field;
import java.net.URI;
import java.util.EnumSet;

import static org.hamcrest.MatcherAssert.assertThat;
import static org.hamcrest.Matchers.*;

/**
 * User: eoff (eoff@yandex-team.ru)
 * Date: 21/01/15
 */
public class ClientSteps {
    private Client client;

    public ClientSteps(Client client) {
        this.client = client;
    }

    @Step("Open {0}")
    public void get(String url) {
        client.target(URI.create(url)).request().buildGet().invoke().close();
    }

    @Step("Logs in as {1}:{2}")
    public void logIn(Domain domain, String login, String password) {
        new PassportRule(ApacheConnectorProvider.getHttpClient(client))
                .onHost(domain.getPassportUrl())
                .withLoginPassword(login, password)
                .withRetpath(domain.getYandexUrl())
                .login();
    }

    @Step("Should see page \"{0}\"")
    public void shouldSeePage(Response response, String url) throws Exception {
        assertThat(getResponseUrl(response), startsWith(url));
    }

    @Step("Should see ok tune response")
    public void shouldSeeOkTuneResponse(TuneResponse response) {
        assertThat("Tune response not ok: " + response, response.getStatus(), equalTo("ok"));
        assertThat("Tune response not ok: " + response, response.getMsg(), isEmptyOrNullString());
    }

    @Step("Should see error tune response")
    public void shouldSeeErrorTuneResponse(TuneResponse response) {
        assertThat("Tune response not error: " + response, response.getStatus(), equalTo("error"));
        assertThat("Tune response not error: " + response, response.getMsg(), not(isEmptyOrNullString()));
    }

    public static String getResponseUrl(Response response) throws Exception {
        Field context = response.getClass().getDeclaredField("context");
        context.setAccessible(true);
        Object c = context.get(response);

        if (c instanceof ClientResponse) {
            ClientResponse r = (ClientResponse) context.get(response);
            Field resolvedUri = r.getClass().getDeclaredField("resolvedUri");
            resolvedUri.setAccessible(true);
            System.out.println(resolvedUri.get(r));
            return ((URI) resolvedUri.get(r)).toString();
        } else {
            throw new RuntimeException("Wrong type of c");
        }
    }

    public void authIfNeeded(Authorized authorized, Domain domain) {
        if (authorized.equals(Authorized.AUTH)) {
            logIn(domain, "widgetnew-test", "widget");
            if (EnumSet.of(Domain.BY, Domain.UA, Domain.KZ).contains(domain)) {
                logIn(Domain.RU, "widgetnew-test", "widget");
            }
        }
    }
}
