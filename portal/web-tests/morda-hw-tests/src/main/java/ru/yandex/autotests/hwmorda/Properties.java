package ru.yandex.autotests.hwmorda;

import ru.yandex.autotests.utils.morda.BaseProperties;
import ru.yandex.autotests.utils.morda.url.Domain;
import ru.yandex.qatools.properties.PropertyLoader;

import static ru.yandex.autotests.utils.morda.url.Domain.RU;


/**
 * User: alex89
 * Date: 12.09.12
 */
public class Properties extends BaseProperties {
    public Properties() {
        super();
        PropertyLoader.populate(this);
    }

    @Override
    public String getBaseURL() {
        return super.getBaseURL().replace("hw", "www");
    }

    public String getBMWBaseUrl() {
        return super.getBaseURL() + "/bmw";
    }

    public String getLgBaseUrl() {
        return super.getBaseURL() + "/lg";
    }

    public String getFotkiBaseUrl() {
        return "https://fotki.yandex.ru";
    }

    @Override
    public Domain getBaseDomain() {
        return RU;
    }
}
