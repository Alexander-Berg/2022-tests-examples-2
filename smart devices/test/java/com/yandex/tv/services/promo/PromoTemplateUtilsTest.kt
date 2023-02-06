package com.yandex.tv.services.promo

import org.junit.Assert.assertEquals
import org.junit.Test

class PromoTemplateUtilsTest {

    @Test
    fun buildTandemRequest_1() {
        testTandemRequest(isTandemDevicesAvailable = true, isTandemConnected = true)
    }

    @Test
    fun buildTandemRequest_2() {
        testTandemRequest(isTandemDevicesAvailable = true, isTandemConnected = false)
    }

    @Test
    fun buildTandemRequest_3() {
        testTandemRequest(isTandemDevicesAvailable = false, isTandemConnected = true)
    }

    @Test
    fun buildTandemRequest_4() {
        testTandemRequest(isTandemDevicesAvailable = false, isTandemConnected = false)
    }

    @Test
    fun getTemplateFromRequest_tandem() {
        val request = PromoTemplateUtils.buildTandemRequest(
            isTandemDevicesAvailable = false,
            isTandemConnected = false
        )
        val template = PromoTemplateUtils.getTemplateFromRequest(request)
        assertEquals(PromoApi.TANDEM_PROMO, template)
    }

    private fun testTandemRequest(isTandemDevicesAvailable: Boolean, isTandemConnected: Boolean) {
        val request = PromoTemplateUtils.buildTandemRequest(
            isTandemDevicesAvailable = isTandemDevicesAvailable,
            isTandemConnected = isTandemConnected
        )
        assertEquals(isTandemDevicesAvailable, request.tandemTemplate.isTandemDevicesAvailable)
        assertEquals(isTandemConnected, request.tandemTemplate.isTandemConnected)
    }
}
