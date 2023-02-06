package ru.yandex.autotests.morda.pages.touch.comtr.htmlelements.domik;

import org.openqa.selenium.support.FindBy;
import ru.yandex.autotests.morda.pages.interfaces.validation.Validateable;
import ru.yandex.autotests.morda.pages.interfaces.validation.Validator;
import ru.yandex.autotests.morda.pages.touch.comtr.TouchComTrMorda;
import ru.yandex.autotests.morda.rules.errorcollector.HierarchicalErrorCollector;
import ru.yandex.qatools.allure.annotations.Step;
import ru.yandex.qatools.htmlelements.annotations.Name;
import ru.yandex.qatools.htmlelements.element.HtmlElement;

import java.util.List;
import java.util.function.Function;

import static java.util.Arrays.asList;
import static org.hamcrest.Matchers.containsString;
import static org.hamcrest.Matchers.equalTo;
import static ru.yandex.autotests.morda.rules.errorcollector.HierarchicalErrorCollector.collector;
import static ru.yandex.autotests.morda.steps.CheckSteps.shouldSeeElement;
import static ru.yandex.autotests.morda.steps.CheckSteps.shouldSeeElementMatchingTo;
import static ru.yandex.autotests.morda.utils.matchers.AllOfDetailedMatcher.allOfDetailed;
import static ru.yandex.autotests.mordacommonsteps.matchers.HtmlAttributeMatcher.hasAttribute;
import static ru.yandex.autotests.mordacommonsteps.utils.HtmlAttribute.CLASS;
import static ru.yandex.autotests.mordacommonsteps.utils.HtmlAttribute.TITLE;
import static ru.yandex.qatools.htmlelements.matchers.WrapsElementMatchers.hasText;

/**
 * User: eoff (eoff@yandex-team.ru)
 * Date: 31/03/15
 */
@Name("Блок с социальной регистрацией")
@FindBy(xpath = ".//div[contains(@class, 'social')]")
public class LoginDomikSocial extends HtmlElement implements Validateable<TouchComTrMorda> {


    @Name("Заголовок")
    @FindBy(xpath = ".//div[contains(@class, 'social-title')]")
    private HtmlElement title;

    @Name("Социальные иконки")
    @FindBy(xpath = ".//div[contains(@class, 'social-icon')]")
    private List<HtmlElement> socialIcons;

    @Override
    @Step("Check login domik social block")
    public HierarchicalErrorCollector validate(Validator<? extends TouchComTrMorda> validator) {
        return collector()
                .check(shouldSeeElement(this))
                .check(
                        validateSocialTitle(validator),
                        validateSocialIcons(validator)
                );

    }

    @Step("Check social block title")
    public HierarchicalErrorCollector validateSocialTitle(Validator<? extends TouchComTrMorda> validator) {
        return collector()
                .check(shouldSeeElement(title))
                .check(shouldSeeElementMatchingTo(title, hasText("Sosyal ağlarla giriş yap")));
    }

    @Step("Check social block icons")
    public HierarchicalErrorCollector validateSocialIcons(Validator<? extends TouchComTrMorda> validator) {
        List<Function<HtmlElement,HierarchicalErrorCollector>> iconsCollectors = getIconsCollectors();
        return collector()
                .check(
                        iconsCollectors.get(0).apply(socialIcons.get(0)),
                        iconsCollectors.get(1).apply(socialIcons.get(1)),
                        iconsCollectors.get(2).apply(socialIcons.get(2))
                );
    }

    private List<Function<HtmlElement, HierarchicalErrorCollector>> getIconsCollectors() {
        return asList(
                (icon) -> collector()
                        .check(shouldSeeElement(icon))
                        .check(shouldSeeElementMatchingTo(icon, allOfDetailed(
                                hasAttribute(TITLE, equalTo("Facebook")),
                                hasAttribute(CLASS, containsString("social-icon_type_fb"))
                        ))),
                (icon) -> collector()
                        .check(shouldSeeElement(icon))
                        .check(shouldSeeElementMatchingTo(icon, allOfDetailed(
                                hasAttribute(TITLE, equalTo("Twitter")),
                                hasAttribute(CLASS, containsString("social-icon_type_tw"))
                        ))),
                (icon) -> collector()
                        .check(shouldSeeElement(icon))
                        .check(shouldSeeElementMatchingTo(icon, allOfDetailed(
                                hasAttribute(TITLE, equalTo("Google")),
                                hasAttribute(CLASS, containsString("social-icon_type_gg"))
                        )))
        );
    }

    public HtmlElement getTitle() {
        return title;
    }

    public List<HtmlElement> getSocialIcons() {
        return socialIcons;
    }


}
