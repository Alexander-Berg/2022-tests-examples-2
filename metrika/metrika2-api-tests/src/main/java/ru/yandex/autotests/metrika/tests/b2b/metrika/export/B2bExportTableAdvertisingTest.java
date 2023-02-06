package ru.yandex.autotests.metrika.tests.b2b.metrika.export;

import org.junit.Before;
import ru.yandex.autotests.metrika.Requirements;
import ru.yandex.autotests.metrika.data.common.DateConstants;
import ru.yandex.autotests.metrika.data.common.counters.Counter;
import ru.yandex.autotests.metrika.data.parameters.management.v1.ClientsParameters;
import ru.yandex.autotests.metrika.data.parameters.report.v1.TableReportParameters;
import ru.yandex.qatools.allure.annotations.Features;
import ru.yandex.qatools.allure.annotations.Stories;
import ru.yandex.qatools.allure.annotations.Title;

import java.util.List;

import static ru.yandex.autotests.metrika.data.common.counters.Counter.ID;
import static ru.yandex.autotests.metrika.data.common.counters.Counter.U_LOGIN;
import static ru.yandex.autotests.metrika.data.common.counters.Counters.SENDFLOWERS_RU;
import static ru.yandex.autotests.metrika.data.common.handles.RequestTypes.TABLE;
import static ru.yandex.autotests.metrika.data.parameters.management.v1.DelegateParameters.ulogin;

/**
 * Created by sourx on 27/06/16.
 */
@Features(Requirements.Feature.DATA)
@Stories({Requirements.Story.Report.Type.TABLE, Requirements.Story.Report.Format.CSV,
        Requirements.Story.Report.Format.XLSX})
@Title("B2B - Экспорт отчета 'таблица' по кликам Директа в excel")
public class B2bExportTableAdvertisingTest extends BaseB2bExportTest {
    private static final Counter COUNTER = SENDFLOWERS_RU;

    private static final String START_DATE = DateConstants.Advertising.START_DATE;
    private static final String END_DATE = DateConstants.Advertising.END_DATE;

    private static final String PRESET = "sources_direct_clicks";

    @Before
    public void setup() {
        List<String> directClientLogins = userOnRef.onManagementSteps().onClientSteps().getClientLogins(
                new ClientsParameters()
                        .withCounters(COUNTER.get(ID))
                        .withDate1(START_DATE)
                        .withDate2(END_DATE),
                ulogin(COUNTER.get(U_LOGIN)));

        requestType = TABLE;
        reportParameters = new TableReportParameters()
                .withId(COUNTER.get(ID))
                .withPreset(PRESET)
                .withDate1(START_DATE)
                .withDate2(END_DATE)
                .withAccuracy("low")
                .withDirectClientLogins(directClientLogins);
    }
}
