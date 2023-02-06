package ru.yandex.autotests.morda.pages.desktop.main.blocks;

import org.openqa.selenium.support.FindBy;
import ru.yandex.autotests.morda.pages.desktop.main.htmlelements.SettingsCheckBox;
import ru.yandex.autotests.morda.pages.desktop.main.htmlelements.SettingsSelect;
import ru.yandex.autotests.morda.pages.desktop.main.htmlelements.WidgetSetupPopup;
import ru.yandex.qatools.allure.annotations.Step;
import ru.yandex.qatools.htmlelements.annotations.Name;

import java.util.List;

import static ch.lambdaj.Lambda.having;
import static ch.lambdaj.Lambda.on;
import static java.util.Arrays.asList;
import static org.hamcrest.Matchers.equalTo;
import static org.junit.Assert.assertThat;
import static ru.yandex.autotests.morda.pages.desktop.main.blocks.RatesSettingsBlock.DecimalPlacesType.*;
import static ru.yandex.autotests.morda.steps.WebElementSteps.withWait;

/**
 * User: asamar
 * Date: 17.01.2016.
 */
@Name("Окно настройки котировок")
public class RatesSettingsBlock extends WidgetSetupPopup {

    @Name("Чек боксы")
    @FindBy(xpath = ".//div[contains(@class, 'multiselect__item')]/span")
    public List<SettingsCheckBox> quotes;

    @Name("Автообновление блока")
    @FindBy(xpath = ".//span[contains(@class, 'checkbox_theme_normal')][.//input[@name='autoreload']]")
    public SettingsCheckBox autoUpdate;

    @Name("Помечать цветом при резком обновлении курса")
    @FindBy(xpath = ".//span[contains(@class, 'checkbox_theme_normal')][.//input[@name='hl']]")
    public SettingsCheckBox markColor;

    @Name("Селектор количества знаков после запятой")
    @FindBy(xpath = ".//span[contains(@class, 'select_size_s')]")
    public SettingsSelect decimalPlacesSelector;

    @Step("Auto update: {0}")
    public RatesSettingsBlock autoUpdate(boolean isAutoUpdate) {
        if (isAutoUpdate) {
            autoUpdate.check();
        } else {
            autoUpdate.uncheck();
        }
        return this;
    }

    @Step("Color mark: {0}")
    public RatesSettingsBlock colorMark(boolean isMark) {
        if (isMark) {
            markColor.check();
        } else {
            markColor.uncheck();
        }
        return this;
    }

    @Step("Select quotes by id: {0}")
    public RatesSettingsBlock selectQuotesById(List<String> ids) {
        quotes.stream()
                .filter(e -> ids.contains(e.input.getWrappedElement().getAttribute("value")))
                .forEach(SettingsCheckBox::check);

        return this;
    }

    public RatesSettingsBlock selectQuotesById(String... ids) {
        return selectQuotesById(asList(ids));
    }

    @Step("Deselect quotes by id: {0}")
    public RatesSettingsBlock deselectQuotesById(List<String> ids) {
        quotes.stream()
                .filter(e -> ids.contains(e.input.getWrappedElement().getAttribute("value")))
                .forEach(SettingsCheckBox::uncheck);

        return this;
    }

    public RatesSettingsBlock deselectQuotesById(String... ids) {
        return deselectQuotesById(asList(ids));
    }

    public RatesSettingsBlock setAutoSign(){
        return setDecimalPlaces(AUTO);
    }

    public RatesSettingsBlock setTwoSign(){
        return setDecimalPlaces(TWO);
    }

    public RatesSettingsBlock setFourSign(){
        return setDecimalPlaces(FOUR);
    }

    @Step("Set decimal places: {0}")
    public RatesSettingsBlock setDecimalPlaces(DecimalPlacesType type) {
        decimalPlacesSelector.selectByValue(type.getValue());

        assertThat(decimalPlacesSelector,
                withWait(having(on(SettingsSelect.class).getSelectedValue(), equalTo(type.getValue()))));

        return this;
    }

    @Step("Should see decimal places: {0}")
    public RatesSettingsBlock shouldSeeDecimalPlaces(DecimalPlacesType type) {

        assertThat(decimalPlacesSelector,
                withWait(having(on(SettingsSelect.class).getSelectedValue(), equalTo(type.getValue()))));

        return this;
    }

    public enum DecimalPlacesType {
        AUTO("auto"),
        TWO("2"),
        FOUR("4");

        private String value;

        DecimalPlacesType(String value) {
            this.value = value;
        }

        public DecimalPlacesType getTopnewsNumeration(String value) {
            for (DecimalPlacesType type : DecimalPlacesType.values()) {
                if (type.value.equals(value)) {
                    return type;
                }
            }

            throw new IllegalArgumentException("Unknown topnews numeration type \"" + value + "\"");
        }

        public String getValue() {
            return value;
        }
    }
}
