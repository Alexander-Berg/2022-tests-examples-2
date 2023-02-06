package ru.yandex.autotests.morda.pages.desktop.main.blocks;

import org.openqa.selenium.support.FindBy;
import ru.yandex.autotests.morda.pages.desktop.main.DesktopMainMorda;
import ru.yandex.autotests.morda.pages.desktop.main.htmlelements.Widget;
import ru.yandex.autotests.morda.pages.interfaces.validation.Validateable;
import ru.yandex.autotests.morda.pages.interfaces.validation.Validator;
import ru.yandex.autotests.morda.rules.errorcollector.HierarchicalErrorCollector;
import ru.yandex.autotests.mordabackend.beans.tv.TvAnnounce;
import ru.yandex.autotests.mordabackend.beans.tv.TvEvent;
import ru.yandex.autotests.utils.morda.language.Dictionary;
import ru.yandex.qatools.allure.annotations.Step;
import ru.yandex.qatools.htmlelements.annotations.Name;
import ru.yandex.qatools.htmlelements.element.HtmlElement;

import java.util.List;

import static org.hamcrest.Matchers.equalTo;
import static org.hamcrest.Matchers.hasSize;
import static ru.yandex.autotests.morda.pages.desktop.main.blocks.TvBlock.TvItem.validateTvEvent;
import static ru.yandex.autotests.morda.rules.errorcollector.HierarchicalErrorCollector.collector;
import static ru.yandex.autotests.morda.steps.CheckSteps.shouldSeeElement;
import static ru.yandex.autotests.morda.steps.CheckSteps.shouldSeeElementMatchingTo;
import static ru.yandex.autotests.morda.steps.CheckSteps.url;
import static ru.yandex.autotests.morda.utils.matchers.AllOfDetailedMatcher.allOfDetailed;
import static ru.yandex.autotests.mordacommonsteps.matchers.HtmlAttributeMatcher.hasAttribute;
import static ru.yandex.autotests.mordacommonsteps.utils.HtmlAttribute.HREF;
import static ru.yandex.autotests.mordacommonsteps.utils.HtmlAttribute.TITLE;
import static ru.yandex.autotests.utils.morda.language.LanguageManager.getTranslation;
import static ru.yandex.qatools.htmlelements.matchers.WrapsElementMatchers.hasText;

/**
 * User: eoff (eoff@yandex-team.ru)
 * Date: 01/04/15
 */
@Name("ТВ")
@FindBy(xpath = "//div[contains(@id,'wd-wrapper-_tv')]")
public class TvBlock extends Widget<TvSettingsBlock> implements Validateable<DesktopMainMorda> {

    @Name("Заголовок")
    @FindBy(xpath = ".//h1//a")
    public HtmlElement title;

    @Name("Список передач")
    @FindBy(xpath = ".//ul[contains(@class, 'tv-list')]//li[not(./a)]")
    public List<TvItem> tvEvents;

    @Name("Анонс")
    @FindBy(xpath = ".//ul[contains(@class, 'tv-list')]//li[./a]/a")
    public HtmlElement tvPromo;

    public TvSettingsBlock tvSettingsBlock;

    @Override
    protected TvSettingsBlock getSetupPopup() {
        return tvSettingsBlock;
    }

    @Step("{0}")
    public static HierarchicalErrorCollector validateTitle(HtmlElement title, Validator<? extends DesktopMainMorda> validator) {

        return collector()
                .check(shouldSeeElement(title))
                .check(
                        shouldSeeElementMatchingTo(title, allOfDetailed(
                                hasText(getTranslation(Dictionary.Home.Tv.TV_PROGRAM, validator.getMorda().getLanguage())),
                                hasAttribute(HREF, equalTo(url(validator.getCleanvars().getTV().getHref(), validator.getMorda().getScheme())))
                        ))
                );
    }

