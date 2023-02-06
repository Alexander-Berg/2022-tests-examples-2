package ru.yandex.autotests.morda.pages.touch.ru.blocks;

import org.openqa.selenium.support.FindBy;
import ru.yandex.autotests.morda.pages.interfaces.validation.Validateable;
import ru.yandex.autotests.morda.pages.interfaces.validation.Validator;
import ru.yandex.autotests.morda.pages.touch.ru.TouchRuMorda;
import ru.yandex.autotests.morda.rules.errorcollector.HierarchicalErrorCollector;
import ru.yandex.autotests.mordabackend.beans.application.AppItem;
import ru.yandex.autotests.utils.morda.url.Domain;
import ru.yandex.qatools.allure.annotations.Step;
import ru.yandex.qatools.htmlelements.annotations.Name;
import ru.yandex.qatools.htmlelements.element.HtmlElement;

import java.util.List;

import static org.hamcrest.Matchers.equalTo;
import static org.hamcrest.Matchers.hasSize;
import static ru.yandex.autotests.morda.rules.errorcollector.HierarchicalErrorCollector.collector;
import static ru.yandex.autotests.morda.steps.CheckSteps.shouldSeeElement;
import static ru.yandex.autotests.morda.steps.CheckSteps.shouldSeeElementMatchingTo;
import static ru.yandex.autotests.morda.utils.matchers.AllOfDetailedMatcher.allOfDetailed;
import static ru.yandex.autotests.mordacommonsteps.matchers.HtmlAttributeMatcher.hasAttribute;
import static ru.yandex.autotests.mordacommonsteps.utils.HtmlAttribute.DATA_IMAGE;
import static ru.yandex.autotests.mordacommonsteps.utils.HtmlAttribute.HREF;
import static ru.yandex.qatools.htmlelements.matchers.WrapsElementMatchers.hasText;

/**
 * User: eoff (eoff@yandex-team.ru)
 * Date: 19/05/15
 */
@Name("Блок приложений")
@FindBy(xpath = "//div[contains(@class,'apps ')]")
public class AppsBlock extends HtmlElement implements Validateable<TouchRuMorda> {

    @Name("Заголовок")
    @FindBy(xpath = ".//a[contains(@class, 'apps__title')]")
    private HtmlElement title;

    @Name("Список приложений")
    @FindBy(xpath = ".//a[contains(@class, 'apps__item')]")
    private List<ApplicationItem> items;

    @Override
    @Step("Check apps")
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
                        shouldSeeElementMatchingTo(title, allOfDetailed(
                                hasText(validator.getCleanvars().getApplication().getTitle().trim()),
                                hasAttribute(HREF, equalTo(
                                        validator.getMorda().getRegion().getDomain().equals(Domain.UA)
                                                ? "https://mobile.yandex.ua/"
                                                : "https://mobile.yandex.ru/"
                                ))
                        ))
                );
    }

    @Step("Check items")
    public HierarchicalErrorCollector validateItems(Validator<? extends TouchRuMorda> validator) {
        HierarchicalErrorCollector collector = collector();

        for (int i = 0; i != Math.min(validator.getCleanvars().getApplication().getList().size(), items.size()); i++) {
            ApplicationItem item = items.get(i);
            AppItem appItem = validator.getCleanvars().getApplication().getList().get(i);

            collector.check(validateItem(validator, item, appItem));
        }

        HierarchicalErrorCollector appCountCollector = collector().check(
                shouldSeeElementMatchingTo(items,
                        hasSize(validator.getCleanvars().getApplication().getList().size())
                ));

        collector.check(appCountCollector);

        return collector;
    }

    @Step("Check item: {1}")
    public HierarchicalErrorCollector validateItem(Validator<? extends TouchRuMorda> validator,
                                                   ApplicationItem item,
                                                   AppItem appItem) {
        return collector()
                .check(shouldSeeElement(item))
                .check(
                        collector()
                                .check(shouldSeeElementMatchingTo(item, hasAttribute(HREF,
                                                equalTo(appItem.getUrl()))
                                )),
                        collector()
                                .check(shouldSeeElement(item.itemIcon))
                                .check(shouldSeeElementMatchingTo(item.itemIcon,
                                        hasAttribute(DATA_IMAGE, equalTo(
                                                "{\"svg\":\"" + appItem.getIconSvg() + "\",\"png\":\"" + appItem.getIcon() + "\"}"))
                                )),
                        collector()
                                .check(shouldSeeElement(item.itemText))
                                .check(shouldSeeElementMatchingTo(item.itemText, hasText(appItem.getTitle())))
                );
    }


    public static class ApplicationItem extends HtmlElement {
        @Name("Иконка приложения")
        @FindBy(xpath = ".//span[contains(@class, 'apps__item__icon')]")
        private HtmlElement itemIcon;

        @Name("Название приложения")
        @FindBy(xpath = ".//span[contains(@class, 'apps__item__text')]")
        private HtmlElement itemText;
    }

}
