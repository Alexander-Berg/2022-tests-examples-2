package ru.yandex.autotests.mainmorda.steps;

import org.openqa.selenium.WebDriver;
import ru.yandex.autotests.mainmorda.Properties;
import ru.yandex.autotests.mainmorda.blocks.NewsBlock;
import ru.yandex.autotests.mainmorda.blocks.TvAfishaNewsTab;
import ru.yandex.autotests.mainmorda.data.NewsBlockData;
import ru.yandex.autotests.mainmorda.data.NewsSettingsData;
import ru.yandex.autotests.mainmorda.pages.BasePage;
import ru.yandex.autotests.mainmorda.pages.MainPage;
import ru.yandex.autotests.mordacommonsteps.steps.CommonMordaSteps;
import ru.yandex.autotests.mordacommonsteps.utils.HtmlAttribute;
import ru.yandex.autotests.mordacommonsteps.utils.LinkInfo;
import ru.yandex.autotests.mordacommonsteps.utils.TestFailedFlag;
import ru.yandex.autotests.utils.morda.language.Language;
import ru.yandex.autotests.utils.morda.region.RegionManager;
import ru.yandex.qatools.allure.annotations.Step;
import ru.yandex.qatools.htmlelements.element.HtmlElement;

import java.sql.Time;
import java.util.ArrayList;
import java.util.HashSet;
import java.util.List;
import java.util.Set;

import static org.hamcrest.MatcherAssert.assertThat;
import static org.hamcrest.Matchers.equalTo;
import static org.hamcrest.Matchers.greaterThanOrEqualTo;
import static org.hamcrest.Matchers.hasSize;
import static org.hamcrest.Matchers.lessThanOrEqualTo;
import static org.junit.Assume.assumeTrue;
import static ru.yandex.autotests.mainmorda.blocks.NewsBlock.NewsItem;
import static ru.yandex.autotests.mainmorda.data.NewsBlockData.DEFAULT_NEWS_SIZE;
import static ru.yandex.autotests.mordacommonsteps.matchers.LanguageMatcher.inLanguage;
import static ru.yandex.autotests.mordacommonsteps.matchers.WithWaitForMatcher.withWaitFor;
import static ru.yandex.autotests.utils.morda.url.Domain.KZ;
import static ru.yandex.qatools.htmlelements.matchers.TypifiedElementMatchers.isSelected;
import static ru.yandex.qatools.htmlelements.matchers.WrapsElementMatchers.hasText;

/**
 * Created with IntelliJ IDEA.
 * User: arttimofeev
 * Date: 26.09.12
 * Time: 18:14
 */

public class NewsSteps {
    private static final Properties CONFIG = new Properties();

    private WebDriver driver;
    private CommonMordaSteps userSteps;
    private BasePage basePage;
    private MainPage mainPage;

    public NewsSteps(WebDriver driver) {
        this.driver = driver;
        this.userSteps = new CommonMordaSteps(driver);
        this.basePage = new BasePage(driver);
        this.mainPage = new MainPage(driver);
    }

    @Step
    public void ifSportPresent() {
        assumeTrue("Текущий домен не подходит для тестирования наличия Блогов или спортивной рубрики",
                CONFIG.domainIs(KZ));
        userSteps.shouldSeeElement(basePage.newsBlock.sportTab);
    }

    @Step
    public void switchToTab(TvAfishaNewsTab tab) {
        if (!tab.isSelected()) {
            tab.click();
        }
        withWaitFor(isSelected()).matches(tab);
    }

    @Step
    public void shouldSeeLinks(TvAfishaNewsTab tab, List<NewsBlock.NewsItem> items, LinkInfo info) {
        userSteps.shouldSeeListWithSize(items, equalTo(DEFAULT_NEWS_SIZE));
        for (int i = 0; i != DEFAULT_NEWS_SIZE; i++) {
            userSteps.opensPage(CONFIG.getBaseURL());
            switchToTab(tab);
            userSteps.shouldSeeLink(items.get(i).link, info);
        }
    }

    @Step
    public void shouldSeeNumeration(List<NewsItem> newsList) {
        int i = 1;
        for (NewsItem item : newsList) {
            userSteps.shouldSeeElementWithText(item.number, equalTo(i++ + "."));
        }
    }

    @Step
    public void shouldNotSeeNumeration(List<NewsItem> newsList) {
        for (NewsItem item : newsList) {
            userSteps.shouldNotSeeElement(item.number);
        }
    }

    @Step
    public void shouldSeeLanguage(List<NewsItem> newsList, Language language) {
        for (NewsItem item : newsList) {
            assertThat(item, hasText(inLanguage(language)));
        }
    }

    @Step
    public void shouldNotSeeDuplicates(List<String> news) {
        Set<String> withoutDuplicates = new HashSet<String>(news);
        assertThat("В новостях есть дубликаты!", withoutDuplicates, hasSize(news.size()));
    }

    @Step
    public void shouldBeDifferent(List<String> list1, List<String> list2) {
        list1.removeAll(list2);
        assertThat("В новостях есть дубликаты!", list1, hasSize(greaterThanOrEqualTo(2)));
    }

    @Step
    public List<String> getNewsTexts(List<NewsItem> list) {
        List<String> news = new ArrayList<String>();
        if (TestFailedFlag.notFailed()) {
            for (NewsItem item : list) {
                String text = item.getText();
                news.add(text.substring(text.indexOf(".") + 1));
            }
        }
        return news;
    }

    @Step
    public void shouldSeeEnumerationOptionsText() {
        for (HtmlElement element : mainPage.newsSettings.enumerationSelect
                .getOptionsAsHtmlElements()) {
            userSteps.shouldSeeElementWithText(element, equalTo(NewsSettingsData.ENUMERATION_MAP
                    .get(element.getAttribute(HtmlAttribute.VALUE.toString()))));
        }
    }

    @Step
    public void shouldSeeLanguageOptionsText() {
        for (HtmlElement element : mainPage.newsSettings.languageSelect
                .getOptionsAsHtmlElements()) {
            userSteps.shouldSeeElementWithText(element, equalTo(NewsSettingsData.LANGUAGE_MAP
                    .get(element.getAttribute(HtmlAttribute.VALUE.toString()))));
        }
    }

    @Step
    public void shouldSeeActualTime() {
        Time time = basePage.newsBlock.time.getTime();
        Time realTime = RegionManager.getDayTime(CONFIG.getBaseDomain().getCapital());
        assertThat(Math.abs(time.getTime() - realTime.getTime()), lessThanOrEqualTo(3000L * 60L));
    }

    @Step
    public void shouldSeeActualDate() {
        userSteps.shouldSeeElementWithText(basePage.newsBlock.date.wDay,
                NewsBlockData.getWDayMatcher(CONFIG.getBaseDomain().getCapital()));
        userSteps.shouldSeeElementWithText(basePage.newsBlock.date.day,
                NewsBlockData.getDayMatcher(CONFIG.getBaseDomain().getCapital()));
        userSteps.shouldSeeElementWithText(basePage.newsBlock.date.month,
                NewsBlockData.getMonthMatcher(CONFIG.getBaseDomain().getCapital()));
    }

}