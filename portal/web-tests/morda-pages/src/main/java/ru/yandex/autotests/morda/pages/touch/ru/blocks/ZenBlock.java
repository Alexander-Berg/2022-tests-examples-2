package ru.yandex.autotests.morda.pages.touch.ru.blocks;

import org.openqa.selenium.support.FindBy;
import ru.yandex.autotests.morda.pages.interfaces.validation.Validateable;
import ru.yandex.autotests.morda.pages.interfaces.validation.Validator;
import ru.yandex.autotests.morda.pages.touch.ru.TouchRuMorda;
import ru.yandex.autotests.morda.rules.errorcollector.HierarchicalErrorCollector;
import ru.yandex.autotests.morda.utils.matchers.UrlMatcher;
import ru.yandex.qatools.allure.annotations.Step;
import ru.yandex.qatools.htmlelements.annotations.Name;
import ru.yandex.qatools.htmlelements.element.HtmlElement;

import java.util.List;

import static org.hamcrest.Matchers.endsWith;
import static org.hamcrest.Matchers.hasSize;
import static org.hamcrest.Matchers.isEmptyOrNullString;
import static org.hamcrest.Matchers.not;
import static org.hamcrest.Matchers.startsWith;
import static ru.yandex.autotests.morda.rules.errorcollector.HierarchicalErrorCollector.collector;
import static ru.yandex.autotests.morda.steps.CheckSteps.shouldSeeElement;
import static ru.yandex.autotests.morda.steps.CheckSteps.shouldSeeElementMatchingTo;
import static ru.yandex.autotests.morda.utils.matchers.AllOfDetailedMatcher.allOfDetailed;
import static ru.yandex.autotests.morda.utils.matchers.UrlMatcher.ParamMatcher.urlParam;
import static ru.yandex.autotests.morda.utils.matchers.UrlMatcher.urlMatcher;
import static ru.yandex.autotests.mordacommonsteps.matchers.HtmlAttributeMatcher.hasAttribute;
import static ru.yandex.autotests.mordacommonsteps.utils.HtmlAttribute.DATA_IMAGE;
import static ru.yandex.autotests.mordacommonsteps.utils.HtmlAttribute.HREF;
import static ru.yandex.autotests.utils.morda.language.LanguageManager.getTranslation;
import static ru.yandex.autotests.utils.morda.language.LanguageManager.getTranslationSafely;
import static ru.yandex.qatools.htmlelements.matchers.WrapsElementMatchers.hasText;

/**
 * @author Ivan Nikolaev <ivannik@yandex-team.ru>
 */
@Name("Блок Дзена")
@FindBy(xpath = "//div[contains(@class, 'zen ')]")
public class ZenBlock extends HtmlElement implements Validateable<TouchRuMorda> {

    @Name("Заголовок")
    @FindBy(xpath = ".//a[@class = 'zen__title block__title-text']")
    private HtmlElement title;

    @Name("Список карточек")
    @FindBy(xpath = ".//a[@class = 'zen__item-link ']")
    private List<ZenCard> zenCards;

    @Name("Еще больше статей на каждый день")
    @FindBy(xpath = ".//a[contains(@class, 'zen__more-link')]")
    private ZenMoreCard more;

    private static UrlMatcher baseUrlMatcher = urlMatcher()
            .scheme("https")
            .host("zen.yandex.ru")
            .urlParams(
                    urlParam("api_name", "web"),
                    urlParam("clid", "100"),
                    urlParam("country_code", "ru")
            )
            .build();

    @Step("Check title")
    public static HierarchicalErrorCollector validateTitle(HtmlElement title, Validator<? extends TouchRuMorda> validator) {
        return collector()
                .check(shouldSeeElement(title))
                .check(
                        shouldSeeElementMatchingTo(title, allOfDetailed(
                                        hasText(getTranslation("home", "mobile", "zen.title", validator.getMorda().getLanguage())),
                                        hasAttribute(HREF, baseUrlMatcher)
                                )
                        )
                );
    }

