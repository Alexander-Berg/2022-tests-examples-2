package ru.yandex.autotests.mainmorda.steps;

import org.hamcrest.Matcher;
import org.hamcrest.Matchers;
import org.openqa.selenium.WebDriver;
import ru.yandex.autotests.mainmorda.Properties;
import ru.yandex.autotests.mainmorda.blocks.AfishaTvBlock;
import ru.yandex.autotests.mainmorda.blocks.TvAfishaNewsTab;
import ru.yandex.autotests.mainmorda.data.TVAfishaData;
import ru.yandex.autotests.mainmorda.data.TvSettingsData;
import ru.yandex.autotests.mainmorda.pages.BasePage;
import ru.yandex.autotests.mainmorda.pages.MainPage;
import ru.yandex.autotests.mordacommonsteps.steps.CommonMordaSteps;
import ru.yandex.autotests.utils.morda.language.Dictionary;
import ru.yandex.qatools.allure.annotations.Step;
import ru.yandex.qatools.htmlelements.element.HtmlElement;

import java.util.HashSet;
import java.util.List;
import java.util.Set;

import static org.hamcrest.CoreMatchers.equalTo;
import static org.hamcrest.MatcherAssert.assertThat;
import static org.hamcrest.Matchers.greaterThan;
import static org.hamcrest.Matchers.hasItem;
import static org.hamcrest.Matchers.hasSize;
import static org.hamcrest.Matchers.not;
import static org.hamcrest.Matchers.startsWith;
import static org.junit.Assume.assumeFalse;
import static org.junit.Assume.assumeTrue;
import static ru.yandex.autotests.mainmorda.data.TVAfishaData.AFISHA_EVENT_HREF_PATTERN;
import static ru.yandex.autotests.mainmorda.data.TVAfishaData.AFISHA_HREFS;
import static ru.yandex.autotests.mainmorda.data.TVAfishaData.CAPITAL_TV_CODE;
import static ru.yandex.autotests.mainmorda.data.TVAfishaData.GENRES;
import static ru.yandex.autotests.mainmorda.data.TVAfishaData.TV_LINK_PATTERN;
import static ru.yandex.autotests.mainmorda.data.TvSettingsData.DEFAULT_CHANNELS_COUNT;
import static ru.yandex.autotests.mordacommonsteps.matchers.HtmlAttributeMatcher.hasAttribute;
import static ru.yandex.autotests.mordacommonsteps.matchers.RegexMatcher.matches;
import static ru.yandex.autotests.mordacommonsteps.matchers.WithWaitForMatcher.withWaitFor;
import static ru.yandex.autotests.mordacommonsteps.utils.HtmlAttribute.HREF;
import static ru.yandex.autotests.mordacommonsteps.utils.HtmlAttribute.TITLE;
import static ru.yandex.autotests.mordacommonsteps.utils.HtmlAttribute.VALUE;
import static ru.yandex.autotests.utils.morda.language.Dictionary.Home.Tv.TV_PROGRAM;
import static ru.yandex.autotests.utils.morda.language.LanguageManager.getTranslation;
import static ru.yandex.autotests.utils.morda.url.Domain.BY;
import static ru.yandex.autotests.utils.morda.url.Domain.KZ;
import static ru.yandex.autotests.utils.morda.url.Domain.RU;
import static ru.yandex.autotests.utils.morda.url.Domain.UA;
import static ru.yandex.qatools.htmlelements.matchers.TypifiedElementMatchers.isSelected;
import static ru.yandex.qatools.htmlelements.matchers.WrapsElementMatchers.exists;

/**
 * User: alex89
 * Date: 09.08.12
 */
public class TvAfishaSteps {
    private static final Properties CONFIG = new Properties();

    private WebDriver driver;
    private CommonMordaSteps userSteps;
    private BasePage basePage;
    private MainPage mainPage;

    public TvAfishaSteps(WebDriver driver) {
        this.driver = driver;
        this.userSteps = new CommonMordaSteps(driver);
        this.basePage = new BasePage(driver);
        this.mainPage = new MainPage(driver);
    }

    @Step
    public void shouldSeeTvTitle(Matcher<String> title) {
        String allText = userSteps.getElementText(mainPage.tvSettings.tvChannelsTitle);
        assertThat("Неверный тв title", allText.substring(0, allText.indexOf("\n")), title);
    }

    @Step
    public void shouldSeeCorrectChannelsOptionsText() {
        for (HtmlElement element : mainPage.tvSettings.selectProgrammeLength
                .getOptionsAsHtmlElements()) {
            userSteps.shouldSeeElementWithText(element, equalTo(TvSettingsData.DEFAULT_CHANNELS_TEXT
                    .get(element.getAttribute(VALUE.toString()))));
        }
    }

