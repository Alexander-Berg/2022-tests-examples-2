package ru.yandex.autotests.metrika.converters;

import ch.lambdaj.function.convert.Converter;
import ru.yandex.autotests.metrika.data.metadata.legacy.LegacyPresetWrapper;
import ru.yandex.metrika.api.constructor.presets.PresetExternal;

/**
 * Created by konkov on 03.09.2014.
 *
 * Конвертер для преобразования шаблона отчета в обертку - параметр теста.
 */
public class LegacyPresetConverter implements Converter<PresetExternal, LegacyPresetWrapper> {
    @Override
    public LegacyPresetWrapper convert(PresetExternal from) {
        return new LegacyPresetWrapper(from);
    }
}
