package ru.yandex.autotests.morda.pages.desktop.main.blocks;

import org.hamcrest.Matcher;
import org.openqa.selenium.support.FindBy;
import ru.yandex.autotests.morda.pages.desktop.main.DesktopMainMorda;
import ru.yandex.autotests.morda.pages.interfaces.validation.Validateable;
import ru.yandex.autotests.morda.pages.interfaces.validation.Validator;
import ru.yandex.autotests.morda.rules.errorcollector.HierarchicalErrorCollector;
import ru.yandex.autotests.mordabackend.beans.afisha.Afisha;
import ru.yandex.autotests.mordabackend.beans.afisha.AfishaEvent;
import ru.yandex.autotests.mordabackend.beans.afisha.AfishaExample;
import ru.yandex.autotests.mordabackend.beans.afisha.AfishaPremiereEvent;
import ru.yandex.autotests.mordabackend.beans.afisha.AfishaPromo;
import ru.yandex.autotests.utils.morda.language.Dictionary;
import ru.yandex.autotests.utils.morda.url.UrlManager;
import ru.yandex.qatools.allure.annotations.Step;
import ru.yandex.qatools.htmlelements.annotations.Name;
import ru.yandex.qatools.htmlelements.element.HtmlElement;

import javax.ws.rs.core.UriBuilder;
import java.util.List;

import static org.hamcrest.Matchers.equalTo;
import static org.hamcrest.Matchers.hasSize;
import static org.hamcrest.Matchers.isEmptyOrNullString;
import static org.hamcrest.Matchers.startsWith;
import static ru.yandex.autotests.morda.pages.desktop.main.blocks.AfishaBlock.AfishaItem.validateAfishaItem;
import static ru.yandex.autotests.morda.pages.desktop.main.blocks.AfishaBlock.AfishaPremiere.validateAfishaPremiere;
import static ru.yandex.autotests.morda.rules.errorcollector.HierarchicalErrorCollector.collector;
import static ru.yandex.autotests.morda.steps.CheckSteps.shouldNotSeeElement;
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
@Name("Афиша")
@FindBy(xpath = "//div[@class = 'afisha']")
public class AfishaBlock extends HtmlElement implements Validateable<DesktopMainMorda> {

    @Name("Заголовок")
    @FindBy(xpath = ".//h1//a")
    public HtmlElement title;

    @Name("Список событий")
    @FindBy(xpath = ".//ul[contains(@class, 'b-afisha-list')]//li[./a[contains(@class, 'b-afisha__item')]]")
    public List<AfishaItem> afishaItems;

    @Name("Премьера")
    @FindBy(xpath = ".//div[contains(@class, 'afisha__premiere')]")
    public AfishaPremiere afishaPremiere;

    @Name("Поисковый пример афиши")
    @FindBy(xpath = ".//a[contains(@class, 'example-link')]")
    public HtmlElement afishaExample;

    @Name("Промо афиши")
    @FindBy(xpath = ".//ul[contains(@class, 'b-afisha-list')]//li[contains(@class, 'list__item_promo')]//a[last()]")
    public HtmlElement afishaPromo;

    @Step("{0}")
    public static HierarchicalErrorCollector validateTitle(HtmlElement title, Validator<? extends DesktopMainMorda> validator) {
        Afisha afishaData = validator.getCleanvars().getAfisha();
        String afishaTitle = getTranslation(Dictionary.Home.Afisha.TITLE, validator.getMorda().getLanguage());
        if (afishaData.getCityPloc() != null && !afishaData.getCityPloc().isEmpty()) {
            afishaTitle += " " + afishaData.getCityPloc().replace("&nbsp;", " ");
        }

        return collector()
                .check(shouldSeeElement(title))
                .check(
                        shouldSeeElementMatchingTo(title, allOfDetailed(
                                hasText(afishaTitle),
                                hasAttribute(HREF, equalTo(url(afishaData.getHref(), validator.getMorda().getScheme())))
                        ))
                );
    }

    @Step("{0}")
    public static HierarchicalErrorCollector validateExample(HtmlElement afishaExample, Validator<? extends DesktopMainMorda> validator) {
        Afisha afishaData = validator.getCleanvars().getAfisha();
        AfishaExample afishaExampleData = afishaData.getExample();
        if (afishaExampleData == null) {
            return collector()
                    .check(shouldNotSeeElement(afishaExample));
        }

        String exampleHref = UriBuilder.fromUri(afishaData.getSearchUrl())
                .queryParam("text", UrlManager.encodeRequest(afishaExampleData.getText()))
                .queryParam("lr", afishaData.getGeo())
                .build()
                .toString();

        return collector()
                .check(shouldSeeElement(afishaExample))
                .check(shouldSeeElementMatchingTo(afishaExample, allOfDetailed(
                        hasText(afishaExampleData.getText() + " "),
                        hasAttribute(HREF, startsWith(exampleHref))
                )));
    }

    @Step("{0}")
    public static HierarchicalErrorCollector validatePromo(HtmlElement afishaPromo, Validator<? extends DesktopMainMorda> validator) {
        Afisha afishaData = validator.getCleanvars().getAfisha();
        AfishaPromo afishaPromoData = afishaData.getPromo();
        if (afishaPromoData == null) {
            return collector()
                    .check(shouldNotSeeElement(afishaPromo));
        }

        return collector()
                .check(shouldSeeElement(afishaPromo))
                .check(shouldSeeElementMatchingTo(afishaPromo, allOfDetailed(
                        hasText(afishaPromoData.getText()),
                        hasAttribute(HREF, equalTo(afishaPromoData.getUrlHttps()))
                )));
    }

