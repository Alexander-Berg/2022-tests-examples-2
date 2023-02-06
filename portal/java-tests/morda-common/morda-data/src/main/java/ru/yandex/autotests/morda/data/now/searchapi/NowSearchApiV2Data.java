package ru.yandex.autotests.morda.data.now.searchapi;

import ru.yandex.autotests.morda.api.search.SearchApiRequestData;
import ru.yandex.autotests.morda.beans.api.search.v2.SearchApiV2Response;
import ru.yandex.autotests.morda.beans.api.search.v2.now.NowApiV2Data;
import ru.yandex.qatools.allure.annotations.Step;

import static ch.lambdaj.Lambda.on;
import static org.hamcrest.MatcherAssert.assertThat;
import static org.hamcrest.Matchers.notNullValue;
import static ru.yandex.autotests.morda.matchers.NestedPropertyMatcher.hasPropertyWithValue;
import static ru.yandex.autotests.morda.steps.CheckSteps.checkBean;

/**
 * User: eoff (eoff@yandex-team.ru)
 * Date: 10/10/16
 */
public class NowSearchApiV2Data {

    private SearchApiRequestData requestData;

    public NowSearchApiV2Data(SearchApiRequestData requestData) {
        this.requestData = requestData;
    }

    @Step("Check now")
    public void check(SearchApiV2Response response) {
        checkExists(response);

        checkData(response.getNow().getData());
    }

    @Step("Check now exists")
    public void checkExists(SearchApiV2Response response) {
        assertThat("response is null", response, notNullValue());
        checkBean(response, hasPropertyWithValue(on(SearchApiV2Response.class).getNow(), notNullValue()));
    }

    @Step("Check data")
    public void checkData(NowApiV2Data data) {
//        checkGeo(data.getGeo());
//        checkTime(data.getTime());
    }

//    @Step("Check geo")
//    public void checkGeo(NowGeo geo) {
//        checkBean(geo, hasPropertyWithValue(on(NowGeo.class).getName(),
//                equalTo(requestData.getGeo().getTranslations(requestData.getLanguage().getValue()).getNominativeCase())));
//    }
//
//    @Step("Check time")
//    public void checkTime(NowTime time) {
//        String dayOfWeek = "" + (requestData.getGeo().getDateTime().getDayOfWeek().getValue() % 7);
//        String dayOfMonth = "" + requestData.getGeo().getDateTime().getDayOfMonth();
//        String monthKey = "" + requestData.getGeo().getDateTime().getMonthValue();
//        String wday = TankerManager.get("home", "wday", dayOfWeek, requestData.getLanguage());
//        String wdayShort = TankerManager.get("home", "wday_short", dayOfWeek, requestData.getLanguage());
//        String month = TankerManager.get("home", "spok_yes", "month_accus." + monthKey, requestData.getLanguage());
//        checkBean(time, allOfDetailed(
//                hasPropertyWithValue(on(NowTime.class).getDay(), equalTo(requestData.getGeo().getDate().getDayOfMonth())),
//                hasPropertyWithValue(on(NowTime.class).getWday(), equalTo(wday)),
//                hasPropertyWithValue(on(NowTime.class).getWdayShort(), equalTo(wdayShort)),
//                hasPropertyWithValue(on(NowTime.class).getWdayShortUc(), equalTo(wdayShort.toUpperCase())),
//                hasPropertyWithValue(on(NowTime.class).getMonth(), equalTo(month)),
//                hasPropertyWithValue(on(NowTime.class).getReady(), equalTo(String.format("%s %s, %s", dayOfMonth, month, wdayShort.toUpperCase())))
//        ));
//    }

}
