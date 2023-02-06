package ru.yandex.autotests.morda.client.requests;

import com.fasterxml.jackson.databind.JsonNode;

import javax.ws.rs.client.Invocation;
import javax.ws.rs.core.GenericType;
import javax.ws.rs.core.Response;

/**
 * @author Ivan Nikolaev <ivannik@yandex-team.ru>
 */
public abstract class Request<T> {
    protected GenericType<T> responseGenericType;
    protected Invocation invocation;
    protected String toString;
    protected String description;

    protected Request(GenericType<T> responseGenericType, RequestBuilder requestBuilder) {
        this.responseGenericType = responseGenericType;
        this.invocation = requestBuilder.getInvocation();
        this.toString = requestBuilder.toString();
        this.description = requestBuilder.description();
    }

    public <E> E read(Class<E> clazz) {
        if (clazz == null) {
            throw new RuntimeException("clazz must be not null");
        }
        return invocation.invoke(clazz);
    }

    public <E> E read(GenericType<E> genericType) {
        if (genericType == null) {
            throw new RuntimeException("genericType must be not null");
        }

        return invocation.invoke(genericType);
    }

    public T read() {
        return read(responseGenericType);
    }

    public Response readAsResponse() {
        return invocation
                .invoke();
    }

    public JsonNode readAsJsonNode() {
        return read(JsonNode.class);
    }

    public String getDescription() {
        return description;
    }

    @Override
    public String toString() {
        return toString;
    }
}
