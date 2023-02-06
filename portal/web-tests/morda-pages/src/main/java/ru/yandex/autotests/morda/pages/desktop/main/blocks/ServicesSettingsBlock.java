package ru.yandex.autotests.morda.pages.desktop.main.blocks;

import org.openqa.selenium.support.FindBy;
import ru.yandex.autotests.morda.pages.desktop.main.htmlelements.SettingsCheckBox;
import ru.yandex.autotests.morda.pages.desktop.main.htmlelements.WidgetSetupPopup;
import ru.yandex.qatools.allure.annotations.Step;
import ru.yandex.qatools.htmlelements.annotations.Name;

import java.util.List;

import static java.util.Arrays.asList;

/**
 * User: asamar
 * Date: 14.01.2016.
 */
@Name("Окно настройки посещаемого")
public class ServicesSettingsBlock extends WidgetSetupPopup {

    @Name("Список сервисов")
    @FindBy(xpath = ".//div[contains(@class, 'multiselect')]/span")
    public List<SettingsCheckBox> services;

    @Step("Select services by id: {0}")
    public ServicesSettingsBlock selectServicesById(List<String> ids) {
        services.stream()
                .filter(e -> ids.contains(e.input.getWrappedElement().getAttribute("value")))
                .forEach(SettingsCheckBox::check);

        return this;
    }

    public ServicesSettingsBlock selectServicesById(String... ids) {
        return selectServicesById(asList(ids));
    }

    @Step("Select services by name: {0}")
    public ServicesSettingsBlock selectServicesByName(List<String> names) {
        services.stream()
                .filter(e -> names.contains(e.getText()))
                .forEach(SettingsCheckBox::check);

        return this;
    }

    public ServicesSettingsBlock selectServicesByName(String... names) {
        return selectServicesByName(asList(names));
    }

    @Step("Deselect services by id: {0}")
    public ServicesSettingsBlock deselectServicesById(List<String> ids) {
        services.stream()
                .filter(e -> ids.contains(e.input.getWrappedElement().getAttribute("value")))
                .forEach(SettingsCheckBox::uncheck);

        return this;
    }

    public ServicesSettingsBlock deselectServicesById(String... ids) {
        return deselectServicesById(asList(ids));
    }

    @Step("Deselect services by name: {0}")
    public ServicesSettingsBlock deselectServicesByName(List<String> names) {
        services.stream()
                .filter(e -> names.contains(e.getText()))
                .forEach(SettingsCheckBox::uncheck);

        return this;
    }

    public ServicesSettingsBlock deselectServicesByName(String... names) {
        return deselectServicesByName(asList(names));
    }
}
