package ru.yandex.autotests.morda.client.requests;

import com.fasterxml.jackson.core.JsonProcessingException;
import com.fasterxml.jackson.databind.ObjectMapper;

import java.net.URI;

/**
 * @author Ivan Nikolaev <ivannik@yandex-team.ru>
 */
public abstract class PostRequestBuilder<T, C extends PostRequestBuilder<T, C>> extends RequestBuilder<C> {

    protected T postData;

    public PostRequestBuilder(URI host) {
        super(host);
    }

    public C post(T postData) {
        this.postData = postData;
        return me();
    }

    @Override
    public String description() {
        try {
            return toString() + "\n" +
                    super.description() + "\n" +
                    new ObjectMapper().writerWithDefaultPrettyPrinter().writeValueAsString(postData);
        } catch (JsonProcessingException e) {
            throw new RuntimeException("Failed to generate toString for request", e);
        }
    }

    @Override
    public String toString() {
        return "POST " + getURI().toString();
    }
}
