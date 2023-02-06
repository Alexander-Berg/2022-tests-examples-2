package ru.yandex.autotests.morda.utils.client.requests;

import java.net.URI;

/**
 * @author Ivan Nikolaev <ivannik@yandex-team.ru>
 */
public abstract class GetRequestBuilder<C extends GetRequestBuilder<C>> extends RequestBuilder<C> {

    public GetRequestBuilder(URI host) {
        super(host);
    }

    @Override
    public String description() {
        return toString() + "\n" + super.description() + "\n";
    }

    @Override
    public String toString() {
        return "GET " + getURI().toString();
    }
}
