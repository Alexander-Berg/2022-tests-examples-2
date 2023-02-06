package ru.yandex.autotests.morda.tests.web.utils;

import org.openqa.selenium.WebDriver;
import ru.yandex.autotests.morda.pages.desktop.main.DesktopMainPage;
import ru.yandex.autotests.morda.pages.desktop.main.blocks.TopnewsSettingsBlock;
import ru.yandex.autotests.morda.pages.desktop.main.htmlelements.Widget;
import ru.yandex.autotests.mordacommonsteps.steps.CommonMordaSteps;
import ru.yandex.autotests.utils.morda.language.Language;
import ru.yandex.autotests.utils.morda.region.Region;
import ru.yandex.qatools.allure.annotations.Step;

import java.net.URI;

import static ch.lambdaj.Lambda.on;
import static java.lang.Thread.sleep;
import static javax.ws.rs.core.UriBuilder.fromUri;
import static org.hamcrest.Matchers.containsString;
import static org.hamcrest.Matchers.equalTo;
import static org.hamcrest.Matchers.not;
import static ru.yandex.autotests.morda.steps.WebElementSteps.withWait;
import static ru.yandex.autotests.utils.morda.language.LanguageManager.getTranslation;
import static ru.yandex.qatools.htmlelements.matchers.WrapsElementMatchers.hasClass;
import static ru.yandex.qatools.htmlelements.matchers.WrapsElementMatchers.hasText;

/**
 * User: asamar
 * Date: 20.04.16
 */
public class WidgetSteps {

    private WebDriver driver;
    private CommonMordaSteps user;
    private DesktopMainPage page;

    public WidgetSteps(WebDriver driver) {
        this.driver = driver;
        this.page = new DesktopMainPage(driver);
        this.user = new CommonMordaSteps(driver);
    }

    public static URI rssBlockUrl(URI mordaUrl){
        return addWidgetUri(mordaUrl, 28);
    }

    public static URI militaryReviewUrl(URI mordaUrl){
        return addWidgetUri(mordaUrl, 60766);
    }

    private static URI addWidgetUri(URI mordaUrl, int widgetId){
        return fromUri(mordaUrl)
                .queryParam("add", widgetId)
                .build();
    }

    @Step
    public void acceptAddition(Widget widget){
        String addedWidgetId = widget.getId();
        widget.widgetAddControls.acceptAddition();
        shouldSee(addedWidgetId);
    }

    @Step
    public void cancelAddition(Widget widget){
        String addedWidgetId = widget.getId();
        widget.widgetAddControls.cancelAddition();
        shouldNotSee(addedWidgetId);
    }

    @Step
    public void shouldSee(String widgetId){
        user.shouldSeeElementInList(page.getWidgets(), on(Widget.class).getId(), equalTo(widgetId));
    }

    @Step
    public void shouldNotSee(String widgetId){
        user.shouldNotSeeElementInList(page.getWidgets(), on(Widget.class).getId(), equalTo(widgetId));
    }

    @Step
    public Widget getRandomWidget(){
        return user.getRandomItem(page.getWidgets());
    }

    @Step("Reset settings")
    public void resetSettings() {
        page.getEditModeControls().resetSettings();
        user.acceptsAlert();
        try {
            sleep(3000);
        } catch (InterruptedException e) {
            e.printStackTrace();
        }
    }

    @Step("Should see news numbers")
    public void shouldSeeNumbers() {
        user.shouldSeeElementMatchingTo(page.getNewsBlock().numbersHiddenFlag,
                withWait(hasClass(not(containsString("news_numbers_hide")))));
    }

    @Step("Should not see news numbers")
    public void shouldNotSeeNumbers() {
        user.shouldSeeElementMatchingTo(page.getNewsBlock().numbersHiddenFlag,
                withWait(hasClass(containsString("news_numbers_hide"))));
    }

    @Step("Should see news rubric: {0}")
    public void shouldSeeCustomRubric(TopnewsSettingsBlock.TopnewsRubricsType rubricsType, Language lang) {
        user.shouldSeeElementMatchingTo(
                page.getNewsBlock().newsBlockHeader.newsTabs.stream()
                        .reduce((a, b) -> b).orElse(null),
                withWait(hasText(
                        getTranslation("home", "news", "switch." + rubricsType.getValue(), lang))));
    }

    @Step("Should not see news rubric: {0}")
    public void shouldNotSeeCustomRubric() {
        page.getNewsBlock().newsBlockHeader.newsTabs
                .forEach(e ->
                        user.shouldSeeElementMatchingTo(e, hasClass(not(containsString("tab_topnews - 1_custom")))));
    }

    @Step
    public void shouldSeeWeatherRegion(Region region){
        user.shouldSeeElementMatchingTo(
                page.getWeatherBlock().city,
                hasText("(" + region.getName() + ")"));
    }
}
