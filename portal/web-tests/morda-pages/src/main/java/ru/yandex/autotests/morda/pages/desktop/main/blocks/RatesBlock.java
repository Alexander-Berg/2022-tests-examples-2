package ru.yandex.autotests.morda.pages.desktop.main.blocks;

import org.openqa.selenium.support.FindBy;
import ru.yandex.autotests.morda.pages.desktop.main.htmlelements.Widget;
import ru.yandex.autotests.morda.steps.WebElementSteps;
import ru.yandex.qatools.allure.annotations.Step;
import ru.yandex.qatools.htmlelements.annotations.Name;
import ru.yandex.qatools.htmlelements.element.HtmlElement;

import java.util.List;

import static java.util.Arrays.asList;
import static ru.yandex.autotests.morda.steps.WebElementSteps.clickOn;
import static ru.yandex.autotests.morda.steps.WebElementSteps.shouldSee;

/**
 * Created by asamar on 19.01.16.
 */
@Name("Блок котировок в новостях")
@FindBy(xpath = "//div[contains(@class, 'inline-stocks__popup-wrap')]")
public class RatesBlock extends Widget<RatesSettingsBlock> {
    @Name("Шестеренка настройки")
    @FindBy(xpath = ".//a[contains(@class, 'inline-stocks__tune')]")
    public HtmlElement setupIcon;

    @FindBy(xpath = ".//div[contains(@class, 'popup__close')]")
    public HtmlElement popupCloseCross;

    @Name("Котировки")
    @FindBy(xpath = ".//tr[contains(@class, 'inline-stocks__row')]")
    public List<HtmlElement> quotes;

    public RatesSettingsBlock ratesSettingsBlock;

    @Override
    protected RatesSettingsBlock getSetupPopup() {
        return ratesSettingsBlock;
    }

    @Step("Should see elements")
    public void shouldSeeQuotesByValue(List<String> values) {
        quotes.stream()
                .filter(e -> values
                        .contains(e.getWrappedElement()
                                .getAttribute("class")
                                .replace("inline-stocks__row_id_", "")
                        )
                )
                .forEach(WebElementSteps::shouldSee);
    }

    public void shouldSeeQuotesByValue(String... values){
        this.shouldSeeQuotesByValue(asList(values));
    }

    @Step("Open widget settings")
    @Override
    public RatesSettingsBlock setup() {
        shouldSee(setupIcon);
        clickOn(setupIcon);

        return ratesSettingsBlock;
    }
}
