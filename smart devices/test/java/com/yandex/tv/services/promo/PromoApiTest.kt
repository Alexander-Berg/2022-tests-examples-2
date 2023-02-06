package com.yandex.tv.services.promo

import android.content.Context
import android.os.Build
import com.yandex.tv.services.common.internal.CompletableServiceFuture
import org.junit.Test
import org.junit.runner.RunWith
import org.mockito.kotlin.any
import org.mockito.kotlin.argThat
import org.mockito.kotlin.mock
import org.mockito.kotlin.never
import org.mockito.kotlin.verify
import org.mockito.kotlin.whenever
import org.robolectric.RobolectricTestRunner
import org.robolectric.annotation.Config

private const val DIVJSON = "{divjson}"

@RunWith(RobolectricTestRunner::class)
@Config(sdk = [Build.VERSION_CODES.P], manifest=Config.NONE)
class PromoApiTest {

    private val context: Context = mock()
    private val sdk: PromoServiceSdk2 = mock()
    private val api = PromoApi(context, sdk)

    @Test
    fun `check tryToShowPromo() start activity on completed gift request`() {
        val future = CompletableServiceFuture<String?>()
        whenever(sdk.requestPromo(PromoApi.MAIN_GIFT_PROMO, null)).thenReturn(future)

        api.tryToShowMainGiftPromo()
        future.complete(DIVJSON)

        verify(context).startActivity(argThat {
            action == PromoActivityContract.PROMO_ACTION &&
            getStringExtra(PromoActivityContract.PROMO_TEMPLATE_KEY) == PromoApi.MAIN_GIFT_PROMO &&
            getStringExtra(PromoActivityContract.PROMO_DIVJSON_KEY) == DIVJSON
        })
    }

    @Test
    fun `check tryToShowPromo() start activity on completed tandem request`() {
        val future = CompletableServiceFuture<String?>()
        val promoRequest = PromoTemplateUtils
            .buildTandemRequest(isTandemDevicesAvailable = true, isTandemConnected = false)
        whenever(sdk.requestGrpcPromo(promoRequest)).thenReturn(future)

        api.tryToShowTandemPromo(true, false)
        future.complete(DIVJSON)

        val reportRequest = PromoTemplateUtils
            .buildTandemRequest(isTandemDevicesAvailable = true, isTandemConnected = false)
        verify(context).startActivity(argThat {
            action == PromoActivityContract.PROMO_ACTION &&
            PromoActivityContract.retrieveRequest(this) == reportRequest &&
            getStringExtra(PromoActivityContract.PROMO_DIVJSON_KEY) == DIVJSON
        })
    }

    @Test
    fun `check tryToShowPromo() not show activity on null result of request`() {
        val future = CompletableServiceFuture<String?>()
        whenever(sdk.requestPromo(PromoApi.MAIN_GIFT_PROMO, null)).thenReturn(future)

        api.tryToShowMainGiftPromo()
        future.complete(null)

        verify(context, never()).startActivity(any())
    }

    @Test
    fun `check tryToShowPromo() not show activity after shutdown`() {
        val future = CompletableServiceFuture<String?>()
        whenever(sdk.requestPromo(PromoApi.MAIN_GIFT_PROMO, null)).thenReturn(future)

        api.tryToShowMainGiftPromo()
        api.shutdownNow()
        future.complete(DIVJSON)

        verify(context, never()).startActivity(any())
    }

    @Test
    fun `check tryToShowPromo() not show activity on request error`() {
        val future = CompletableServiceFuture<String?>()
        whenever(sdk.requestPromo(PromoApi.MAIN_GIFT_PROMO, null)).thenReturn(future)

        api.tryToShowMainGiftPromo()
        future.completeExceptionally(RuntimeException("error occurred"))

        verify(context, never()).startActivity(any())
    }
}
