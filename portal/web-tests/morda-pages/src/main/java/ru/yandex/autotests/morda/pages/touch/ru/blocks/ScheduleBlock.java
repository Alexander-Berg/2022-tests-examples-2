package ru.yandex.autotests.morda.pages.touch.ru.blocks;

import org.openqa.selenium.support.FindBy;
import ru.yandex.autotests.morda.pages.interfaces.validation.Validateable;
import ru.yandex.autotests.morda.pages.interfaces.validation.Validator;
import ru.yandex.autotests.morda.pages.touch.ru.TouchRuMorda;
import ru.yandex.autotests.morda.rules.errorcollector.HierarchicalErrorCollector;
import ru.yandex.autotests.mordabackend.beans.geohelper.RaspItem;
import ru.yandex.autotests.mordabackend.beans.rasp.Rasp;
import ru.yandex.autotests.mordabackend.beans.servicesmobile.ServiceMobileItem;
import ru.yandex.autotests.utils.morda.language.Dictionary;
import ru.yandex.qatools.allure.annotations.Step;
import ru.yandex.qatools.htmlelements.annotations.Name;
import ru.yandex.qatools.htmlelements.element.HtmlElement;

import java.util.List;
import java.util.Optional;
import java.util.function.Predicate;
import java.util.stream.Collectors;

import static java.util.Arrays.asList;
import static org.hamcrest.Matchers.containsString;
import static org.hamcrest.Matchers.equalTo;
import static org.hamcrest.Matchers.hasSize;
import static org.hamcrest.Matchers.startsWith;
import static org.junit.Assert.assertThat;
import static ru.yandex.autotests.morda.rules.errorcollector.HierarchicalErrorCollector.collector;
import static ru.yandex.autotests.morda.steps.CheckSteps.shouldSeeElement;
import static ru.yandex.autotests.morda.steps.CheckSteps.shouldSeeElementMatchingTo;
import static ru.yandex.autotests.morda.steps.WebElementSteps.clickOn;
import static ru.yandex.autotests.morda.steps.WebElementSteps.shouldSee;
import static ru.yandex.autotests.morda.utils.matchers.AllOfDetailedMatcher.allOfDetailed;
import static ru.yandex.autotests.mordacommonsteps.matchers.HtmlAttributeMatcher.hasAttribute;
import static ru.yandex.autotests.mordacommonsteps.utils.HtmlAttribute.CLASS;
import static ru.yandex.autotests.mordacommonsteps.utils.HtmlAttribute.HREF;
import static ru.yandex.autotests.utils.morda.language.LanguageManager.getTranslation;
import static ru.yandex.qatools.htmlelements.matchers.WrapsElementMatchers.hasText;

/**
 * User: eoff (eoff@yandex-team.ru)
 * Date: 19/05/15
 */
@Name("Блок Расписания")
@FindBy(xpath = "//div[contains(@class,'schedule')]")
public class ScheduleBlock extends HtmlElement implements Validateable<TouchRuMorda> {

    private static final List<ScheduleItemInfo> SCHEDULE_ITEMS = asList(
            new ScheduleItemInfo("plane", "stations/plane", (rasp) -> rasp.getAero() == 1),
            new ScheduleItemInfo("train", "stations/train", (rasp) -> rasp.getTrain() == 1),
            new ScheduleItemInfo("bus", "stations/bus", (rasp) -> rasp.getBus() == 1),
            new ScheduleItemInfo("suburban", "suburban-directions", (rasp) -> rasp.getEl() == 1),
            new ScheduleItemInfo("water", "stations/water", (rasp) -> rasp.getShip() == 1)
    );

    @Name("Заголовок")
    @FindBy(xpath = ".//a[contains(@class, 'block__title-text')]")
    private HtmlElement title;

    @Name("Дополнительные табы")
    @FindBy(xpath = ".//a[contains(@data-statlog,'rasp')]")
    private List<HtmlElement> raspTabs;

    @Name("Список расписаний")
    @FindBy(xpath = ".//a[contains(@class, 'schedule__item')]")
    private List<ScheduleItem> items;

    @Name("Иконка определения местоположения")
    @FindBy(xpath = ".//div[contains(@class, 'geoblock2__locate-icon')]")
    private HtmlElement locateIcon;

    @Name("\"Показать станции поблизости\"")
    @FindBy(xpath = ".//span[contains(@class, 'geoblock2__locate-text')]")
    private HtmlElement locateText;

    @Name("Список станций")
    @FindBy(xpath = ".//a[contains(@class, 'swiper__category')]")
    private List<HtmlElement> stationList;

    @Step("Set second category")
    public void setSecondCategory() {
        HtmlElement category = stationList.get(1);
        shouldSee(category);
        clickOn(category);
    }

    @Step("Should be selected second category")
    public void shouldBeSelectedSecondCategory(){
        String classAttribute = stationList.get(1).getAttribute("class");
        assertThat("Category don't selected",
                classAttribute,
                containsString("swiper__category_selected_yes"));
    }

    private String getRaspHost(Validator<? extends TouchRuMorda> validator) {
        Optional<ServiceMobileItem> item = validator.getCleanvars().getServicesMobile().getList().stream()
                .filter((e) -> e.getId().equals("rasp")).findFirst();
        if (item.isPresent()) {
            return item.get().getUrl();
        } else {
            return "https://m.rasp.yandex.ru/";
        }
    }

    @Override
    @Step("Check schedule")
    public HierarchicalErrorCollector validate(Validator<? extends TouchRuMorda> validator) {
        return collector()
                .check(shouldSeeElement(this))
                .check(
                        validateTitle(validator),
                        validateItems(validator),
                        validateLocationDataItems(validator)
                );
    }