    @Step
    public void setChannelsCount(int listElementNumber) {
        userSteps.selectOption(mainPage.tvSettings.selectProgrammeLength, listElementNumber);
        userSteps.clicksOn(mainPage.tvSettings.okButton);
        userSteps.shouldNotSeeElement(mainPage.tvSettings);
    }

    @Step
    public void shouldSeeChannelProgram(String channelName) {
        for (AfishaTvBlock.TvEvent event : TvSettingsData.getTvBlock(basePage).tvEvents) {
            userSteps.shouldSeeElementWithText(event.channel, equalTo(channelName));
        }
    }

    @Step
    public void shouldSeeSelectProgramLength() {
        userSteps.shouldSeeSelectWithSize(mainPage.tvSettings.selectProgrammeLength,
                greaterThan(0));
        if (mainPage.tvSettings.selectProgrammeLength.getOptionsAsHtmlElements().size() > 0) {
            userSteps.shouldSeeElement(mainPage.tvSettings.selectProgrammeLength
                    .getOptionsAsHtmlElements().get(0));
            userSteps.shouldSeeElementMatchingTo(mainPage.tvSettings.selectProgrammeLength
                    .getFirstSelectedOptionAsHtmlElement(),
                    hasAttribute(VALUE, equalTo(DEFAULT_CHANNELS_COUNT)));
        }
    }

    //afisha-Tv tabs
    @Step
    public void switchesToTab(TvAfishaNewsTab tab) {
        if (!tab.isSelected()) {
            tab.click();
        }
        withWaitFor(isSelected()).matches(tab);
    }

    //////////////////   TV
    @Step
    public void shouldSeeDifferentTvEventsInWidget(AfishaTvBlock tvBlock) {
        Set<String> texts = new HashSet<String>();
        for (AfishaTvBlock.TvEvent program : tvBlock.tvEvents) {
            texts.add(program.getText());
        }
        assertThat("Среди телепередач есть дубли!", texts, hasSize(tvBlock.tvEvents.size()));
    }

    @Step
    public void shouldSeeTvEventsTimeInWidget(AfishaTvBlock tvBlock) {
        List<AfishaTvBlock.TvEvent> programs = tvBlock.tvEvents;
        for (AfishaTvBlock.TvEvent event : programs) {
            assertThat("Некорректный формат времени! ",
                    event.time.getText(), matches(TVAfishaData.TIME_PATTERN));
        }
    }

    @Step
    public void shouldSeeTvEventsLinksInWidget(AfishaTvBlock tvBlock) {
        for (AfishaTvBlock.TvEvent event : tvBlock.tvEvents) {
            userSteps.shouldSeeElementMatchingTo(event.eventLink,
                    hasAttribute(HREF, matches(String.format(TVAfishaData.TV_EVENT_HREF_PATTERN,
                            CONFIG.getBaseDomain(), CAPITAL_TV_CODE.get(CONFIG.getBaseDomain()).getRegionId()))));
        }
    }

    @Step
    public void shouldSeeTvTabInWidget(AfishaTvBlock tvBlock) {
        assumeFalse("В Астане по-умолчанию нет виджета ТВ-Афиша", CONFIG.domainIs(KZ));
        userSteps.shouldSeeElement(tvBlock.tvTab);
        userSteps.shouldSeeElementWithText(tvBlock.tvTab, getTranslation(TV_PROGRAM, CONFIG.getLang()));
        userSteps.shouldSeeElementIsSelected(tvBlock.tvTab);
        userSteps.shouldSeeElementMatchingTo(tvBlock.tvTab,
                hasAttribute(HREF, equalTo(String.format(TV_LINK_PATTERN,
                        CONFIG.getBaseDomain()) + CAPITAL_TV_CODE.get(CONFIG.getBaseDomain()).getRegionId() + "/")));
    }

    @Step
    public void shouldSeeTvTitleLinkInWidget(AfishaTvBlock tvBlock) {
        assumeTrue("В Киеве, Москве и Минске по-умолчанию нет 2х раздельных виджетов ТВ и Афиша", CONFIG.domainIs(KZ));
        userSteps.shouldSeeElement(tvBlock.tvTab);
        userSteps.shouldSeeElementWithText(tvBlock.tvTab, getTranslation(TV_PROGRAM, CONFIG.getLang()));
        userSteps.shouldSeeElementMatchingTo(tvBlock.tvTab,
                hasAttribute(HREF, startsWith(String.format(TV_LINK_PATTERN,
                        CONFIG.getBaseDomain()) + CAPITAL_TV_CODE.get(CONFIG.getBaseDomain()).getRegionId())));
    }

