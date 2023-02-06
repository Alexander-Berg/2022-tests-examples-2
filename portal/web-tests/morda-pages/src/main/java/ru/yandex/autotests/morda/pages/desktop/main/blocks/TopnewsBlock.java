package ru.yandex.autotests.morda.pages.desktop.main.blocks;

import org.openqa.selenium.support.FindBy;
import ru.yandex.autotests.morda.pages.desktop.main.DesktopMainMorda;
import ru.yandex.autotests.morda.pages.desktop.main.htmlelements.SelectableTab;
import ru.yandex.autotests.morda.pages.desktop.main.htmlelements.Widget;
import ru.yandex.autotests.morda.pages.interfaces.validation.Validateable;
import ru.yandex.autotests.morda.pages.interfaces.validation.Validator;
import ru.yandex.autotests.morda.rules.errorcollector.HierarchicalErrorCollector;
import ru.yandex.autotests.mordabackend.beans.topnews.Topnews;
import ru.yandex.autotests.mordabackend.beans.topnews.TopnewsSpecial;
import ru.yandex.autotests.mordabackend.beans.topnews.TopnewsTab;
import ru.yandex.autotests.mordabackend.beans.topnews.TopnewsTabItem;
import ru.yandex.qatools.allure.annotations.Step;
import ru.yandex.qatools.htmlelements.annotations.Name;
import ru.yandex.qatools.htmlelements.element.HtmlElement;

import java.util.List;

import static org.hamcrest.Matchers.equalTo;
import static org.hamcrest.Matchers.hasSize;
import static ru.yandex.autotests.morda.pages.desktop.main.blocks.TopnewsBlock.NewsBlockHeader.NewsBlockHeaderDateTime.NewsBlockHeaderTime.validateTime;
import static ru.yandex.autotests.morda.pages.desktop.main.blocks.TopnewsBlock.NewsBlockHeader.NewsBlockHeaderDateTime.validateDateTime;
import static ru.yandex.autotests.morda.pages.desktop.main.blocks.TopnewsBlock.NewsBlockHeader.validateHeader;
import static ru.yandex.autotests.morda.rules.errorcollector.HierarchicalErrorCollector.collector;
import static ru.yandex.autotests.morda.steps.CheckSteps.*;
import static ru.yandex.autotests.morda.utils.matchers.AllOfDetailedMatcher.allOfDetailed;
import static ru.yandex.autotests.mordacommonsteps.matchers.HtmlAttributeMatcher.hasAttribute;
import static ru.yandex.autotests.mordacommonsteps.matchers.RegexMatcher.matches;
import static ru.yandex.autotests.mordacommonsteps.utils.HtmlAttribute.HREF;
import static ru.yandex.autotests.utils.morda.language.LanguageManager.getTranslation;
import static ru.yandex.autotests.utils.morda.language.LanguageManager.getTranslationSafely;
import static ru.yandex.qatools.htmlelements.matchers.WrapsElementMatchers.hasText;

/**
 * User: eoff (eoff@yandex-team.ru)
 * Date: 26/02/15
 */
@Name("Новости")
@FindBy(xpath = "//div[contains(@id,'wd-wrapper-_topnews')]")
public class TopnewsBlock extends Widget<TopnewsSettingsBlock> implements Validateable<DesktopMainMorda> {

    public NewsBlockHeader newsBlockHeader;

    @FindBy(xpath = ".//div[@class = 'news__header']/parent::div")
    public HtmlElement numbersHiddenFlag;

    @Name("Содержимое таба новостей")
    @FindBy(xpath = ".//div[@role='tabpanel']")
    public List<NewsBlockTabContent> allNewsTabContents;

    @Name("Активный таб новостей")
    @FindBy(xpath = ".//div[@role='tabpanel' and contains(@class, 'active_true')]")
    public NewsBlockTabContent activeNewsTabContent;

    @Name("Открыть Виджет котировок")
    @FindBy(xpath = ".//span[contains(@class, 'inline-stocks__more')]")
    public HtmlElement quotesMore;

    public TopnewsSettingsBlock topnewsSettingsBlock;

    @Step("{0}")
    public static HierarchicalErrorCollector validateNewsItem(HtmlElement newsEntry,
                                                              TopnewsTabItem newsEntryData,
                                                              Validator<? extends DesktopMainMorda> validator) {
        return collector()
                .check(shouldSeeElement(newsEntry))
                .check(shouldSeeElementMatchingTo(newsEntry, allOfDetailed(
                        hasText(newsEntryData.getText() + newsEntryData.getHreftext()),
                        hasAttribute(HREF, equalTo(url(newsEntryData.getHref(), validator.getMorda().getScheme())))
                )));
    }

