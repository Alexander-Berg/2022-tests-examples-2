package ru.yandex.autotests.morda.pages.desktop.main.blocks;

import org.openqa.selenium.support.FindBy;
import ru.yandex.autotests.morda.pages.desktop.main.htmlelements.SettingsCheckBox;
import ru.yandex.autotests.morda.pages.desktop.main.htmlelements.SettingsSelect;
import ru.yandex.autotests.morda.pages.desktop.main.htmlelements.WidgetSetupPopup;
import ru.yandex.qatools.allure.annotations.Step;
import ru.yandex.qatools.htmlelements.annotations.Name;

import static ch.lambdaj.Lambda.having;
import static ch.lambdaj.Lambda.on;
import static org.hamcrest.Matchers.equalTo;
import static org.junit.Assert.assertThat;
import static ru.yandex.autotests.morda.pages.desktop.main.blocks.RssSettingsBlock.ViewType.*;
import static ru.yandex.autotests.morda.pages.desktop.main.blocks.RssSettingsBlock.ViewType.STANDART;
import static ru.yandex.autotests.morda.pages.desktop.main.blocks.RssSettingsBlock.WidgetHeqght.*;
import static ru.yandex.autotests.morda.steps.WebElementSteps.withWait;

/**
 * User: asamar
 * Date: 29.12.2015.
 */
public class RssSettingsBlock extends WidgetSetupPopup {

    @Name("Показывать только заголовки")
    @FindBy(xpath = ".//span[contains(@class, 'checkbox_theme_normal')][.//input[@name='no-text']]")
    public SettingsCheckBox showTitleOnlyCheckBox;

    @Name("Селектор Внешнего вида")
    @FindBy(xpath = ".//span[contains(@class, 'select_theme_normal')][./select[@name='type']]")
    public SettingsSelect appearanceSelector;

    @Name("Селектор Высоты виджета")
    @FindBy(xpath = ".//span[contains(@class, 'select_theme_normal')][./select[@name='wht']]")
    public SettingsSelect heightSelector;

    @Step("Title only: {0}")
    public RssSettingsBlock showTitleOnly(boolean isTitleOnly) {
        if (isTitleOnly) {
            showTitleOnlyCheckBox.check();
        } else {
            showTitleOnlyCheckBox.uncheck();
        }

        return this;
    }

    public RssSettingsBlock setStandartView() {
        return setView(STANDART);
    }

    public RssSettingsBlock setViewWithPhoto() {
        return setView(STANDART_WITH_PHOTO);
    }

    public RssSettingsBlock setJournalView() {
        return setView(JOURNAL);
    }

    public RssSettingsBlock setRandomTextView() {
        return setView(RANDOM_TEXT);
    }

    @Step("Set view: {0}")
    public RssSettingsBlock setView(ViewType view) {
        appearanceSelector.selectByValue(view.getValue());

        assertThat(appearanceSelector, withWait(having(on(SettingsSelect.class).getSelectedValue(), equalTo(view.getValue()))));

        return this;
    }

    public RssSettingsBlock setAutoHeight() {
        return setHeight(AUTO);
    }

    public RssSettingsBlock setStandartHeight() {
        return setHeight(WidgetHeqght.STANDART);
    }

    public RssSettingsBlock setCompactHeight() {
        return setHeight(COMPACT);
    }

    public RssSettingsBlock setBigHeight() {
        return setHeight(BIG);
    }

    @Step("Set height: {0}")
    public RssSettingsBlock setHeight(WidgetHeqght height) {
        heightSelector.selectByValue(height.getValue());

        assertThat(heightSelector, withWait(having(on(SettingsSelect.class).getSelectedValue(), equalTo(height.getValue()))));

        return this;
    }

    @Step("Should see height: {0}")
    public RssSettingsBlock shouldHaveHeight(WidgetHeqght widgetHeqght) {
        assertThat(heightSelector, withWait(having(on(SettingsSelect.class).getSelectedValue(),
                        equalTo(widgetHeqght.getValue())))
        );

        return this;
    }

    @Step("Should see height: {0}")
    public RssSettingsBlock shouldHaveView(ViewType viewType) {
        assertThat(appearanceSelector, withWait(having(on(SettingsSelect.class).getSelectedValue(),
                        equalTo(viewType.getValue())))
        );

        return this;
    }

    public enum ViewType {
        STANDART("3"),
        STANDART_WITH_PHOTO("4"),
        JOURNAL("2"),
        RANDOM_TEXT("5");

        private String value;

        ViewType(String value) {
            this.value = value;
        }

        public ViewType getLentaView(String value) {
            for (ViewType type : ViewType.values()) {
                if (type.value.equals(value)) {
                    return type;
                }
            }

            throw new IllegalArgumentException("Unknown lenta view type \"" + value + "\"");
        }

        public String getValue() {
            return value;
        }
    }


    public enum WidgetHeqght {
        AUTO("0"),
        STANDART("1"),
        COMPACT("2"),
        BIG("3");

        private String value;

        WidgetHeqght(String value) {
            this.value = value;
        }

        public WidgetHeqght getLentaView(String value) {
            for (WidgetHeqght type : WidgetHeqght.values()) {
                if (type.value.equals(value)) {
                    return type;
                }
            }

            throw new IllegalArgumentException("Unknown widget height type \"" + value + "\"");
        }

        public String getValue() {
            return value;
        }
    }
}
