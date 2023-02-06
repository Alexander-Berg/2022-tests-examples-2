package ru.yandex.autotests.morda.exports.filters;

import org.apache.log4j.Logger;
import ru.yandex.autotests.morda.exports.interfaces.EntryWithDomain;
import ru.yandex.autotests.morda.pages.MordaDomain;

import java.util.List;
import java.util.function.Predicate;

import static java.util.Arrays.asList;

/**
 * User: eoff (eoff@yandex-team.ru)
 * Date: 19/06/16
 */
public enum MordaDomainFilter {
    UNKNOWN("unknown"),
    ALL("all", MordaDomain.getBigDomains()),
    RU("ru", MordaDomain.RU),
    UA("ua", MordaDomain.UA),
    BY("by", MordaDomain.BY),
    KZ("kz", MordaDomain.KZ),
    COM("com", MordaDomain.COM),
    COM_TR("com.tr", MordaDomain.COM_TR),
    KUB("kub", MordaDomain.RU, MordaDomain.KZ, MordaDomain.UA, MordaDomain.BY),
    ALL_NOT_COMTR("all-com.tr", MordaDomain.RU, MordaDomain.UA, MordaDomain.KZ, MordaDomain.BY, MordaDomain.COM),
    KUBR_NOT_UA("kubr-ua", MordaDomain.RU, MordaDomain.BY, MordaDomain.KZ);

    private static final Logger LOGGER = Logger.getLogger(MordaDomainFilter.class);

    private String value;
    private List<MordaDomain> acceptedDomains;

    MordaDomainFilter(String value, List<MordaDomain> acceptedDomains) {
        this.value = value;
        this.acceptedDomains = acceptedDomains;
    }

    MordaDomainFilter(String value, MordaDomain... acceptedDomains) {
        this(value, asList(acceptedDomains));
    }

    public static MordaDomainFilter fromString(String v) {
        for (MordaDomainFilter filter : MordaDomainFilter.values()) {
            if (filter.getValue().equalsIgnoreCase(v)) {
                return filter;
            }
        }
        LOGGER.warn("No domain filter found for value " + v);
        return UNKNOWN;
    }

    public static Predicate<EntryWithDomain> filter(MordaDomain domain) {

        return e -> e.getDomain().matches(domain);
    }

    public boolean matches(MordaDomain domain) {
        return this == ALL || acceptedDomains.contains(domain);
    }

    public String getValue() {
        return value;
    }


    @Override
    public String toString() {
        return value;
    }
}
