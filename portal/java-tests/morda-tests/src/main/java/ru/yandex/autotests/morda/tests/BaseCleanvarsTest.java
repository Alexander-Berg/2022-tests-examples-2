package ru.yandex.autotests.morda.tests;

import org.junit.Before;
import org.junit.Rule;
import org.junit.Test;
import ru.yandex.autotests.morda.api.MordaClient;
import ru.yandex.autotests.morda.beans.cleanvars.MordaCleanvars;
import ru.yandex.autotests.morda.pages.Morda;
import ru.yandex.autotests.morda.rules.allure.AllureLoggingRule;
import ru.yandex.qatools.allure.annotations.Stories;

import static org.hamcrest.MatcherAssert.assertThat;
import static org.hamcrest.Matchers.notNullValue;
import static org.hamcrest.Matchers.equalTo;

/**
 * Created by wwax on 09.09.16.
 */
public abstract class BaseCleanvarsTest<T> {
    public static final MordaTestsProperties CONFIG = new MordaTestsProperties();

    protected MordaCleanvars cleanvars;
    private Morda<?> morda;

    @Rule
    public AllureLoggingRule allureLoggingRule = new AllureLoggingRule();

    public BaseCleanvarsTest(Morda<?> morda) {
        this.morda = morda;
    }

    @Before
    public void init() {
        this.cleanvars = new MordaClient().cleanvars(morda).read();
    }

    public abstract T getBlock();
    public abstract int getShow();

    @Test
    @Stories("block")
    public void checkExists() {
        assertThat(this.getBlock(), notNullValue());
        assertThat(this.getShow(), equalTo(1));
    }
}
