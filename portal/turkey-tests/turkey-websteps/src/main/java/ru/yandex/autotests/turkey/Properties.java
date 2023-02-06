package ru.yandex.autotests.turkey;

import ru.yandex.autotests.utils.morda.BaseProperties;
import ru.yandex.autotests.utils.morda.language.Language;
import ru.yandex.autotests.utils.morda.url.Domain;
import ru.yandex.qatools.properties.PropertyLoader;

import static ru.yandex.autotests.utils.morda.language.Language.TR;
import static ru.yandex.autotests.utils.morda.url.Domain.COM_TR;

/**
 * User: alex89
 * Date: 04.10.12
 */
public class Properties extends BaseProperties {
    public Properties() {
        super();
        PropertyLoader.populate(this);
    }

    @Override
    public Domain getBaseDomain() {
        return COM_TR;
    }

    public Language getLang() {
        return TR;
    }
}
