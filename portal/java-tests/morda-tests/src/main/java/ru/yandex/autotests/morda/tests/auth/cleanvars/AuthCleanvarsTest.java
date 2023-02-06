package ru.yandex.autotests.morda.tests.auth.cleanvars;

import org.junit.Before;
import org.junit.Test;
import org.junit.runner.RunWith;
import org.junit.runners.Parameterized;
import ru.yandex.aqua.annotations.project.Aqua;
import ru.yandex.autotests.morda.beans.cleanvars.MordaCleanvars;
import ru.yandex.autotests.morda.beans.cleanvars.authinfo.AuthInfo;
import ru.yandex.autotests.morda.pages.Morda;
import ru.yandex.autotests.morda.pages.comtr.DesktopComTrFootballMorda;
import ru.yandex.autotests.morda.pages.comtr.DesktopComTrMorda;
import ru.yandex.autotests.morda.pages.comtr.DesktopFamilyComTrMorda;
import ru.yandex.autotests.morda.pages.comtr.PdaComTrMorda;
import ru.yandex.autotests.morda.pages.comtr.TouchComTrMorda;
import ru.yandex.autotests.morda.pages.comtr.TouchComTrWpMorda;
import ru.yandex.autotests.morda.pages.main.DesktopFamilyMainMorda;
import ru.yandex.autotests.morda.pages.main.DesktopFirefoxMorda;
import ru.yandex.autotests.morda.pages.main.DesktopMainMorda;
import ru.yandex.autotests.morda.pages.main.PdaMainMorda;
import ru.yandex.autotests.morda.pages.main.TabletMainMorda;
import ru.yandex.autotests.morda.pages.main.TelMainMorda;
import ru.yandex.autotests.morda.pages.main.TouchMainMorda;
import ru.yandex.autotests.morda.pages.main.TouchMainWpMorda;
import ru.yandex.autotests.morda.pages.tv.TvSmartMorda;
import ru.yandex.autotests.morda.rules.users.MordaUserTag;
import ru.yandex.autotests.morda.tests.MordaTestTags;
import ru.yandex.autotests.morda.tests.auth.AuthTest;
import ru.yandex.qatools.allure.annotations.Features;
import ru.yandex.qatools.allure.annotations.Step;
import ru.yandex.qatools.usermanager.beans.UserData;

import java.util.ArrayList;
import java.util.Collection;
import java.util.List;

import static ch.lambdaj.Lambda.on;
import static org.hamcrest.MatcherAssert.assertThat;
import static org.hamcrest.Matchers.empty;
import static org.hamcrest.Matchers.equalTo;
import static org.hamcrest.Matchers.not;
import static org.hamcrest.Matchers.notNullValue;
import static ru.yandex.autotests.morda.matchers.AllOfDetailedMatcher.allOfDetailed;
import static ru.yandex.autotests.morda.matchers.NestedPropertyMatcher.hasPropertyWithValue;

/**
 * User: eoff (eoff@yandex-team.ru)
 * Date: 19/09/16
 */

@Aqua.Test(title = MordaTestTags.AUTH)
@RunWith(Parameterized.class)
@Features({MordaTestTags.CLEANVARS, MordaTestTags.AUTH})
public class AuthCleanvarsTest extends AuthTest {

    protected Morda<?> morda;
    protected UserData user;

    public AuthCleanvarsTest(Morda<?> morda) {
        this.morda = morda;
    }

    @Parameterized.Parameters(name = "{0}")
    public static Collection<Morda<?>> data() {
        List<Morda<?>> data = new ArrayList<>();
        data.addAll(DesktopComTrFootballMorda.getDefaultList(CONFIG.pages().getEnvironment()));
        data.addAll(DesktopComTrMorda.getDefaultList(CONFIG.pages().getEnvironment()));
        data.addAll(DesktopFamilyComTrMorda.getDefaultList(CONFIG.pages().getEnvironment()));
        data.addAll(PdaComTrMorda.getDefaultList(CONFIG.pages().getEnvironment()));
        data.addAll(TouchComTrMorda.getDefaultList(CONFIG.pages().getEnvironment()));
        data.addAll(TouchComTrWpMorda.getDefaultList(CONFIG.pages().getEnvironment()));

        data.addAll(DesktopFamilyMainMorda.getDefaultList(CONFIG.pages().getEnvironment()));
        data.addAll(DesktopFirefoxMorda.getDefaultList(CONFIG.pages().getEnvironment()));
        data.addAll(DesktopMainMorda.getDefaultList(CONFIG.pages().getEnvironment()));
        data.addAll(PdaMainMorda.getDefaultList(CONFIG.pages().getEnvironment()));
        data.addAll(TabletMainMorda.getDefaultList(CONFIG.pages().getEnvironment()));
        data.addAll(TelMainMorda.getDefaultList(CONFIG.pages().getEnvironment()));
        data.addAll(TouchMainMorda.getDefaultList(CONFIG.pages().getEnvironment()));
        data.addAll(TouchMainWpMorda.getDefaultList(CONFIG.pages().getEnvironment()));

        data.addAll(TvSmartMorda.getDefaultList(CONFIG.pages().getEnvironment()));
        return data;
    }

    @Before
    public void getUser() {
        user = userManagerRule.getMordaUser(MordaUserTag.DEFAULT);
        morda.login(user);
    }

    @Test
    public void checkAuth() throws Exception {
        MordaCleanvars cleanvars = client.cleanvars(morda, "AuthInfo").read();

        shouldBeAuthorized(cleanvars);
    }

    @Step("Should be authorized")
    protected void shouldBeAuthorized(MordaCleanvars cleanvars) {
        assertThat("AuthInfo not found", cleanvars.getAuthInfo(), notNullValue());
        AuthInfo authInfo = cleanvars.getAuthInfo();

        assertThat(authInfo, allOfDetailed(
                hasPropertyWithValue(on(AuthInfo.class).getLogged(), equalTo(1)),
                hasPropertyWithValue(on(AuthInfo.class).getLogin(), equalTo(user.getLogin())),
                hasPropertyWithValue(on(AuthInfo.class).getStatus(), equalTo("VALID")),
                hasPropertyWithValue(on(AuthInfo.class).getUsers(), not(empty()))
        ));
    }
}
