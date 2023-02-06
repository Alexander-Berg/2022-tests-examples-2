package ru.yandex.autotests.metrika.appmetrica.tests.ft.management.application;

import org.junit.AfterClass;
import org.junit.Before;
import org.junit.BeforeClass;
import org.junit.Test;
import ru.yandex.autotests.metrika.appmetrica.data.User;
import ru.yandex.autotests.metrika.appmetrica.parameters.AppListV2SortParameter;
import ru.yandex.autotests.metrika.appmetrica.parameters.ApplicationsRequestV2;
import ru.yandex.autotests.metrika.appmetrica.steps.UserSteps;
import ru.yandex.autotests.metrika.appmetrica.tests.Requirements;
import ru.yandex.autotests.metrika.appmetrica.tests.ft.management.TestData;
import ru.yandex.autotests.metrika.appmetrica.wrappers.GrantWrapper;
import ru.yandex.metrika.mobmet.management.Application;
import ru.yandex.metrika.mobmet.model.ApplicationsPage;
import ru.yandex.qatools.allure.annotations.Features;
import ru.yandex.qatools.allure.annotations.Stories;
import ru.yandex.qatools.allure.annotations.Title;

import java.util.Collections;
import java.util.List;
import java.util.stream.Collectors;

import static ch.lambdaj.Lambda.having;
import static ch.lambdaj.Lambda.on;
import static java.util.Comparator.comparing;
import static org.hamcrest.Matchers.allOf;
import static org.hamcrest.Matchers.containsString;
import static org.hamcrest.Matchers.equalTo;
import static org.hamcrest.Matchers.everyItem;
import static org.hamcrest.Matchers.hasItem;
import static org.hamcrest.Matchers.hasSize;
import static org.hamcrest.Matchers.not;
import static org.hamcrest.Matchers.notNullValue;
import static ru.yandex.autotests.irt.testutils.allure.TestSteps.assertThat;
import static ru.yandex.autotests.irt.testutils.allure.TestSteps.assumeThat;
import static ru.yandex.autotests.metrika.appmetrica.data.Partners.DIRECT;
import static ru.yandex.autotests.metrika.appmetrica.data.User.LOGIN;
import static ru.yandex.autotests.metrika.appmetrica.data.Users.SIMPLE_USER;
import static ru.yandex.autotests.metrika.appmetrica.data.Users.SIMPLE_USER_2;
import static ru.yandex.autotests.metrika.appmetrica.matchers.ResponseMatchers.equivalentTo;
import static ru.yandex.autotests.metrika.appmetrica.matchers.SortedByMatcher.sortedBy;
import static ru.yandex.autotests.metrika.appmetrica.tests.ft.management.TestData.GrantCreator.forUser;
import static ru.yandex.autotests.metrika.appmetrica.tests.ft.management.TestData.getApplicationWithAppNamePrefix;
import static ru.yandex.autotests.metrika.appmetrica.tests.ft.management.TestData.getDefaultLabel;
import static ru.yandex.metrika.api.management.client.external.GrantType.AGENCY_VIEW;

@Features(Requirements.Feature.Management.APPLICATION)
@Stories({
        Requirements.Story.Application.INFO,
        Requirements.Story.Application.LIST
})
@Title("Получение списка приложений (v2)")
public class GetApplicationsV2Test {
    private static final String APP_NAME_PREFIX = GetApplicationsV2Test.class.getSimpleName();

    private static final User USER = SIMPLE_USER;
    private static final User ANOTHER_USER = SIMPLE_USER_2;

    private final static UserSteps user = UserSteps.onTesting(USER);
    private final static UserSteps anotherUser = UserSteps.onTesting(ANOTHER_USER);

    private static final TestData.GrantCreator GRANTS = forUser(USER);

    private static Application simpleApplication;
    private static Application labelApplication;
    private static Application agencyApplication;

    private static Long labelId;

    @BeforeClass
    public static void setup() {
        simpleApplication = user.onApplicationSteps().addApplication(getApplicationWithAppNamePrefix(APP_NAME_PREFIX));

        labelId = user.onLabelSteps().addLabel(getDefaultLabel());
        labelApplication = user.onApplicationSteps().addApplication(getApplicationWithAppNamePrefix(APP_NAME_PREFIX));
        user.onLabelSteps().linkApplicationToLabel(labelApplication.getId(), labelId);

        agencyApplication = anotherUser.onApplicationSteps().addApplication(getApplicationWithAppNamePrefix(APP_NAME_PREFIX));
        anotherUser.onGrantSteps().createGrant(agencyApplication.getId(), new GrantWrapper(GRANTS.grant(AGENCY_VIEW, DIRECT)));
    }

    @Before
    public void assumeInit() {
        assumeThat("обычное приложение создано", simpleApplication, notNullValue());
        assumeThat("папка создана", labelId, notNullValue());
        assumeThat("приложение для папки создано", labelApplication, notNullValue());
        assumeThat("приложение для проверки агентских доступов создано", agencyApplication, notNullValue());
    }

