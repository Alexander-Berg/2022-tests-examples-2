package ru.yandex.autotests.morda.pages.touch.ru.blocks;

import org.openqa.selenium.support.FindBy;
import ru.yandex.autotests.morda.pages.interfaces.validation.Validateable;
import ru.yandex.autotests.morda.pages.interfaces.validation.Validator;
import ru.yandex.autotests.morda.pages.touch.ru.TouchRuMorda;
import ru.yandex.autotests.morda.rules.errorcollector.HierarchicalErrorCollector;
import ru.yandex.autotests.mordabackend.beans.aeroexpress.TrainItem;
import ru.yandex.autotests.mordabackend.beans.aeroexpress.TransportItem;
import ru.yandex.qatools.allure.annotations.Step;
import ru.yandex.qatools.htmlelements.annotations.Name;
import ru.yandex.qatools.htmlelements.element.HtmlElement;

import java.text.SimpleDateFormat;
import java.util.Date;
import java.util.List;

import static org.hamcrest.Matchers.containsString;
import static org.hamcrest.Matchers.equalTo;
import static org.hamcrest.Matchers.hasSize;
import static ru.yandex.autotests.morda.rules.errorcollector.HierarchicalErrorCollector.collector;
import static ru.yandex.autotests.morda.steps.CheckSteps.shouldSeeElement;
import static ru.yandex.autotests.morda.steps.CheckSteps.shouldSeeElementMatchingTo;
import static ru.yandex.autotests.mordacommonsteps.matchers.HtmlAttributeMatcher.hasAttribute;
import static ru.yandex.autotests.mordacommonsteps.utils.HtmlAttribute.CLASS;
import static ru.yandex.autotests.mordacommonsteps.utils.HtmlAttribute.HREF;
import static ru.yandex.autotests.utils.morda.language.LanguageManager.getTranslation;
import static ru.yandex.qatools.htmlelements.matchers.WrapsElementMatchers.hasText;

/**
 * @author Ivan Nikolaev <ivannik@yandex-team.ru>
 */
@Name("Блок Аэроэкспресс")
@FindBy(xpath = "//div[contains(concat(' ',@class,' '),' aeroexpress ')]")
public class AeroexpressBlock extends HtmlElement implements Validateable<TouchRuMorda> {

    @Name("Заголовок")
    @FindBy(xpath = ".//div[contains(@class,'block__title-text')]")
    private HtmlElement title;

    @Name("Список ссылок")
    @FindBy(xpath = ".//div[contains(@class,'aeroexpress__items')]//a")
    private List<AeroexpressItem> aeroexpressItems;

    @Override
    @Step("Check aeroexpress")
    public HierarchicalErrorCollector validate(Validator<? extends TouchRuMorda> validator) {
        return collector()
                .check(shouldSeeElement(this))
                .check(
                        validateTitle(validator),
                        validateItems(validator)
                );
    }

    @Step("Check title")
    public HierarchicalErrorCollector validateTitle(Validator<? extends TouchRuMorda> validator) {
        return collector()
                .check(shouldSeeElement(title))
                .check(
                        shouldSeeElementMatchingTo(title,
                                hasText(
                                        getTranslation("home", "aeroexpress", "point." +
                                                        validator.getCleanvars().getAeroexpress().getActiveAirport().getId(),
                                                validator.getMorda().getLanguage()) +
                                                " → " +
                                                validator.getCleanvars().getAeroexpress().getActiveAirport().getTargetName()
                                )
                        )
                );
    }

    @Step("Check items")
    public HierarchicalErrorCollector validateItems(Validator<? extends TouchRuMorda> validator) {
        HierarchicalErrorCollector collector = collector();

        List<TransportItem> expectedAeroexpressItems = validator.getCleanvars().getAeroexpress().getActiveAirport().getTransports();

        for (int i = 0; i != Math.min(expectedAeroexpressItems.size(), aeroexpressItems.size()); i++) {
            AeroexpressItem item = aeroexpressItems.get(i);
            TransportItem expectedItem = expectedAeroexpressItems.get(i);

            collector.check(validateItem(validator, item, expectedItem));
        }

        HierarchicalErrorCollector transportCountCollector = collector().check(
                shouldSeeElementMatchingTo(aeroexpressItems,
                        hasSize(expectedAeroexpressItems.size())
                ));

        collector.check(transportCountCollector);

        return collector;
    }

