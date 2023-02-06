package ru.yandex.autotests.morda.restassured.requests;

import java.net.URI;
import java.util.function.Supplier;

/**
 * User: eoff (eoff@yandex-team.ru)
 * Date: 18/03/16
 */
public class RestAssuredPostRequest<E> extends RestAssuredRequest<RestAssuredPostRequest<E>>
        implements PostRequest<RestAssuredPostRequest<E>, E> {

    private Supplier<E> post;
    private E postData;

    public RestAssuredPostRequest(String host) {
        super(host);
    }

    public RestAssuredPostRequest(URI host) {
        super(host);
    }

    @Override
    public RestAssuredPostRequest<E> me() {
        return this;
    }

    @Override
    public E getPost() {
        if (postData == null) {
            postData = post.get();
        }
        return postData;
    }

    @Override
    public void setPost(Supplier<E> post) {
        this.post = post;
    }

    @Override
    public Supplier<E> getPostSupplier() {
        return post;
    }
}
