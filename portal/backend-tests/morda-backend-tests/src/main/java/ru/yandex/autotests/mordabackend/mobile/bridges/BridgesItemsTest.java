package ru.yandex.autotests.mordabackend.mobile.bridges;

import org.junit.Before;
import org.junit.Test;
import org.junit.runner.RunWith;
import ru.yandex.aqua.annotations.project.Aqua;
import ru.yandex.autotests.mordabackend.MordaClient;
import ru.yandex.autotests.mordabackend.beans.bridges.BridgeInfo;
import ru.yandex.autotests.mordabackend.beans.cleanvars.Cleanvars;
import ru.yandex.autotests.mordabackend.useragents.UserAgent;
import ru.yandex.autotests.mordabackend.utils.parameters.BridgesParametrProvider;
import ru.yandex.autotests.mordabackend.utils.parameters.ParametersUtils;
import ru.yandex.autotests.mordabackend.utils.runner.CleanvarsParametrizedRunner;
import ru.yandex.autotests.mordaexportsclient.MordaExports;
import ru.yandex.autotests.mordaexportsclient.beans.BridgesEntry;
import ru.yandex.autotests.utils.morda.language.Language;
import ru.yandex.autotests.utils.morda.region.Region;
import ru.yandex.qatools.allure.annotations.Features;
import ru.yandex.qatools.allure.annotations.Stories;

import javax.ws.rs.client.Client;

import static ch.lambdaj.Lambda.having;
import static ch.lambdaj.Lambda.on;
import static org.hamcrest.Matchers.allOf;
import static org.hamcrest.Matchers.equalTo;
import static org.hamcrest.Matchers.notNullValue;
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
import static ru.yandex.autotests.mordaexportslib.ExportProvider.export;
import static ru.yandex.autotests.mordaexportslib.matchers.GeoMatcher.geo;
import static ru.yandex.autotests.utils.morda.language.Language.BE;
import static ru.yandex.autotests.utils.morda.language.Language.KK;
import static ru.yandex.autotests.utils.morda.language.Language.RU;
import static ru.yandex.autotests.utils.morda.language.Language.TT;
import static ru.yandex.autotests.utils.morda.language.Language.UK;
import static ru.yandex.autotests.utils.morda.language.LanguageManager.getTranslation;
import static ru.yandex.autotests.utils.morda.region.Region.SANKT_PETERBURG;

/**
 * User: ivannik
 * Date: 10.09.2014
 */
@Aqua.Test(title = "Bridges Block Items")
@Features("Mobile")
@Stories("Bridges Block Items")
@RunWith(CleanvarsParametrizedRunner.class)
public class BridgesItemsTest {

    @CleanvarsParametrizedRunner.Parameters("{3}, {4}, {5}")
    public static ParametersUtils parameters =
            parameters(SANKT_PETERBURG)
                    .withLanguages(RU, UK, BE, KK, TT)
                    .withUserAgents(TOUCH, WP8, ANDROID_HTC_SENS)
                    .withParameterProvider(new BridgesParametrProvider())
                    .withCleanvarsBlocks(BRIDGES, HIDDENTIME);

    private Language language;
    private String bridgeId;
    private BridgeInfo bridgeInfo;
    private BridgesEntry export;

    public BridgesItemsTest(MordaClient mordaClient, Client client, Cleanvars cleanvars, Region region,
                            Language language, UserAgent userAgent, String bridgeId, BridgeInfo bridgeInfo) {
        this.language = language;
        this.bridgeId = bridgeId;
        this.bridgeInfo = bridgeInfo;
        this.export = export(MordaExports.BRIDGES,
                having(on(BridgesEntry.class).getFrom(),
                        before("yyyy-MM-dd", "yyyy-MM-dd HH:mm:ss", cleanvars.getHiddenTime())),
                having(on(BridgesEntry.class).getTill(),
                        after("yyyy-MM-dd", "yyyy-MM-dd HH:mm:ss", cleanvars.getHiddenTime())),
                geo(region.getRegionIdInt()), having(on(BridgesEntry.class).getBridgeId(), equalTo(bridgeId)));
    }

    @Before
    public void setUp() {
        assumeThat("Не найден экспорт с id " + bridgeId, export, notNullValue());
    }

    @Test
    public void bridgeExportValues() {
        shouldMatchTo(bridgeInfo, allOf(
                having(on(BridgeInfo.class).getGeo(), equalTo(export.getGeo())),
                having(on(BridgeInfo.class).getBridgeId(), equalTo(export.getBridgeId())),
//                having(on(BridgeInfo.class).getBridgePriority(), equalTo(export.getBridgePriority())),
                having(on(BridgeInfo.class).getBridgeLower1(), equalTo(cutTime(export.getBridgeLower1()))),
                having(on(BridgeInfo.class).getBridgeLower2(), equalTo(cutTime(export.getBridgeLower2()))),
                having(on(BridgeInfo.class).getBridgeRaise1(), equalTo(cutTime(export.getBridgeRaise1()))),
                having(on(BridgeInfo.class).getBridgeRaise2(), equalTo(cutTime(export.getBridgeRaise2()))),
                having(on(BridgeInfo.class).getFrom(), equalTo(export.getFrom())),
                having(on(BridgeInfo.class).getTill(), equalTo(export.getTill()))
        ));
    }

    @Test
    public void bridgeName() {
        String[] textIdValues = bridgeInfo.getBridgeId().split("\\.");
        shouldHaveParameter(bridgeInfo, having(on(BridgeInfo.class).getBridgeName(),
                equalTo(getTranslation("home", textIdValues[0],
                        bridgeInfo.getBridgeId().substring(bridgeInfo.getBridgeId().indexOf('.') + 1), language))));
    }

    private static String cutTime(String time) {
        if (time != null && time.length() == 5 && time.startsWith("0")) {
            return time.substring(1);
        } else {
            return time;
        }
    }
}
