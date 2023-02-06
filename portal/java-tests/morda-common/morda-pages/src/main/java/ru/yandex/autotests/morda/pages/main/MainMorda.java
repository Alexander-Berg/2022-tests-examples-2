package ru.yandex.autotests.morda.pages.main;

import ru.yandex.autotests.morda.pages.MordaLanguage;
import ru.yandex.autotests.morda.pages.AbstractMorda;
import ru.yandex.autotests.morda.pages.MordaDomain;
import ru.yandex.autotests.morda.pages.MordaWithLanguage;
import ru.yandex.autotests.morda.pages.MordaWithRegion;
import ru.yandex.geobase.regions.GeobaseRegion;
import ru.yandex.geobase.regions.Russia;

import javax.ws.rs.core.UriBuilder;
import java.net.URI;
import java.util.ArrayList;
import java.util.HashSet;
import java.util.List;
import java.util.Set;

import static java.util.Arrays.asList;

/**
 * User: eoff (eoff@yandex-team.ru)
 * Date: 20/07/16
 */
public abstract class MainMorda<T> extends AbstractMorda<T>
        implements MordaWithLanguage<T>, MordaWithRegion<T> {

    protected static final Set<MordaLanguage> AVAILABLE_LANGUAGES =
            new HashSet<>(asList(MordaLanguage.RU, MordaLanguage.BE, MordaLanguage.KK, MordaLanguage.UK, MordaLanguage.TT));

    protected MainMorda(String scheme, String prefix, String environment) {
        super(scheme, prefix, environment);
        language(MordaLanguage.RU);
        region(Russia.MOSCOW);
    }

    public static List<MainMorda<?>> getDefaultMainList(String environment) {
        List<MainMorda<?>> data = new ArrayList<>();
        data.addAll(DesktopMain404Morda.getDefaultList(environment));
        data.addAll(DesktopMainAllMorda.getDefaultList(environment));
        data.addAll(DesktopMainMorda.getDefaultList(environment));
        data.addAll(DesktopFamilyMainMorda.getDefaultList(environment));
        data.addAll(PdaMainAllMorda.getDefaultList(environment));
        data.addAll(PdaMainMorda.getDefaultList(environment));
        data.addAll(TouchMainAllMorda.getDefaultList(environment));
        data.addAll(TouchMainMorda.getDefaultList(environment));
        data.addAll(TouchMainWpMorda.getDefaultList(environment));
        data.addAll(TelMainMorda.getDefaultList(environment));
//        data.addAll(TabletMainMorda.getDefaultList(environment));
        data.addAll(DesktopFirefoxMorda.getDefaultList(environment));
        return data;
    }

    @Override
    public URI getPassportHost() {
        return UriBuilder.fromUri("https://passport.yandex{domain}/")
                .build(getDomain().getValue());
    }

    @Override
    public URI getTuneHost() {
        return UriBuilder.fromUri("https://tune.yandex{domain}/")
                .build(getDomain().getValue());
    }

    @Override
    public URI getBaseUrl() {
        return UriBuilder.fromUri("scheme://{env}yandex{domain}/")
                .scheme(getScheme())
                .build(getEnvironment(), getDomain().getValue());
    }

    @Override
    public MordaDomain getDomain() {
        return MordaDomain.fromString(getRegion().getKubrDomain());
    }

    @Override
    public Set<MordaLanguage> getAvailableLanguages() {
        return AVAILABLE_LANGUAGES;
    }

    @Override
    public T language(MordaLanguage language) {
        return super.language(language);
    }

    @Override
    public T region(GeobaseRegion region) {
        return super.region(region);
    }

    @Override
    public GeobaseRegion getRegion() {
        return super.getRegion();
    }

    @Override
    public String toString() {
        return super.toString() + " " + getRegion() + " " + getLanguage();
    }
}
