package ru.yandex.autotests.morda.pages.touch.ru.blocks;

import org.openqa.selenium.support.FindBy;
import ru.yandex.autotests.morda.pages.interfaces.validation.Validateable;
import ru.yandex.autotests.morda.pages.interfaces.validation.Validator;
import ru.yandex.autotests.morda.pages.touch.ru.TouchRuMorda;
import ru.yandex.autotests.morda.rules.errorcollector.HierarchicalErrorCollector;
import ru.yandex.autotests.morda.utils.matchers.UrlMatcher;
import ru.yandex.autotests.mordabackend.beans.edadeal.RetailerItem;
import ru.yandex.qatools.allure.annotations.Step;
import ru.yandex.qatools.htmlelements.annotations.Name;
import ru.yandex.qatools.htmlelements.element.HtmlElement;

import java.util.List;

import static java.lang.String.format;
import static org.hamcrest.CoreMatchers.endsWith;
import static org.hamcrest.CoreMatchers.equalTo;
import static org.hamcrest.CoreMatchers.startsWith;
import static org.hamcrest.Matchers.hasSize;
import static ru.yandex.autotests.morda.rules.errorcollector.HierarchicalErrorCollector.collector;
import static ru.yandex.autotests.morda.steps.CheckSteps.shouldSeeElement;
import static ru.yandex.autotests.morda.steps.CheckSteps.shouldSeeElementMatchingTo;
import static ru.yandex.autotests.morda.utils.matchers.AllOfDetailedMatcher.allOfDetailed;
import static ru.yandex.autotests.morda.utils.matchers.UrlMatcher.urlMatcher;
import static ru.yandex.autotests.mordacommonsteps.matchers.HtmlAttributeMatcher.hasAttribute;
import static ru.yandex.autotests.mordacommonsteps.utils.HtmlAttribute.DATA_IMAGE;
import static ru.yandex.autotests.mordacommonsteps.utils.HtmlAttribute.HREF;
import static ru.yandex.autotests.mordacommonsteps.utils.HtmlAttribute.TITLE;
import static ru.yandex.autotests.utils.morda.language.LanguageManager.getTranslationSafely;
import static ru.yandex.qatools.htmlelements.matchers.common.HasTextMatcher.hasText;

/**
 * User: asamar
 * Date: 17.02.17
 */
@Name("Блок едадил")
@FindBy(xpath = "//div[contains(@class, 'edadeal ')]")
public class EdadealBlock extends HtmlElement implements Validateable<TouchRuMorda> {

    @Name("Заголовок")
    @FindBy(xpath = ".//a[contains(@class, 'edadeal__title')]")
    private HtmlElement edadealTitle;

    @Name("Список скидок")
    @FindBy(xpath = ".//a[contains(@class, 'edadeal__item') and not(contains(@class, 'edadeal__item-all'))]")
    private List<EdadealItem> edadealItems;

    @Name("Показать все предложения")
    @FindBy(xpath = "//a[contains(@class, 'edadeal__item-all')]")
    private AllDeals allDeals;

    @Name("Список категорий")
    @FindBy(xpath = ".//a[contains(@class, 'edadeal__category')]")
    private List<HtmlElement> edadealCategories;

    @Name("ВСЕ (категории)")
    @FindBy(xpath = ".//a[@data-id = 'all']")
    private HtmlElement all;

    @Name("Рядом со мной (категории)")
    @FindBy(xpath = ".//a[@data-id = 'near']")
    private HtmlElement near;

    @Override
    public HierarchicalErrorCollector validate(Validator<? extends TouchRuMorda> validator) {
        return collector()
                .check(validateTitle(edadealTitle, validator))
                .check(validateItems(edadealItems, validator))
                .check(allDeals.validate(validator))
                .check(validateAll(all, validator))
                .check(validateNear(near, validator));
//                .check(validateCategories(edadealCategories, validator));
    }

    @Step("{0}")
    public HierarchicalErrorCollector validateTitle(HtmlElement title, Validator<? extends TouchRuMorda> validator) {

        String localityUrl = validator.getCleanvars().getEdadeal().getLocalityURL();

        return collector()
                .check(shouldSeeElement(title))
                .check(shouldSeeElementMatchingTo(title, allOfDetailed(
                        hasText(getTranslationSafely("home", "edadeal", "title", validator.getMorda().getLanguage())),
                        hasAttribute(HREF, equalTo(localityUrl))
                )));
    }

    @Step("{0}")
    public HierarchicalErrorCollector validateItems(List<EdadealItem> items, Validator<? extends TouchRuMorda> validator) {
        HierarchicalErrorCollector collector = collector();

        List<RetailerItem> retailerItems = validator.getCleanvars().getEdadeal().getRetailers();

        for (int i = 0; i != Math.min(retailerItems.size(), items.size()); i++) {
            RetailerItem retailerItem = retailerItems.get(i);
            EdadealItem edadealItem = items.get(i);

            collector.check(validateItem(retailerItem, edadealItem, validator));
        }

        HierarchicalErrorCollector edadealCountCollector = collector().check(
                shouldSeeElementMatchingTo(items,
                        hasSize(validator.getCleanvars().getEdadeal().getRetailers().size())
                ));

        collector.check(edadealCountCollector);

        return collector;
    }

