package ru.yandex.autotests.morda.pages.touch.comtr.blocks;

import org.openqa.selenium.support.FindBy;
import ru.yandex.autotests.morda.pages.interfaces.blocks.BlockWithContactLink;
import ru.yandex.autotests.morda.pages.interfaces.blocks.BlockWithCopyright;
import ru.yandex.autotests.morda.pages.interfaces.blocks.BlockWithSettingsLink;
import ru.yandex.autotests.morda.pages.interfaces.validation.Validateable;
import ru.yandex.autotests.morda.pages.interfaces.validation.Validator;
import ru.yandex.autotests.morda.pages.touch.comtr.TouchComTrMorda;
import ru.yandex.autotests.morda.rules.errorcollector.HierarchicalErrorCollector;
import ru.yandex.autotests.utils.morda.language.Dictionary;
import ru.yandex.qatools.allure.annotations.Step;
import ru.yandex.qatools.htmlelements.annotations.Name;
import ru.yandex.qatools.htmlelements.element.HtmlElement;

import static org.hamcrest.Matchers.equalTo;
import static ru.yandex.autotests.morda.rules.errorcollector.HierarchicalErrorCollector.collector;
import static ru.yandex.autotests.morda.steps.CheckSteps.shouldSeeElement;
import static ru.yandex.autotests.morda.steps.CheckSteps.shouldSeeElementMatchingTo;
import static ru.yandex.autotests.morda.utils.matchers.AllOfDetailedMatcher.allOfDetailed;
import static ru.yandex.autotests.mordacommonsteps.matchers.HtmlAttributeMatcher.hasAttribute;
import static ru.yandex.autotests.mordacommonsteps.utils.HtmlAttribute.HREF;
import static ru.yandex.autotests.utils.morda.language.Language.TR;
import static ru.yandex.autotests.utils.morda.language.LanguageManager.getTranslation;
import static ru.yandex.qatools.htmlelements.matchers.WrapsElementMatchers.hasText;

/**
 * User: eoff (eoff@yandex-team.ru)
 * Date: 01/04/15
 */
@Name("Футер")
@FindBy(xpath = "//div[contains(@class, 'content__footer')]")
public class FooterBlock extends HtmlElement implements BlockWithContactLink, BlockWithSettingsLink,
        BlockWithCopyright, Validateable<TouchComTrMorda> {

    @Name("Ссылка \"Обратная связь\"")
    @FindBy(xpath = ".//div[contains(@class, 'mfooter')]//a[1]")
    private HtmlElement feedbackLink;

    @Name("Ссылка \"Настройки\"")
    @FindBy(xpath = ".//div[contains(@class, 'mfooter')]//a[2]")
    private HtmlElement settingsLink;

    @Name("Копирайт")
    @FindBy(xpath = ".//span[contains(@class, 'mfooter__yandex')]")
    private HtmlElement copyright;

    @Override
    public HtmlElement getFeedbackLink() {
        return feedbackLink;
    }

    @Override
    public HtmlElement getCopyright() {
        return copyright;
    }

    @Override
    public HtmlElement getSettingsLink() {
        return settingsLink;
    }

    @Step("Check feedback link")
    public HierarchicalErrorCollector validateFeedbackLink(Validator<? extends TouchComTrMorda> validator) {
        return collector()
                .check(shouldSeeElement(feedbackLink))
                .check(shouldSeeElementMatchingTo(feedbackLink, allOfDetailed(
                        hasText(equalTo(getTranslation(Dictionary.Home.Foot.FEEDBACK, TR))),
                        hasAttribute(HREF, equalTo(validator.getMorda().getScheme() + "://m.contact.yandex.com.tr/mainpage/"))
                )));
    }

    @Step("Check settings link")
    public HierarchicalErrorCollector validateSettingsLink(Validator<? extends TouchComTrMorda> validator) {
        return collector()
                .check(shouldSeeElement(settingsLink))
                .check(shouldSeeElementMatchingTo(settingsLink, allOfDetailed(
                        hasText(equalTo(getTranslation(Dictionary.Home.Mobile.FOOT_TUNE, TR))),
                        hasAttribute(HREF, equalTo(validator.getCleanvars().getSetupPages().getAll().replace("&amp;", "&")))
                )));
    }

    @Step("Check copyright")
    public HierarchicalErrorCollector validateCopyright(Validator<? extends TouchComTrMorda> validator) {
        return collector()
                .check(shouldSeeElement(copyright))
                .check(shouldSeeElementMatchingTo(copyright, hasText("© Yandex")));
    }

    @Override
    public HierarchicalErrorCollector validate(Validator<? extends TouchComTrMorda> validator) {
        return collector()
                .check(validateFeedbackLink(validator),
                        validateSettingsLink(validator),
                        validateCopyright(validator));
    }
}
