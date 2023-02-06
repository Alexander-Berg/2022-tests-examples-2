package ru.yandex.autotests.morda.tests.web.utils;

import com.fasterxml.jackson.databind.ObjectMapper;
import org.junit.Assert;
import org.openqa.selenium.By;
import org.openqa.selenium.JavascriptExecutor;
import org.openqa.selenium.WebDriver;
import org.openqa.selenium.WebElement;
import ru.yandex.autotests.morda.pages.desktop.main.DesktopMainPage;
import ru.yandex.autotests.morda.tests.web.widgets.wpattern.Widget;
import ru.yandex.autotests.morda.tests.web.widgets.wpattern.WidgetPattern;
import ru.yandex.autotests.mordacommonsteps.steps.CommonMordaSteps;
import ru.yandex.autotests.utils.morda.matchers.LoginMatcher;
import ru.yandex.qatools.allure.annotations.Step;

import java.io.IOException;
import java.net.URI;
import java.util.List;

import static java.lang.Thread.sleep;
import static java.util.stream.Collectors.toList;
import static org.hamcrest.MatcherAssert.assertThat;
import static org.hamcrest.Matchers.equalTo;
import static org.hamcrest.Matchers.greaterThan;

/**
 * User: asamar
 * Date: 04.03.16
 */
public class PatternSteps {
    private WebDriver driver;
    private DesktopMainPage page;
    private CommonMordaSteps user;
    public static final ObjectMapper OBJECT_MAPPER = new ObjectMapper();

    public PatternSteps(WebDriver driver) {
        this.driver = driver;
        this.user = new CommonMordaSteps(driver);
        this.page = new DesktopMainPage(driver);

    }

    private String getPatternMeta(WebDriver driver){
        WebElement meta = driver.findElement(By.xpath("//meta[@name='yamm']"));
        return meta.getAttribute("content");
    }

    @Step
    public void shouldSeePlainPatternMeta(){
        try {
            sleep(1000);
        } catch (InterruptedException e) {
            throw new RuntimeException(e);
        }
        assertThat("Паттерн не плоский", getPatternMeta(driver), equalTo("p"));
    }

    @Step
    public void shouldSeeWidgetPatternMeta(){
        try {
            sleep(1000);
        } catch (InterruptedException e) {
            throw new RuntimeException(e);
        }
        assertThat("Паттерн не виджетный", getPatternMeta(driver), equalTo("w"));
    }

//    @Step("Reset all settings")
//    public void resetPattern() throws InterruptedException {
//        page.getEditModeControls().resetSettings();
//        user.acceptsAlert();
//        sleep(1000);
//        user.refreshPage();
//    }

    @Step("Get pattern")
    private WidgetPattern getPattern(WebDriver driver) {
        String pattern = (String) ((JavascriptExecutor) driver)
                .executeScript(" return $('.widgets').bem('widgets').collectData().save");
        WidgetPattern widgetPattern;
        try {
            widgetPattern = OBJECT_MAPPER.readValue(pattern, WidgetPattern.class);
        } catch (IOException ex) {
            throw new RuntimeException("Не удалось получить паттерн", ex);
        }
        return widgetPattern;
    }

    @Step("Should see plain pattern")
    public void shouldSeePlainPattern() {
        user.shouldSeeListWithSize(getPattern(driver).getWidgets(), equalTo(0));
//        shouldSeeElementMatchingTo(pattern.getWidgets(), hasSize(0));
    }

    @Step("Should see widget pattern")
    public void shouldSeeWidgetPattern() {
//        shouldSeeElementMatchingTo(getPattern(driver).getWidgets(), hasSize(not(0)));
        List<Widget> count = getPattern(driver).getWidgets().stream()
                .filter(e -> e.getUsrCh() > 0)
                .collect(toList());
//        user.shouldSeeListWithSize(count, greaterThan(0));
        assertThat("Паттерн плоский!", count.size(), greaterThan(0));
//        shouldSeeElementMatchingTo(count, hasSize(not(0)));
    }


    @Step("Set edit mode")
    public void setEditMode(URI editUrl) {
        driver.get(editUrl.toString());
    }

    @Step("Set plain mode logged")
    public void setPlainModeLogged(String url) throws InterruptedException {
        shouldLoggedIn();
        driver.get(url + "/autopattern?mode=drop");
        shouldSeePlainPatternMeta();
    }

    @Step("Set widget mode logged")
    public void setWidgetModeLogged(String url) throws InterruptedException {
        shouldLoggedIn();
        driver.get(url + "/autopattern?mode=drop");
        driver.get(url + "/autopattern?mode=create");
        shouldSeeWidgetPatternMeta();
    }

    @Step("Should be logged")
    public void shouldLoggedIn() {
        Assert.assertThat("Говняшка не залогинилась", driver, LoginMatcher.isLogged());
    }

}
