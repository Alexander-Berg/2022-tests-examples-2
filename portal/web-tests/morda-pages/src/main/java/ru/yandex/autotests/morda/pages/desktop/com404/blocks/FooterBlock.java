package ru.yandex.autotests.morda.pages.desktop.com404.blocks;

import org.openqa.selenium.support.FindBy;
import ru.yandex.autotests.morda.pages.desktop.com404.Com404Morda;
import ru.yandex.autotests.morda.pages.interfaces.validation.Validateable;
import ru.yandex.autotests.morda.pages.interfaces.validation.Validator;
import ru.yandex.autotests.morda.rules.errorcollector.HierarchicalErrorCollector;
import ru.yandex.qatools.allure.annotations.Step;
import ru.yandex.qatools.htmlelements.annotations.Name;
import ru.yandex.qatools.htmlelements.element.HtmlElement;

import static org.hamcrest.Matchers.equalTo;
import static ru.yandex.autotests.morda.rules.errorcollector.HierarchicalErrorCollector.collector;
import static ru.yandex.autotests.morda.steps.CheckSteps.shouldSeeElement;
import static ru.yandex.autotests.morda.steps.CheckSteps.shouldSeeElementMatchingTo;
import static ru.yandex.autotests.mordacommonsteps.matchers.HtmlAttributeMatcher.hasAttribute;
import static ru.yandex.autotests.mordacommonsteps.utils.HtmlAttribute.HREF;
import static ru.yandex.qatools.htmlelements.matchers.WrapsElementMatchers.hasText;


/**
 * User: asamar
 * Date: 06.10.2015.
 */
@Name("Футер")
@FindBy(xpath = "//div[contains(@class, 'foot')]")
public class FooterBlock extends HtmlElement implements Validateable<Com404Morda> {

    @Name("Ссылка 'About'")
    @FindBy(xpath = ".//a[1]")
    private HtmlElement aboutLink;

    @Name("Ссылка 'Yandex'")
    @FindBy(xpath = ".//a[2]")
    private HtmlElement yandexLink;


    @Override
    @Step("Validate footer")
    public HierarchicalErrorCollector validate(Validator<? extends Com404Morda> validator) {
        return collector()
                .check(shouldSeeElement(this))
                .check(shouldSeeElementMatchingTo(this,
                        hasText("About© Yandex")))
//                        hasText(getTranslation(
//                                "home",
//                                "error404_spok_yes",
//                                "about",
//                                validator.getMorda().getLanguage()) + "© Yandex")))
                .check(
                        validateAbout(aboutLink, validator),
                        validateYandex(yandexLink, validator)
                );
    }

    @Step("{0}")
    private static HierarchicalErrorCollector validateAbout(HtmlElement aboutLink,
                                                            Validator<? extends Com404Morda> validator){
        return collector()
                .check(shouldSeeElement(aboutLink))
                .check(shouldSeeElementMatchingTo(aboutLink,
                        hasAttribute(HREF, equalTo("https://yandex.com/company/"))));
    }

    @Step("{0}")
    private static HierarchicalErrorCollector validateYandex(HtmlElement yandexLink,
                                                             Validator<? extends Com404Morda> validator){
        return collector()
                .check(shouldSeeElement(yandexLink))
                .check(shouldSeeElementMatchingTo(yandexLink,
                        hasAttribute(HREF, equalTo("https://yandex.com/"))));
    }
}
