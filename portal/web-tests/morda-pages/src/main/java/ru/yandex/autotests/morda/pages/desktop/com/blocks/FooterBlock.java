package ru.yandex.autotests.morda.pages.desktop.com.blocks;

import org.openqa.selenium.support.FindBy;
import ru.yandex.autotests.morda.pages.desktop.com.DesktopComMorda;
import ru.yandex.autotests.morda.pages.interfaces.validation.Validateable;
import ru.yandex.autotests.morda.pages.interfaces.validation.Validator;
import ru.yandex.autotests.morda.rules.errorcollector.HierarchicalErrorCollector;
import ru.yandex.qatools.allure.annotations.Step;
import ru.yandex.qatools.htmlelements.annotations.Name;
import ru.yandex.qatools.htmlelements.element.HtmlElement;

import static org.hamcrest.CoreMatchers.equalTo;
import static ru.yandex.autotests.morda.rules.errorcollector.HierarchicalErrorCollector.collector;
import static ru.yandex.autotests.morda.steps.CheckSteps.shouldSeeElement;
import static ru.yandex.autotests.morda.steps.CheckSteps.shouldSeeElementMatchingTo;
import static ru.yandex.autotests.morda.utils.matchers.AllOfDetailedMatcher.allOfDetailed;
import static ru.yandex.autotests.mordacommonsteps.matchers.HtmlAttributeMatcher.hasAttribute;
import static ru.yandex.autotests.mordacommonsteps.utils.HtmlAttribute.HREF;
import static ru.yandex.autotests.utils.morda.language.Dictionary.Home.SpokYes.FOOT_API;
import static ru.yandex.autotests.utils.morda.language.Dictionary.Home.SpokYes.FOOT_COMPANY;
import static ru.yandex.autotests.utils.morda.language.Dictionary.Home.SpokYes.FOOT_COPYRIGHT;
import static ru.yandex.autotests.utils.morda.language.Dictionary.Home.SpokYes.FOOT_FEEDBACK;
import static ru.yandex.autotests.utils.morda.language.Dictionary.Home.SpokYes.FOOT_PRIVACY;
import static ru.yandex.autotests.utils.morda.language.Dictionary.Home.SpokYes.FOOT_TERMS;
import static ru.yandex.autotests.utils.morda.language.LanguageManager.getTranslation;
import static ru.yandex.qatools.htmlelements.matchers.WrapsElementMatchers.hasText;

/**
 * User: asamar
 * Date: 28.09.2015.
 */
@Name("Футер")
@FindBy(xpath = "//div[contains(@class, 'b-line__mfooter')]")
public class FooterBlock extends HtmlElement implements Validateable<DesktopComMorda> {

    @Name("Ссылка 'Technologies'")
    @FindBy(xpath = "./a[1]")
    public HtmlElement technologiesLink;

    @Name("Ссылка 'About Yandex'")
    @FindBy(xpath = "./a[2]")
    public HtmlElement aboutLink;

    @Name("Ссылка 'Terms of Service'")
    @FindBy(xpath = "./a[3]")
    public HtmlElement termsOfServiceLink;

    @Name("Ссылка 'Privacy Policy'")
    @FindBy(xpath = "./a[4]")
    public HtmlElement privacyLink;

    @Name("Ссылка 'Contact us'")
    @FindBy(xpath = "./a[5]")
    public HtmlElement contactUs;

    @Name("Ссылка 'Copyright Notice'")
    @FindBy(xpath = "./a[6]")
    public HtmlElement copyrightLink;

    @Name("Копирайт")
    @FindBy(xpath = ".//span")
    public HtmlElement copyrightIcon;


    @Override
    @Step("Check footer")
    public HierarchicalErrorCollector validate(Validator<? extends DesktopComMorda> validator) {
        return collector()
                .check(shouldSeeElement(this))
                .check(
                        validateTechnologies(technologiesLink, validator),
                        validateAbout(aboutLink, validator),
                        validateTermsOfService(termsOfServiceLink, validator),
                        validatePrivacyPolicy(privacyLink, validator),
                        validateFeedback(contactUs, validator),
                        validateCopyRight(copyrightLink, validator),
                        validateCopyrightIcon(copyrightIcon, validator)
                );

    }