    @Test
    public void defaultParams() {
        final ApplicationsRequestV2 request = new ApplicationsRequestV2();
        final ApplicationsPage page = user.onApplicationSteps().getApplicationsV2(request);
        // шаблоны матчеров не дружат друг с другом, поэтому проверяем по отдельности
        // зато у матчеров есть нормальные комментарии
        assertThat("параметр сортировки по умолчанию", page.getApplications(), sortedBy(comparing(Application::getName)));
        assertThat("параметры смещения по умолчанию", page.getApplications(), hasSize(page.getTotals().intValue()));
        assertThat("параметры фильтрации приложений по умолчанию", page.getApplications(), allOf(
                hasItem(having(on(Application.class).getId(), equalTo(simpleApplication.getId()))),
                hasItem(having(on(Application.class).getId(), equalTo(labelApplication.getId()))),
                not(hasItem(having(on(Application.class).getId(), equalTo(agencyApplication.getId()))))));
    }

    @Test
    public void sortedByName() {
        final ApplicationsRequestV2 request = new ApplicationsRequestV2().withSort(AppListV2SortParameter.name);
        final ApplicationsPage page = user.onApplicationSteps().getApplicationsV2(request);
        assertThat("список приложений отсортирован по дате получения доступа по неубыванию",
                page.getApplications(), sortedBy(comparing(Application::getName)));
    }

    @Test
    public void sortedByNameReversed() {
        final ApplicationsRequestV2 request = new ApplicationsRequestV2()
                .withSort(AppListV2SortParameter.name)
                .withReverse(true);
        final ApplicationsPage page = user.onApplicationSteps().getApplicationsV2(request);
        assertThat("список приложений отсортирован по дате получения доступа по невозрастанию",
                page.getApplications(), sortedBy(comparing(Application::getName).reversed()));
    }

    @Test
    public void limitOffset() {
        final ApplicationsRequestV2 request = new ApplicationsRequestV2()
                .withLimit(1L)
                .withOffset(2L)
                .withSearchString(APP_NAME_PREFIX);
        final ApplicationsPage page = user.onApplicationSteps().getApplicationsV2(request);

        final ApplicationsRequestV2 allRequest = new ApplicationsRequestV2()
                .withSearchString(APP_NAME_PREFIX);
        final ApplicationsPage allPage = user.onApplicationSteps().getApplicationsV2(allRequest);

        final ApplicationsPage expected = new ApplicationsPage()
                .withTotals((long) allPage.getApplications().size())
                .withApplications(Collections.singletonList(allPage.getApplications().get(1)));

        assertThat("запрос со смещением и лимитом вернул корректный ответ", page, equivalentTo(expected));
    }

    @Test
    public void searchByName() {
        final String namePart = labelApplication.getName().substring(1, 4);
        final ApplicationsRequestV2 request = new ApplicationsRequestV2().withSearchString(namePart);
        final ApplicationsPage page = user.onApplicationSteps().getApplicationsV2(request);

        final List<String> names = page.getApplications().stream().map(Application::getName).collect(Collectors.toList());

        assertThat("все имена приложений содержат искомую подстроку", names, everyItem(containsString(namePart)));
    }

    @Test
    public void agencyIncluded() {
        final ApplicationsRequestV2 request = new ApplicationsRequestV2().withIncludeAgencyApps(true);
        final ApplicationsPage page = user.onApplicationSteps().getApplicationsV2(request);
        assertThat("список приложений содержит агентское приложение", page.getApplications(),
                hasItem(having(on(Application.class).getId(), equalTo(agencyApplication.getId()))));
    }

    @Test
    public void agencyNotIncluded() {
        final ApplicationsRequestV2 request = new ApplicationsRequestV2();
        final ApplicationsPage page = user.onApplicationSteps().getApplicationsV2(request);
        assertThat("список приложений не содержит агентское приложение", page.getApplications(),
                not(hasItem(having(on(Application.class).getId(), equalTo(agencyApplication.getId())))));
    }

    @Test
    public void labelFilter() {
        final ApplicationsRequestV2 request = new ApplicationsRequestV2().withLabelId(labelId);
        final ApplicationsPage page = user.onApplicationSteps().getApplicationsV2(request);
        assertThat("запрос приложений в папке содержит искомое приложение",
                page.getApplications(), equivalentTo(Collections.singletonList(labelApplication)));
    }

    @AfterClass
    public static void teardown() {
        if (simpleApplication != null) {
            user.onApplicationSteps().deleteApplication(simpleApplication.getId());
        }
        if (labelApplication != null) {
            user.onApplicationSteps().deleteApplication(labelApplication.getId());
        }
        if (labelId != null) {
            user.onLabelSteps().deleteLabel(labelId);
        }
        if (agencyApplication != null) {
            anotherUser.onGrantSteps().deleteGrantIgnoringResult(agencyApplication.getId(), USER.get(LOGIN));
            anotherUser.onApplicationSteps().deleteApplication(agencyApplication.getId());
        }
    }
}
