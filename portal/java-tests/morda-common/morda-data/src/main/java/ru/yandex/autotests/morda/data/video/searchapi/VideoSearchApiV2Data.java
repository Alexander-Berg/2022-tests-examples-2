package ru.yandex.autotests.morda.data.video.searchapi;

import ru.yandex.autotests.morda.api.search.SearchApiRequestData;
import ru.yandex.autotests.morda.beans.api.search.v2.SearchApiV2Response;
import ru.yandex.autotests.morda.beans.api.search.v2.video.VideoApiV2;
import ru.yandex.autotests.morda.beans.api.search.v2.video.VideoApiV2Data;
import ru.yandex.autotests.morda.data.TankerManager;
import ru.yandex.autotests.morda.steps.links.LinkUtils;
import ru.yandex.qatools.allure.annotations.Step;

import java.util.HashSet;
import java.util.Set;

import static ch.lambdaj.Lambda.on;
import static org.hamcrest.MatcherAssert.assertThat;
import static org.hamcrest.Matchers.equalTo;
import static org.hamcrest.Matchers.notNullValue;
import static ru.yandex.autotests.morda.matchers.NestedPropertyMatcher.hasPropertyWithValue;
import static ru.yandex.autotests.morda.steps.CheckSteps.checkBean;
import static ru.yandex.autotests.morda.tanker.home.ApiSearch.VIDEO_TITLE;

/**
 * User: eoff (eoff@yandex-team.ru)
 * Date: 17/10/16
 */
public class VideoSearchApiV2Data {
    private SearchApiRequestData requestData;

    public VideoSearchApiV2Data(SearchApiRequestData requestData) {
        this.requestData = requestData;
    }

    @Step("Check video")
    public void check(SearchApiV2Response response) {
        checkExists(response);

        checkBean(response.getVideo(), hasPropertyWithValue(
                on(VideoApiV2.class).getTitle(),
                equalTo(TankerManager.get(VIDEO_TITLE, requestData.getLanguage()))
        ));

        checkData(response.getVideo().getData());
    }

    @Step("Check video data")
    public void checkData(VideoApiV2Data videoData) {
        checkBean(videoData, hasPropertyWithValue(on(VideoApiV2Data.class).getColor(), equalTo("#152438")));
    }

    @Step("Check video exists")
    public void checkExists(SearchApiV2Response response) {
        assertThat("response is null", response, notNullValue());
        checkBean(response, hasPropertyWithValue(on(SearchApiV2Response.class).getVideo(), notNullValue()));
    }

    @Step("Ping static")
    public void pingStatic(SearchApiV2Response response) {
        checkExists(response);
        VideoApiV2Data video = response.getVideo().getData();

        Set<String> urls = new HashSet<>();

        video.getResources().forEach(resource -> {
            urls.add(resource.getUrl());
        });

        LinkUtils.ping(urls);
    }
}
