package ru.yandex.autotests.mainmorda.steps;

import org.openqa.selenium.NoAlertPresentException;
import org.openqa.selenium.WebDriver;
import org.openqa.selenium.internal.WrapsElement;
import ru.yandex.autotests.mainmorda.Properties;
import ru.yandex.autotests.mainmorda.pages.MainPage;
import ru.yandex.autotests.mordacommonsteps.rules.MordaAllureBaseRule;
import ru.yandex.autotests.mordacommonsteps.steps.CommonMordaSteps;
import ru.yandex.autotests.mordacommonsteps.utils.Mode;
import ru.yandex.qatools.allure.annotations.Step;
import ru.yandex.qatools.htmlelements.element.HtmlElement;

import static org.hamcrest.MatcherAssert.assertThat;
import static org.hamcrest.Matchers.is;
import static org.hamcrest.Matchers.not;
import static org.hamcrest.Matchers.startsWith;
import static org.junit.Assert.fail;
import static ru.yandex.autotests.mordacommonsteps.matchers.AlertAcceptedMatcher.isAlertAccepted;
import static ru.yandex.autotests.mordacommonsteps.matchers.ModeMatcher.inEditMode;
import static ru.yandex.autotests.mordacommonsteps.matchers.ModeMatcher.inFakeMode;
import static ru.yandex.autotests.mordacommonsteps.matchers.ModeMatcher.inPlainMode;
import static ru.yandex.autotests.mordacommonsteps.matchers.ModeMatcher.inWidgetMode;
import static ru.yandex.autotests.mordacommonsteps.matchers.UrlMatcher.urlMatches;
import static ru.yandex.autotests.mordacommonsteps.matchers.WithWaitForMatcher.withWaitFor;
import static ru.yandex.autotests.mordacommonsteps.utils.Mode.WIDGET;
import static ru.yandex.autotests.utils.morda.matchers.LoginMatcher.isLogged;
import static ru.yandex.autotests.utils.morda.users.UserType.DEFAULT;
import static ru.yandex.qatools.htmlelements.matchers.WrapsElementMatchers.exists;
import static ru.yandex.qatools.htmlelements.matchers.WrapsElementMatchers.isDisplayed;

/**
 * User: eoff (eoff@yandex-team.ru)
 * Date: 14.04.13
 */
public class ModeSteps {
    private static final Properties CONFIG = new Properties();

    private static final String EDIT_URL_PART = "/?edit=1";
    public static final int NUMBER_OF_ATTEMPTS = 3;

    private WebDriver driver;
    private MainPage mainPage;
    private CommonMordaSteps userSteps;

    public ModeSteps(WebDriver driver) {
        this.driver = driver;
        this.mainPage = new MainPage(driver);
        this.userSteps = new CommonMordaSteps(driver);
    }

    public void shouldSeeElement(WrapsElement element) {
        assertThat(element + " отсутствует в верстке страницы!", element,
                withWaitFor(exists())
        );
        assertThat(element + " не отображается на странице!", element,
                withWaitFor(isDisplayed())
        );
    }

    @Step
    public void setEditMode(String url) {
        setEditModeMethod(url);
    }

    @Step
    public void setEditMode() {
        setEditModeMethod(CONFIG.getBaseURL());
    }

    public void setEditModeMethod(String url) {
        for (int cnt = 0; cnt < NUMBER_OF_ATTEMPTS; cnt++) {
            driver.get(url + EDIT_URL_PART);
            acceptsAlertIfNeeded();
            withWaitFor(urlMatches(startsWith(url + EDIT_URL_PART))).matches(driver);
            if (withWaitFor(is(inEditMode())).matches(driver)) {
                return;
            }
        }
        fail("Не удалось выставить режим редактирования!");
    }

    @Step
    public void setWidgetMode() {
        resetSettings(CONFIG.getBaseURL());
        setWidgetModeMethod(CONFIG.getBaseURL());
    }

    @Step
    public void setWidgetMode(String url) {
        resetSettings(url);
        setWidgetModeMethod(url);
    }

    private void setWidgetModeMethod(String url) {
        if (is(inWidgetMode()).matches(driver)) {
            return;
        }
        setEditModeMethod(url);

        shouldSeeElement(mainPage.geoBlock);
        shouldSeeElement(mainPage.geoBlock.closeCross);
        mainPage.geoBlock.closeCross.click();
        shouldSeeElement(mainPage.widgetSettingsHeader.undoButton);
        mainPage.widgetSettingsHeader.undoButton.click();
        saveSettingsMethod();
        assertThat("Не удалось настроить виджетный режим!", driver,
                withWaitFor(is(inWidgetMode())));
        acceptsAlertIfNeeded();
    }

    @Step
    public void acceptsAlertIfNeeded() {
        try {
            driver.switchTo().alert().accept();
        } catch (NoAlertPresentException e) {
            // doesn't matter
        }
    }

    /**
     * Сбрасывает настройки морды.
     *
     * @param url -- морда, на которой нужно сбросить настройки
     */
    @Step
    public void resetSettings(String url) {
        resetSettingsMethod(url);
    }

    @Step
    public void resetSettings() {
        resetSettingsMethod(CONFIG.getBaseURL());
    }

    private void tryClick(HtmlElement element) {
        if (withWaitFor(exists()).matches(element)) {
            element.click();
        }
    }

