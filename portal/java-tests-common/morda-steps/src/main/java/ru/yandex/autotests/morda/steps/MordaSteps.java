package ru.yandex.autotests.morda.steps;

import org.openqa.selenium.Cookie;
import org.openqa.selenium.WebDriver;
import ru.yandex.qatools.allure.annotations.Step;

import javax.ws.rs.core.UriBuilder;
import java.net.URI;

import static org.hamcrest.MatcherAssert.assertThat;
import static org.hamcrest.Matchers.allOf;
import static org.hamcrest.Matchers.containsString;
import static org.hamcrest.Matchers.notNullValue;
import static ru.yandex.autotests.morda.utils.cookie.CookieUtilsFactory.cookieUtils;
import static ru.yandex.autotests.morda.utils.cookie.MordaCookieUtils.YP;

/**
 * User: eoff (eoff@yandex-team.ru)
 * Date: 31/03/15
 */
public class MordaSteps {

    public static URI getMgpsaveUri(URI uri, String lat, String lon, String sk) {
        return UriBuilder.fromUri(uri)
                .path("mgpsave")
                .queryParam("lat", lat)
                .queryParam("lon", lon)
                .queryParam("precision", "30")
                .queryParam("sk", sk)
                .build();
    }

    @Step("Set coordinates {3} {4}")
    public static void setCoordinates(WebDriver driver, URI uri, String cookieDomain, String lat, String lon) {
        String u = getMgpsaveUri(uri, lat, lon, cookieUtils(driver).getSecretKey(cookieDomain)).toString();
        System.out.println(u);
        driver.get(u);
        driver.get(uri.toString());

        Cookie yp = cookieUtils(driver).getCookieNamed(YP, cookieDomain);

        assertThat("Cookie yp not found", yp, notNullValue());
        assertThat("Cookie yp", yp.getValue(), allOf(containsString(lat.replace('.', '_')), containsString(lon.replace('.', '_'))));
    }
}
