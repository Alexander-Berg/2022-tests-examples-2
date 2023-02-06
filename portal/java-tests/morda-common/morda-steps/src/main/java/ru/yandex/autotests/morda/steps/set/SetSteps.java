package ru.yandex.autotests.morda.steps.set;

import com.jayway.restassured.response.Cookie;
import com.jayway.restassured.response.Response;
import ru.yandex.autotests.morda.api.set.SetError;
import ru.yandex.autotests.morda.pages.MordaLanguage;
import ru.yandex.qatools.allure.annotations.Step;
import ru.yandex.qatools.cookies.my.CookieMy;

import static org.hamcrest.CoreMatchers.containsString;
import static org.hamcrest.CoreMatchers.endsWith;
import static org.hamcrest.CoreMatchers.equalTo;
import static org.hamcrest.MatcherAssert.assertThat;
import static ru.yandex.autotests.morda.utils.cookie.MordaCookieUtils.MY;
import static ru.yandex.autotests.morda.utils.cookie.MordaCookieUtils.YP;

/**
 * User: asamar
 * Date: 20.10.16
 */
public class SetSteps {

    @Step("Should see language {1}")
    public void shouldSeeLanguage(Response response, MordaLanguage lang) {
        CookieMy cookieMy = new CookieMy(response.getCookie(MY));
        Integer langNumber = cookieMy.getBlock(39).get(1);
        assertThat("В куке my неверный язык", langNumber, equalTo(lang.getIntl()));
    }

    @Step("Should see error: {1}")
    public void shouldSeeError(Response response, SetError error) {
        assertThat("Должна быть ошибка " + error,
                response.getHeader("Location"), endsWith(error.getValue()));
    }

    @Step("YP cookie should contains {0}.{1}")
    public void ypShouldContains(Response response, String paramName, String paramValue) {
        this.ypShouldContains(paramName + "." + paramValue, response);
    }

    @Step("YP cookie should contains {0}")
    public void ypShouldContains(String substring, Response response) {
        assertThat("YP должна содержать " + substring,
                response.getCookie(YP), containsString(substring));
    }

    @Step("MY should equal to {0}")
    public void shouldSeeMyCookie(String expectedMy, Response response) {
        assertThat("Кука MY плохая",
                expectedMy, equalTo(response.getCookie(MY)));
    }

    public void ypDetailedShouldContains(String paramName, String paramValue, Response response, String cookieDomain) {
        this.ypDetailedShouldContains(paramName + "." + paramValue, response, cookieDomain);
    }

    @Step("YP on {2} should contains {0}")
    public void ypDetailedShouldContains(String substring, Response response, String cookieDomain) {
        Cookie yp = response.getDetailedCookies().getList(YP).stream()
                .filter(e -> cookieDomain.equals(e.getDomain()))
                .findFirst()
                .orElseThrow(() -> new RuntimeException("There is no yp cookie on " + cookieDomain));

        assertThat("YP должна содержать " + substring,
                yp.getValue(), containsString(substring));
    }

}