    @Step("{0}")
    public static HierarchicalErrorCollector validateItems(List<ZenCard> zenCards,
                                                           Validator<? extends TouchRuMorda> validator) {
        HierarchicalErrorCollector collector = collector();

        for (int i = 0; i != zenCards.size(); i++) {
            ZenCard item = zenCards.get(i);

            collector
                    .check(validateItem(item, validator));
        }

        int count = 8;

        HierarchicalErrorCollector zenCountCollector = collector().check(
                shouldSeeElementMatchingTo(zenCards, hasSize(count)));

        collector.check(zenCountCollector);

        return collector;
    }

    @Step("{0}")
    public static HierarchicalErrorCollector validateItem(ZenCard item, Validator<? extends TouchRuMorda> validator) {
        return collector()
                .check(shouldSeeElement(item))
                .check(shouldSeeElementMatchingTo(item, hasAttribute(HREF, startsWith("https://zen.yandex.ru/"))))
                .check(
                        collector()
                                .check(shouldSeeElement(item.background))
                                .check(shouldSeeElementMatchingTo(item.background,
                                        hasAttribute(DATA_IMAGE, startsWith("https://avatars.mds.yandex.net/get-zen_doc/"))
                                )),

                        collector()
                                .check(shouldSeeElement(item.domain)),
//                                .check(shouldSeeElementMatchingTo(item.domain,
//                                        hasText(not(isEmptyOrNullString()))
//                                )),

                        collector()
                                .check(shouldSeeElement(item.text))
                                .check(shouldSeeElementMatchingTo(item.text,
                                        hasText(not(isEmptyOrNullString()))
                                ))
                );
    }

    @Step("Check more card")
    public static HierarchicalErrorCollector validateMoreCard(ZenMoreCard zenMoreCard, Validator<? extends TouchRuMorda> validator) {
        UrlMatcher yastaticNetUrlMatcher = urlMatcher()
                .host("yastatic.net")
                .path(
                        allOfDetailed(
                                startsWith("/www/"),
                                endsWith("/js_touch_exp/blocks/touch/zen/zen.assets/zen-logo.svg")
                        ))
                .build();

        return collector()
                .check(shouldSeeElement(zenMoreCard))
                .check(shouldSeeElementMatchingTo(zenMoreCard, hasAttribute(HREF, baseUrlMatcher)))
                .check(
                        collector()
                                .check(shouldSeeElement(zenMoreCard.background))
                                .check(shouldSeeElementMatchingTo(zenMoreCard.background,
                                        hasAttribute(DATA_IMAGE, yastaticNetUrlMatcher)
                                )),
                        collector()
                                .check(shouldSeeElement(zenMoreCard.text))
                                .check(shouldSeeElementMatchingTo(zenMoreCard.text,
                                        hasText(getTranslationSafely("home", "mobile", "zen.more",
                                                validator.getMorda().getLanguage()).replace("&nbsp;", " "))
                                ))
                );
    }

    @Override
    @Step("Check zen")
    public HierarchicalErrorCollector validate(Validator<? extends TouchRuMorda> validator) {
        return collector()
                .check(shouldSeeElement(this))
                .check(
                        validateTitle(this.title, validator),
                        validateItems(this.zenCards, validator),
                        validateMoreCard(this.more, validator)
                );
    }

    public static class ZenCard extends HtmlElement {
        @Name("Домен")
        @FindBy(xpath = ".//span[@class='zen__item-domain']")
        private HtmlElement domain;

        @Name("Фон")
        @FindBy(xpath = ".//span[contains(@class, 'zen__item-image')]")
        private HtmlElement background;

        @Name("Текст карточки")
        @FindBy(xpath = ".//span[@class = 'zen__item-title']")
        private HtmlElement text;

    }

    public static class ZenMoreCard extends HtmlElement {
        @Name("Лого")
        @FindBy(xpath = ".//span[contains(@class, 'zen__more-logo')]")
        private HtmlElement background;

        @Name("Текст карточки")
        @FindBy(xpath = ".//span[@class = 'zen__more-title']")
        private HtmlElement text;
    }

}
