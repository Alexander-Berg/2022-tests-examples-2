package com.yandex.launcher.updaterapp.ota

import com.yandex.launcher.updaterapp.BaseRobolectricTest
import com.yandex.launcher.updaterapp.ota.updater.recovery.RecoveryUpdater
import org.junit.Assert.assertThrows
import org.junit.Before
import org.junit.Test
import org.mockito.kotlin.doReturn
import org.mockito.kotlin.spy
import org.mockito.kotlin.whenever
import java.util.Properties

class RecoveryUpdaterTest : BaseRobolectricTest() {

    lateinit var recoveryUpdater: RecoveryUpdater

    @Before
    override fun setUp() {
        super.setUp()
        recoveryUpdater = spy(RecoveryUpdater(app, otaUpdateContext))
    }

    @Test
    fun `should allow same dimlist and values to pass check`() {
        val metadata = Properties().apply {
            put("yndx.dimlist", "wifi,tuner")
            put("yndx.dim.wifi", "value_wifi")
            put("yndx.dim.tuner", "value_tuner")
        }

        whenever(recoveryUpdater.readSystemProperty("ro.yndx.dimlist")).doReturn("wifi,tuner")
        whenever(recoveryUpdater.readSystemProperty("ro.yndx.dim.wifi")).doReturn("value_wifi")
        whenever(recoveryUpdater.readSystemProperty("ro.yndx.dim.tuner")).doReturn("value_tuner")

        recoveryUpdater.checkDimLists(metadata)
    }

    @Test
    fun `should not allow same dimlist and different value to pass check`() {
        val metadata = Properties().apply {
            put("yndx.dimlist", "wifi,tuner")
            put("yndx.dim.wifi", "value_wifi")
            put("yndx.dim.tuner", "value_tuner")
        }

        whenever(recoveryUpdater.readSystemProperty("ro.yndx.dimlist")).doReturn("wifi,tuner")
        whenever(recoveryUpdater.readSystemProperty("ro.yndx.dim.wifi")).doReturn("value_wifi")
        whenever(recoveryUpdater.readSystemProperty("ro.yndx.dim.tuner")).doReturn("value_tuner_1")

        assertThrows(Exception::class.java) { recoveryUpdater.checkDimLists(metadata) }
    }

    @Test
    fun `should not allow lesser dimlist to pass check`() {
        val metadata = Properties().apply {
            put("yndx.dimlist", "wifi,tuner")
            put("yndx.dim.wifi", "value_wifi")
            put("yndx.dim.tuner", "value_tuner")
        }

        whenever(recoveryUpdater.readSystemProperty("ro.yndx.dimlist")).doReturn("wifi")
        whenever(recoveryUpdater.readSystemProperty("ro.yndx.dim.wifi")).doReturn("value_wifi")

        assertThrows(Exception::class.java) { recoveryUpdater.checkDimLists(metadata) }
    }

    @Test
    fun `should not allow greater dimlist to pass check`() {
        val metadata = Properties().apply {
            put("yndx.dimlist", "wifi,tuner")
            put("yndx.dim.wifi", "value_wifi")
            put("yndx.dim.tuner", "value_tuner")
        }

        whenever(recoveryUpdater.readSystemProperty("ro.yndx.dimlist")).doReturn("wifi,tuner,board")
        whenever(recoveryUpdater.readSystemProperty("ro.yndx.dim.wifi")).doReturn("value_wifi")
        whenever(recoveryUpdater.readSystemProperty("ro.yndx.dim.tuner")).doReturn("value_tuner")
        whenever(recoveryUpdater.readSystemProperty("ro.yndx.dim.board")).doReturn("value_board")

        assertThrows(Exception::class.java) { recoveryUpdater.checkDimLists(metadata) }
    }

    @Test
    fun `should not allow lesser dimlist and different value to pass check`() {
        val metadata = Properties().apply {
            put("yndx.dimlist", "wifi,tuner")
            put("yndx.dim.wifi", "value_wifi")
            put("yndx.dim.tuner", "value_tuner")
        }

        whenever(recoveryUpdater.readSystemProperty("ro.yndx.dimlist")).doReturn("wifi")
        whenever(recoveryUpdater.readSystemProperty("ro.yndx.dim.wifi")).doReturn("value_wifi1")

        assertThrows(Exception::class.java) { recoveryUpdater.checkDimLists(metadata) }
    }
}
