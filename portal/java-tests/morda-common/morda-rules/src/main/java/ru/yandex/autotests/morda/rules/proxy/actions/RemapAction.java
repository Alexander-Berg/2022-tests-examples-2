package ru.yandex.autotests.morda.rules.proxy.actions;

import org.apache.log4j.Logger;
import ru.yandex.autotests.morda.rules.MordaRulesProperties;

import java.util.HashMap;
import java.util.List;
import java.util.Map;
import java.util.regex.Pattern;

/**
 * User: asamar
 * Date: 07.09.2015.
 */
public abstract class RemapAction<T> extends Action<T> {
    private static final MordaRulesProperties CONFIG = new MordaRulesProperties();
    protected final Logger LOG = Logger.getLogger(this.getClass());
    protected Map<Pattern, String> remapData;

    public RemapAction(T rule) {
        super(rule);
        this.remapData = new HashMap<>();
        populateFromProperties();
    }

    public RemapAction<T> remap(String remapFromPattern, String remapTo) {
        return remap(Pattern.compile(remapFromPattern), remapTo);
    }

    public RemapAction<T> remap(Pattern remapFromPattern, String remapTo) {
        this.remapData.put(remapFromPattern, remapTo);
        return this;
    }

    @Override
    protected void populateFromProperties() {
        List<String> remaps = CONFIG.getRemap();
        remaps.forEach(
                e -> {
                    String[] remap = e.split("=");
                    if (remap.length != 2) {
                        throw new IllegalArgumentException("Failed to parse remapData from properties: " + e);
                    }
                    remap(remap[0], remap[1]);
                }
        );
    }

    @Override
    public void perform() {
        for (Map.Entry<Pattern, String> remap : remapData.entrySet()) {
            LOG.info("Set remap \"" + remap.getKey() + ": " + remap.getValue() + "\"");
        }
    }
}
