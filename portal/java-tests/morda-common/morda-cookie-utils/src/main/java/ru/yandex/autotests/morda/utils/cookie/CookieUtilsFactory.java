package ru.yandex.autotests.morda.utils.cookie;

import org.apache.http.client.HttpClient;
import org.openqa.selenium.WebDriver;

import javax.ws.rs.client.Client;

/**
 * User: eoff (eoff@yandex-team.ru)
 * Date: 08/04/15
 */
public class CookieUtilsFactory {

    public static ClientCookieUtils cookieUtils(Client client) {
        return new ClientCookieUtils(client);
    }

    public static HttpClientCookieUtils cookieUtils(HttpClient httpClient) {
        return new HttpClientCookieUtils(httpClient);
    }

    public static WebDriverCookieUtils cookieUtils(WebDriver driver) {
        return new WebDriverCookieUtils(driver);
    }
}
