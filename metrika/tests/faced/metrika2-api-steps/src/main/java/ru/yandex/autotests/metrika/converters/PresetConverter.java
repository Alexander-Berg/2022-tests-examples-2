package ru.yandex.autotests.metrika.converters;

import ch.lambdaj.function.convert.Converter;
import ru.yandex.autotests.metrika.data.metadata.v1.PresetWrapper;
import ru.yandex.metrika.api.constructor.presets.PresetExternal;

/**
 * Created by konkov on 03.09.2014.
 *
 * Конвертер для преобразования шаблона отчета в обертку - параметр теста.
 */
public class PresetConverter implements Converter<PresetExternal, PresetWrapper> {
    @Override
    public PresetWrapper convert(PresetExternal from) {
        return new PresetWrapper(from);
    }
}