    @Step("{0}")
    public static HierarchicalErrorCollector validateTechnologies(HtmlElement technologiesLink,
                                                                  Validator<? extends DesktopComMorda> validator) {
        return collector()
                .check(shouldSeeElement(technologiesLink))
                .check(
                        shouldSeeElementMatchingTo(technologiesLink,
                                allOfDetailed(
                                        hasText(getTranslation(FOOT_API, validator.getMorda().getLanguage())),
                                        hasAttribute(HREF, equalTo("https://tech.yandex.com/"))))
                );
    }

    @Step("{0}")
    public static HierarchicalErrorCollector validateAbout(HtmlElement aboutLink,
                                                           Validator<? extends DesktopComMorda> validator) {
        return collector()
                .check(shouldSeeElement(aboutLink))
                .check(
                        shouldSeeElementMatchingTo(aboutLink,
                                allOfDetailed(
                                        hasText(getTranslation(FOOT_COMPANY, validator.getMorda().getLanguage())),
                                        hasAttribute(HREF, equalTo("https://yandex.com/company/"))))
                );
    }

    @Step("{0}")
    public static HierarchicalErrorCollector validateTermsOfService(HtmlElement termsOfServiceLink,
                                                                    Validator<? extends DesktopComMorda> validator) {
        return collector()
                .check(shouldSeeElement(termsOfServiceLink))
                .check(
                        shouldSeeElementMatchingTo(termsOfServiceLink,
                                allOfDetailed(
                                        hasText(getTranslation(FOOT_TERMS, validator.getMorda().getLanguage())),
                                        hasAttribute(HREF, equalTo("https://yandex.com/legal/termsofservice/"))))
                );
    }

    @Step("{0}")
    public static HierarchicalErrorCollector validatePrivacyPolicy(HtmlElement privacyLink,
                                                                   Validator<? extends DesktopComMorda> validator) {
        return collector()
                .check(shouldSeeElement(privacyLink))
                .check(
                        shouldSeeElementMatchingTo(privacyLink, allOfDetailed(
                                hasText(getTranslation(FOOT_PRIVACY, validator.getMorda().getLanguage())),
                                hasAttribute(HREF, equalTo("https://yandex.com/legal/privacy/"))))
                );
    }

    @Step("{0}")
    public static HierarchicalErrorCollector validateFeedback(HtmlElement contactUs,
                                                              Validator<? extends DesktopComMorda> validator) {
        return collector()
                .check(shouldSeeElement(contactUs))
                .check(
                        shouldSeeElementMatchingTo(contactUs,
                                allOfDetailed(
                                        hasText(getTranslation(FOOT_FEEDBACK, validator.getMorda().getLanguage())),
                                        hasAttribute(HREF, equalTo("https://feedback2.yandex.com/default/"))))
                );
    }

    @Step("{0}")
    public static HierarchicalErrorCollector validateCopyRight(HtmlElement copyrightLink,
                                                               Validator<? extends DesktopComMorda> validator) {
        return collector()
                .check(shouldSeeElement(copyrightLink))
                .check(
                        shouldSeeElementMatchingTo(copyrightLink,
                                allOfDetailed(
                                        hasText(getTranslation(FOOT_COPYRIGHT, validator.getMorda().getLanguage())),
                                        hasAttribute(HREF, equalTo("https://feedback2.yandex.com/copyright-complaint/"))))
                );
    }

    @Step("{0}")
    public static HierarchicalErrorCollector validateCopyrightIcon(HtmlElement copyrightIcon,
                                                                   Validator<? extends DesktopComMorda> validator) {
        return collector()
                .check(shouldSeeElement(copyrightIcon))
                .check(shouldSeeElementMatchingTo(copyrightIcon, hasText("© Yandex")));
    }
}
