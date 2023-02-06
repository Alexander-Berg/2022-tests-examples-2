package ru.yandex.autotests.morda.pages;

import java.util.List;
import java.util.stream.Collectors;
import java.util.stream.Stream;

public enum MordaDomain {
    RU(".ru", MordaLanguage.RU),
    UA(".ua", MordaLanguage.UK),
    KZ(".kz", MordaLanguage.RU),
    BY(".by", MordaLanguage.RU),
    COM(".com", MordaLanguage.EN),
    COM_TR(".com.tr", MordaLanguage.TR),
    AZ(".az", MordaLanguage.RU, true),
    COM_AM(".com.am", MordaLanguage.RU, true),
    CO_IL(".co.il", MordaLanguage.RU, true),
    KG(".kg", MordaLanguage.RU, true),
    LV(".lv", MordaLanguage.RU, true),
    TJ(".tj", MordaLanguage.RU, true),
    TM(".tm", MordaLanguage.RU, true),
    EE(".ee", MordaLanguage.RU, true),
    LT(".lt", MordaLanguage.RU, true),
    FR(".fr", MordaLanguage.RU, true),
    MD(".md", MordaLanguage.RU, true);

    private String value;
    private boolean isSpok;
    private MordaLanguage defaultLanguage;

    MordaDomain(String value, MordaLanguage defaultLanguage) {
        this(value, defaultLanguage, false);
    }

    MordaDomain(String value, MordaLanguage defaultLanguage, boolean isSpok) {
        this.value = value;
        this.defaultLanguage = defaultLanguage;
        this.isSpok = isSpok;
    }

    public static List<MordaDomain> getBigDomains() {
        return Stream.of(MordaDomain.values()).filter(e -> !e.isSpok).collect(Collectors.toList());
    }

    public static List<MordaDomain> getSpokDomains() {
        return Stream.of(MordaDomain.values()).filter(e -> e.isSpok).collect(Collectors.toList());
    }

    public static MordaDomain fromString(String domain) {
        if (domain == null || domain.isEmpty()) {
            throw new IllegalArgumentException("Domain must not be empty or null");
        }

        for (MordaDomain d : MordaDomain.values()) {
            if (d.getValue().equals(domain) || d.getValue().substring(1).equals(domain)) {
                return d;
            }
        }
        throw new IllegalStateException("No domain found for \"" + domain + "\"");
    }

    public String getValue() {
        return value;
    }

    public MordaLanguage getDefaultLanguage() {
        return defaultLanguage;
    }
}
