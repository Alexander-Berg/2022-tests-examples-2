package ru.yandex.autotests.morda.rules.proxy.actions;

import org.apache.log4j.Logger;
import ru.yandex.autotests.morda.rules.MordaRulesProperties;

import java.util.HashMap;
import java.util.HashSet;
import java.util.List;
import java.util.Map;
import java.util.Set;
import java.util.stream.Collectors;

import static java.lang.String.format;
import static java.lang.String.valueOf;
import static java.util.Arrays.asList;
import static ru.yandex.autotests.morda.rules.proxy.actions.CookieAction.CookieData.cookie;

/**
 * User: asamar
 * Date: 04.09.2015.
 */
public abstract class CookieAction<T> extends Action<T> {
    private static final MordaRulesProperties CONFIG = new MordaRulesProperties();
    protected final Map<String, CookieData> cookiesToAdd;
    protected final Map<String, CookieData> cookiesToOverride;
    protected final Set<String> cookiesToDelete;
    protected final Logger LOG = Logger.getLogger(this.getClass());

    public CookieAction(T rule) {
        super(rule);
        this.cookiesToAdd = new HashMap<>();
        this.cookiesToOverride = new HashMap<>();
        this.cookiesToDelete = new HashSet<>();
        populateFromProperties();
    }

    @Override
    protected void populateFromProperties() {
        List<String> cookiesToOverride = CONFIG.getCookiesToOverride();
        cookiesToOverride.stream().forEach(
                e -> {
                    String[] cookie = e.split("=");
                    if (cookie.length != 2) {
                        throw new IllegalArgumentException("Failed to parse cookie from properties: " + e);
                    }
                    override(cookie[0], cookie[1]);
                }
        );

        String yandexuidConfigCookie = CONFIG.getOverrideYandexuidCookie();
        if (yandexuidConfigCookie != null && !yandexuidConfigCookie.isEmpty()) {
            override("yandexuid", yandexuidConfigCookie);
        }
    }

    public CookieAction<T> override(String name, String value) {
        this.cookiesToOverride.put(name, cookie(name, value));
        return this;
    }

    public CookieAction<T> overrideYandexuid(String value) {
        override("yandexuid", value);
        return this;
    }

    public CookieAction<T> overrideMy(String value) {
        override("my", value);
        return this;
    }

    public CookieAction<T> overrideYandexGid(String value) {
        override("yandex_gid", value);
        return this;
    }

    public CookieAction<T> overrideYandexGid(int value) {
        override("yandex_gid", valueOf(value));
        return this;
    }

    public CookieAction<T> add(String name, String value, String domain) {
        this.cookiesToAdd.put(name, cookie(name, value, domain));
        return this;
    }

    public CookieAction<T> remove(String... names) {
        return remove(asList(names));
    }

    public CookieAction<T> remove(List<String> names) {
        this.cookiesToDelete.addAll(names);
        return this;
    }

    @Override
    public void perform() {
        if (!cookiesToAdd.isEmpty()) {
            String cookies = cookiesToAdd.values()
                    .stream()
                    .map(CookieData::toString)
                    .collect(Collectors.joining(", "));
            LOG.info("Add cookies: [" + cookies + "]");
        }
        if (!cookiesToOverride.isEmpty()) {
            String cookies = cookiesToOverride.values()
                    .stream()
                    .map(CookieData::toString)
                    .collect(Collectors.joining(", "));
            LOG.info("Override cookies: [" + cookies + "]");
        }
        if (!cookiesToDelete.isEmpty()) {
            String cookies = cookiesToDelete
                    .stream()
                    .collect(Collectors.joining(", "));
            LOG.info("Delete cookies: [" + cookies + "]");
        }
    }

    protected static class CookieData {
        public String name;
        public String value;
        public String domain;

        public CookieData(String name, String value, String domain) {
            this.name = name;
            this.value = value;
            this.domain = domain;
        }

        public static CookieData cookie(String name, String value) {
            return cookie(name, value, null);
        }

        public static CookieData cookie(String name, String value, String domain) {
            return new CookieData(name, value, domain);
        }

        @Override
        public String toString() {
            String formatShort = "%s=%s";
            String formatFull = "%s=%s; domain=%s";
            if (domain != null && !domain.isEmpty()) {
                return format(formatFull, name, value, domain);
            } else {
                return format(formatShort, name, value);
            }
        }
    }
}
