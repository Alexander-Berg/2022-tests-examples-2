package ru.yandex.autotests.morda.tests.web.utils;

import org.hamcrest.MatcherAssert;
import org.hamcrest.Matchers;
import org.junit.Assert;
import org.openqa.selenium.NoAlertPresentException;
import org.openqa.selenium.WebDriver;
import ru.yandex.autotests.morda.pages.desktop.main.DesktopMainPage;
import ru.yandex.autotests.morda.tests.web.MordaWebTestsProperties;
import ru.yandex.autotests.mordacommonsteps.matchers.AlertAcceptedMatcher;
import ru.yandex.autotests.mordacommonsteps.matchers.ModeMatcher;
import ru.yandex.autotests.mordacommonsteps.matchers.UrlMatcher;
import ru.yandex.autotests.mordacommonsteps.matchers.WithWaitForMatcher;
import ru.yandex.autotests.mordacommonsteps.utils.Mode;
import ru.yandex.autotests.utils.morda.matchers.LoginMatcher;
import ru.yandex.qatools.allure.annotations.Step;
import ru.yandex.qatools.htmlelements.element.HtmlElement;
import ru.yandex.qatools.htmlelements.matchers.WrapsElementMatchers;

/**
 * User: asamar
 * Date: 10.12.2015.
 */
public class ModeSteps {
    private static final MordaWebTestsProperties CONFIG = new MordaWebTestsProperties();
    private WebDriver driver;
    private DesktopMainPage page;

    public ModeSteps(WebDriver driver) {
        this.driver = driver;
        this.page = new DesktopMainPage(driver);
    }

    @Step
    public void setModeLogged(Mode mode) {
        MatcherAssert.assertThat("Для установки режима надо залогиниться", this.driver, LoginMatcher.isLogged());
        if(mode.equals(Mode.WIDGET)) {
            this.setWidgetModeLogged();
            MatcherAssert.assertThat(this.driver, Matchers.is(ModeMatcher.inWidgetMode()));
        } else {
//            this.resetSettings();
            MatcherAssert.assertThat(this.driver, Matchers.is(ModeMatcher.inPlainMode()));
        }

    }

    @Step
    public void setWidgetModeLogged() {
        MatcherAssert.assertThat("Говняшка не залогинилась", this.driver, LoginMatcher.isLogged());
//        this.driver.get(CONFIG.getBaseURL() + "/autopattern?mode=drop");

        try {
            Thread.sleep(1000L);
        } catch (InterruptedException var2) {
            var2.printStackTrace();
        }

//        this.driver.get(CONFIG.getBaseURL() + "/autopattern?mode=create");
        MatcherAssert.assertThat(this.driver, Matchers.is(ModeMatcher.inWidgetMode()));
    }

    private void resetSettings(String url) {
        this.setEditModeMethod(url);

        for(int cnt = 0; cnt < 3; ++cnt) {
            this.tryClick(this.page.resetButton);
            if(this.resetSuccess()) {
                return;
            }
        }

    }

    private void tryClick(HtmlElement element) {
        if(WithWaitForMatcher.withWaitFor(WrapsElementMatchers.exists()).matches(element)) {
            element.click();
        }

    }

    private boolean resetSuccess() {
        return WithWaitForMatcher.withWaitFor(AlertAcceptedMatcher.isAlertAccepted()).matches(this.driver) && WithWaitForMatcher.withWaitFor(Matchers.is(ModeMatcher.inPlainMode())).matches(this.driver);
    }

    public void setEditModeMethod(String url) {
        for(int cnt = 0; cnt < 3; ++cnt) {
            this.driver.get(url + "/?edit=1");
            this.acceptsAlertIfNeeded();
            WithWaitForMatcher.withWaitFor(UrlMatcher.urlMatches(Matchers.startsWith(url + "/?edit=1"))).matches(this.driver);
            if(WithWaitForMatcher.withWaitFor(Matchers.is(ModeMatcher.inEditMode())).matches(this.driver)) {
                return;
            }
        }

        Assert.fail("Не удалось выставить режим редактирования!");
    }

    @Step
    public void acceptsAlertIfNeeded() {
        try {
            this.driver.switchTo().alert().accept();
        } catch (NoAlertPresentException var2) {

        }

    }
}
