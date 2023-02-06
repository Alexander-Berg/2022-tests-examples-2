package ru.yandex.autotests.morda.pages.touch.ru.blocks;

import org.openqa.selenium.support.FindBy;
import ru.yandex.autotests.morda.pages.interfaces.validation.Validateable;
import ru.yandex.autotests.morda.pages.interfaces.validation.Validator;
import ru.yandex.autotests.morda.pages.touch.ru.TouchRuMorda;
import ru.yandex.autotests.morda.rules.errorcollector.HierarchicalErrorCollector;
import ru.yandex.autotests.mordabackend.beans.geohelper.PoiObject;
import ru.yandex.autotests.mordabackend.beans.poi_groups.PoiGroupsItem;
import ru.yandex.qatools.allure.annotations.Step;
import ru.yandex.qatools.htmlelements.annotations.Name;
import ru.yandex.qatools.htmlelements.element.HtmlElement;

import java.util.ArrayList;
import java.util.List;
import java.util.Locale;
import java.util.stream.Collectors;

import static java.util.Arrays.asList;
import static org.hamcrest.Matchers.containsString;
import static org.hamcrest.Matchers.equalTo;
import static org.hamcrest.Matchers.hasSize;
import static org.hamcrest.Matchers.startsWith;
import static ru.yandex.autotests.morda.rules.errorcollector.HierarchicalErrorCollector.collector;
import static ru.yandex.autotests.morda.steps.CheckSteps.shouldSeeElement;
import static ru.yandex.autotests.morda.steps.CheckSteps.shouldSeeElementMatchingTo;
import static ru.yandex.autotests.morda.utils.matchers.AllOfDetailedMatcher.allOfDetailed;
import static ru.yandex.autotests.mordacommonsteps.matchers.HtmlAttributeMatcher.hasAttribute;
import static ru.yandex.autotests.mordacommonsteps.utils.HtmlAttribute.CLASS;
import static ru.yandex.autotests.mordacommonsteps.utils.HtmlAttribute.DATA_ID;
import static ru.yandex.autotests.mordacommonsteps.utils.HtmlAttribute.DATA_STATLOG;
import static ru.yandex.autotests.mordacommonsteps.utils.HtmlAttribute.HREF;
import static ru.yandex.autotests.utils.morda.language.LanguageManager.getTranslation;
import static ru.yandex.qatools.htmlelements.matchers.WrapsElementMatchers.hasText;

/**
 * User: eoff (eoff@yandex-team.ru)
 * Date: 19/05/15
 */
@Name("Блок POI")
@FindBy(xpath = "//div[contains(@class,'places')]")
public class PoiBlock extends HtmlElement implements Validateable<TouchRuMorda> {

    @Name("Заголовок")
    @FindBy(xpath = ".//div[contains(@class, 'places__title')]")
    private HtmlElement title;

    @Name("Группы мест")
    @FindBy(xpath = ".//div[contains(@class, 'places__categories')]/div[contains(@class, 'places__category')]")
    private List<PoiItem> items;

    @Name("Места")
    @FindBy(xpath = ".//div[contains(@class, 'places__items')]//a[contains(@class, 'places__card-info')]")
    private List<PoiPlaces> poiPlaces;

    @Override
    @Step("Check POI")
    public HierarchicalErrorCollector validate(Validator<? extends TouchRuMorda> validator) {
        return collector()
                .check(shouldSeeElement(this))
                .check(
                        validateTitle(validator),
                        validateItems(validator),
                        validatePlaces(validator)
                );
    }

    @Step("Check title")
    public HierarchicalErrorCollector validateTitle(Validator<? extends TouchRuMorda> validator) {
        if (validator.isGeoLocated()) {
            return collector()
                    .check(shouldSeeElement(title))
                    .check(
                            shouldSeeElementMatchingTo(title, hasText(validator.getGeohelperResponse().getGeocoder()))
                    );
        } else {
            return collector()
                    .check(shouldSeeElement(title))
                    .check(
                            shouldSeeElementMatchingTo(title, hasText(getTranslation("home", "places", "title", validator.getMorda().getLanguage())))
                    );
        }
    }

    @Step("Check items")
    public HierarchicalErrorCollector validateItems(Validator<? extends TouchRuMorda> validator) {
        List<String> expectedPoi = new ArrayList<>();
        expectedPoi.add("interest");
        expectedPoi.addAll(validator.getCleanvars().getPoiGroups().getList().stream().map(PoiGroupsItem::getGroup)
                .collect(Collectors.toList()));
        expectedPoi.add("search");

        HierarchicalErrorCollector collector = collector();

        for (int i = 0; i != Math.min(expectedPoi.size(), items.size()); i++) {
            PoiItem item = items.get(i);
            String poi = expectedPoi.get(i);

            collector.check(validateItem(validator, item, poi));
        }

        HierarchicalErrorCollector poiCountCollector = collector().check(
                shouldSeeElementMatchingTo(items, hasSize(expectedPoi.size()))
        );

        collector.check(poiCountCollector);

        return collector;
    }

