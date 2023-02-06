package ru.yandex.autotests.morda.pages.touch.ru.blocks;

import org.openqa.selenium.support.FindBy;
import ru.yandex.autotests.morda.pages.interfaces.validation.Validateable;
import ru.yandex.autotests.morda.pages.interfaces.validation.Validator;
import ru.yandex.autotests.morda.pages.touch.ru.TouchRuMorda;
import ru.yandex.autotests.morda.rules.errorcollector.HierarchicalErrorCollector;
import ru.yandex.autotests.mordabackend.beans.geohelper.MetroItem;
import ru.yandex.autotests.utils.morda.language.Dictionary;
import ru.yandex.qatools.allure.annotations.Step;
import ru.yandex.qatools.htmlelements.annotations.Name;
import ru.yandex.qatools.htmlelements.element.HtmlElement;

import java.util.List;
import java.util.Locale;

import static org.hamcrest.Matchers.anyOf;
import static org.hamcrest.Matchers.containsString;
import static org.hamcrest.Matchers.equalTo;
import static org.hamcrest.Matchers.hasSize;
import static ru.yandex.autotests.morda.rules.errorcollector.HierarchicalErrorCollector.collector;
import static ru.yandex.autotests.morda.steps.CheckSteps.shouldSeeElement;
import static ru.yandex.autotests.morda.steps.CheckSteps.shouldSeeElementMatchingTo;
import static ru.yandex.autotests.mordacommonsteps.matchers.HtmlAttributeMatcher.hasAttribute;
import static ru.yandex.autotests.mordacommonsteps.utils.HtmlAttribute.CLASS;
import static ru.yandex.autotests.mordacommonsteps.utils.HtmlAttribute.HREF;
import static ru.yandex.autotests.mordacommonsteps.utils.HtmlAttribute.STYLE;
import static ru.yandex.autotests.utils.morda.language.LanguageManager.getTranslation;
import static ru.yandex.qatools.htmlelements.matchers.WrapsElementMatchers.hasText;

/**
 * User: eoff (eoff@yandex-team.ru)
 * Date: 19/05/15
 */
@Name("Блок Метро")
@FindBy(xpath = "//div[contains(@class,'metro')]")
public class MetroBlock extends HtmlElement implements Validateable<TouchRuMorda> {

    @Name("Ссылка на метро")
    @FindBy(xpath = ".//a[contains(@class, 'metro__item')]")
    private MetroLink metroLink;

    @Name("Станции метро рядом")
    @FindBy(xpath = ".//a[contains(@class, 'metro__station')]")
    private List<StationLink> stationLinks;

    @Override
    @Step("Check metro")
    public HierarchicalErrorCollector validate(Validator<? extends TouchRuMorda> validator) {
        HierarchicalErrorCollector collector = collector()
                .check(shouldSeeElement(this));
        if (validator.getCleanvars().getGeoID() != 65) {
            collector.check(validateMetroLink(validator));
        }
        if (validator.isGeoLocated()) {
            collector.check(validateStationLinks(validator));
        }
        return collector;
    }

    @Step("Check metro link")
    public HierarchicalErrorCollector validateMetroLink(Validator<? extends TouchRuMorda> validator) {
        return collector()
                .check(
                        validateText(validator),
                        validateIcon(validator),
                        validateLink(validator)
                );
    }

    @Step("Check station links")
    public HierarchicalErrorCollector validateStationLinks(Validator<? extends TouchRuMorda> validator) {
        HierarchicalErrorCollector collector = collector();
        List<MetroItem> expectedItems = validator.getGeohelperResponse().getMetro();

        for (int i = 0; i != Math.min(expectedItems.size(), stationLinks.size()); i++) {
            StationLink item = stationLinks.get(i);
            MetroItem expectedMetroItem = expectedItems.get(i);

            collector.check(validateStationItem(item, expectedMetroItem));
        }

        HierarchicalErrorCollector stationItemCountCollector = collector().check(
                shouldSeeElementMatchingTo(stationLinks, hasSize(expectedItems.size())
                ));

        collector.check(stationItemCountCollector);

        return collector;
    }