    @Step("{0}")
    public static HierarchicalErrorCollector validateActiveNewsList(TopnewsBlock topnewsBlock,
                                                                    Validator<? extends DesktopMainMorda> validator) {

        TopnewsTab tabData = validator.getCleanvars().getTopnews().getTabs()
                .get(getActiveTab(topnewsBlock.newsBlockHeader.newsTabs));

        HierarchicalErrorCollector collector = collector();

        for (int i = 0; i != Math.min(tabData.getNews().size(), topnewsBlock.activeNewsTabContent.newsList.size()); i++) {
            collector.check(validateNewsItem(
                    topnewsBlock.activeNewsTabContent.newsList.get(i),
                    tabData.getNews().get(i),
                    validator)
            );
        }

        HierarchicalErrorCollector countCollector = collector().check(
                shouldSeeElementMatchingTo(topnewsBlock.activeNewsTabContent.newsList, hasSize(tabData.getNews().size()))
        );
        collector.check(countCollector);

        return collector;
    }

    private static int getActiveTab(List<SelectableTab> tabs) {
        for (int i = 0; i != tabs.size(); i++) {
            if (tabs.get(i).isSelected()) {
                return i;
            }
        }
        throw new IllegalStateException("Failed to get active news tab");
    }

    @Override
    protected TopnewsSettingsBlock getSetupPopup() {
        return topnewsSettingsBlock;
    }

    @Step("Open quotes block")
    public void openQuotesBlock() {
        shouldSeeElement(quotesMore);
        quotesMore.click();
    }

    @Override
    public HierarchicalErrorCollector validate(Validator<? extends DesktopMainMorda> validator) {
        return collector()
                .check(shouldSeeElement(this))
                .check(
                        validateHeader(this.newsBlockHeader, validator),
                        validateActiveNewsList(this, validator)
                );
    }

    @Name("Хедер новостей")
    @FindBy(xpath = ".//div[@class='content-tabs__head']")
    public static class NewsBlockHeader extends HtmlElement {

        @Name("Табы новостей")
        @FindBy(xpath = ".//div[contains(@class, 'content-tabs__head-item')]//a")
        public List<SelectableTab> newsTabs;

        public NewsBlockHeaderDateTime newsDateTime;

        @Name("Алерт новостей")
        @FindBy(xpath = ".//span[contains(@class, 'news__alarm')]//a")
        public HtmlElement newsAlarm;

        @Step("{0}")
        public static HierarchicalErrorCollector validateNewsAlarm(HtmlElement newsAlarm,
                                                                   Validator<? extends DesktopMainMorda> validator) {
            TopnewsSpecial newsAlarmData = validator.getCleanvars().getTopnews().getSpecial();

            if (newsAlarmData == null) {
                return collector()
                        .check(shouldNotSeeElement(newsAlarm));
            }

            return collector()
                    .check(shouldSeeElement(newsAlarm))
                    .check(shouldSeeElementMatchingTo(newsAlarm, allOfDetailed(
                            hasText(newsAlarmData.getTitle()),
                            hasAttribute(HREF, equalTo(url(newsAlarmData.getHref(), validator.getMorda().getScheme())))
                    )));
        }


        @Step("{0}")
        public static HierarchicalErrorCollector validateNewsTab(SelectableTab tab,
                                                                 TopnewsTab tabData,
                                                                 Validator<? extends DesktopMainMorda> validator) {

            String text = null;
            if (tabData.getTitle() == null) {
                String key = tabData.getTitlekey().equals("news") ? "massmedia_title" : "switch." + tabData.getTitlekey();
                text = getTranslationSafely("home", "news",  key, validator.getMorda().getLanguage());
            } else {
                text = tabData.getTitle();
            }

            String href = tabData.getHref() == null || tabData.getHref().isEmpty()
                    ? validator.getCleanvars().getTopnews().getHref()
                    : tabData.getHref();

            return collector()
                    .check(shouldSeeElement(tab))
                    .check(shouldSeeElementMatchingTo(tab, allOfDetailed(
                            hasText(text),
                            hasAttribute(HREF, equalTo(href))
                    )));
        }

        @Step("{0}")
        public static HierarchicalErrorCollector validateNewsTabs(List<SelectableTab> tabs,
                                                                  Validator<? extends DesktopMainMorda> validator) {
            List<TopnewsTab> tabsData = validator.getCleanvars().getTopnews().getTabs();

            HierarchicalErrorCollector collector = collector();

            for (int i = 0; i != Math.min(tabs.size(), tabsData.size()); i++) {
                collector.check(validateNewsTab(tabs.get(i), tabsData.get(i), validator));
            }

            HierarchicalErrorCollector countCollector = collector().check(
                    shouldSeeElementMatchingTo(tabs, hasSize(tabsData.size()))
            );
            collector.check(countCollector);

            return collector;
        }

