package com.yandex.tv.services.promo

import android.os.Build
import androidx.core.os.bundleOf
import com.google.gson.JsonParser
import com.google.protobuf.Struct
import com.google.protobuf.util.JsonFormat
import com.yandex.tv.services.promo.service.PromoConfig
import com.yandex.tv.services.promo.service.PromoServiceApiImpl
import com.yandex.tv.services.promo.service.prefs.PromoPreferences
import com.yandex.tv.services.promo.service.prefs.TemplateCache
import com.yandex.tv.services.promo.service.source.LocalPromoSource
import com.yandex.tv.services.promo.service.source.PromoResponse
import com.yandex.tv.services.promo.service.source.grpc.GrpcPromoSource
import kotlinx.coroutines.runBlocking
import org.hamcrest.MatcherAssert.assertThat
import org.hamcrest.Matchers.allOf
import org.hamcrest.Matchers.equalTo
import org.hamcrest.Matchers.greaterThanOrEqualTo
import org.hamcrest.Matchers.lessThanOrEqualTo
import org.hamcrest.Matchers.nullValue
import org.junit.Test
import org.junit.runner.RunWith
import org.mockito.AdditionalMatchers.and
import org.mockito.AdditionalMatchers.geq
import org.mockito.AdditionalMatchers.leq
import org.mockito.kotlin.argumentCaptor
import org.mockito.kotlin.eq
import org.mockito.kotlin.mock
import org.mockito.kotlin.verify
import org.mockito.kotlin.whenever
import org.robolectric.RobolectricTestRunner
import org.robolectric.annotation.Config
import ru.yandex.alice.protos.data.tv_feature_boarding.TvFeatureBoardingTemplate
import java.util.concurrent.TimeUnit

private const val DIVJSON = "{'obj':'divjson'}"
private const val DIVJSON_2 = "{'obj':'divjson2'}"
private const val TEMPLATE_GIFT = "gift_on_main"
private const val TEMPLATE_TANDEM = "tandem"
private const val TEMPLATE_2 = "template_id_2"
private const val TTL = 1000L
private val MINUTE = TimeUnit.MINUTES.toMillis(1)
private val ARGS = bundleOf("arg" to 1)

@RunWith(RobolectricTestRunner::class)
@Config(sdk = [Build.VERSION_CODES.P], manifest = Config.NONE)
class PromoServiceApiImplTest {

    private val config: PromoConfig = mock()
    private val localSource: LocalPromoSource = mock()
    private val grpcSource: GrpcPromoSource = mock()
    private val prefs: PromoPreferences = mock()
    private val stats: PromoStatistics = mock()
    private val api = PromoServiceApiImpl(config, localSource, grpcSource, prefs, stats)
    private val protoTandemRequest = createTandemRequest(false)
    private val protoTandemIfExistRequest = createTandemRequest(true)

    @Test
    fun `check confirm() confirm, clean cache and set show time`() {
        val beforeTime = System.currentTimeMillis()
        api.confirm(TEMPLATE_GIFT, ARGS)
        val afterTime = System.currentTimeMillis()

        verify(localSource).confirm(eq(TEMPLATE_GIFT))
        verify(prefs).removeCache(eq(TEMPLATE_GIFT))
        verify(prefs).setLastShowPromoTime(and(geq(beforeTime), leq(afterTime)))
    }

    @Test
    fun `check requestPromo() return null if promo is not in config`() {
        whenever(config.enabledPromos).thenReturn(setOf(TEMPLATE_2))
        whenever(localSource.getPromo(PromoApi.MAIN_GIFT_PROMO)).thenReturn(createLocalResponse(DIVJSON, TTL))

        val promo = api.requestPromo(TEMPLATE_GIFT, ARGS)

        assertThat(promo, nullValue())
    }

    @Test
    fun `check requestPromo() return null if prev promo shown recently`() {
        whenever(config.enabledPromos).thenReturn(setOf(TEMPLATE_GIFT))
        whenever(prefs.getLastShowPromoTime()).thenReturn(System.currentTimeMillis())
        whenever(config.minPromoTimeout).thenReturn(MINUTE)
        whenever(localSource.getPromo(PromoApi.MAIN_GIFT_PROMO)).thenReturn(createLocalResponse(DIVJSON, TTL))

        val promo = api.requestPromo(TEMPLATE_GIFT, ARGS)

        assertThat(promo, nullValue())
    }

    @Test
    fun `check requestPromo() return promo from cache if need`() {
        whenever(config.enabledPromos).thenReturn(setOf(TEMPLATE_GIFT))
        whenever(prefs.getLastShowPromoTime()).thenReturn(0)
        whenever(config.minPromoTimeout).thenReturn(MINUTE)
        whenever(prefs.getCache(TEMPLATE_GIFT)).thenReturn(TemplateCache(System.currentTimeMillis() + MINUTE, null, DIVJSON))
        whenever(localSource.getPromo(PromoApi.MAIN_GIFT_PROMO)).thenReturn(createLocalResponse(DIVJSON_2, TTL))

        val promo = api.requestPromo(TEMPLATE_GIFT, ARGS)

        assertThat(promo, equalTo(DIVJSON))
    }