    @Step("Check item: {1}")
    public HierarchicalErrorCollector validateItem(Validator<? extends TouchRuMorda> validator,
                                                   PoiItem item,
                                                   String poi) {
        String poiIcon = poi;
        if (asList("breakfast", "dinner", "supper").contains(poi)) {
            poiIcon = "food";
        }

        if ("barclub".equals(poi)) {
            poiIcon = "night";
        }

        String poiText = poi.equals("interest")
                ? getTranslation("home", "places", "near", validator.getMorda().getLanguage())
                : getTranslation("home", "mobile", "poi.category." + poi, validator.getMorda().getLanguage());

        return collector()
                .check(shouldSeeElement(item))
                .check(
                        collector()
                                .check(shouldSeeElementMatchingTo(item, allOfDetailed(
                                        hasAttribute(DATA_ID, equalTo(poi)),
                                        hasAttribute(DATA_STATLOG, equalTo("poi.tabs." + poi))
                                ))),
                        collector()
                                .check(shouldSeeElement(item.itemIcon))
                                .check(shouldSeeElementMatchingTo(item.itemIcon,
                                        hasAttribute(CLASS, containsString(poiIcon))
                                )),
                        collector()
                                .check(shouldSeeElement(item.itemText))
                                .check(shouldSeeElementMatchingTo(item.itemText, hasText(poiText)))
                );
    }

    @Step("Check places")
    public HierarchicalErrorCollector validatePlaces(Validator<? extends TouchRuMorda> validator) {
        if (validator.isGeoLocated()) {
            HierarchicalErrorCollector collector = collector();

            List<PoiObject> expectedPlaces = validator.getGeohelperResponse().getFav();

            for (int i = 0; i != Math.min(expectedPlaces.size(), poiPlaces.size()); i++) {
                PoiPlaces item = poiPlaces.get(i);
                PoiObject place = expectedPlaces.get(i);

                collector.check(validatePlaceItem(item, place));
            }

            HierarchicalErrorCollector poiCountCollector = collector().check(
                    shouldSeeElementMatchingTo(poiPlaces, hasSize(expectedPlaces.size()))
            );

            collector.check(poiCountCollector);
            return collector;
        } else {
            return collector();
        }
    }



    @Step("Check place: {0}")
    public HierarchicalErrorCollector validatePlaceItem(PoiPlaces item, PoiObject place) {
        String poiIcon = place.getGroup();
        if (asList("breakfast", "dinner", "supper").contains(place.getGroup())) {
            poiIcon = "food";
        }

        String distance;
        if (place.getDistance() > 1000) {
            distance = String.format(Locale.ENGLISH, "%.1f км", place.getDistance() / 1000.0);
        } else {
            int a = place.getDistance();
            if (a < 100) {
                distance = String.format("%d м", 100);
            } else if ((a % 100) < 50) {
                distance = String.format("%d м", a - (a % 100));
            } else {
                distance = String.format("%d м", a - (a % 100) + 100);
            }
        }

        return collector()
                .check(shouldSeeElement(item))
                .check(
                        collector()
                                .check(shouldSeeElementMatchingTo(item,
                                        hasAttribute(HREF, startsWith(
                                                place.getHref()
                                                        .replaceAll("'", "%27")
                                                        .replaceAll(",", "%2C")
                                                )
                                        ))),
                        collector()
                                .check(shouldSeeElement(item.icon))
                                .check(shouldSeeElementMatchingTo(item.icon,
                                        hasAttribute(CLASS, containsString(poiIcon))
                                )),
                        collector()
                                .check(shouldSeeElement(item.title))
                                //неразрывный пробел
                                .check(shouldSeeElementMatchingTo(item.title,
                                        hasText(place.getName().replaceAll(" ", " ")))),
                        collector()
                                .check(shouldSeeElement(item.time))
                                .check(shouldSeeElementMatchingTo(item.time, hasText(place.getHours()))),
                        collector()
                                .check(shouldSeeElement(item.distance))
                                .check(shouldSeeElementMatchingTo(item.distance, hasText(distance)))
                );
    }

    public static class PoiItem extends HtmlElement {
        @Name("Иконка POI")
        @FindBy(xpath = ".//div[contains(@class, 'places__category-icon')]")
        private HtmlElement itemIcon;

        @Name("Название POI")
        @FindBy(xpath = ".//div[contains(@class, 'places__category-text')]")
        private HtmlElement itemText;
    }

    public static class PoiPlaces extends HtmlElement {
        @Name("Иконка")
        @FindBy(xpath = ".//div[contains(@class, 'places__card-group-image')]")
        private HtmlElement icon;

        @Name("Название")
        @FindBy(xpath = ".//div[contains(@class, 'places__card-title')]")
        private HtmlElement title;

        @Name("Время работы")
        @FindBy(xpath = ".//div[contains(@class, 'places__card-time')]")
        private HtmlElement time;

        @Name("Расстояние")
        @FindBy(xpath = ".//span[contains(@class, 'places__card-dist')]")
        private HtmlElement distance;
    }
}
