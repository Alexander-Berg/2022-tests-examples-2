package ru.yandex.autotests.morda.restassured.requests;


import com.jayway.restassured.response.Response;
import com.jayway.restassured.specification.RequestSpecification;

import javax.ws.rs.core.UriBuilder;
import java.net.URI;
import java.util.List;
import java.util.function.Consumer;

import static java.util.Arrays.asList;
import static ru.yandex.autotests.morda.restassured.requests.RequestHelpers.wrapStep;

/**
 * User: eoff (eoff@yandex-team.ru)
 * Date: 04/05/16
 */
public interface Request<T extends Request<T>> {

    T me();

    URI getUri();

    Response invoke();

    RequestSpecification createRequestSpecification();

    T beforeRequest(List<RequestAction<T>> actions);

    T afterRequest(List<RequestAction<T>> actions);

    List<RequestAction> getBeforeRequestActions();

    List<RequestAction> getAfterRequestActions();

    T path(String path);

    T queryParam(String name, Object value);

    String getStepName();

    T step(String stepName);

    String getQueryParam(String param);

    default URI getHost() {
        return UriBuilder.fromUri(getUri())
                .replacePath("")
                .replaceQuery("")
                .build();
    }

    default T beforeRequest(RequestAction<T>... actions) {
        beforeRequest(asList(actions));
        return me();
    }

    default T afterRequest(RequestAction<T>... actions) {
        afterRequest(asList(actions));
        return me();
    }

    default Response readAsResponse() {
        String stepName = getStepName();

        if (stepName != null && !stepName.isEmpty()) {
            return wrapStep(stepName, () -> {
                getBeforeRequestActions().forEach(RequestAction::perform);
                Response response = invoke();
                getAfterRequestActions().forEach(RequestAction::perform);
                return response;
            });
        }

        getBeforeRequestActions().forEach(RequestAction::perform);
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
