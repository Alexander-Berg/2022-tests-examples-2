package ru.yandex.autotests.metrika.data.metadata.v1;


import ru.yandex.metrika.api.constructor.presets.PresetExternal;

/**
 * Created by konkov on 03.09.2014.
 * 
 * Обертка над классом Preset для использования в качестве параметра теста.
 */
public class PresetWrapper {
    private final PresetExternal preset;

    public PresetWrapper(PresetExternal preset) {
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
