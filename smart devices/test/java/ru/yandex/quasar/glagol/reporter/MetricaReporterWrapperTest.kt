/*
 * (C) Copyright 2021 Yandex, LLC. All rights reserved.
 */

package ru.yandex.quasar.glagol.reporter

import org.junit.Assert
import org.junit.Before
import org.junit.Test

class MetricaReporterWrapperTest {

    private lateinit var internal : MockIReporter
    private lateinit var external : MockIReporter
    private lateinit var wrapper : MetricaReporterWrapper

    @Before
    fun prepareWrapper() {
        internal = MockIReporter()
        external = MockIReporter()
        wrapper = MetricaReporterWrapper(internal, external)
    }

    @Test
    fun testReportCalls() {
        wrapper.reportEvent("1")
        Assert.assertEquals(internal.args, external.args)

        wrapper.reportEvent("1", "2")
        Assert.assertEquals(internal.args, external.args)

        wrapper.reportEvent("3", mutableMapOf(Pair("1", 2), Pair("2", 15)))
        Assert.assertEquals(internal.args, external.args)
    }

    @Test
    fun testErrorCalls() {
        wrapper.reportError("1", "2")
        Assert.assertEquals(internal.args, external.args)

        wrapper.reportError("2", RuntimeException("ololo"))
        Assert.assertEquals(internal.args, external.args)

        wrapper.reportError("3", "4", IllegalStateException("ololo2"))
        Assert.assertEquals(internal.args, external.args)

        wrapper.reportUnhandledException(IllegalArgumentException("ololo3"))
        Assert.assertEquals(internal.args, external.args)
    }

    @Test
    fun testUserSessionCalls() {
        wrapper.resumeSession()
        Assert.assertEquals(internal.args, external.args)

        wrapper.pauseSession()
        Assert.assertEquals(internal.args, external.args)

        wrapper.setUserProfileID("user")
        Assert.assertEquals(internal.args, external.args)

        wrapper.sendEventsBuffer()
        Assert.assertEquals(internal.args, external.args)
    }



}