        @Step("{0}")
        public static HierarchicalErrorCollector validateHeader(NewsBlockHeader header,
                                                                Validator<? extends DesktopMainMorda> validator) {
            return collector()
                    .check(shouldSeeElement(header))
                    .check(
                            validateDateTime(header.newsDateTime, validator),
                            validateNewsTabs(header.newsTabs, validator),
                            validateNewsAlarm(header.newsAlarm, validator)
                    );
        }

        @Name("Время и дата в новостях")
        @FindBy(xpath = ".//span[contains(@class, 'datetime_js_inited')]")
        public static class NewsBlockHeaderDateTime extends HtmlElement {

            @Name("День")
            @FindBy(xpath = ".//span[contains(@class, 'datetime__day')]")
            public HtmlElement day;

            @Name("Месяц")
            @FindBy(xpath = ".//span[contains(@class, 'datetime__month')]")
            public HtmlElement month;

            @Name("День недели")
            @FindBy(xpath = ".//span[contains(@class, 'datetime__wday')]")
            public HtmlElement dayOfWeek;

            public NewsBlockHeaderTime newsTime;

            @Step("{0}")
            public static HierarchicalErrorCollector validateDate(NewsBlockHeaderDateTime dateTime,
                                                                  Validator<? extends DesktopMainMorda> validator) {
                Topnews newsData = validator.getCleanvars().getTopnews();

                HierarchicalErrorCollector dayCheck = collector()
                        .check(shouldSeeElement(dateTime.day))
                        .check(shouldSeeElementMatchingTo(dateTime.day, hasText(newsData.getBigDay())));

                HierarchicalErrorCollector monthCheck;
                HierarchicalErrorCollector dayOfWeekCheck;

                if (newsData.getSpecial() != null) {
                    monthCheck = collector()
                            .check(shouldSeeElement(dateTime.month))
                            .check(shouldSeeElementMatchingTo(dateTime.month,
                                    hasText(validator.getCleanvars().getTopnews().getBigMonth() + ",")));
                    dayOfWeekCheck = collector()
                            .check(shouldNotSeeElement(dateTime.dayOfWeek));
                } else {
                    monthCheck = collector()
                            .check(shouldSeeElement(dateTime.month))
                            .check(shouldSeeElementMatchingTo(dateTime.month, hasText(newsData.getBigMonth() + ",")));
                    dayOfWeekCheck = collector()
                            .check(shouldSeeElement(dateTime.dayOfWeek))
                            .check(shouldSeeElementMatchingTo(dateTime.dayOfWeek, hasText(newsData.getBigWday())));
                }

                return collector()
                        .check(
                                dayCheck,
                                monthCheck,
                                dayOfWeekCheck
                        );
            }

            @Step("{0}")
            public static HierarchicalErrorCollector validateDateTime(NewsBlockHeaderDateTime dateTime,
                                                                      Validator<? extends DesktopMainMorda> validator) {
                return collector()
                        .check(shouldSeeElement(dateTime))
                        .check(
                                validateTime(dateTime.newsTime, validator),
                                validateDate(dateTime, validator)
                        );
            }


            @Name("Время в новостях")
            @FindBy(xpath = ".//span[contains(@class, 'datetime__time')]/a")
            public static class NewsBlockHeaderTime extends HtmlElement {

                @Name("Час")
                @FindBy(xpath = ".//span[contains(@class, 'datetime__hour')]")
                public HtmlElement hour;

                @Name("Разделитель")
                @FindBy(xpath = ".//span[contains(@class, 'datetime__flicker')]")
                public HtmlElement timeSeparator;

                @Name("Минута")
                @FindBy(xpath = ".//span[contains(@class, 'datetime__min')]")
                public HtmlElement min;

                @Step("{0}")
                public static HierarchicalErrorCollector validateTime(NewsBlockHeaderTime time,
                                                                      Validator<? extends DesktopMainMorda> validator) {
                    HierarchicalErrorCollector hourCheck = collector()
                            .check(shouldSeeElement(time.hour))
                            .check(shouldSeeElementMatchingTo(time.hour, hasText(matches("[0-1][0-9]|2[0-3]"))));
                    HierarchicalErrorCollector minuteCheck = collector()
                            .check(shouldSeeElement(time.hour))
                            .check(shouldSeeElementMatchingTo(time.hour, hasText(matches("[0-5][0-9]"))));

                    return collector()
                            .check(shouldSeeElement(time))
                            .check(
                                    hourCheck,
                                    minuteCheck
                            );
                }
            }
        }
    }

    public static class NewsBlockTabContent extends HtmlElement {
        @Name("Список новостей")
        @FindBy(xpath = ".//ol[contains(@class, 'b-news-list')]//a")
        public List<HtmlElement> newsList;
    }
}