    private boolean resetSuccess() {
        if (withWaitFor(isAlertAccepted()).matches(driver)) {
            if (withWaitFor(is(inPlainMode())).matches(driver)) {
                return true;
            }
        }
        return false;
    }

    private void resetSettingsMethod(String url) {
        setEditModeMethod(url);
        for (int cnt = 0; cnt < NUMBER_OF_ATTEMPTS; cnt++) {
            tryClick(mainPage.widgetSettingsHeader.resetButton);
            if (resetSuccess()) {
                return;
            }
        }
    }


    /**
     * Сохраняет настройки, произведенные в режиме редактирования
     */
    @Step
    public void saveSettings() {
        saveSettingsMethod();
        try {
            Thread.sleep(1000);
        } catch (InterruptedException e) {
            e.printStackTrace();
        }
    }

    private void saveSettingsMethod() {
        for (int cnt = 0; cnt < NUMBER_OF_ATTEMPTS; cnt++) {
            tryClick(mainPage.widgetSettingsHeader.saveButton);
            if (withWaitFor(is(inWidgetMode())).matches(driver)) {
                return;
            }
        }
        fail("Не удалось сохранить настройки, выставленные в режиме редактирования!");
    }

    @Step
    public void setMode(Mode mode) {
        assertThat("Для установки режима надо разлогиниться", driver, not(isLogged()));
        if (mode.equals(WIDGET)) {
            setWidgetMode();
            assertThat(driver, is(inWidgetMode()));
        } else {
            resetSettings();
            assertThat(driver, is(inPlainMode()));
        }
    }

    @Step
    public void setModeLogged(Mode mode) {
        assertThat("Для установки режима надо залогиниться", driver, isLogged());
        if (mode.equals(WIDGET)) {
            setWidgetModeLogged();
            assertThat(driver, is(inWidgetMode()));
        } else {
            resetSettings();
            assertThat(driver, is(inPlainMode()));
        }
    }

    @Step
    public void setMode(Mode mode, MordaAllureBaseRule rule) {
        if (mode.equals(WIDGET)) {
            if (!isLogged().matches(driver)) {
                userSteps.logsInAs(rule.getUser(DEFAULT, WIDGET), CONFIG.getBaseURL());
            }
            setWidgetModeLogged();
            assertThat(driver, is(inWidgetMode()));
        } else {
            if (!is(inPlainMode()).matches(driver)) {
                resetSettings();
            }
            assertThat(driver, is(inPlainMode()));
        }
    }

    @Step
    public void setMode(Mode mode, String url, MordaAllureBaseRule rule) {
        if (mode.equals(WIDGET)) {
            if (!isLogged().matches(driver)) {
                userSteps.logsInAs(rule.getUser(DEFAULT, WIDGET), url);
            }
            setWidgetModeLogged(url);
            assertThat(driver, is(inWidgetMode()));
        } else {
            if (!is(inPlainMode()).matches(driver)) {
                resetSettings();
            }
            assertThat(driver, is(inPlainMode()));
        }
    }

    @Step
    public void setWidgetModeLogged() {
        assertThat("Говняшка не залогинилась", driver, isLogged());
        driver.get(CONFIG.getBaseURL() + "/autopattern?mode=drop");
        try {
            Thread.sleep(1000);
        } catch (InterruptedException e) {
            e.printStackTrace();
        }
        driver.get(CONFIG.getBaseURL() + "/autopattern?mode=create");
        assertThat(driver, is(inWidgetMode()));
    }

    @Step
    public void setWidgetModeLogged(String url) {
        assertThat("Говняшка не залогинилась", driver, isLogged());
        driver.get(url + "/autopattern?mode=drop");
        try {
            Thread.sleep(1000);
        } catch (InterruptedException e) {
            e.printStackTrace();
        }
        driver.get(url + "/autopattern?mode=create");
        assertThat(driver, is(inWidgetMode()));
    }

    @Step
    public void resetSettingsLogged() {
        assertThat("Говняшка не залогинилась", driver, isLogged());
        driver.get(CONFIG.getBaseURL() + "/autopattern?mode=drop");
    }

    @Step
    public void resetSettingsLogged(String url) {
        assertThat("Говняшка не залогинилась", driver, isLogged());
        driver.get(url + "/autopattern?mode=drop");
    }

    @Step
    public void shouldSeeWidgetMode() {
        assertThat(driver, withWaitFor(is(inWidgetMode())));
    }

    @Step
    public void shouldSeePlainMode() {
        assertThat(driver, withWaitFor(is(inPlainMode())));
    }

    @Step
    public void shouldSeeEditMode() {
        assertThat(driver, withWaitFor(is(inEditMode())));
    }

    @Step
    public void shouldSeeFakeMode() {
        assertThat(driver, withWaitFor(is(inFakeMode())));
    }

    @Step("{0}")
    public void shouldSeeMode(Mode mode) {
        if (mode.equals(WIDGET)) {
            shouldSeeWidgetMode();
        } else if (mode.equals(Mode.PLAIN)) {
            shouldSeePlainMode();
        } else if (mode.equals(Mode.FAKE)) {
            shouldSeeFakeMode();
        } else {
            shouldSeeEditMode();
        }
    }
}