    ////Afisha
    @Step
    public AfishaTvBlock shouldSeeAnyAfishaWidget() {
        AfishaTvBlock requiredVersionOfAfishaWidget;
        if (CONFIG.domainIs(RU) || CONFIG.domainIs(UA) || CONFIG.domainIs(BY)) {
            requiredVersionOfAfishaWidget = basePage.tvBlock;
            userSteps.shouldSeeElement(requiredVersionOfAfishaWidget);
            switchesToTab(requiredVersionOfAfishaWidget.afishaTab);
        } else {
            requiredVersionOfAfishaWidget = basePage.afishaBlock;
            userSteps.shouldSeeElement(requiredVersionOfAfishaWidget);
        }
        return requiredVersionOfAfishaWidget;
    }

    @Step
    public void shouldSeeAfishaEventsInWidget(AfishaTvBlock afishaBlock) {
        for (AfishaTvBlock.AfishaEvent event : afishaBlock.afishaEvents) {
            shouldSeeThatAfishaLinkAndGenreAreCorrectInEvent(event);
        }
    }

    @Step
    public void shouldSeeThatAfishaLinkAndGenreAreCorrectInEvent(AfishaTvBlock.AfishaEvent event) {
        assertThat("Пустой текст события афиши!", event.eventLink.getText(), not(Matchers.equalTo("")));
        assertThat("Некорректный href события афиши! ",
                event.eventLink, hasAttribute(HREF, matches(String.format(AFISHA_EVENT_HREF_PATTERN,
                CONFIG.getBaseDomain()))));
        if (event.eventLink.getText().endsWith("…")) {
            assertThat("Атрибут title события афиши некорректен!",
                    event.eventLink, hasAttribute(TITLE, startsWith(event.eventLink.getText().replaceAll("…$", ""))));
        }
        assertThat("Отсутсвует жанр у события афиши:" + event.getText(), event.genre, exists());
        assertThat("Некорректный жанр события афиши:" + event.genre.getText(),
                GENRES, hasItem(event.genre.getText()));
    }

    @Step
    public void shouldSeeAfishaTabInWidget(AfishaTvBlock afishaBlock) {
        userSteps.shouldSeeElement(afishaBlock.afishaTab);
        userSteps.shouldSeeElementWithText(afishaBlock.afishaTab,
                getTranslation(Dictionary.Home.Afisha.TITLE, CONFIG.getLang()));
        userSteps.shouldSeeElementMatchingTo(afishaBlock.afishaTab,
                hasAttribute(HREF, equalTo(AFISHA_HREFS.get(CONFIG.getBaseDomain()))));
    }

    @Step
    public void shouldSeeAfishaTitle(AfishaTvBlock afishaBlock) {
        userSteps.shouldSeeElement(afishaBlock.afishaTitle);
        userSteps.shouldSeeElementWithText(afishaBlock.afishaTitle,
                getTranslation(Dictionary.Home.Afisha.TITLE, CONFIG.getLang()));
        userSteps.shouldSeeElementMatchingTo(afishaBlock.afishaTitle,
                hasAttribute(HREF, equalTo(AFISHA_HREFS.get(CONFIG.getBaseDomain()))));
    }

    //////////Премьера
    @Step
    public void shouldSeePremiereInTheMiddleOfWeek(AfishaTvBlock afishaBlock) {
        userSteps.shouldSeeElement(afishaBlock.afishaPremiere);
        userSteps.shouldSeeListWithSize(afishaBlock.afishaPremiere.afishaPremiereLinks, equalTo(1));
        shouldSeePremiereLink(afishaBlock);
        userSteps.shouldSeeElement(afishaBlock.afishaPremiere.afishaPremiereDate);
    }

    @Step
    public void shouldSeePremiereLink(AfishaTvBlock afishaBlock) {
        assertThat("Отсутствует название премьеры!", afishaBlock.afishaPremiere.afishaPremiereLinks.get(0).getText(),
                not(equalTo("")));
        assertThat("Некорректный href у премьеры!", afishaBlock.afishaPremiere.afishaPremiereLinks.get(0),
                hasAttribute(HREF, matches(String.format(TVAfishaData.AFISHA_EVENT_HREF_PATTERN,
                        CONFIG.getBaseDomain()))));
    }

    @Step
    public void shouldSeeRuUaByDomainForTabTesting() {
        assumeFalse("В Астане по-умолчанию нет виджета ТВ-Афиша, проверять переключалку не нужно!",
                CONFIG.domainIs(KZ));
    }
}