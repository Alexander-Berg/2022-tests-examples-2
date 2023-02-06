package ru.yandex.autotests.metrika.tests.ft.report.metrika.filters.table;

import com.google.common.collect.ImmutableList;
import org.junit.Test;
import org.junit.runners.Parameterized;
import ru.yandex.autotests.httpclient.lite.core.IFormParameters;
import ru.yandex.autotests.metrika.Requirements;
import ru.yandex.autotests.metrika.data.common.handles.RequestTypes;
import ru.yandex.autotests.metrika.data.parameters.report.v1.TableReportParameters;
import ru.yandex.autotests.metrika.errors.ReportError;
import ru.yandex.qatools.allure.annotations.Features;
import ru.yandex.qatools.allure.annotations.Stories;
import ru.yandex.qatools.allure.annotations.Title;

import java.util.Collection;

import static org.apache.commons.lang3.ArrayUtils.toArray;
import static ru.yandex.autotests.metrika.data.common.counters.Counters.SENDFLOWERS_RU;
import static ru.yandex.autotests.metrika.data.parameters.FreeFormParameters.makeParameters;

/**
 * Created by sourx on 20.03.17.
 */
@Features(Requirements.Feature.DATA)
@Stories({Requirements.Story.Report.MANUAL_SAMPLES, Requirements.Story.Report.Type.TABLE})
@Title("Фильтры: на отобранных вручную параметрах запросов Table (негативные)")
public class ParticularsTableNegativeTest extends ParticularsBaseTableTest {

    @Parameterized.Parameter(value = 2)
    public ReportError error;

    protected static Object[] createParams(String title, ReportError error, IFormParameters... params) {
        return toArray(title, params, error);
    }

    @Test
    public void check() {
        userOnTest.onReportSteps().getReportAndExpectError(RequestTypes.TABLE, error, reportParameters);
    }

    @Parameterized.Parameters(name = "{0}")
    public static Collection<Object[]> createParameters() {
        return ImmutableList.of(
                createParams("METR-25694 invalid filter", ReportError.WRONG_FILTER,
                        new TableReportParameters()
                                .withId(SENDFLOWERS_RU)
                                .withDate1("2016-08-16")
                                .withDate2("2016-08-22")
                                .withDimension("ym:s:age")
                                .withFilters("\\\\")
                                .withMetric("ym:s:visits")),
                createParams("METR-26421 date1[date]", ReportError.WRONG_PARAM_NAME,
                        new TableReportParameters()
                                .withId(SENDFLOWERS_RU)
                                .withMetric("ym:s:visits"),
                        makeParameters("date1[date]", "2017-09-08 00:00:00.000000")),
                createParams("METR-44297 Too many values in filter", ReportError.TOO_MANY_VALUES_IN_FILTER_YM_LAST_SING_SEARCH_ENGINE_ROOT,
                        new TableReportParameters()
                                .withId(SENDFLOWERS_RU)
                                .withDate1("2016-08-16")
                                .withDate2("2016-08-22")
                                .withDimension("ym:s:age")
                                .withFilters("ym:s:lastSignSearchEngineRoot IN('google','yandex','mail_ru','bing','yahoo','duckduckgo','baidu','rambler','unknown','ecosia','coccoc','so360','qwant','sogou','naver','ukr_net','nigma','tut_by','aol_search','meta_ua','poisk_ru','seznam','babylon_search','qip_search','ask_com','dogpile','daum','yaani','icq_search','search_gmx_net','startpagina','web_de','hi_ru','wow','alhea','k9safesearch','skydns','zapmeta','1and1','hotline','istella','liveinternet','finnerask','sputnik','biglobe_ne','kvasir','yam','onet_pl','wp_pl','virgilio_it','voila','about','startsiden_no','metacrawler','sapo_pt','najdi_si','goo_ne','icerocket','arama','scrubtheweb','netsearch','myahint','mamma','yippy','acoon','amfibi','gigablast','hotbot','hakia','speedbit','smilebox','crawler','7search','incredibar','searchcompletion','plusnetwork','searchya','iminet','funmoods','softonic','sweetim','handycafe','avg','searchresults','v9','infospace','gmx_net','kaz_kz','gigabase','km_search','rx24','topsy','blekko','kazah_ru','nur_kz','winamp_search','pivim_com','gbg_bg','aport','myweb_search','gde_ru','mystart','daemon_search','i_ua','conduit','metabot_ru','webalta','quintura','magna','gogo','alexa_web','cuil_com','exalead_fr','wikia_search','altavista','msn','livesearch','lycos','search_com','bigmir_net','all_by')")
                                .withMetric("ym:s:visits")),
                createParams("METR-44043 filter by counterIDName", ReportError.AMBIGUOUS_REQUEST,
                        new TableReportParameters()
                                .withIds(6025L, 6364L) // оба счётчика имеют название test
                                .withFilters("ym:s:counterIDName IN ('test')")
                                .withMetric("ym:s:visits")),
                createParams("METR-43773 regexp invalid escape sequence", ReportError.WRONG_FILTER,
                        new TableReportParameters()
                                .withId(SENDFLOWERS_RU)
                                .withDate1("2016-08-16")
                                .withDate2("2016-08-22")
                                .withDimension("ym:s:age")
                                .withFilters("ym:s:searchPhrase!~'дом\\\\sкофе|кофе\\\\дом|domcof|domkof|dom kof|coffeedom|cofedom|домкофе|кофедом|ljv rjat|\\\\.ru|\\\\.ру'")
                                .withMetric("ym:s:visits")
                )
        );
    }
}