    @Step("Check station link: {0}")
    public HierarchicalErrorCollector validateStationItem(StationLink item, MetroItem metroItem) {

        String distance;
        double d = Double.parseDouble(metroItem.getDistance());
        if (d > 1000.0) {
            distance = String.format(Locale.ENGLISH, "%.1f км", d / 1000.0);
        } else {
            if (d < 100) {
                distance = "100 м";
            } else {
                distance = String.format("%d м", Math.round(d / 100.0) * 100);
            }
        }

        int color = Integer.parseInt(metroItem.getColor().substring(1), 16);
        String backgroundStyle = String.format("background: rgb(%d, %d, %d) none repeat scroll 0%% 0%%;",
                (color >> 16) & 0xff, (color >> 8) & 0xff, color & 0xff);
        String backgroundStyle1 = String.format("background: none repeat scroll 0%% 0%% rgb(%d, %d, %d);",
                (color >> 16) & 0xff, (color >> 8) & 0xff, color & 0xff);


        return collector()
                .check(
                        shouldSeeElement(item),
                        shouldSeeElementMatchingTo(item, hasAttribute(HREF, equalTo(metroItem.getMapLink())))
                )
                .check(
                        shouldSeeElement(item.stationText),
                        shouldSeeElementMatchingTo(item.stationText, hasText(metroItem.getName()))
                )
                .check(
                        shouldSeeElement(item.stationIcon),
                        shouldSeeElementMatchingTo(item.stationIcon,
                                hasAttribute(STYLE, anyOf(
                                        equalTo(backgroundStyle),
                                        equalTo(backgroundStyle1)))
                        )
                );
//                .check(
//                        shouldSeeElement(item.stationDistance),
//                        shouldSeeElementMatchingTo(item.stationDistance, hasText(distance))
//                )
    }

    @Step("Check text")
    public HierarchicalErrorCollector validateText(Validator<? extends TouchRuMorda> validator) {
        return collector()
                .check(shouldSeeElement(metroLink.metroText))
                .check(
                        shouldSeeElementMatchingTo(metroLink.metroText,
                                hasText(getTranslation(Dictionary.Home.Maps.METRO, validator.getMorda().getLanguage())))
                );
    }

    @Step("Check icon")
    public HierarchicalErrorCollector validateIcon(Validator<? extends TouchRuMorda> validator) {
        return collector()
                .check(shouldSeeElement(metroLink.metroIcon))
                .check(
                        shouldSeeElementMatchingTo(metroLink.metroIcon, hasAttribute(CLASS,
                                containsString("metro__icon_city_" + validator.getCleanvars().getMetro().getIcon())))
                );
    }

    @Step("Check link")
    public HierarchicalErrorCollector validateLink(Validator<? extends TouchRuMorda> validator) {
        return collector()
                .check(shouldSeeElement(metroLink))
                .check(shouldSeeElementMatchingTo(metroLink, hasAttribute(HREF,
                        equalTo(validator.getMorda().getScheme() + ":" + validator.getCleanvars().getMetro().getUrl()))));
    }

    public static class MetroLink extends HtmlElement {

        @Name("Текст \"Схема метро\"")
        @FindBy(xpath = ".//span[contains(@class, 'metro__text')]")
        private HtmlElement metroText;

        @Name("Иконка метро")
        @FindBy(xpath = ".//span[contains(@class, 'metro__icon')]")
        private HtmlElement metroIcon;

    }

    public static class StationLink extends HtmlElement {
        @Name("Название станции")
        @FindBy(xpath = ".//span[contains(@class, 'metro__text')]")
        private HtmlElement stationText;

        @Name("Иконка станции")
        @FindBy(xpath = ".//span[contains(@class, 'metro__circle')]")
        private HtmlElement stationIcon;

        @Name("Расстояние до станции")
        @FindBy(xpath = ".//span[contains(@class, 'dist')]")
        private HtmlElement stationDistance;
    }
}
