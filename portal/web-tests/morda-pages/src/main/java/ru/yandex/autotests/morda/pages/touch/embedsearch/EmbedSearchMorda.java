package ru.yandex.autotests.morda.pages.touch.embedsearch;

import org.openqa.selenium.WebDriver;
import org.openqa.selenium.remote.DesiredCapabilities;
import ru.yandex.autotests.morda.pages.Morda;
import ru.yandex.autotests.morda.pages.MordaType;
import ru.yandex.autotests.morda.rules.allure.AllureFeatureRule;
import ru.yandex.autotests.mordacommonsteps.rules.MordaAllureBaseRule;
import ru.yandex.autotests.mordacommonsteps.rules.proxy.configactions.Header;
import ru.yandex.autotests.mordacommonsteps.rules.proxy.configactions.HeaderAction;

import javax.ws.rs.core.UriBuilder;
import java.net.URI;
import java.util.HashSet;
import java.util.List;

import static java.util.Arrays.asList;
import static ru.yandex.autotests.morda.pages.MordaType.EMBED_SEARCH;

/**
 * User: asamar
 * Date: 29.11.16
 */
public class EmbedSearchMorda extends Morda<EmbedSearchPage> {

    protected EmbedSearchMorda(String scheme, MordaEnvironment environment) {
        super(scheme, environment);
    }

    public static EmbedSearchMorda embedSearchMorda(String scheme, String environment) {
        return new EmbedSearchMorda(scheme, new MordaEnvironment("www", environment, true));
    }

    @Override
    public MordaType getMordaType() {
        return EMBED_SEARCH;
    }

    @Override
    public MordaAllureBaseRule getRule(DesiredCapabilities caps) {
        List<Header> headers = asList(
                new Header("X-Yandex-TestExpForceDisabled", "1"),
                new Header("X-Yandex-TestCounters", "0")
        );
        return new MordaAllureBaseRule(caps)
                .withRule(new AllureFeatureRule(getFeature()))
                .mergeProxyAction(HeaderAction.class, new HashSet<>(headers));
    }

    @Override
    public EmbedSearchPage getPage(WebDriver driver) {
        return new EmbedSearchPage(driver);
    }

    @Override
    public URI getUrl() {
        return UriBuilder.fromUri("scheme://{env}yandex.ru/portal/embed_search")
                .scheme(scheme)
                .build(environment.parseEnvironment());
    }

    @Override
    public URI getPassportUrl(String passportEnv) {
        return UriBuilder.fromUri("https://{passportEnv}.yandex.ru/")
                .build(passportEnv);
    }

    @Override
    public URI getTuneUrl(String tuneEnv) {
        return UriBuilder.fromUri("https://{tuneEnv}.yandex.ru/")
                .build(tuneEnv);
    }

    @Override
    public URI getSerpUrl() {
        return UriBuilder.fromUri("{scheme}://yandex.ru/search")
                .build(scheme);
    }

    @Override
    public String getCookieDomain() {
        return ".yandex.ru";
    }

    @Override
    public String getFeature() {
        return "embed_search " + getUrl();
    }

    @Override
    public String toString() {
        return "embed_search " + getUrl();
    }
}
