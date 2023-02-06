package ru.yandex.autotests.mordabackend.utils.parameters;

import ch.lambdaj.Lambda;
import ch.lambdaj.function.convert.Converter;
import ch.lambdaj.function.matcher.Predicate;
import ru.yandex.autotests.mordabackend.MordaClient;
import ru.yandex.autotests.mordabackend.beans.cleanvars.Cleanvars;
import ru.yandex.autotests.mordabackend.mobile.application.ApplicationUtils;
import ru.yandex.autotests.mordabackend.useragents.UserAgent;
import ru.yandex.autotests.mordaexportsclient.beans.ApplicationEntry;
import ru.yandex.autotests.utils.morda.language.Language;
import ru.yandex.autotests.utils.morda.region.Region;

import javax.ws.rs.client.Client;
import java.util.ArrayList;
import java.util.Arrays;
import java.util.Collection;
import java.util.HashMap;
import java.util.List;
import java.util.Map;

import static java.lang.Integer.parseInt;
import static org.hamcrest.CoreMatchers.equalTo;
import static org.hamcrest.core.AnyOf.anyOf;
import static ru.yandex.autotests.mordabackend.utils.parameters.ApplicationParameterProvider.PlatformPredicate.platform;
import static ru.yandex.autotests.mordaexportsclient.MordaExports.APPLICATION;
import static ru.yandex.autotests.mordaexportslib.ExportProvider.exports;
import static ru.yandex.autotests.mordaexportslib.matchers.DomainMatcher.domain;
import static ru.yandex.autotests.mordaexportslib.matchers.GeosMatcher.geos;
import static ru.yandex.autotests.mordaexportslib.matchers.LangMatcher.lang;

/**
 * User: eoff (eoff@yandex-team.ru)
 * Date: 16.07.14
 */
public class ApplicationParameterProvider implements ParameterProvider {

    public ApplicationParameterProvider() {
    }

    @Override
    public List<Object[]> getParams(MordaClient mordaClient, Client client, Cleanvars cleanvars, Region region,
                                    Language language, final UserAgent userAgent) {

        Collection<ApplicationEntry> entries = getApplications(region, language, userAgent);

        List<Object[]> data = new ArrayList<>();

        for (ApplicationEntry entry : entries) {
            data.add(new Object[]{entry.getId(), entry});
        }

        return data;
    }

    public static Collection<ApplicationEntry> getApplications(Region region, Language language, UserAgent userAgent) {
        List<ApplicationEntry> entries = exports(
                APPLICATION,
                domain(anyOf(
                        equalTo(region.getDomain().toString().substring(1)),
                        equalTo("kub")
                )),
                geos(region.getRegionIdInt()),
                lang(language),
                platform(userAgent)
        );

        System.out.println(entries);
        Map<String, ApplicationEntry> map = new HashMap<>();

        for (ApplicationEntry e : entries) {
            if (!map.containsKey(e.getId()) ||
                    //если более точный таргетинг по региону и больше вес
                    (map.get(e.getId()).getGeos().split(",").length > e.getGeos().split(",").length
                            && parseInt(map.get(e.getId()).getWeight()) < parseInt(e.getWeight()))) {
                map.put(e.getId(), e);
            }
        }
        System.out.println(map);
        return map.values();
    }

    protected static class PlatformPredicate extends Predicate<ApplicationEntry> {

        private UserAgent userAgent;

        public PlatformPredicate(UserAgent userAgent) {
            this.userAgent = userAgent;
        }

        @Override
        public boolean apply(ApplicationEntry applicationEntry) {
            List<String> platforms = Lambda.convert(Arrays.asList(applicationEntry.getPlatform().split(",")),
                    new Converter<String, String>() {
                        @Override
                        public String convert(String from) {
                            return from.trim();
                        }
                    });
            return platforms.contains(ApplicationUtils.PLATFORM_TYPES.get(userAgent));
        }

        protected static PlatformPredicate platform(UserAgent userAgent) {
            return new PlatformPredicate(userAgent);
        }
    }

}