    @Test
    fun `check requestPromo() return promo from source if cache is not valid`() = runBlocking {
        whenever(config.enabledPromos).thenReturn(setOf(TEMPLATE_TANDEM))
        whenever(prefs.getLastShowPromoTime()).thenReturn(0)
        whenever(config.minPromoTimeout).thenReturn(MINUTE)
        whenever(prefs.getCache(TEMPLATE_TANDEM)).thenReturn(TemplateCache(MINUTE, api.getBase64String(protoTandemRequest), DIVJSON_2))
        whenever(localSource.getPromo(PromoApi.MAIN_GIFT_PROMO)).thenReturn(createLocalResponse(DIVJSON, TTL))
        whenever(grpcSource.getPromo(protoTandemRequest)).thenReturn(createGrpcResponse(DIVJSON, TTL))

        val beforeTime = System.currentTimeMillis()
        val promo = api.requestGrpcPromo(protoTandemRequest)
        val afterTime = System.currentTimeMillis()

        val captor = argumentCaptor<TemplateCache>()
        verify(prefs).putCache(eq(TEMPLATE_TANDEM), captor.capture())

        val jsonExpected = JsonParser.parseString(DIVJSON)
        val jsonActual = JsonParser.parseString(promo)
        assertThat(jsonActual, equalTo(jsonExpected))

        val cachedJsonActual = JsonParser.parseString(captor.firstValue.divjson)
        assertThat(cachedJsonActual, equalTo(jsonExpected))
        assertThat(
            captor.firstValue.liveBefore,
            allOf(greaterThanOrEqualTo(beforeTime + TTL), lessThanOrEqualTo(afterTime + TTL))
        )
    }

    @Test
    fun `check requestPromo() return promo from source if cache is for other request`() = runBlocking {
        whenever(config.enabledPromos).thenReturn(setOf(TEMPLATE_TANDEM))
        whenever(prefs.getLastShowPromoTime()).thenReturn(0)
        whenever(config.minPromoTimeout).thenReturn(MINUTE)
        whenever(prefs.getCache(TEMPLATE_TANDEM)).thenReturn(TemplateCache(System.currentTimeMillis() + MINUTE, api.getBase64String(protoTandemIfExistRequest), DIVJSON_2))
        whenever(localSource.getPromo(PromoApi.MAIN_GIFT_PROMO)).thenReturn(createLocalResponse(DIVJSON, TTL))
        whenever(grpcSource.getPromo(protoTandemRequest)).thenReturn(createGrpcResponse(DIVJSON, TTL))

        val beforeTime = System.currentTimeMillis()
        val promo = api.requestGrpcPromo(protoTandemRequest)
        val afterTime = System.currentTimeMillis()

        val captor = argumentCaptor<TemplateCache>()
        verify(prefs).putCache(eq(TEMPLATE_TANDEM), captor.capture())

        val jsonExpected = JsonParser.parseString(DIVJSON)
        val jsonActual = JsonParser.parseString(promo)
        assertThat(jsonActual, equalTo(jsonExpected))

        val cachedJsonActual = JsonParser.parseString(captor.firstValue.divjson)
        assertThat(cachedJsonActual, equalTo(jsonExpected))
        assertThat(
            captor.firstValue.liveBefore,
            allOf(greaterThanOrEqualTo(beforeTime + TTL), lessThanOrEqualTo(afterTime + TTL))
        )
    }

    @Test
    fun `check requestPromo() return promo from source if cache is null`() = runBlocking {
        whenever(config.enabledPromos).thenReturn(setOf(TEMPLATE_TANDEM))
        whenever(prefs.getLastShowPromoTime()).thenReturn(0)
        whenever(config.minPromoTimeout).thenReturn(MINUTE)
        whenever(prefs.getCache(TEMPLATE_TANDEM)).thenReturn(null)
        whenever(localSource.getPromo(PromoApi.MAIN_GIFT_PROMO)).thenReturn(createLocalResponse(DIVJSON, TTL))
        whenever(grpcSource.getPromo(protoTandemRequest)).thenReturn(createGrpcResponse(DIVJSON, TTL))

        val beforeTime = System.currentTimeMillis()
        val promo = api.requestGrpcPromo(protoTandemRequest)
        val afterTime = System.currentTimeMillis()

        val captor = argumentCaptor<TemplateCache>()
        verify(prefs).putCache(eq(TEMPLATE_TANDEM), captor.capture())
        verify(stats).reportResponse(eq(TEMPLATE_TANDEM), eq(false))

        val jsonExpected = JsonParser.parseString(DIVJSON)
        val jsonActual = JsonParser.parseString(promo)
        assertThat(jsonActual, equalTo(jsonExpected))

        val cachedJsonActual = JsonParser.parseString(captor.firstValue.divjson)
        assertThat(cachedJsonActual, equalTo(jsonExpected))
        assertThat(
            captor.firstValue.liveBefore,
            allOf(greaterThanOrEqualTo(beforeTime + TTL), lessThanOrEqualTo(afterTime + TTL))
        )
    }

    @Test
    fun `check getDivJsonString() return null on empty divJson`() {
        val emptyResponse = TvFeatureBoardingTemplate.TTemplateResponse.newBuilder().setDivJson(Struct.getDefaultInstance()).build()
        val divJson = api.getDivJsonString(emptyResponse)
        assertThat(divJson, nullValue())
    }

    private fun createTandemRequest(hasTandem: Boolean): TvFeatureBoardingTemplate.TTemplateRequest {
        return PromoTemplateUtils.buildTandemRequest(
            isTandemDevicesAvailable = true,
            isTandemConnected = hasTandem
        )
    }

    private fun createLocalResponse(divjson: String, ttl: Long): PromoResponse {
        return PromoResponse(divjson, ttl)
    }

    private fun createGrpcResponse(divjson: String, ttl: Long): TvFeatureBoardingTemplate.TTemplateResponse {
        val builder = TvFeatureBoardingTemplate.TTemplateResponse.newBuilder().setTtl(ttl.toInt())
        JsonFormat.parser().merge(divjson, builder.divJsonBuilder)
        return builder.build()
    }
}