    @Step("Check item: {0}")
    public HierarchicalErrorCollector validateItem(Validator<? extends TouchRuMorda> validator,
                                                   AeroexpressItem item, TransportItem expectedItem)
    {
        return collector()
                .check(shouldSeeElement(item))
                .check(
                        collector()
                                .check(shouldSeeElementMatchingTo(item,
                                                hasAttribute(HREF, equalTo(getLink(expectedItem))))
                                ),
                        collector()
                                .check(shouldSeeElement(item.icon))
                                .check(shouldSeeElementMatchingTo(item.icon,
                                                hasAttribute(CLASS, containsString("aeroexpress__icon_type_" + expectedItem.getType())))
                                ),
                        collector()
                                .check(shouldSeeElement(item.title))
                                .check(shouldSeeElementMatchingTo(item.title,
                                                hasText(getTitle(validator, expectedItem)))
                                ),
                        collector()
                                .check(shouldSeeElement(item.time))
                                .check(shouldSeeElementMatchingTo(item.time,
                                                hasText(getTime(validator, expectedItem)))
                                ),
                        collector()
                                .check(shouldSeeElement(item.info))
                                .check(shouldSeeElementMatchingTo(item.info,
                                                hasText(getInfo(validator, expectedItem)))
                                )
                );
    }

    private String getTitle(Validator<? extends TouchRuMorda> validator, TransportItem expectedItem) {
        if ("aeroexpress".equals(expectedItem.getType())) {
            return getTranslation("home", "aeroexpress", "type." + expectedItem.getType(), validator.getMorda().getLanguage()) + "\n" +
                    getTranslation("home", "aeroexpress", "target." + expectedItem.getId(),  validator.getMorda().getLanguage());
        } else if ("taxi".equals(expectedItem.getType())) {
            return getTranslation("home", "aeroexpress", "target.taxi2", validator.getMorda().getLanguage());
        }
        return "";
    }

    private String getLink(TransportItem expectedItem) {
        if ("aeroexpress".equals(expectedItem.getType())) {
            return String.format("https://aeroexpress.ru/m/order.html?prev_date=%s&prev_count=1&prev_menus=%s",
                    new SimpleDateFormat("d-M-yyyy").format(new Date()), expectedItem.getOrderId());
        } else if ("taxi".equals(expectedItem.getType())) {
            return "https://m.taxi.yandex.ru/";
        }
        return "";
    }

    private String getTime(Validator<? extends TouchRuMorda> validator, TransportItem expectedItem) {
        if ("aeroexpress".equals(expectedItem.getType())) {
            return String.format(getTranslation("home", "aeroexpress", "time.min",
                    validator.getMorda().getLanguage()), expectedItem.getDuration());
        } else if ("taxi".equals(expectedItem.getType())) {
            int mins = Integer.parseInt(expectedItem.getDuration());
            if (mins < 60) {
                return "~" + String.format(getTranslation("home", "aeroexpress", "time.min",
                        validator.getMorda().getLanguage()), mins);
            } else {
                return "~" + String.format(getTranslation("home", "aeroexpress", "time.hour",
                        validator.getMorda().getLanguage()), mins / 60, mins % 60);
            }
        }
        return "";
    }

    private String getInfo(Validator<? extends TouchRuMorda> validator, TransportItem expectedItem) {
        if ("aeroexpress".equals(expectedItem.getType())) {
            return expectedItem.getTrains().stream().map(TrainItem::getDeparture).reduce((a, b) -> a + ", " + b).get();
        } else if ("taxi".equals(expectedItem.getType())) {
            return String.format(getTranslation("home", "aeroexpress", "cost", validator.getMorda().getLanguage()),
                    expectedItem.getTaxiCost()) + " Р\n–";
        }
        return "";
    }

    public static class AeroexpressItem extends HtmlElement {
        @Name("Иконка")
        @FindBy(xpath = ".//div[contains(@class,'aeroexpress__icon_type_')]")
        private HtmlElement icon;

        @Name("Название ссылки")
        @FindBy(xpath = ".//div[contains(@class,'aeroexpress__title')]")
        private HtmlElement title;

        @Name("Продолжительность")
        @FindBy(xpath = ".//span[contains(@class,'aeroexpress__time')]")
        private HtmlElement time;

        @Name("Информация")
        @FindBy(xpath = ".//span[contains(@class,'aeroexpress__info')]")
        private HtmlElement info;
    }
}
