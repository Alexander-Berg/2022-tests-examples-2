package ru.yandex.autotests.mordabackend.mobile.alert;

import org.junit.Before;
import org.junit.Test;
import org.junit.runner.RunWith;
import ru.yandex.aqua.annotations.project.Aqua;
import ru.yandex.autotests.mordabackend.MordaClient;
import ru.yandex.autotests.mordabackend.beans.alert.Alert;
import ru.yandex.autotests.mordabackend.beans.alert.AlertItem;
import ru.yandex.autotests.mordabackend.beans.cleanvars.Cleanvars;
import ru.yandex.autotests.mordabackend.useragents.UserAgent;
import ru.yandex.autotests.mordabackend.utils.parameters.ParametersUtils;
import ru.yandex.autotests.mordabackend.utils.runner.CleanvarsParametrizedRunner;
import ru.yandex.autotests.mordaexportsclient.beans.AlertTypesEntry;
import ru.yandex.autotests.utils.morda.region.Region;
import ru.yandex.qatools.allure.annotations.Features;
import ru.yandex.qatools.allure.annotations.Stories;

import javax.ws.rs.client.Client;
import java.util.Collections;
import java.util.List;
import java.util.Map;

import static ch.lambdaj.Lambda.extract;
import static ch.lambdaj.Lambda.having;
import static ch.lambdaj.Lambda.index;
import static ch.lambdaj.Lambda.on;
import static ch.lambdaj.Lambda.sort;
import static org.hamcrest.MatcherAssert.assertThat;
import static org.hamcrest.Matchers.allOf;
import static org.hamcrest.Matchers.anyOf;
import static org.hamcrest.Matchers.containsString;
import static org.hamcrest.Matchers.equalTo;
import static org.hamcrest.Matchers.greaterThan;
import static org.hamcrest.Matchers.hasSize;
import static org.hamcrest.Matchers.isEmptyOrNullString;
import static org.hamcrest.Matchers.notNullValue;
import static ru.yandex.autotests.morda.utils.matchers.AllOfDetailedMatcher.allOfDetailed;
import static ru.yandex.autotests.morda.utils.matchers.NestedPropertyMatcher.hasPropertyWithValue;
import static ru.yandex.autotests.mordabackend.blocks.CleanvarsBlock.ALERT;
import static ru.yandex.autotests.mordabackend.blocks.CleanvarsBlock.ISHOLIDAY;
import static ru.yandex.autotests.mordabackend.blocks.CleanvarsBlock.LOCAL;
import static ru.yandex.autotests.mordabackend.useragents.UserAgent.ANDROID_HTC_SENS;
import static ru.yandex.autotests.mordabackend.useragents.UserAgent.TOUCH;
import static ru.yandex.autotests.mordabackend.utils.CleanvarsUtils.shouldMatchTo;
import static ru.yandex.autotests.mordabackend.utils.parameters.ParametersUtils.parameters;
import static ru.yandex.autotests.mordabackend.utils.predicates.ExportDateMatcher.after;
import static ru.yandex.autotests.mordabackend.utils.predicates.ExportDateMatcher.before;
import static ru.yandex.autotests.mordaexportsclient.MordaExports.ALERT_TYPES;
import static ru.yandex.autotests.mordaexportslib.ExportProvider.exports;
import static ru.yandex.autotests.utils.morda.region.Region.CHELYABINSK;
import static ru.yandex.autotests.utils.morda.region.Region.KAZAN;
import static ru.yandex.autotests.utils.morda.region.Region.KIEV;
import static ru.yandex.autotests.utils.morda.region.Region.LYUDINOVO;
import static ru.yandex.autotests.utils.morda.region.Region.MINSK;
import static ru.yandex.autotests.utils.morda.region.Region.MOSCOW;
import static ru.yandex.autotests.utils.morda.region.Region.NIZHNIY_NOVGOROD;
import static ru.yandex.autotests.utils.morda.region.Region.NOVOSIBIRSK;
import static ru.yandex.autotests.utils.morda.region.Region.SAMARA;
import static ru.yandex.autotests.utils.morda.region.Region.SANKT_PETERBURG;
import static ru.yandex.autotests.utils.morda.region.Region.VOLGOGRAD;
import static ru.yandex.qatools.matchers.collection.HasSameItemsAsListMatcher.hasSameItemsAsList;

/**
 * @author Ivan Nikolaev <ivannik@yandex-team.ru>
 */
@Aqua.Test(title = "Alert Block")
@Features("Mobile")
@Stories("Alert Block")
@RunWith(CleanvarsParametrizedRunner.class)
public class AlertTouchBlockTest {

    @CleanvarsParametrizedRunner.Parameters("{3}, {4}")
    public static ParametersUtils parameters =
            parameters(MOSCOW, KIEV, SANKT_PETERBURG,
                    SAMARA, MINSK, CHELYABINSK, NOVOSIBIRSK, KAZAN, NIZHNIY_NOVGOROD, VOLGOGRAD, LYUDINOVO)
                    .withUserAgents(TOUCH, ANDROID_HTC_SENS)
                    .withCleanvarsBlocks(ALERT, ISHOLIDAY, LOCAL);

