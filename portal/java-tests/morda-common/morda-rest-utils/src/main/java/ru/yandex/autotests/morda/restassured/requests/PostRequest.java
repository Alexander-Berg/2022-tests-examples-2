package ru.yandex.autotests.morda.restassured.requests;


import java.util.function.Supplier;

import com.jayway.restassured.response.Response;

import static ru.yandex.autotests.morda.restassured.requests.RequestHelpers.wrapStep;

/**
 * User: eoff (eoff@yandex-team.ru)
 * Date: 04/05/16
 */
public interface PostRequest<REQ extends PostRequest<REQ, IN>, IN> extends Request<REQ> {

    default REQ post(Supplier<IN> post) {
        setPost(post);
        return me();
    }

    default REQ post(IN post) {
        setPost(post);
        return me();
    }

    IN getPost();

    void setPost(Supplier<IN> post);

    void setPostData(IN postData);

    default void setPost(IN post) {
        setPost(() -> post);
    }

    Supplier<IN> getPostSupplier();

    default Response invoke() {
        Supplier<Response> request = () -> createRequestSpecification()
                .body(getPost())
                .post();

        Response response = isSilent() ? request.get() : wrapStep("POST " + getUri(), request);
        setPostData(null);
        return response;
    }
}
