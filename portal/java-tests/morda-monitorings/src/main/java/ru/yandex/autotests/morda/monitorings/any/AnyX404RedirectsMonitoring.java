package ru.yandex.autotests.morda.monitorings.any;

import org.junit.ClassRule;
import org.junit.Rule;
import org.junit.Test;
import org.junit.runner.RunWith;
import org.junit.runners.Parameterized;
import ru.yandex.aqua.annotations.project.Aqua;
import ru.yandex.autotests.morda.tests.any.AnyX404RedirectsTest;
import ru.yandex.qatools.allure.annotations.Features;
import ru.yandex.qatools.monitoring.MonitoringNotifierRule;
import ru.yandex.qatools.monitoring.golem.GolemEvent;
import ru.yandex.qatools.monitoring.golem.GolemObject;
import ru.yandex.qatools.monitoring.graphite.GraphiteMetric;
import ru.yandex.qatools.monitoring.graphite.GraphiteMetricPrefix;
import ru.yandex.qatools.monitoring.yasm.YasmSignal;

import static ru.yandex.qatools.monitoring.MonitoringNotifierRule.notifierRule;

/**
 * User: eoff (eoff@yandex-team.ru)
 * Date: 29/06/16
 */
@Aqua.Test(title = "Редиректы any")
@Features({"Any", "x404_redirects"})
@RunWith(Parameterized.class)
@GolemObject("portal_any")
public class AnyX404RedirectsMonitoring extends AnyX404RedirectsTest {

    @Rule
    @ClassRule
    public static MonitoringNotifierRule notifierRule = notifierRule();

    public AnyX404RedirectsMonitoring(String fromUrl, String toUrl) {
        super(fromUrl, toUrl);
    }

    @Test
    @Override
    @GolemEvent("any")
    @YasmSignal(signal = "redirect_any_%s_tttt")
    public void anyRedirect() throws Exception {
        super.anyRedirect();
    }

    @Test
    @Override
    @GolemEvent("plain")
    @YasmSignal(signal = "redirect_any_plain_%s_tttt")
    public void plainRedirect() throws Exception {
        super.plainRedirect();
    }
}
