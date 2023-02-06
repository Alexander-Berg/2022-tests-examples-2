package ru.yandex.autotests.morda.pages.tv;

import ru.yandex.autotests.morda.pages.MordaLanguage;
import ru.yandex.autotests.morda.pages.AbstractMorda;
import ru.yandex.autotests.morda.pages.MordaDomain;
import ru.yandex.autotests.morda.pages.MordaType;
import ru.yandex.autotests.morda.pages.MordaWithRegion;
import ru.yandex.geobase.regions.GeobaseRegion;
import ru.yandex.geobase.regions.Russia;

import javax.ws.rs.core.UriBuilder;
import java.net.URI;
import java.util.HashSet;
import java.util.List;
import java.util.Set;

import static java.util.Arrays.asList;

/**
 * User: eoff (eoff@yandex-team.ru)
 * Date: 20/07/16
 */
public class TvSmartMorda extends AbstractMorda<TvSmartMorda>
        implements MordaWithRegion<TvSmartMorda> {

    protected static final Set<MordaLanguage> AVAILABLE_LANGUAGES =
            new HashSet<>(asList(MordaLanguage.RU));
    private static final URI PASSPORT_HOST = URI.create("https://passport.yandex.ru/");
    private static final URI TUNE_HOST = URI.create("https://tune.yandex.ru/");

    protected TvSmartMorda(String scheme, String prefix, String environment) {
        super(scheme, prefix, environment);
        region(Russia.MOSCOW);
        language(MordaLanguage.RU);
        experiments("tv_2");
    }

    public static TvSmartMorda tvSmart() {
        return tvSmart("production");
    }

    public static TvSmartMorda tvSmart(String environment) {
        return tvSmart("https", environment);
    }

    public static TvSmartMorda tvSmart(String scheme, String environment) {
        return new TvSmartMorda(scheme, "www", environment);
    }

    public static List<TvSmartMorda> getDefaultList(String environment) {
        return asList(tvSmart(environment));
    }

    @Override
    public MordaType getMordaType() {
        return MordaType.TV_SMART;
    }

    @Override
    public String getDefaultUserAgent() {
        return CONFIG.getSmartTvUserAgent();
    }

    @Override
    public URI getBaseUrl() {
        return UriBuilder.fromUri("scheme://{env}yandex{domain}/")
                .scheme(getScheme())
                .build(getEnvironment(), getDomain().getValue());
    }

    @Override
    public URI getPassportHost() {
        return PASSPORT_HOST;
    }

    @Override
    public URI getTuneHost() {
        return TUNE_HOST;
    }

    @Override
    public TvSmartMorda me() {
        return this;
    }

    @Override
    public GeobaseRegion getRegion() {
        return super.getRegion();
    }

    @Override
    public TvSmartMorda region(GeobaseRegion region) {
        return super.region(region);
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
    public String toString() {
        return super.toString() + " " + getRegion() + " " + getLanguage();
    }
}