    @Step("{0}")
    public HierarchicalErrorCollector validateItem(RetailerItem retailerItem,
                                                   EdadealItem edadealItem,
                                                   Validator<? extends TouchRuMorda> validator) {

        HierarchicalErrorCollector collector = collector();

        String retailerUrl = retailerItem.getRetailerURL();
        String retailerName = retailerItem.getRetailer();
        String retailerIcon = retailerItem.getLogo().get200X200();

        collector
                .check(shouldSeeElement(edadealItem))
                .check(shouldSeeElementMatchingTo(edadealItem,
                        hasAttribute(HREF, equalTo(retailerUrl)))
                )
                .check(
                        collector()
                                .check(shouldSeeElement(edadealItem.edadealItemLogo))
                                .check(shouldSeeElementMatchingTo(edadealItem.edadealItemLogo,
                                        allOfDetailed(
                                                hasAttribute(TITLE, equalTo(retailerName)),
                                                hasAttribute(DATA_IMAGE, equalTo(retailerIcon))
                                        )))
                );

        if (retailerItem.getRndDiscount() != null) {
            String discountCategory = retailerItem.getRndDiscount().getCategory();
            int discountPersent = retailerItem.getRndDiscount().getDiscount();
            String to = getTranslationSafely("home", "edadeal", "to", validator.getMorda().getLanguage());

            String discount = format("%s\n%s", to, discountPersent) + "%";

            collector
                    .check(
                            collector()
                                    .check(shouldSeeElement(edadealItem.edadealItemCategoryText))
                                    .check(shouldSeeElementMatchingTo(edadealItem.edadealItemCategoryText,
                                            hasText(discountCategory))),

                            collector()
                                    .check(shouldSeeElement(edadealItem.edadealItemDiscount))
                                    .check(shouldSeeElementMatchingTo(edadealItem.edadealItemDiscount,
                                            hasText(discount)))
                    );
        }

        return collector;

    }


    @Step("{0}")
    public HierarchicalErrorCollector validateCategories(List<HtmlElement> categories,
                                                         Validator<? extends TouchRuMorda> validator) {
        return collector();
    }

    @Step("{0}")
    public HierarchicalErrorCollector validateAll(HtmlElement all,
                                                  Validator<? extends TouchRuMorda> validator) {

        String localityUrl = validator.getCleanvars().getEdadeal().getLocalityURL();

        return collector()
                .check(shouldSeeElement(all))
                .check(shouldSeeElementMatchingTo(all, allOfDetailed(
                        hasText(getTranslationSafely("home", "mobile", "service.all", validator.getMorda().getLanguage())
                                .toUpperCase()),
                        hasAttribute(HREF, equalTo(localityUrl))
                )));
    }

    @Step("{0}")
    public HierarchicalErrorCollector validateNear(HtmlElement near,
                                                   Validator<? extends TouchRuMorda> validator) {
        String localityUrl = validator.getCleanvars().getEdadeal().getLocalityURL();

        return collector()
                .check(shouldSeeElement(near))
                .check(shouldSeeElementMatchingTo(near, allOfDetailed(
                        hasText(getTranslationSafely("home", "edadeal", "near", validator.getMorda().getLanguage())
                                .toUpperCase()),
                        hasAttribute(HREF, equalTo(localityUrl))
                )));
    }


    public static class EdadealItem extends HtmlElement {

        @Name("Лого")
        @FindBy(xpath = ".//div[contains(@class, 'edadeal__item-img')]")
        private HtmlElement edadealItemLogo;

        @Name("Категория продукта")
        @FindBy(xpath = ".//div[contains(@class, 'edadeal__discount-text-inner')]")
        private HtmlElement edadealItemCategoryText;

        @Name("Скидон")
        @FindBy(xpath = ".//div[@class = 'edadeal__percent']")
        private HtmlElement edadealItemDiscount;

    }

    @Name("Показать все предложения")
    @FindBy(xpath = "//a[contains(@class, 'edadeal__item-all')]")
    public static class AllDeals extends HtmlElement {

        @Name("Иконка Едадила")
        @FindBy(xpath = ".//div[contains(@class, 'edadeal__item-img')]")
        private HtmlElement edadealIcon;

        @Name("Текст \"Показать все предложения\"")
        @FindBy(xpath = ".//div[@class = 'edadeal__item-all__inner']")
        private HtmlElement showAllDealsText;


        @Step("Validate \"Показать все предложения\"")
        public HierarchicalErrorCollector validate(Validator<? extends TouchRuMorda> validator) {

            String url = validator.getCleanvars().getEdadeal().getLocalityURL();

            return collector()
                    .check(shouldSeeElement(this))
                    .check(shouldSeeElementMatchingTo(this, hasAttribute(HREF, equalTo(url))))
                    .check(
                            validateIcon(edadealIcon, validator),
                            validateText(showAllDealsText, validator)
                    );
        }

        @Step("{0}")
        public HierarchicalErrorCollector validateIcon(HtmlElement icon, Validator<? extends TouchRuMorda> validator) {

            UrlMatcher yastaticNetUrlMatcher = urlMatcher()
                    .host("yastatic.net")
                    .path(
                            allOfDetailed(
                                    startsWith("/www/"),
                                    endsWith("/js_touch_exp/blocks/touch/edadeal/edadeal.assets/edadeal-logo.png")
                            ))
                    .build();

            return collector()
                    .check(shouldSeeElement(icon))
                    .check(shouldSeeElementMatchingTo(icon, allOfDetailed(
                            hasAttribute(TITLE, equalTo("Edadeal")),
                            hasAttribute(DATA_IMAGE, yastaticNetUrlMatcher)
                    )));
        }

        @Step("{0}")
        public HierarchicalErrorCollector validateText(HtmlElement text, Validator<? extends TouchRuMorda> validator) {

            return collector()
                    .check(shouldSeeElement(text))
                    .check(shouldSeeElementMatchingTo(text, hasText(
                            equalTo(getTranslationSafely("home", "edadeal", "show_all", validator.getMorda().getLanguage())
                            .replaceAll(" ", " "))
                    )));

        }
    }

}
