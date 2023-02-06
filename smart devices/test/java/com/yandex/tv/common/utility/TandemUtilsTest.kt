package com.yandex.tv.common.utility

import org.json.JSONObject
import org.junit.Assert
import org.junit.Test

class TandemUtilsTest {
    @Test
    fun yandexstation() {
        testColorCode("FF98F02900289569BC39E5BB", "yandexstation", null)
        testColorCode("", "yandexstation", null)
    }

    @Test
    fun yandexstation_2() {
        testColorCode("XK000000000000000000000000000000", "yandexstation_2", "K")
        testColorCode("XW000000000000000000000000000000", "yandexstation_2", "W")
        testColorCode("XB000000000000000000000000000000", "yandexstation_2", "B")
        testColorCode("XR000000000000000000000000000000", "yandexstation_2", "R")
        testColorCode("X000000000000K", "yandexstation_2", "K")
        testColorCode("X000000000000W", "yandexstation_2", "W")
        testColorCode("X000000000000B", "yandexstation_2", "B")
        testColorCode("X000000000000R", "yandexstation_2", "R")
        testColorCode("", "yandexstation_2", null)
    }

    @Test
    fun yandexmini() {
        testColorCode("FF98F02900289569BC39E5BB", "yandexmini", null)
        testColorCode("", "yandexmini", null)
    }

    @Test
    fun yandexmini_2() {
        testColorCode("MK000000000000000000000000000000", "yandexmini_2", "K")
        testColorCode("MB000000000000000000000000000000", "yandexmini_2", "B")
        testColorCode("MR000000000000000000000000000000", "yandexmini_2", "R")
        testColorCode("MG000000000000000000000000000000", "yandexmini_2", "G")
        testColorCode("M000000000000K", "yandexmini_2", "K")
        testColorCode("M000000000000B", "yandexmini_2", "B")
        testColorCode("M000000000000R", "yandexmini_2", "R")
        testColorCode("M000000000000G", "yandexmini_2", "G")
        testColorCode("", "yandexmini_2", null)
    }

    @Test
    fun yandexmicro() {
        testColorCode("LG000000000000000000000000000000", "yandexmicro", "G")
        testColorCode("LP000000000000000000000000000000", "yandexmicro", "P")
        testColorCode("LR000000000000000000000000000000", "yandexmicro", "R")
        testColorCode("LB000000000000000000000000000000", "yandexmicro", "B")
        testColorCode("LY000000000000000000000000000000", "yandexmicro", "Y")
        testColorCode("LN000000000000000000000000000000", "yandexmicro", "N")
        testColorCode("", "yandexmicro", null)
    }

    @Test
    fun yandexmidi() {
        testColorCode("U000000000000K", "yandexmidi", "K")
        testColorCode("U000000000000B", "yandexmidi", "B")
        testColorCode("U000000000000R", "yandexmidi", "R")
        testColorCode("U000000000000G", "yandexmidi", "G")
        testColorCode("U000000000000L", "yandexmidi", "L")
        testColorCode("U000000000000P", "yandexmidi", "P")
        testColorCode("", "yandexmidi", null)
    }

    @Test
    fun `unknown platform`() {
        testColorCode("LN000000000000000000000000000000", "yandexsomething", null)
    }

    @Test
    fun `add new platform with additional JSON config`() {
        val jsonConfig = JSONObject("""
            {
                "yandexsomething": {
                    "5": [0, 1],
                    "6": [5, 6]
                }
            }
        """)
        testColorCode("50000", "yandexsomething", "5", jsonConfig)
        testColorCode("000006", "yandexsomething", "6", jsonConfig)
        testColorCode("", "yandexsomething", null, jsonConfig)
    }

    @Test
    fun `override existing platform with additional JSON config`() {
        val jsonConfig = JSONObject("""
            {
                "yandexmini_2": {
                    "32": [0, 1]
                }
            }
        """)
        testColorCode("MK000000000000000000000000000000", "yandexmini_2", "M", jsonConfig)
        testColorCode("M000000000000K", "yandexmini_2", "K", jsonConfig)
        testColorCode("", "yandexmini_2", null, jsonConfig)
    }

    @Test
    fun `supplement existing platform with additional JSON config`() {
        val jsonConfig = JSONObject("""
            {
                "yandexstation_2": {
                    "14": [13, 14]
                }
            }
        """)
        testColorCode("XK000000000000000000000000000000", "yandexstation_2", "K", jsonConfig)
        testColorCode("X000000000000K", "yandexstation_2", "K", jsonConfig)
        testColorCode("", "yandexstation_2", null, jsonConfig)
    }

    private fun testColorCode(deviceId: String, platform: String, expectedResult: String?, cfg: JSONObject? = null) {
        Assert.assertEquals(expectedResult, TandemUtils.extractColorCode(deviceId, platform, cfg ?: JSONObject()))
    }
}
