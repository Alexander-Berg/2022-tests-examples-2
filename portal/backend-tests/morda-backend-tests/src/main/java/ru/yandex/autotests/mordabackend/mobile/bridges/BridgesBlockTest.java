package ru.yandex.autotests.mordabackend.mobile.bridges;

import ch.lambdaj.function.convert.Converter;
import org.joda.time.LocalTime;
import org.joda.time.format.DateTimeFormat;
import org.junit.Test;
import org.junit.runner.RunWith;
import ru.yandex.aqua.annotations.project.Aqua;
import ru.yandex.autotests.mordabackend.MordaClient;
import ru.yandex.autotests.mordabackend.beans.bridges.BridgeInfo;
import ru.yandex.autotests.mordabackend.beans.bridges.Bridges;
import ru.yandex.autotests.mordabackend.beans.cleanvars.Cleanvars;
import ru.yandex.autotests.mordabackend.useragents.UserAgent;
import ru.yandex.autotests.mordabackend.utils.parameters.ParametersUtils;
import ru.yandex.autotests.mordabackend.utils.runner.CleanvarsParametrizedRunner;
import ru.yandex.autotests.mordaexportsclient.MordaExports;
import ru.yandex.autotests.mordaexportsclient.beans.BridgesEntry;
import ru.yandex.autotests.utils.morda.language.Language;
import ru.yandex.autotests.utils.morda.region.Region;
import ru.yandex.qatools.allure.annotations.Features;
import ru.yandex.qatools.allure.annotations.Stories;

import javax.ws.rs.client.Client;

import java.util.Collections;
import java.util.List;

import static ch.lambdaj.Lambda.convert;
import static ch.lambdaj.Lambda.extract;
import static ch.lambdaj.Lambda.having;
import static ch.lambdaj.Lambda.on;
import static ch.lambdaj.Lambda.select;
import static org.hamcrest.Matchers.empty;
import static org.hamcrest.Matchers.equalTo;
import static org.hamcrest.Matchers.not;
import static org.junit.Assume.assumeThat;
import static ru.yandex.autotests.mordabackend.blocks.CleanvarsBlock.BRIDGES;
import static ru.yandex.autotests.mordabackend.blocks.CleanvarsBlock.HIDDENTIME;
import static ru.yandex.autotests.mordabackend.useragents.UserAgent.ANDROID_HTC_SENS;
import static ru.yandex.autotests.mordabackend.useragents.UserAgent.TOUCH;
import static ru.yandex.autotests.mordabackend.useragents.UserAgent.WP8;
import static ru.yandex.autotests.mordabackend.utils.CleanvarsUtils.shouldHaveParameter;
import static ru.yandex.autotests.mordabackend.utils.CleanvarsUtils.shouldMatchTo;
import static ru.yandex.autotests.mordabackend.utils.parameters.ParametersUtils.parameters;
import static ru.yandex.autotests.mordabackend.utils.predicates.ExportDateMatcher.after;
import static ru.yandex.autotests.mordabackend.utils.predicates.ExportDateMatcher.before;
import static ru.yandex.autotests.mordaexportslib.ExportProvider.exports;
import static ru.yandex.autotests.mordaexportslib.matchers.GeoMatcher.geo;
import static ru.yandex.autotests.utils.morda.language.Language.BE;
import static ru.yandex.autotests.utils.morda.language.Language.KK;
import static ru.yandex.autotests.utils.morda.language.Language.RU;
import static ru.yandex.autotests.utils.morda.language.Language.TT;
import static ru.yandex.autotests.utils.morda.language.Language.UK;
import static ru.yandex.autotests.utils.morda.region.Region.SANKT_PETERBURG;
import static ru.yandex.qatools.matchers.collection.HasSameItemsAsCollectionMatcher.hasSameItemsAsCollection;

/**
 * User: ivannik
 * Date: 09.09.2014
 */
@Aqua.Test(title = "Bridges Block")
@Features("Mobile")
@Stories("Bridges Block")
@RunWith(CleanvarsParametrizedRunner.class)
public class BridgesBlockTest {

