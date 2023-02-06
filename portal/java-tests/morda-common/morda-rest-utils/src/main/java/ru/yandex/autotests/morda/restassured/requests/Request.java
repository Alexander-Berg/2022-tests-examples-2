package ru.yandex.autotests.morda.restassured.requests;


import java.net.URI;
import java.util.List;
import java.util.function.Consumer;

import javax.ws.rs.core.UriBuilder;

import com.jayway.restassured.http.ContentType;
import com.jayway.restassured.response.Response;
import com.jayway.restassured.specification.RequestSpecification;

import ru.yandex.autotests.morda.restassured.filters.RestAssuredCookieStorageFilter;

import static java.util.Arrays.asList;
import static ru.yandex.autotests.morda.restassured.requests.RequestHelpers.wrapStep;

/**
 * User: eoff (eoff@yandex-team.ru)
 * Date: 04/05/16
 */
public interface Request<REQ extends Request<REQ>> {

    REQ me();

    URI getUri();

    Response invoke();

    RequestSpecification createRequestSpecification();

    REQ beforeRequest(List<RequestAction<REQ>> actions);

    REQ afterRequest(List<RequestAction<REQ>> actions);

    List<RequestAction> getBeforeRequestActions();

    List<RequestAction> getAfterRequestActions();

    REQ followRedirects(boolean follow);

    REQ path(String path);

    default REQ urlEncoding() {
        return urlEncoding(true);
    }

    REQ urlEncoding(boolean urlEncoding);

    REQ queryParam(String name, Object value);

    List<String> getQueryParam(String param);

    void removeQueryParam(String param);

    REQ cookie(String name, String value);

    REQ header(String name, String value);

    String getStepName();

    REQ silent();

    boolean isSilent();

    REQ step(String stepName);

    REQ accept(String contentType);

    default REQ accept(ContentType contentType) {
        return accept(contentType.toString());
    }

    REQ contentType(String contentType);

    default REQ contentType(ContentType contentType) {
        return contentType(contentType.toString());
    }

    RestAssuredCookieStorageFilter getCookieStorage();

    default URI getHost() {
        return UriBuilder.fromUri(getUri())
                .replacePath("")
                .replaceQuery("")
                .build();
    }

    default REQ beforeRequest(RequestAction<REQ> actions) {
        beforeRequest(asList(actions));
        return me();
    }

    default REQ afterRequest(RequestAction<REQ> actions) {
        afterRequest(asList(actions));
        return me();
    }

    default Response readAsResponse() {
        String stepName = getStepName();

        if (!isSilent() && stepName != null && !stepName.isEmpty()) {
            return wrapStep(stepName, () -> {
                getBeforeRequestActions().forEach(RequestAction::perform);
                Response response = invoke();
                getAfterRequestActions().forEach(RequestAction::perform);
                return response;
            });
        }

        getBeforeRequestActions().forEach(RequestAction::perform);
        Response response = invoke();
        getAfterRequestActions().forEach(RequestAction::perform);

        return response;
    }

    default <M> M read(Class<M> clazz) {
        Response response = readAsResponse();
        if (response.getBody().asString().isEmpty()) {
            return null;
        }
        return response.as(clazz);
    }

    class RequestAction<T extends Request<T>> {
        private T request;
        private String stepName;
        private Consumer<T> action;

        public RequestAction(Consumer<T> action) {
            this(null, action);
        }

        public RequestAction(String stepName, Consumer<T> action) {
            this.action = action;
            this.stepName = stepName;
        }

        public static <T extends Request<T>> RequestAction<T> requestAction(Consumer<T> action) {
            return new RequestAction<>(action);
        }

        public static <T extends Request<T>> RequestAction<T> empty() {
            return requestAction((e) -> {});
        }

        public static <T extends Request<T>> RequestAction<T> requestAction(String stepName, Consumer<T> action) {
            return new RequestAction<>(stepName, action);
        }

        public void setRequest(T request) {
            this.request = request;
        }

        void perform() {
            if (stepName != null && !stepName.isEmpty()) {
                wrapStep(stepName, () -> {
                    action.accept(request);
                    return null;
                });
            } else {
                action.accept(request);
            }
        }
    }
}
