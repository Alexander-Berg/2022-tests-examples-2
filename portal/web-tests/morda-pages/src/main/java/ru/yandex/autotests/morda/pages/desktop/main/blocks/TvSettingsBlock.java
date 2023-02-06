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
import static ru.yandex.autotests.morda.pages.desktop.main.blocks.TvSettingsBlock.ChannelsNumberType.*;
import static ru.yandex.autotests.morda.steps.WebElementSteps.withWait;

/**
 * User: eoff (eoff@yandex-team.ru)
 * Date: 01/04/15
 */
@Name("Окно настройки ТВ")
public class TvSettingsBlock extends WidgetSetupPopup {

    @Name("Список каналов")
    @FindBy(xpath = ".//div[contains(@class, 'multiselect')]/span")
    public List<SettingsCheckBox> channels;

    @Name("Группировка по каналам")
    @FindBy(xpath = ".//span[contains(@class, 'checkbox_theme_normal')][.//input[@name='grouping']]")
    public SettingsCheckBox groupByChannels;

    @Name("Переключать в вечерний режим")
    @FindBy(xpath = ".//span[contains(@class, 'checkbox_theme_normal')][.//input[@name='noannounces']]")
    public SettingsCheckBox eveningMode;

    @Name("Автообновление блока")
    @FindBy(xpath = ".//span[contains(@class, 'checkbox_theme_normal')][.//input[@name='autoreload']]")
    public SettingsCheckBox autoUpdate;

    @Name("Селектор количества передач")
    @FindBy(xpath = ".//span[contains(@class, 'select_theme_normal ')]")
    public SettingsSelect channelsNumberSelect;

    @Step("Group by channels: {0}")
    public TvSettingsBlock groupByChannel(boolean isGroupByChannels) {
        if (isGroupByChannels) {
            groupByChannels.check();
        } else {
            groupByChannels.uncheck();
        }
        return this;
    }

    @Step("Evening mode: {0}")
    public TvSettingsBlock eveningMode(boolean isEveningMode) {
        if (isEveningMode) {
            eveningMode.check();
        } else {
            eveningMode.uncheck();
        }
        return this;
    }

    @Step("Auto update: {0}")
    public TvSettingsBlock autoUpdate(boolean isAutoUpdate) {
        if (isAutoUpdate) {
            autoUpdate.check();
        } else {
            autoUpdate.uncheck();
        }
        return this;
    }

    @Step("Select channels by id: {0}")
    public TvSettingsBlock selectChannelsById(List<String> ids) {
        channels.stream()
                .filter(e -> ids.contains(e.input.getWrappedElement().getAttribute("value")))
                .forEach(SettingsCheckBox::check);

        return this;
    }

    public TvSettingsBlock selectChannelsById(String... ids) {
        return selectChannelsById(asList(ids));
    }

    @Step("Select channels by name: {0}")
    public TvSettingsBlock selectChannelsByName(List<String> names) {
        channels.stream()
                .filter(e -> names.contains(e.getText()))
                .forEach(SettingsCheckBox::check);

        return this;
    }

    public TvSettingsBlock selectChannelByName(String... names) {
        return selectChannelsByName(asList(names));
    }

    @Step("Deselect channels by id: {0}")
    public TvSettingsBlock deselectChannelsById(List<String> ids) {
        channels.stream()
                .filter(e -> ids.contains(e.input.getWrappedElement().getAttribute("value")))
                .forEach(SettingsCheckBox::uncheck);

        return this;
    }

    public TvSettingsBlock deselectChannelsById(String... ids) {
        return deselectChannelsById(asList(ids));
    }

    @Step("Deselect channels by name: {0}")
    public TvSettingsBlock deselectChannelsByName(List<String> names) {
        channels.stream()
                .filter(e -> names.contains(e.getText()))
                .forEach(SettingsCheckBox::uncheck);

        return this;
    }

    public TvSettingsBlock deselectChannelByName(String... names) {
        return deselectChannelsByName(asList(names));
    }

    public SettingsCheckBox getChannelById(String id){
     return channels.stream()
             .filter(e -> id.equals(e.input.getWrappedElement().getAttribute("value")))
             .findFirst()
             .get();
    }

    public TvSettingsBlock sixChannels() {
        return setChannelsNumber(SIX);
    }

    public TvSettingsBlock sevenChannels() {
        return setChannelsNumber(SEVEN);
    }

    public TvSettingsBlock tenChannels() {
        return setChannelsNumber(TEN);
    }

    @Step("Set number of channels: {0}")
    public TvSettingsBlock setChannelsNumber(ChannelsNumberType type) {
        channelsNumberSelect.selectByValue(type.getValue());

        assertThat(channelsNumberSelect, withWait(having(on(SettingsSelect.class).getSelectedValue(), equalTo(type.getValue()))));

        return this;
    }

    @Step("Should see number of channels: {0}")
    public TvSettingsBlock shouldSeeNumeration(ChannelsNumberType type) {

        assertThat(channelsNumberSelect, withWait(having(on(SettingsSelect.class).getSelectedValue(), equalTo(type.getValue()))));

        return this;
    }

    public enum ChannelsNumberType {
        SIX("6"),
        SEVEN("7"),
        TEN("10");

        private String value;

        ChannelsNumberType(String value) {
            this.value = value;
        }

        public ChannelsNumberType getChannelsNumber(String value) {
            for (ChannelsNumberType type : ChannelsNumberType.values()) {
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
