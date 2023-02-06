package ru.yandex.autotests.morda.pages.touch.ru.blocks;

import org.hamcrest.Matcher;
import org.openqa.selenium.support.FindBy;
import ru.yandex.autotests.morda.pages.interfaces.validation.Validateable;
import ru.yandex.autotests.morda.pages.interfaces.validation.Validator;
import ru.yandex.autotests.morda.pages.touch.ru.TouchRuMorda;
import ru.yandex.autotests.morda.rules.errorcollector.HierarchicalErrorCollector;
import ru.yandex.autotests.mordabackend.beans.tv.TvEvent;
import ru.yandex.autotests.mordabackend.beans.tv.TvTab;
import ru.yandex.qatools.allure.annotations.Step;
import ru.yandex.qatools.htmlelements.annotations.Name;
import ru.yandex.qatools.htmlelements.element.HtmlElement;

import java.util.List;

import static org.hamcrest.Matchers.containsString;
import static org.hamcrest.Matchers.equalTo;
import static org.hamcrest.Matchers.hasSize;
import static org.junit.Assert.assertThat;
import static ru.yandex.autotests.morda.rules.errorcollector.HierarchicalErrorCollector.collector;
import static ru.yandex.autotests.morda.steps.CheckSteps.shouldSeeElement;
import static ru.yandex.autotests.morda.steps.CheckSteps.shouldSeeElementMatchingTo;
import static ru.yandex.autotests.morda.steps.WebElementSteps.clickOn;
import static ru.yandex.autotests.morda.steps.WebElementSteps.shouldSee;
import static ru.yandex.autotests.morda.utils.matchers.AllOfDetailedMatcher.allOfDetailed;
import static ru.yandex.autotests.mordacommonsteps.matchers.HtmlAttributeMatcher.hasAttribute;
import static ru.yandex.autotests.mordacommonsteps.utils.HtmlAttribute.DATA_KEY;
import static ru.yandex.autotests.mordacommonsteps.utils.HtmlAttribute.DATA_STAT_SELECT;
import static ru.yandex.autotests.mordacommonsteps.utils.HtmlAttribute.HREF;
import static ru.yandex.autotests.utils.morda.language.LanguageManager.getTranslation;
import static ru.yandex.qatools.htmlelements.matchers.WrapsElementMatchers.hasText;

/**
 * User: eoff (eoff@yandex-team.ru)
 * Date: 19/05/15
 */
@Name("Блок ТВ")
@FindBy(xpath = "//div[contains(@class, 'content')]/div[contains(@class,'tv ')]")
public class TvBlock extends HtmlElement implements Validateable<TouchRuMorda> {

    @Name("Список каналов")
    @FindBy(xpath = ".//a[contains(@class, 'swiper__category')]")
    private List<HtmlElement> channels;

    @Name("Список фильмов")
    @FindBy(xpath = ".//div[contains(@class, 'swiper__page') and not(contains(@class, 'swiper__page_visible_no'))]" +
            "//a[not(contains(@class, 'tv__item-all'))]")
    private List<TvItem> items;


    @Step("Set second category")
    public void setSecondCategory() {
        HtmlElement category = channels.get(1);
        shouldSee(category);
        clickOn(category);
    }

    @Step("Should be selected second category")
    public void shouldBeSelectedSecondCategory(){
        String classAttribute = channels.get(1).getAttribute("class");
        assertThat("Category don't selected",
                classAttribute,
                containsString("swiper__category_selected_yes"));
    }

    @Override
    @Step("Check tv")
    public HierarchicalErrorCollector validate(Validator<? extends TouchRuMorda> validator) {
        return collector()
                .check(shouldSeeElement(this))
                .check(
                        validateTvChannels(validator),
                        validateItems(validator)
                );
    }

    @Step("Check channels")
    public HierarchicalErrorCollector validateTvChannels(Validator<? extends TouchRuMorda> validator) {
        HierarchicalErrorCollector collector = collector();

        for (int i = 0; i != Math.min(validator.getCleanvars().getTV().getTabs().size(), channels.size()); i++) {
            HtmlElement item = channels.get(i);
            TvTab tab = validator.getCleanvars().getTV().getTabs().get(i);

            collector.check(validateTvChannel(validator, item, tab));
        }

        HierarchicalErrorCollector channelsCountCollector = collector().check(
                shouldSeeElementMatchingTo(channels,
                        hasSize(validator.getCleanvars().getTV().getTabs().size())
                ));

        collector.check(channelsCountCollector);

        return collector;
    }

