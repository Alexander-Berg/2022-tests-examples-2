package ru.yandex.autotests.metrika.converters;

import com.google.common.collect.Lists;
import ru.yandex.autotests.metrika.data.inpage.Click;

import java.util.Collection;
import java.util.List;

/**
 * Конвертирует список чисел, полученных из карты кликов
 * в список объектов кликов, построенных по последовательным тройкам из входа/
 */
public class CollectionToClicksConverter{

    public static Collection<Click> convert(Collection<Integer> integers) {
        if (integers.size() % 3 != 0){
            throw new IllegalArgumentException("количество чисел в коллекции кликов должно быть кратно 3");
        }
        List<Integer> data = Lists.newArrayList(integers);
        List<Click> clicks = Lists.newArrayList();
        for (int i = 0; i < integers.size(); i += 3) {
            clicks.add(new Click(data.get(i), data.get(i + 1), data.get(i + 2)));
        }
        return clicks;
    }
}
