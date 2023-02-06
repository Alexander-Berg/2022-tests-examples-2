package ru.yandex.autotests.mordabackend.services;

import ch.lambdaj.function.matcher.Predicate;
import ru.yandex.autotests.mordabackend.utils.MordaVersion;
import ru.yandex.autotests.mordaexportsclient.MordaExports;
import ru.yandex.autotests.mordaexportsclient.beans.ServicesDefaultsV2Entry;
import ru.yandex.autotests.mordaexportsclient.beans.ServicesV122Entry;
import ru.yandex.autotests.mordaexportsclient.beans.SignEntry;
import ru.yandex.autotests.utils.morda.language.Language;
import ru.yandex.autotests.utils.morda.region.Region;
import ru.yandex.autotests.utils.morda.url.Domain;

import java.util.ArrayList;
import java.util.Arrays;
import java.util.Collections;
import java.util.List;

import static ch.lambdaj.Lambda.*;
import static org.hamcrest.Matchers.*;
import static ru.yandex.autotests.mordaexportsclient.MordaExports.ALL_EXPORTS;
import static ru.yandex.autotests.mordaexportsclient.MordaExports.SERVICES_DEFAULTS_V2;
import static ru.yandex.autotests.mordaexportslib.ExportProvider.export;
import static ru.yandex.autotests.mordaexportslib.ExportProvider.exports;
import static ru.yandex.autotests.mordaexportslib.matchers.DomainMatcher.domain;
import static ru.yandex.autotests.mordaexportslib.matchers.GeoMatcher.geo;
import static ru.yandex.autotests.mordaexportslib.matchers.GeosMatcher.geos;
import static ru.yandex.autotests.mordaexportslib.matchers.LangMatcher.lang;
import static ru.yandex.autotests.mordaexportslib.matchers.ServicesV122EntryMatcher.with;

/**
 * @author Ivan Nikolaev <ivannik@yandex-team.ru>
 */
public class ServicesUtils {

    public static List<ServicesV122Entry> getAllDefaultBlockServices(MordaVersion mordaVersion,
                                                                     Region region) {
        List<ServicesV122Entry> defaultServices = new ArrayList<>();
        defaultServices.addAll(getDefaultBlockServicesWithComments(mordaVersion, region));
        defaultServices.addAll(getPinnedServices(mordaVersion, region));
        return defaultServices;
    }

    public static List<ServicesV122Entry> getDefaultBlockServicesWithComments(MordaVersion mordaVersion,
                                                                              final Region region) {

        ServicesDefaultsV2Entry export = export(SERVICES_DEFAULTS_V2, geos(region.getRegionIdInt()),
                having(on(ServicesDefaultsV2Entry.class).getMorda(), equalTo(mordaVersion.getName())),
                having(on(ServicesDefaultsV2Entry.class).getExp(), nullValue()));
        List<String> defaultServices = new ArrayList<>();
        defaultServices.addAll(Arrays.asList(export.getDefaultSign().split(" ")));
        return exports(mordaVersion.getExport(),
                domain(region.getDomain()),
                with().morda(anyOf(equalTo("4"), containsString("market"))),
                with().id(not("browser")),
                with().id(isIn(defaultServices)),
                new Predicate<ServicesV122Entry>() {
                    @Override
                    public boolean apply(ServicesV122Entry item) {
                        return hasDefaultSigns(item.getId(), region);
                    }
                });

    }

    public static List<ServicesV122Entry> getPinnedServices(MordaVersion mordaVersion, final Region region) {
        ServicesDefaultsV2Entry export = export(SERVICES_DEFAULTS_V2, geos(region.getRegionIdInt()),
                having(on(ServicesDefaultsV2Entry.class).getMorda(), equalTo(mordaVersion.getName())),
                having(on(ServicesDefaultsV2Entry.class).getExp(), nullValue()));
        List<String> pinnedServices = new ArrayList<>();
        pinnedServices.addAll(Arrays.asList(export.getPinned().split(" ")));
        return exports(mordaVersion.getExport(),
                domain(region.getDomain()),
                with().morda(anyOf(equalTo("4"), containsString("market"))),
                with().id(isIn(pinnedServices)),
                new Predicate<ServicesV122Entry>() {
                    @Override
                    public boolean apply(ServicesV122Entry item) {
                        return hasDefaultSigns(item.getId(), region);
                    }
                });
    }

    private static boolean hasDefaultSigns(String serviceId, Region region, Language language) {
        return getSigns(serviceId, region.getDomain(), language, region.getRegionIdInt()).size() > 0;
    }

    private static boolean hasDefaultSigns(String serviceId, Region region) {
        return getSigns(serviceId, region.getDomain(), region.getRegionIdInt()).size() > 0;
    }

    private static List<SignEntry> getSigns(String serviceId, Domain d, int gid) {
        MordaExports.MordaExport<SignEntry> signExport = getSignExport(serviceId);
        if (signExport != null) {
            return exports(signExport, domain(d), geo(gid),
                    having(on(SignEntry.class).getBkTag(), isEmptyOrNullString()));
        }
        return Collections.emptyList();
    }

    private static List<SignEntry> getSigns(String serviceId, Domain d, Language l, int gid) {
        MordaExports.MordaExport<SignEntry> signExport = getSignExport(serviceId);
        if (signExport != null) {
            return exports(signExport, domain(d), geo(gid), lang(l),
                    having(on(SignEntry.class).getBkTag(), isEmptyOrNullString()));
        }
        return Collections.emptyList();
    }

    private static MordaExports.MordaExport<SignEntry> getSignExport(String serviceId) {
        return selectFirst(ALL_EXPORTS,
                having(on(MordaExports.MordaExport.class).getName(), equalTo("sign_" + serviceId + "_v2")));
    }
}