    @Step("Check channel: {1}")
    public HierarchicalErrorCollector validateTvChannel(Validator<? extends TouchRuMorda> validator,
                                                        HtmlElement channel,
                                                        TvTab tab
    ) {
        System.out.println(tab.getHref());
        Matcher<String> tabText;
        Matcher<String> tabDataKey;
        Matcher<String> tabDataStatSelect;
        Matcher<String> href;

        if (tab.getType().equals("channel")) {
            tabText = equalTo(tab.getChname().toUpperCase());
            tabDataKey = equalTo(String.valueOf(tab.getChannelId()));
            tabDataStatSelect = equalTo("tv.tabs.select." + tab.getType());
        } else if (tab.getType().equals("now")) {
            tabText = equalTo(
                    getTranslation("home", "tv", "title_now_api", validator.getMorda().getLanguage())
                            .toUpperCase());
            tabDataKey = equalTo(tab.getType());
            tabDataStatSelect = equalTo("tv.tabs.select." + tab.getType());
        } else {
            tabText = equalTo(getTranslation("home", "tv", "title_" + tab.getType(), validator.getMorda().getLanguage()).toUpperCase());
            tabDataKey = equalTo(String.valueOf(tab.getType()));
            tabDataStatSelect = equalTo("tv.tabs.select." + tab.getType());
        }

        href = equalTo(tab.getHref());//tab.getType().equals("evening")
//                ? equalTo(tab.getHref() + "?period=evening")
//                : equalTo(tab.getHref());

        return collector()
                .check(shouldSeeElement(channel))
                .check(
                        shouldSeeElementMatchingTo(channel, allOfDetailed(
                                hasText(tabText),
                                hasAttribute(HREF, href),
                                hasAttribute(DATA_KEY, tabDataKey),
                                hasAttribute(DATA_STAT_SELECT, tabDataStatSelect)
                        ))
                );
    }

    @Step("Check tab items")
    public HierarchicalErrorCollector validateItems(Validator<? extends TouchRuMorda> validator) {
        HierarchicalErrorCollector collector = collector();

        //todo: check tv events in all tabs
        collector.check(validateTvItems(validator, channels.get(0), validator.getCleanvars().getTV().getTabs().get(0)));

        return collector;
    }

    @Step("Check tab tv events: {1}")
    public HierarchicalErrorCollector validateTvItems(Validator<? extends TouchRuMorda> validator,
                                                      HtmlElement channel,
                                                      TvTab tab
    ) {
        HierarchicalErrorCollector collector = collector();

        for (int i = 0; i != Math.min(tab.getProgramms().size(), items.size()); i++) {
            TvItem item = items.get(i);
            TvEvent tvEvent = tab.getProgramms().get(i);

            collector.check(validateTvItem(validator, item, tvEvent));
        }

        HierarchicalErrorCollector tvEventsCountCollector = collector().check(
                shouldSeeElementMatchingTo(items,
                        hasSize(tab.getProgramms().size())
                ));

        collector.check(tvEventsCountCollector);

        return collector;
    }

    @Step("Check tab tv event: {1}")
    public HierarchicalErrorCollector validateTvItem(Validator<? extends TouchRuMorda> validator,
                                                     TvItem item,
                                                     TvEvent tvEvent

    ) {

        return collector()
                .check(shouldSeeElement(item))
                .check(
                        collector()
                                .check(shouldSeeElementMatchingTo(item,
                                        hasAttribute(HREF, equalTo(tvEvent.getHref())))),
                        collector()
                                .check(shouldSeeElement(item.tvTime))
                                .check(shouldSeeElementMatchingTo(item.tvTime, hasText(tvEvent.getTime()))),
                        collector()
                                .check(shouldSeeElement(item.tvName))
                                .check(shouldSeeElementMatchingTo(item.tvName, hasText(tvEvent.getFull()))),
                        collector()
                                .check(shouldSeeElement(item.tvChannel))
                                .check(shouldSeeElementMatchingTo(item.tvChannel, hasText(tvEvent.getChannel())))

                );
    }

    public static class TvItem extends HtmlElement {
        @Name("Время передачи")
        @FindBy(xpath = ".//span[contains(@class, 'tv__item__time')]")
        private HtmlElement tvTime;

        @Name("Название передачи")
        @FindBy(xpath = ".//span[contains(@class, 'tv__item__name')]")
        private HtmlElement tvName;

        @Name("Канал передачи")
        @FindBy(xpath = ".//span[contains(@class, 'tv__item__channel')]")
        private HtmlElement tvChannel;
    }

}
