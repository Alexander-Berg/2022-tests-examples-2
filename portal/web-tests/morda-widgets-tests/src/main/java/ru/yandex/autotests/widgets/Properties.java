package ru.yandex.autotests.widgets;

import ru.yandex.autotests.utils.morda.BaseProperties;
import ru.yandex.qatools.properties.PropertyLoader;
import ru.yandex.qatools.properties.annotations.Property;


/**
 * User: leonsabr
 * Date: 08.11.11
 * Класс со свойствами для профиля каталога виджетов.
 */
public class Properties extends BaseProperties {
    public Properties() {
        super();
        PropertyLoader.populate(this);
    }

    @Property("tagsNumber")
    private int tagsNumber = 25;

    public int getTagsNumber() {
        return tagsNumber;
    }
}