    @Step("{0}")
    public static HierarchicalErrorCollector validateTvEvents(List<TvItem> tvEvents,
                                                              Validator<? extends DesktopMainMorda> validator) {
        List<TvEvent> tvEventsData = validator.getCleanvars().getTV().getProgramms();

        HierarchicalErrorCollector collector = collector();

        for (int i = 0; i != Math.min(tvEventsData.size(), tvEvents.size()); i++) {
            collector.check(validateTvEvent(tvEvents.get(i), tvEventsData.get(i), validator));
        }

        HierarchicalErrorCollector countCollector = collector().check(
                shouldSeeElementMatchingTo(tvEvents, hasSize(tvEventsData.size()))
        );
        collector.check(countCollector);

        return collector;
    }


    @Step("{0}")
    public static HierarchicalErrorCollector validateTvPromo(HtmlElement tvPromo,
                                                             Validator<? extends DesktopMainMorda> validator) {
        if (validator.getCleanvars().getTV().getAnnounces().isEmpty()) {
            return collector();
        }

        TvAnnounce announce = validator.getCleanvars().getTV().getAnnounces().get(0);
        return collector()
                .check(shouldSeeElement(tvPromo))
                .check(
                        shouldSeeElementMatchingTo(tvPromo, allOfDetailed(
                                hasText(announce.getText().trim()),
                                hasAttribute(HREF, equalTo(url(announce.getUrl(), validator.getMorda().getScheme())))
                        ))
                );
    }

    @Override
    @Step("Check tv block")
    public HierarchicalErrorCollector validate(Validator<? extends DesktopMainMorda> validator) {
        return collector()
                .check(shouldSeeElement(this))
                .check(
                        validateTitle(title, validator),
                        validateTvEvents(tvEvents, validator),
                        validateTvPromo(tvPromo, validator)
                );
    }

    public static class TvItem extends HtmlElement {

        @Name("Время")
        @FindBy(xpath = ".//span[contains(@class, 'time')]")
        public HtmlElement time;

        @Name("Название передачи")
        @FindBy(xpath = ".//span[contains(@class, 'title')]/a[contains(@class, 'tv-program__item')]")
        public HtmlElement program;

        @Name("Название канала")
        @FindBy(xpath = ".//span[contains(@class, 'tv-list__channel')]//a")
        public HtmlElement channel;

        @Step("{0}")
        public static HierarchicalErrorCollector validateTime(HtmlElement time,
                                                              TvEvent tvEventData,
                                                              Validator<? extends DesktopMainMorda> validator) {

            return collector()
                    .check(shouldSeeElement(time))
                    .check(
                            shouldSeeElementMatchingTo(time, hasText(tvEventData.getTime()))
                    );
        }

        @Step("{0}")
        public static HierarchicalErrorCollector validateProgram(HtmlElement program,
                                                                 TvEvent tvEventData,
                                                                 Validator<? extends DesktopMainMorda> validator) {

            return collector()
                    .check(shouldSeeElement(program))
                    .check(
                            shouldSeeElementMatchingTo(program, allOfDetailed(
                                    hasText(tvEventData.getName()),
                                    hasAttribute(TITLE, equalTo(tvEventData.getTitle())),
                                    hasAttribute(HREF, equalTo(url(tvEventData.getHref(), validator.getMorda().getScheme())))
                            ))
                    );
        }

        @Step("{0}")
        public static HierarchicalErrorCollector validateChannel(HtmlElement channel,
                                                                 TvEvent tvEventData,
                                                                 Validator<? extends DesktopMainMorda> validator) {

            return collector()
                    .check(shouldSeeElement(channel))
                    .check(
                            shouldSeeElementMatchingTo(channel, allOfDetailed(
                                    hasText(tvEventData.getChannel()),
                                    hasAttribute(HREF, equalTo(url(tvEventData.getChHref(), validator.getMorda().getScheme())))
                            ))
                    );
        }

        @Step("{0}")
        public static HierarchicalErrorCollector validateTvEvent(TvItem tvItem,
                                                                 TvEvent tvEventData,
                                                                 Validator<? extends DesktopMainMorda> validator) {
            return collector()
                    .check(shouldSeeElement(tvItem))
                    .check(
                            validateTime(tvItem.time, tvEventData, validator),
                            validateProgram(tvItem.program, tvEventData, validator),
                            validateChannel(tvItem.channel, tvEventData, validator)
                    );
        }
    }
}
