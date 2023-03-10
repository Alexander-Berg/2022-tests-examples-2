package ru.yandex.autotests.morda.exports.tests.checks;

import ru.yandex.autotests.morda.steps.UrlSteps;

import javax.ws.rs.core.Response;
import java.util.function.Function;
import java.util.function.Predicate;

import static java.lang.String.format;
import static org.hamcrest.Matchers.equalTo;


/**
 * User: asamar
 * Date: 14.08.2015.
 */
public class HttpResponseCheck<T> extends ExportCheck<T> {

    private HttpResponseCheck(String field,
                              Function<T, String> urlProvider,
                              Predicate<T> condition) {
        super(
                format("\"%s\" response code", field),
                e -> checkUrlResponse(urlProvider.apply(e)),
                condition
        );
    }

    public static <T> HttpResponseCheck<T> httpResponse(String field,
                                                        Function<T, String> urlProvider,
                                                        Predicate<T> condition) {
        return new HttpResponseCheck<>(field, urlProvider, condition);
    }

    public static <T> HttpResponseCheck<T> httpResponse(String field,
                                                        Function<T, String> urlProvider) {
        return httpResponse(field, urlProvider, e -> true);
    }

    private static void checkUrlResponse(String url) {
        if (url.startsWith("//")) {
            checkingUrlResponse("http:" + url);
            checkingUrlResponse("https:" + url);
        } else {
            checkingUrlResponse(url);
        }
    }

    private static void checkingUrlResponse(String url) {
//        Client client = ClientBuilder.newClient()
//                .property(ClientProperties.CONNECT_TIMEOUT, 15000)
//                .property(ClientProperties.READ_TIMEOUT, 15000);
//
//        Response response = client.target(url)
//                .request()
//                .buildGet()
//                .invoke();
//
//        Response.Status status = Response.Status.fromStatusCode(response.getStatus());
//        response.close();

        UrlSteps.checkResponseCodeSilently(url, equalTo(Response.Status.OK.getStatusCode()));

//        assertThat("???????????? ?????? ???????????? ???? \"" + url + "\"", status, equalTo(Response.Status.OK));
    }
}
