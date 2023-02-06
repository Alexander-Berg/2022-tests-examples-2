package ru.yandex.autotests.morda.restassured.requests;

import java.net.URI;
import java.util.function.Supplier;

/**
 * User: eoff (eoff@yandex-team.ru)
 * Date: 18/03/16
 */
public class TypifiedRestAssuredPostRequest<T, E>
        extends TypifiedRestAssuredRequest<TypifiedRestAssuredPostRequest<T, E>, T>
        implements PostRequest<TypifiedRestAssuredPostRequest<T, E>, E> {

    private Supplier<E> post;
    private E postData;

    public TypifiedRestAssuredPostRequest(Class<T> responseClass, String host) {
        super(responseClass, host);
    }

    public TypifiedRestAssuredPostRequest(Class<T> responseClass, URI host) {
        super(responseClass, host);
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

    @Override
    public TypifiedRestAssuredPostRequest<T, E> me() {
        return this;
    }
}