    private final Cleanvars cleanvars;
    private final Client client;
    private final UserAgent userAgent;

    private List<AlertTypesEntry> alertTypesEntry;

    public AlertTouchBlockTest(MordaClient mordaClient, Client client, Cleanvars cleanvars, Region region,
                               UserAgent userAgent) {
        this.cleanvars = cleanvars;
        this.client = client;
        this.userAgent = userAgent;
    }

    @Before
    public void init() {
        boolean isHoliday = cleanvars.getIsHoliday() != null && !cleanvars.getIsHoliday().equals("0");
        String weekDayNumber = cleanvars.getLocal().getWday() == 0 ? "7" :
                String.valueOf(cleanvars.getLocal().getWday());
        String time = cleanvars.getLocal().getHour() + ":" + cleanvars.getLocal().getMin();


        List<AlertTypesEntry> alerts = sort(exports(ALERT_TYPES,
                anyOf(
                        having(on(AlertTypesEntry.class).getWeekDay(),
                                isHoliday ? equalTo("holiday") : equalTo("workday")),
                        having(on(AlertTypesEntry.class).getWeekDay(), containsString(weekDayNumber)),
                        having(on(AlertTypesEntry.class).getWeekDay(), isEmptyOrNullString())
                ),
                anyOf(
                        having(on(AlertTypesEntry.class).getTimeFrom(),
                                before("HH:mm", "HH:mm", time)),
                        having(on(AlertTypesEntry.class).getTimeFrom(), isEmptyOrNullString())
                ),
                anyOf(
                        having(on(AlertTypesEntry.class).getTimeTill(),
                                after("HH:mm", "HH:mm", time)),
                        having(on(AlertTypesEntry.class).getTimeTill(), isEmptyOrNullString())
                )

        ), on(AlertTypesEntry.class).getWeight());

        Collections.reverse(alerts);
        alertTypesEntry = alerts;
        assertThat("Нет соответствующего экспорта alert_types", alertTypesEntry, hasSize(greaterThan(0)));
    }

    @Test
    public void alert() {
        shouldMatchTo(cleanvars.getAlert(), allOfDetailed(
                hasPropertyWithValue(on(Alert.class).getProcessed(), equalTo(1)),
                anyOf(
                        allOf(
                                hasPropertyWithValue(on(Alert.class).getShow(), equalTo(1)),
                                hasPropertyWithValue(on(Alert.class).getList(), hasSize(greaterThan(0)))
                        ),
                        allOf(
                                hasPropertyWithValue(on(Alert.class).getShow(), equalTo(0)),
                                hasPropertyWithValue(on(Alert.class).getList(), hasSize(0))
                        )
                )

        ));
    }

    @Test
    public void alertItems() {
        Map<String, AlertTypesEntry> entries = index(alertTypesEntry, on(AlertTypesEntry.class).getId());
        for (AlertItem alertItem : cleanvars.getAlert().getList()) {
            AlertTypesEntry export = entries.get(alertItem.getId());
            shouldMatchTo(alertItem, allOfDetailed(
                    hasPropertyWithValue(on(AlertItem.class).getId(), equalTo(export.getId())),
                    hasPropertyWithValue(on(AlertItem.class).getGroup(), equalTo(export.getGroup())),
                    hasPropertyWithValue(on(AlertItem.class).getGroupping(), equalTo(export.getGroupping())),
                    hasPropertyWithValue(on(AlertItem.class).getWeight(), equalTo(export.getWeight())),
                    hasPropertyWithValue(on(AlertItem.class).getWeekDay(), equalTo(export.getWeekDay())),
                    hasPropertyWithValue(on(AlertItem.class).getTimeFrom(), equalTo(export.getTimeFrom())),
                    hasPropertyWithValue(on(AlertItem.class).getBk(), equalTo(export.getBk())),
                    hasPropertyWithValue(on(AlertItem.class).getTargeting(), equalTo(export.getTargeting())),

                    hasPropertyWithValue(on(AlertItem.class).getData(), notNullValue())
                    ));
            shouldMatchTo(alertItem.getRF(), equalTo(export.getRF()));
        }
    }

    @Test
    public void alertSorting() {
        List<String> expectrdIds = extract(alertTypesEntry, on(AlertTypesEntry.class).getId());
        List<String> actualIds = extract(cleanvars.getAlert().getList(), on(AlertItem.class).getId());

        for (String id : extract(alertTypesEntry, on(AlertTypesEntry.class).getId())) {
            if (!actualIds.contains(id)) {
                expectrdIds.remove(id);
            }
        }

        shouldMatchTo(actualIds, hasSameItemsAsList(expectrdIds));
    }
}
