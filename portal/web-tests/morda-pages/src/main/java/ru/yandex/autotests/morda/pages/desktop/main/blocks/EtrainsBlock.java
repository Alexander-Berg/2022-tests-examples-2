package ru.yandex.autotests.morda.pages.desktop.main.blocks;

import org.openqa.selenium.WebDriver;
import org.openqa.selenium.support.FindBy;
import ru.yandex.autotests.morda.pages.desktop.main.DesktopMainMorda;
import ru.yandex.autotests.morda.pages.desktop.main.htmlelements.Widget;
import ru.yandex.autotests.morda.pages.interfaces.validation.Validateable;
import ru.yandex.autotests.morda.pages.interfaces.validation.Validator;
import ru.yandex.autotests.morda.rules.errorcollector.HierarchicalErrorCollector;
import ru.yandex.qatools.allure.annotations.Step;
import ru.yandex.qatools.htmlelements.annotations.Name;
import ru.yandex.qatools.htmlelements.element.HtmlElement;

import java.util.List;

import static ru.yandex.autotests.morda.rules.errorcollector.HierarchicalErrorCollector.collector;
import static ru.yandex.autotests.morda.steps.CheckSteps.shouldSeeElement;
import static ru.yandex.autotests.morda.steps.CheckSteps.shouldSeeElementMatchingTo;
import static ru.yandex.autotests.morda.steps.WebElementSteps.shouldSee;
import static ru.yandex.autotests.utils.morda.language.LanguageManager.getTranslation;
import static ru.yandex.qatools.htmlelements.matchers.WrapsElementMatchers.hasText;

/**
 * User: eoff (eoff@yandex-team.ru)
 * Date: 01/04/15
 */
@Name("Электрички")
@FindBy(xpath = "//div[@class='etrains']")
public class EtrainsBlock extends Widget<EtrainsSettingsBlock> implements Validateable<DesktopMainMorda> {

    @Name("Заголовок")
    @FindBy(xpath = ".//h2[contains(@class, 'etrains__subtitle')]")
    public HtmlElement title;

    @FindBy(xpath = ".//span[contains(@class, 'etrains__track') and not(contains(@class, 'hidden'))]")
    public EtrainsTrack visibleTrack;

    public EtrainsSettingsBlock etrainsSettingsBlock;

    @Override
    public EtrainsSettingsBlock getSetupPopup() {
        return etrainsSettingsBlock;
    }

    @FindBy(xpath = "//iframe[@id='wd-prefs-_etrains-2']")
    public HtmlElement iframe;

    @Step("Switch to etrains iframe")
    public void switchToIFrame(WebDriver driver){
        shouldSee(iframe);
        driver.switchTo().frame(iframe);
    }


    @Step("{0}")
    public static HierarchicalErrorCollector validateTitle(HtmlElement title,
                                                           Validator<? extends DesktopMainMorda> validator) {
        String titleText = getTranslation("home", "etrain", "shortTitle", validator.getMorda().getLanguage());
        return collector()
                .check(shouldSeeElement(title))
                .check(shouldSeeElementMatchingTo(title, hasText(titleText)));
    }


    @Override
    @Step("Check etrains block")
    public HierarchicalErrorCollector validate(Validator<? extends DesktopMainMorda> validator) {
        return collector()
                .check(shouldSeeElement(this));
//                .check(
//                        validateTitle(this.title, validator),


//                );
    }

    @Name("Маршрут электричек")
    public static class EtrainsTrack extends HtmlElement {

        @Name("Направление")
        @FindBy(xpath = ".//a[contains(@class, 'etrains__direction')]")
        public HtmlElement direction;

        @Name("Расписание")
        @FindBy(xpath = ".//li[contains(@class, 'etrains__track-time')]/a")
        public List<HtmlElement> times;

        @Name("Подсказки")
        @FindBy(xpath = ".//div[contains(@class, 'etrains__hints_list')]//div[contains(@class, 'etrains__hint')]")
        public List<HtmlElement> hints;

        @Step("{0}")
        public static HierarchicalErrorCollector validateDirection(HtmlElement direction,
                                                                   Validator<? extends DesktopMainMorda> validator) {

            return collector()
                    .check(shouldSeeElement(direction));
//                    .check(
//                            shouldSeeElementMatchingTo(direction, allOfDetailed(
//                                            hasText(getTranslation(POPULAR, validator.getMorda().getLanguage())),
//                                            hasAttribute(HREF, equalTo(mordaAll.getUrl().toString()))
//                            ))
//                    );
        }

//        @Override
        @Step("Check etrains track")
        public static HierarchicalErrorCollector validateTrack(EtrainsTrack track, Validator<? extends DesktopMainMorda> validator) {
            return collector();
//                    .check(shouldSeeElement(this))
//                    .check(
//                            validateDirection(direction, validator)
//                    );
        }
    }
}
