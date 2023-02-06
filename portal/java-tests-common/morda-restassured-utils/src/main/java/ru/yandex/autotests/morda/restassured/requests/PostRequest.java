package ru.yandex.autotests.morda.restassured.requests;


import com.jayway.restassured.response.Response;

import java.util.function.Supplier;

import static ru.yandex.autotests.morda.restassured.requests.RequestHelpers.wrapStep;

/**
 * User: eoff (eoff@yandex-team.ru)
 * Date: 04/05/16
 */
public interface PostRequest<T extends PostRequest<T, E>, E> extends Request<T> {

    default T post(Supplier<E> post) {
        setPost(post);
        return me();
    }

    default T post(E post) {
        setPost(post);
        return me();
    }

    E getPost();

    void setPost(Supplier<E> post);

    default void setPost(E post) {
        setPost(() -> post);
    }

    Supplier<E> getPostSupplier();

    default Response invoke() {
        setPost(getPostSupplier().get());
        return wrapStep("POST " + getUri().getPath(), () -> createRequestSpecification()
                .body(getPost())
                .post()
        );
    }
}
