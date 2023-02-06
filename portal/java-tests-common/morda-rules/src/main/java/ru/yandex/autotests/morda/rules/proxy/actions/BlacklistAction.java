package ru.yandex.autotests.morda.rules.proxy.actions;

import org.apache.log4j.Logger;
import ru.yandex.autotests.morda.rules.MordaRulesProperties;

import java.util.HashSet;
import java.util.List;
import java.util.Set;
import java.util.regex.Pattern;

import static java.util.Arrays.asList;
import static java.util.Arrays.stream;
import static java.util.stream.Collectors.toList;

/**
 * User: asamar
 * Date: 07.09.2015.
 */
public abstract class BlacklistAction<T> extends Action<T> {

    private static final MordaRulesProperties CONFIG = new MordaRulesProperties();
    protected final Logger LOG = Logger.getLogger(this.getClass());
    protected Set<String> patterns;

    public BlacklistAction(T rule) {
        super(rule);
        this.patterns = new HashSet<>();
        populateFromProperties();
    }

    @Override
    protected void populateFromProperties() {
        block(CONFIG.getBlacklist());
    }

    @Override
    public void perform() {
        if (!patterns.isEmpty()) {
            LOG.info("Blacklist: " + patterns);
        }
    }

    public BlacklistAction<T> block(String... patterns) {
        return block(asList(patterns));
    }

    public BlacklistAction<T> block(Pattern... patterns) {
        return block(stream(patterns).map(Pattern::toString).collect(toList()));
    }

    public BlacklistAction<T> block(List<String> patterns) {
        this.patterns.addAll(patterns);
        return this;
    }
}
