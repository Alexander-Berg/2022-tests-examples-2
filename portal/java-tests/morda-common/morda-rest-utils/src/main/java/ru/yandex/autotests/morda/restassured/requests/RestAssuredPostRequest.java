package ru.yandex.autotests.morda.restassured.requests;

import java.net.URI;
import java.util.function.Supplier;

/**
 * User: eoff (eoff@yandex-team.ru)
 * Date: 18/03/16
 */
public class RestAssuredPostRequest<IN>
        extends RestAssuredRequest<RestAssuredPostRequest<IN>>
        implements PostRequest<RestAssuredPostRequest<IN>, IN> {

    private Supplier<IN> post;
    private IN postData;

    public RestAssuredPostRequest(String host) {
        super(host);
    }

    public RestAssuredPostRequest(URI host) {
        super(host);
    }

    @Override
    public RestAssuredPostRequest<IN> me() {
        return this;
    }

    @Override
    public IN getPost() {
        if (postData == null) {
            postData = post.get();
        }
        return postData;
    }

    @Override
    public void setPost(Supplier<IN> post) {
        this.post = post;
    }

    @Override
    public void setPostData(IN postData) {
        this.postData = postData;
    }

    @Override
    public Supplier<IN> getPostSupplier() {
        return post;
    }
}