    @CleanvarsParametrizedRunner.Parameters("{3}, {4}, {5}")
    public static ParametersUtils parameters =
            parameters(SANKT_PETERBURG)
                    .withLanguages(RU, UK, BE, KK, TT)
                    .withUserAgents(TOUCH, WP8, ANDROID_HTC_SENS)
                    .withCleanvarsBlocks(BRIDGES, HIDDENTIME);

    private Cleanvars cleanvars;
    private List<BridgesEntry> bridgesExports;

    public BridgesBlockTest(MordaClient mordaClient, Client client, Cleanvars cleanvars, Region region,
                         Language language, UserAgent userAgent) {
        this.cleanvars = cleanvars;
        this.bridgesExports = exports(MordaExports.BRIDGES,
                having(on(BridgesEntry.class).getFrom(),
                        before("yyyy-MM-dd", "yyyy-MM-dd HH:mm:ss", cleanvars.getHiddenTime())),
                having(on(BridgesEntry.class).getTill(),
                        after("yyyy-MM-dd", "yyyy-MM-dd HH:mm:ss", cleanvars.getHiddenTime())),
                geo(region.getRegionIdInt()));
    }

    @Test
    public void highPriorityBridgesCount() {
        List<String> expectedHighPriorityBridges =
                extract(select(bridgesExports, having(on(BridgesEntry.class).getBridgePriority(), equalTo("1"))),
                        on(BridgesEntry.class).getBridgeId());
        assumeThat("Не мостов с приоритетом 1 для отображения", expectedHighPriorityBridges, not(empty()));
        List<String> actualHighPriorityBridges =
                extract(cleanvars.getBridges().get1(), on(BridgeInfo.class).getBridgeId());
        shouldMatchTo(actualHighPriorityBridges, hasSameItemsAsCollection(expectedHighPriorityBridges));
    }

    @Test
    public void lowPriorityBridgesCount() {
        List<String> expectedLowPriorityBridges =
                extract(select(bridgesExports, having(on(BridgesEntry.class).getBridgePriority(), equalTo("0"))),
                        on(BridgesEntry.class).getBridgeId());
        assumeThat("Не мостов с приоритетом 0 для отображения", expectedLowPriorityBridges, not(empty()));
        List<String> actualLowPriorityBridges =
                extract(cleanvars.getBridges().get0(), on(BridgeInfo.class).getBridgeId());
        shouldMatchTo(actualLowPriorityBridges, hasSameItemsAsCollection(expectedLowPriorityBridges));
    }

    @Test
    public void collapseFlag() {
        assumeThat("Не мостов для отображения", bridgesExports, not(empty()));
        LocalTime endCollapseTime = Collections.min(convert(bridgesExports, new Converter<BridgesEntry, LocalTime>() {
             @Override
             public LocalTime convert(BridgesEntry from) {
                 return DateTimeFormat.forPattern("HH:mm").parseLocalTime(from.getBridgeRaise1());
             }
         })).minusHours(2);
        LocalTime startCollapseTime = LocalTime.parse("6:00");
        LocalTime currentTime = DateTimeFormat.forPattern("yyyy-MM-dd HH:mm:ss").parseLocalTime(cleanvars.getHiddenTime());

        boolean collapse =
                (startCollapseTime.isBefore(endCollapseTime) &&
                        currentTime.isAfter(startCollapseTime) && currentTime.isBefore(endCollapseTime)) ||
                (startCollapseTime.isAfter(endCollapseTime) &&
                        (currentTime.isBefore(endCollapseTime) || currentTime.isAfter(startCollapseTime)));

        if (collapse) {
            shouldHaveParameter(cleanvars.getBridges(), having(on(Bridges.class).getCollapse(), equalTo(1)));
        } else {
            shouldHaveParameter(cleanvars.getBridges(), having(on(Bridges.class).getCollapse(), equalTo(0)));
        }
    }

    @Test
    public void showFlag() {
        shouldHaveParameter(cleanvars.getBridges(), having(on(Bridges.class).getShow(), equalTo(1)));
    }

}
