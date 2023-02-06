package ru.yandex.autotests.morda.rules.proxy.actions;

import org.apache.log4j.Logger;
import ru.yandex.autotests.morda.rules.MordaRulesProperties;

import java.util.HashMap;
import java.util.List;
import java.util.Map;

/**
 * User: asamar
 * Date: 04.09.2015.
 */
public abstract class HeaderAction<T> extends Action<T> {
    private static final MordaRulesProperties CONFIG = new MordaRulesProperties();
    private static final String USER_AGENT_HEADER = "User-Agent";
    private static final String EXP_HEADER = "X-Yandex-TestExp";
    private static final String EXP_FORCE_HEADER = "X-Yandex-TestExpForceDisabled";
    private static final String SAVE_VARS_HEADER = "SaveVars";
    private static final String YANDEX_USER_HEADER = "X-Yandex-User";
    protected final Logger LOG = Logger.getLogger(this.getClass());
    protected Map<String, String> headers;

    public HeaderAction(T rule) {
        super(rule);
        this.headers = new HashMap<>();
    }

    public HeaderAction<T> userAgent(String userAgent) {
        return add(USER_AGENT_HEADER, userAgent);
    }

    public HeaderAction<T> exp(String exp) {
        return add(EXP_HEADER, exp)
                .add(EXP_FORCE_HEADER, "1");
    }

    public HeaderAction<T> saveVars() {
        return add(SAVE_VARS_HEADER, "1")
                .add(YANDEX_USER_HEADER, "autotests");
    }

    public HeaderAction<T> add(String name, String value) {
        this.headers.put(name, value);
        return this;
    }

    @Override
    protected void populateFromProperties() {
        List<String> headers = CONFIG.getHeaders();
        headers.stream().forEach(
                e -> {
                    String[] header = e.split("=");
                    if (header.length != 2) {
                        throw new IllegalArgumentException("Failed to parse header from properties: " + e);
                    }
                    add(header[0], header[1]);
                }
        );

        if (CONFIG.isSaveVars()) {
            saveVars();
        }

        String useragent = CONFIG.getUseragent();
        if (useragent != null && !useragent.isEmpty()) {
            userAgent(useragent);
        }

        String exp = CONFIG.getExp();
        if (exp != null && !exp.isEmpty()) {
            exp(exp);
        }
    }


    @Override
    public void perform() {
        for (Map.Entry<String, String> header : headers.entrySet()) {
            LOG.info("Added header \"" + header.getKey() + ": " + header.getValue() + "\"");
        }
    }
}