    @Step("{0}")
    public static HierarchicalErrorCollector validateAfishaItems(List<AfishaItem> afishaItems,
                                                                 Validator<? extends DesktopMainMorda> validator) {
        List<AfishaEvent> afishaEventsData = validator.getCleanvars().getAfisha().getEvents();

        HierarchicalErrorCollector collector = collector();

        for (int i = 0; i != Math.min(afishaEventsData.size(), afishaItems.size()); i++) {
            collector.check(validateAfishaItem(afishaItems.get(i), afishaEventsData.get(i), validator));
        }

        HierarchicalErrorCollector countCollector = collector().check(
                shouldSeeElementMatchingTo(afishaItems, hasSize(afishaEventsData.size()))
        );
        collector.check(countCollector);

        return collector;
    }

    @Override
    @Step("Check afisha block")
    public HierarchicalErrorCollector validate(Validator<? extends DesktopMainMorda> validator) {
        return collector()
                .check(shouldSeeElement(this))
                .check(
                        validateTitle(title, validator),
                        validateAfishaItems(afishaItems, validator),
                        validateAfishaPremiere(afishaPremiere, validator),
                        validateExample(afishaExample, validator),
                        validatePromo(afishaPromo, validator)
                );
    }

    public static class AfishaPremiere extends HtmlElement {

        @Name("Название")
        @FindBy(xpath = ".//a[contains(@class, 'b-afisha__item')]")
        public HtmlElement premiereName;

        @Name("День премьеры")
        @FindBy(xpath = ".//span[contains(@class, 'premiere_day')]")
        public HtmlElement premiereDay;

        @Step("{0}")
        public static HierarchicalErrorCollector validatePremiereName(HtmlElement eventName,
                                                                      AfishaPremiereEvent premiereData,
                                                                      Validator<? extends DesktopMainMorda> validator) {
            Matcher<String> title = premiereData.getTitle() != null && !premiereData.getTitle().isEmpty()
                    ? equalTo(premiereData.getTitle())
                    : isEmptyOrNullString();

            return collector()
                    .check(shouldSeeElement(eventName))
                    .check(
                            shouldSeeElementMatchingTo(eventName, allOfDetailed(
                                    hasText(premiereData.getName()),
                                    hasAttribute(TITLE, title),
                                    hasAttribute(HREF, equalTo(
                                            url(premiereData.getHref(), validator.getMorda().getScheme())
                                            .replaceAll("&amp;","&"))
                                    )
                            ))
                    );
        }

        @Step("{0}")
        public static HierarchicalErrorCollector validatePremiereDay(HtmlElement premiereDay,
                                                                     AfishaPremiereEvent premiereData,
                                                                     Validator<? extends DesktopMainMorda> validator) {

            return collector()
                    .check(shouldSeeElement(premiereDay))
                    .check(
                            shouldSeeElementMatchingTo(premiereDay,
                                    hasText(premiereData.getPremday().replaceAll("&nbsp;"," ")))
                    );
        }

        @Step("{0}")
        public static HierarchicalErrorCollector validateAfishaPremiere(AfishaPremiere afishaPremiere,
                                                                        Validator<? extends DesktopMainMorda> validator) {
            AfishaPremiereEvent premiereData = validator.getCleanvars().getAfisha().getPremiere();
            if (premiereData == null) {
                return collector()
                        .check(shouldNotSeeElement(afishaPremiere));
            }

            return collector()
                    .check(shouldSeeElement(afishaPremiere))
                    .check(
                            validatePremiereName(afishaPremiere.premiereName, premiereData, validator),
                            validatePremiereDay(afishaPremiere.premiereDay, premiereData, validator)
                    );
        }
    }

    public static class AfishaItem extends HtmlElement {

        @Name("Название")
        @FindBy(xpath = ".//a[contains(@class, 'b-afisha__item')]")
        public HtmlElement eventName;

        @Name("Жанр")
        @FindBy(xpath = ".//span[contains(@class, 'b-afisha__genre')]")
        public HtmlElement genre;

        @Step("{0}")
        public static HierarchicalErrorCollector validateEventName(HtmlElement eventName,
                                                                   AfishaEvent eventData,
                                                                   Validator<? extends DesktopMainMorda> validator) {
            Matcher<String> title = eventData.getTitle() != null && !eventData.getTitle().isEmpty()
                    ? equalTo(eventData.getTitle())
                    : isEmptyOrNullString();

            return collector()
                    .check(shouldSeeElement(eventName))
                    .check(
                            shouldSeeElementMatchingTo(eventName, allOfDetailed(
                                    hasText(eventData.getName()),
                                    hasAttribute(TITLE, title),
                                    hasAttribute(HREF, equalTo(
                                            url(eventData.getHref(), validator.getMorda().getScheme())
                                                    .replaceAll("&amp;", "&"))
                                    )
                            ))
                    );
        }

        @Step("{0}")
        public static HierarchicalErrorCollector validateGenre(HtmlElement genre,
                                                               AfishaEvent eventData,
                                                               Validator<? extends DesktopMainMorda> validator) {
            if (eventData.getGenre() == null || eventData.getGenre().isEmpty()) {
                return collector()
                        .check(shouldNotSeeElement(genre));
            }

            return collector()
                    .check(shouldSeeElement(genre))
                    .check(
                            shouldSeeElementMatchingTo(genre, hasText(eventData.getGenre()))
                    );
        }

        @Step("{0}")
        public static HierarchicalErrorCollector validateAfishaItem(AfishaItem afishaItem,
                                                                    AfishaEvent afishaItemData,
                                                                    Validator<? extends DesktopMainMorda> validator) {
            return collector()
                    .check(shouldSeeElement(afishaItem))
                    .check(
                            validateEventName(afishaItem.eventName, afishaItemData, validator),
                            validateGenre(afishaItem.genre, afishaItemData, validator)
                    );
        }
    }
}
