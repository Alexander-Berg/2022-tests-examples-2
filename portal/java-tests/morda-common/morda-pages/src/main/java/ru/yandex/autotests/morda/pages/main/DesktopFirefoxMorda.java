package ru.yandex.autotests.morda.pages.main;

import ru.yandex.autotests.morda.pages.MordaLanguage;
import ru.yandex.autotests.morda.pages.AbstractDesktopMorda;
import ru.yandex.autotests.morda.pages.MordaDomain;
import ru.yandex.autotests.morda.pages.MordaType;
import ru.yandex.geobase.regions.Russia;
import ru.yandex.geobase.regions.Turkey;
import ru.yandex.geobase.regions.Ukraine;

import java.util.HashSet;
import java.util.List;
import java.util.Set;

import static java.util.Arrays.asList;
import static ru.yandex.autotests.morda.pages.MordaDomain.COM_TR;
import static ru.yandex.autotests.morda.pages.MordaDomain.RU;
import static ru.yandex.autotests.morda.pages.MordaDomain.UA;

/**
 * User: eoff (eoff@yandex-team.ru)
 * Date: 27/02/15
 */
public class DesktopFirefoxMorda extends MainMorda<DesktopFirefoxMorda>
        implements AbstractDesktopMorda<DesktopFirefoxMorda> {

    protected static final Set<MordaLanguage> AVAILABLE_LANGUAGES =
            new HashSet<>(asList(MordaLanguage.RU, MordaLanguage.UK, MordaLanguage.TR));

    private MordaDomain domain;

    private DesktopFirefoxMorda(MordaDomain domain, String scheme, String prefix, String environment) {
        super(scheme, prefix, environment);
        this.domain = domain;
    }

    public static DesktopFirefoxMorda desktopFirefox(MordaDomain domain) {
        return desktopFirefox(domain, "production");
    }

    public static DesktopFirefoxMorda desktopFirefox(MordaDomain domain, String environment) {
        return desktopFirefox(domain, "https", environment);
    }

    public static DesktopFirefoxMorda desktopFirefox(MordaDomain domain, String scheme, String environment) {
        return new DesktopFirefoxMorda(domain, scheme, "firefox", environment);
    }

    public static List<DesktopFirefoxMorda> getDefaultList(String environment) {
        return asList(
                desktopFirefox(RU, environment).region(Russia.MOSCOW).language(MordaLanguage.RU),
                desktopFirefox(UA, environment).region(Ukraine.KYIV).language(MordaLanguage.UK),
                desktopFirefox(COM_TR, environment).region(Turkey.ISTANBUL_11508).language(MordaLanguage.TR)
        );
    }

    @Override
    public MordaType getMordaType() {
        return MordaType.DESKTOP_FIREFOX;
    }

    @Override
    public MordaDomain getDomain() {
        return domain;
    }

    @Override
    public Set<MordaLanguage> getAvailableLanguages() {
        return AVAILABLE_LANGUAGES;
    }

    @Override
    public DesktopFirefoxMorda me() {
        return this;
    }
}
