// Copyright 2021 Yandex LLC. All rights reserved.

package com.yandex.tv.services.policymanagerservice

import android.app.Application
import androidx.test.core.app.ApplicationProvider
import com.yandex.tv.services.policymanagerservice.model.PolicyManagerServiceApiImpl
import com.yandex.tv.services.policymanagerservice.model.SYSTEM_FEATURE_CHILD_MODE
import com.yandex.tv.services.policymanagerservice.ui.settings.Limit
import org.hamcrest.Matchers.equalTo
import org.hamcrest.MatcherAssert.assertThat
import org.junit.Before
import org.junit.Test
import org.junit.runner.RunWith
import org.robolectric.RobolectricTestRunner
import org.robolectric.Shadows

@RunWith(RobolectricTestRunner::class)
class PolicyManagerServiceApiTest {

    private val app = ApplicationProvider.getApplicationContext<Application>()
    private var apiImpl = PolicyManagerServiceApiImpl(app)
    private val api: PolicyManagerServiceApi get() = apiImpl

    init {
        Shadows.shadowOf(app.packageManager).setSystemFeature(SYSTEM_FEATURE_CHILD_MODE, true)
    }

    @Before
    fun setPin() {
        apiImpl.setPin("1111")
    }

    @Test
    fun `check isTvProgramsAvailable() with different policy settings`() {
        apiImpl.setPolicy(PolicyLevel.NO_LIMITS.ordinal)
        assertThat(api.isTvProgramAvailable(Limit.AGE_6.age), equalTo(true))

        apiImpl.setPolicy(PolicyLevel.LIMITED.ordinal)
        apiImpl.setLimitedAgeLimit(Limit.AGE_6.age)
        assertThat(api.isTvProgramAvailable(Limit.AGE_0.age), equalTo(true))
        assertThat(api.isTvProgramAvailable(Limit.AGE_6.age), equalTo(false))
        assertThat(api.isTvProgramAvailable(Limit.AGE_12.age), equalTo(false))

        apiImpl.setPolicy(PolicyLevel.KIDS.ordinal)
        apiImpl.setKidsAgeLimit(Limit.AGE_12.age)
        assertThat(api.isTvProgramAvailable(Limit.AGE_0.age), equalTo(true))
        assertThat(api.isTvProgramAvailable(Limit.AGE_6.age), equalTo(true))
        assertThat(api.isTvProgramAvailable(Limit.AGE_12.age), equalTo(false))
    }

    @Test
    fun `check getPolicy() returns actual policy`() {
        val policy = Policy(PolicyLevel.LIMITED, SearchMode.FAMILY, Limit.AGE_16.age)
        apiImpl.setPolicy(policy.level.ordinal)
        apiImpl.setLimitedPolicySearchMode(policy.searchMode)
        apiImpl.setLimitedAgeLimit(policy.ageLimit)
        assertThat(policy, equalTo(api.policy))
    }

    @Test
    fun `check all content available before PIN is set`() {
        apiImpl = PolicyManagerServiceApiImpl(app)
        assertThat(api.isTvProgramAvailable(Limit.AGE_18.age), equalTo(true))
        assertThat(api.policy, equalTo(DEFAULT_POLICY))
        assertThat(api.isAppAvailable(IMAGINARY_APP_PACKAGE_NAME), equalTo(true))
        assertThat(api.isSiteAvailable(IMAGINARY_SITE_HOST_NAME), equalTo(true))
    }

    @Test
    fun `check isAppAvailable() with different policy settings`() {
        apiImpl.setAppIsAvailable(IMAGINARY_APP_PACKAGE_NAME, PolicyLevel.KIDS.ordinal, false)

        apiImpl.setPolicy(PolicyLevel.NO_LIMITS.ordinal)
        assertThat(api.isAppAvailable(IMAGINARY_APP_PACKAGE_NAME), equalTo(true))

        apiImpl.setPolicy(PolicyLevel.LIMITED.ordinal)
        assertThat(api.isAppAvailable(IMAGINARY_APP_PACKAGE_NAME), equalTo(true))

        apiImpl.setPolicy(PolicyLevel.KIDS.ordinal)
        assertThat(api.isAppAvailable(IMAGINARY_APP_PACKAGE_NAME), equalTo(false))
    }

    @Test
    fun `check isSiteAvailable() with different policy settings`() {
        apiImpl.setSiteIsAvailable(IMAGINARY_SITE_HOST_NAME, PolicyLevel.LIMITED.ordinal, false)

        apiImpl.setPolicy(PolicyLevel.NO_LIMITS.ordinal)
        assertThat(api.isSiteAvailable(IMAGINARY_SITE_HOST_NAME), equalTo(true))

        apiImpl.setPolicy(PolicyLevel.LIMITED.ordinal)
        assertThat(api.isSiteAvailable(IMAGINARY_SITE_HOST_NAME), equalTo(false))

        apiImpl.setPolicy(PolicyLevel.KIDS.ordinal)
        assertThat(api.isSiteAvailable(IMAGINARY_SITE_HOST_NAME), equalTo(true))
    }

    companion object {
        private const val IMAGINARY_APP_PACKAGE_NAME = "com.somecompany.someapp"
        private const val IMAGINARY_SITE_HOST_NAME = "somesite.com"
        private val DEFAULT_POLICY = Policy(PolicyLevel.LIMITED, SearchMode.MODERATE, Limit.NO_LIMIT.age)
    }
}
