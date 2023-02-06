package ru.yandex.autotests.morda.pages.yaru;

import ru.yandex.autotests.morda.pages.MordaLanguage;
import ru.yandex.autotests.morda.pages.AbstractMorda;
import ru.yandex.autotests.morda.pages.MordaDomain;

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
public abstract class YaruMorda<T> extends AbstractMorda<T> {

    protected static final Set<MordaLanguage> AVAILABLE_LANGUAGES =
            new HashSet<>(asList(MordaLanguage.RU));
    private static final URI PASSPORT_HOST = URI.create("https://passport.yandex.ru/");
    private static final URI TUNE_HOST = URI.create("https://tune.yandex.ru/");

    protected YaruMorda(String scheme, String prefix, String environment) {
        super(scheme, prefix, environment);
        language(MordaLanguage.RU);
    }

    public static List<YaruMorda<?>> getDefaultYaruList(String environment) {
        List<YaruMorda<?>> data = new ArrayList<>();
        data.addAll(DesktopYaruMorda.getDefaultList(environment));
        data.addAll(PdaYaruMorda.getDefaultList(environment));
        data.addAll(TouchYaruMorda.getDefaultList(environment));
        return data;
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
    public URI getBaseUrl() {
        return UriBuilder.fromUri("scheme://{env}ya.ru/")
                .scheme(getScheme())
                .build(getEnvironment());
    }

    @Override
    public MordaDomain getDomain() {
        return MordaDomain.RU;
    }

    @Override
    public String getCookieDomain() {
        return ".ya" + getDomain().getValue();
    }

    @Override
    public Set<MordaLanguage> getAvailableLanguages() {
        return AVAILABLE_LANGUAGES;
    }

    @Override
    public T language(MordaLanguage language) {
        return super.language(language);
    }
}
