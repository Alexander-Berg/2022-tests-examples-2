package ru.yandex.autotests.morda.steps;

import org.hamcrest.Matcher;
import org.openqa.selenium.WebDriver;
import ru.yandex.qatools.allure.annotations.Step;

import javax.ws.rs.client.Client;
import java.net.URI;
import java.net.URL;

import static org.hamcrest.core.StringStartsWith.startsWith;

/**
 * User: eoff (eoff@yandex-team.ru)
 * Date: 08/04/15
 */
public class NavigationSteps {

    @Step("Open \"{1}\"")
    public static void open(WebDriver driver, String url) {
        driver.navigate().to(url);
    }

    @Step("Get \"{1}\"")
    public static void get(Client client, String url) {
        client.target(url)
                .request()
                .buildGet()
                .invoke()
                .close();
    }


    @Step("Open \"{1}\", check url \"{2}\"")
    public static void openAndCheck(WebDriver driver, String url, Matcher<String> urlMatcher) {
        driver.navigate().to(url);
    }

    @Step("Return back")
    public static void returnBack(WebDriver driver) {
        driver.navigate().back();
    }

    @Step("Refresh page")
    public static void refresh(WebDriver driver) {
        driver.navigate().refresh();
    }

    public static void open(WebDriver driver, URI url) {
        open(driver, url.toString());
    }

    public static void open(WebDriver driver, URL url) {
        open(driver, url.toString());
    }

    public static void openAndCheck(WebDriver driver, String url) {
        openAndCheck(driver, url, startsWith(url));
    }

    public static void openAndCheck(WebDriver driver, URI url) {
        openAndCheck(driver, url.toString());
    }

    public static void openAndCheck(WebDriver driver, URL url) {
        openAndCheck(driver, url.toString());
    }

    public static void openAndCheck(WebDriver driver, URI url, Matcher<String> urlMatcher) {
        openAndCheck(driver, url.toString(), urlMatcher);
    }

    public static void openAndCheck(WebDriver driver, URL url, Matcher<String> urlMatcher) {
        openAndCheck(driver, url.toString(), urlMatcher);
    }

    public static void get(Client client, URI url) {
        get(client, url.toString());
    }

    public static void get(Client client, URL url) {
        get(client, url.toString());
    }

}
