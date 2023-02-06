package ru.yandex.autotests.metrika.data.metadata.legacy;

import ru.yandex.metrika.api.constructor.presets.PresetExternal;

/**
 * Created by konkov on 03.09.2014.
 *
 * Обертка над классом Preset в legacy api для использования в качестве параметра теста.
 */
public class LegacyPresetWrapper {
    private final PresetExternal preset;

    public LegacyPresetWrapper(PresetExternal preset) {
        this.preset = preset;
    }

    public PresetExternal getPreset() {
        return preset;
    }

    @Override
    public String toString() {
        return preset == null ? "null" : preset.getName();
    }
}
