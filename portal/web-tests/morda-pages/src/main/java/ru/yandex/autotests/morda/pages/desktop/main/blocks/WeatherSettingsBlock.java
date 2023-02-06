package ru.yandex.autotests.morda.pages.desktop.main.blocks;

import org.hamcrest.MatcherAssert;
import org.openqa.selenium.support.FindBy;
import ru.yandex.autotests.morda.pages.desktop.main.htmlelements.SettingsCheckBox;
import ru.yandex.autotests.morda.pages.desktop.main.htmlelements.WidgetSetupPopup;
import ru.yandex.autotests.mordacommonsteps.utils.TextInput;
import ru.yandex.autotests.utils.morda.region.Region;
import ru.yandex.qatools.allure.annotations.Step;
import ru.yandex.qatools.htmlelements.annotations.Name;
import ru.yandex.qatools.htmlelements.element.HtmlElement;

import java.util.List;

import static org.hamcrest.CoreMatchers.equalTo;
import static org.hamcrest.text.IsEmptyString.isEmptyOrNullString;
import static ru.yandex.autotests.morda.steps.WebElementSteps.clickOn;
import static ru.yandex.autotests.mordacommonsteps.matchers.WithWaitForMatcher.withWaitFor;
import static ru.yandex.qatools.htmlelements.matchers.WebElementMatchers.hasText;

/**
 * User: eoff (eoff@yandex-team.ru)
 * Date: 01/04/15
 */
@Name("Окно настройки Погоды")
public class WeatherSettingsBlock extends WidgetSetupPopup {

    @Name("Регион")
    @FindBy(xpath = ".//span[@class='input__box']//input")
    public TextInput regionInput;

    @Name("Саджест регионов")
    @FindBy(xpath = ".//div[contains(@class, 'popup_visibility_visible')]//li")
    public List<HtmlElement> regionSuggestItems;

    @Name("Автообновление блока")
    @FindBy(xpath = "//span[contains(@class, 'checkbox_theme_normal')][.//input[@name='autoreload']]")
    public SettingsCheckBox autoUpdate;

    @Step("Set region: {0}")
    public WeatherSettingsBlock region(Region region) {
        regionInput.clear();
        MatcherAssert.assertThat("Не дождались отчистки поля ввода", regionInput,
                withWaitFor(hasText(isEmptyOrNullString())));

        regionInput.sendKeys(region.toString());
        MatcherAssert.assertThat("Не дождались текста " + region.toString() + " в поле ввода", regionInput,
                withWaitFor(hasText(equalTo(region.toString()))));

        clickOn(regionSuggestItems.get(0));

        return this;
    }

    @Step("Auto update: {0}")
    public WeatherSettingsBlock autoUpdate(boolean isAutoUpdate) {
        if (isAutoUpdate) {
            autoUpdate.check();
        } else {
            autoUpdate.uncheck();
        }
        return this;
    }

}
