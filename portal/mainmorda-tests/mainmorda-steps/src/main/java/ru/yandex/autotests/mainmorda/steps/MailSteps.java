package ru.yandex.autotests.mainmorda.steps;

import org.openqa.selenium.WebDriver;
import ru.yandex.autotests.mainmorda.Properties;
import ru.yandex.autotests.mainmorda.data.MailData;
import ru.yandex.autotests.mordacommonsteps.steps.CommonMordaSteps;
import ru.yandex.qatools.allure.annotations.Step;

import static org.hamcrest.Matchers.equalTo;
import static ru.yandex.autotests.mainmorda.data.MailData.MAIL_AUTH_FAILED_PAGE_URL;
import static ru.yandex.autotests.mainmorda.data.MailData.MAIL_PAGE_SECURE_LOGGED_URL_MATCHER;

/**
 * User: alex89
 * Date: 06.10.12
 */

public class MailSteps {
    private static final Properties CONFIG = new Properties();

    private WebDriver driver;
    private CommonMordaSteps userSteps;

    public MailSteps(WebDriver driver) {
        this.driver = driver;
        this.userSteps = new CommonMordaSteps(driver);
    }

    @Step
    public void shouldSeeMailPage() {
        userSteps.shouldSeePage(equalTo(MailData.MAIL_PAGE_URL_HTTPS));
    }

    @Step
    public void shouldSeeMailAuthFailedPage() {
        userSteps.shouldSeePage(equalTo(MAIL_AUTH_FAILED_PAGE_URL));
    }

    @Step
    public void shouldSeeLoggedMailPageWithHttps() {
        userSteps.shouldSeePage(MAIL_PAGE_SECURE_LOGGED_URL_MATCHER);
    }
}
