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
import static ru.yandex.autotests.morda.pages.desktop.main.blocks.TopnewsSettingsBlock.TopnewsRubricsType.*;
import static ru.yandex.autotests.morda.steps.WebElementSteps.*;

/**
 * User: eoff (eoff@yandex-team.ru)
 * Date: 01/04/15
 */
@Name("Окно настройки новостей")
public class TopnewsSettingsBlock extends WidgetSetupPopup {

    @Name("Автообновление блока")
    @FindBy(xpath = ".//span[contains(@class, 'checkbox_theme_normal')][.//input[@name='autoreload']]")
    public SettingsCheckBox autoUpdate;

    @Name("Показывать нумерацию")
    @FindBy(xpath = ".//span[contains(@class, 'checkbox_theme_normal')][.//input[@name='shownum']]")
    public SettingsCheckBox numeration;

    @Name("Селектор рубрик")
    @FindBy(xpath = ".//span[contains(@class, 'select_theme_normal')][./select[@name='customCatId']]")
    public SettingsSelect rubricSelect;

    @Step("Auto update: {0}")
    public TopnewsSettingsBlock autoUpdate(boolean isAutoUpdate) {
        if (isAutoUpdate) {
            autoUpdate.check();
        } else {
            autoUpdate.uncheck();
        }
        return this;
    }

    @Step("Show numeration: {0}")
    public TopnewsSettingsBlock showNumeration(boolean isShow) {
        if (isShow) {
            numeration.check();
        } else {
            numeration.uncheck();
        }
        return this;
    }


    public TopnewsSettingsBlock sportRubric() {
        return setRubric(SPORT);
    }

    public TopnewsSettingsBlock scienceRubric() {
        return setRubric(SCIENCE);
    }

    @Step("Set rubric: {0}")
    public TopnewsSettingsBlock setRubric(TopnewsRubricsType type) {
        rubricSelect.selectByValue(type.getValue());

        assertThat(rubricSelect,
                withWait(having(on(SettingsSelect.class).getSelectedValue(),
                        equalTo(type.getValue()))));

        return this;
    }

    @Step("Should see numeration: {0}")
    public TopnewsSettingsBlock shouldSeeRubric(TopnewsRubricsType type) {

        assertThat(rubricSelect,
                withWait(having(on(SettingsSelect.class).getSelectedValue(),
                        equalTo(type.getValue()))));

        return this;
    }

    public enum TopnewsRubricsType {
        SPORT("sport"),
        SCIENCE("science");

        private String value;

        TopnewsRubricsType(String value) {
            this.value = value;
        }

        public TopnewsRubricsType getTopnewsNumeration(String value) {
            for (TopnewsRubricsType type : TopnewsRubricsType.values()) {
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