    @Step("Check title")
    public HierarchicalErrorCollector validateTitle(Validator<? extends TouchRuMorda> validator) {
        return collector()
                .check(shouldSeeElement(title))
                .check(
                        shouldSeeElementMatchingTo(title, allOfDetailed(
                                hasText(getTranslation(Dictionary.Home.Mobile.SCHEDULE_TITLE, validator.getMorda().getLanguage())),
                                hasAttribute(HREF, equalTo(getRaspHost(validator)))
                        ))
                );
    }

    @Step("Check items")
    public HierarchicalErrorCollector validateItems(Validator<? extends TouchRuMorda> validator) {

        HierarchicalErrorCollector collector = collector();

        List<ScheduleItemInfo> expectedItems = SCHEDULE_ITEMS.stream().filter(
                (item) -> item.getConsumer().test(validator.getCleanvars().getRasp())
        ).collect(Collectors.toList());
        expectedItems = expectedItems.subList(0, Math.min(expectedItems.size(), 5));

        for (int i = 0; i != Math.min(expectedItems.size(), items.size()); i++) {
            ScheduleItem item = items.get(i);
            ScheduleItemInfo info = expectedItems.get(i);

            collector.check(validateItem(validator, item, info));
        }

        HierarchicalErrorCollector raspCountCollector = collector().check(
                shouldSeeElementMatchingTo(items, hasSize(expectedItems.size())
                ));

        collector.check(raspCountCollector);

        return collector;
    }

    @Step("Check item: {1}")
    public HierarchicalErrorCollector validateItem(Validator<? extends TouchRuMorda> validator,
                                                   ScheduleItem item,
                                                   ScheduleItemInfo info) {
        int regionId = validator.getMorda().getRegion().getRegionIdInt();
        String raspHost = getRaspHost(validator);
        return collector()
                .check(shouldSeeElement(item))
                .check(
                        collector()
                                .check(shouldSeeElementMatchingTo(item,
                                                hasAttribute(HREF, equalTo(raspHost + info.getPath() + "?city_geo_id=" + regionId)))
                                ),
                        collector()
                                .check(shouldSeeElement(item.scheduleText))
                                .check(shouldSeeElementMatchingTo(item.scheduleText,
                                                hasText(getTranslation("home", "schedule", info.getId(), validator.getMorda().getLanguage())))
                                ),
                        collector()
                                .check(shouldSeeElement(item.scheduleIcon))
                                .check(shouldSeeElementMatchingTo(item.scheduleIcon,
                                                hasAttribute(CLASS, containsString("schedule__icon_" + info.getId())))
                                )
                );
    }

    @Step("Check location data items")
    public HierarchicalErrorCollector validateLocationDataItems(Validator<? extends TouchRuMorda> validator) {
        if (validator.isGeoLocated()) {
            return collector().check(validateRaspTabs(validator));
        } else {
            return collector().check(validateLocationBlock(validator));
        }
    }

    @Step("Check schedule tabs")
    private HierarchicalErrorCollector validateRaspTabs(Validator<? extends TouchRuMorda> validator) {
        HierarchicalErrorCollector collector = collector();
        List<RaspItem> expectedItems = validator.getGeohelperResponse().getRasp();

        for (int i = 0; i != Math.min(expectedItems.size(), raspTabs.size()); i++) {
            HtmlElement item = raspTabs.get(i);
            RaspItem info = expectedItems.get(i);

            collector.check(validateRaspTabItem(item, info));
        }

        HierarchicalErrorCollector raspTabsCountCollector = collector().check(
                shouldSeeElementMatchingTo(raspTabs, hasSize(expectedItems.size())
                ));

        collector.check(raspTabsCountCollector);

        return collector;
    }

    @Step("Check tab item: {0}")
    private HierarchicalErrorCollector validateRaspTabItem(HtmlElement item, RaspItem info) {
        return collector()
                .check(shouldSeeElement(item))
                .check(shouldSeeElementMatchingTo(item, hasText(startsWith(info.getTitle() == null ? info.getPopularTitle().toUpperCase() : info.getTitle().toUpperCase()))))
                .check(shouldSeeElementMatchingTo(item, hasAttribute(HREF, equalTo(info.getRaspLink()))));
    }

    @Step("Check location block")
    public HierarchicalErrorCollector validateLocationBlock(Validator<? extends TouchRuMorda> validator) {
        return collector()
                .check(
                        collector()
                                .check(shouldSeeElement(locateIcon)),
                        collector()
                                .check(shouldSeeElement(locateText))
                                .check(shouldSeeElementMatchingTo(locateText, hasText(
                                        getTranslation(Dictionary.Home.Schedule.SHOW_OBJECTS, validator.getMorda().getLanguage()))))
                );
    }

    public static class ScheduleItemInfo {
        String id;
        String path;
        Predicate<Rasp> consumer;

        public ScheduleItemInfo(String id, String path, Predicate<Rasp> consumer) {
            this.id = id;
            this.path = path;
            this.consumer = consumer;
        }

        public String getId() {
            return id;
        }

        public String getPath() {
            return path;
        }

        public Predicate<Rasp> getConsumer() {
            return consumer;
        }

        public String getUrl(String host) {
            return host + path;
        }
    }

    public static class ScheduleItem extends HtmlElement {
        @Name("Иконка расписания")
        @FindBy(xpath = ".//span[contains(@class, 'schedule__icon')]")
        private HtmlElement scheduleIcon;

        @Name("Категория расписаний")
        @FindBy(xpath = ".//span[contains(@class, 'schedule__text')]")
        private HtmlElement scheduleText;
    }

}
