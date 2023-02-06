package ru.yandex.autotests.morda.restassured.requests;

import java.net.URI;
import java.util.function.Supplier;

/**
 * User: eoff (eoff@yandex-team.ru)
 * Date: 18/03/16
 */
public class TypifiedRestAssuredPostRequest<RES, IN>
        extends TypifiedRestAssuredRequest<TypifiedRestAssuredPostRequest<RES, IN>, RES>
        implements PostRequest<TypifiedRestAssuredPostRequest<RES, IN>, IN> {

    private Supplier<IN> post;
    private IN postData;

    public TypifiedRestAssuredPostRequest(Class<RES> responseClass, String host) {
        super(responseClass, host);
    }

    public TypifiedRestAssuredPostRequest(Class<RES> responseClass, URI host) {
        super(responseClass, host);
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

    @Override
    public TypifiedRestAssuredPostRequest<RES, IN> me() {
        return this;
    }
}
