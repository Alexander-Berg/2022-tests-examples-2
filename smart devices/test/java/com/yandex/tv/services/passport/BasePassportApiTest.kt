// Copyright 2021 Yandex LLC. All rights reserved.

package com.yandex.tv.services.passport

import android.app.Application
import android.content.Context
import android.content.Intent
import android.content.IntentFilter
import androidx.test.core.app.ApplicationProvider
import org.mockito.kotlin.any
import org.mockito.kotlin.doReturn
import org.mockito.kotlin.mock
import org.mockito.kotlin.spy
import org.mockito.kotlin.whenever
import com.yandex.passport.api.Passport
import com.yandex.passport.api.PassportApi
import com.yandex.passport.api.PassportFilter
import com.yandex.passport.api.PassportUid
import com.yandex.tv.common.di.NetworkComponent
import com.yandex.tv.common.network.AuthInterceptor
import com.yandex.tv.common.network.DefaultAuthSelector
import com.yandex.tv.common.utility.test.EmptyMetricaServiceSdk2
import com.yandex.tv.services.experiments.ExperimentsHelper
import io.reactivex.rxjava3.android.plugins.RxAndroidPlugins
import io.reactivex.rxjava3.core.Completable
import io.reactivex.rxjava3.core.Scheduler
import io.reactivex.rxjava3.internal.schedulers.SingleScheduler
import okhttp3.Request
import okhttp3.mockwebserver.MockResponse
import okhttp3.mockwebserver.MockWebServer
import org.junit.After
import org.junit.Before
import org.mockito.Mockito
import retrofit2.Retrofit
import retrofit2.adapter.rxjava3.RxJava3CallAdapterFactory
import retrofit2.converter.gson.GsonConverterFactory

abstract class BasePassportApiTest {

    protected val mockWebServer: MockWebServer = MockWebServer()
    protected var mockMainScheduler: Scheduler? = null
    protected var mockOpsProcessingScheduler: Scheduler? = null

    protected val checkAuthApi = lazy {
        val networkComponent = NetworkComponent.instance
        val client = networkComponent.commonHttpClient.newBuilder()
            .addInterceptor(
                AuthInterceptor(
                    networkComponent.refreshableTokenProvider,
                    DefaultAuthSelector(),
                    { request: Request -> request.tag(CheckAuthApi.Uid::class.java)?.value }
                ))
            .build()
        val retrofit = Retrofit.Builder()
            .client(client)
            .baseUrl(mockWebServer.url("/"))
            .addConverterFactory(GsonConverterFactory.create())
            .addCallAdapterFactory(RxJava3CallAdapterFactory.create())
            .build()
        retrofit.create(CheckAuthApi::class.java)
    }

    @Before
    fun setup() {
        mockMainScheduler = SingleScheduler()
        mockOpsProcessingScheduler = SingleScheduler()
        RxAndroidPlugins.setMainThreadSchedulerHandler { mockMainScheduler }
    }

    @After
    fun tearDown() {
        mockMainScheduler?.shutdown()
        mockMainScheduler = null
        mockOpsProcessingScheduler?.shutdown()
        mockOpsProcessingScheduler = null
    }

    protected fun createPassportApi(): PassportApi {
        return mock()
    }

    protected fun createRxApi(passportApi: PassportApi): PassportRxApi {
        val context = ApplicationProvider.getApplicationContext<Application>()
        val experimentsHelper = Mockito.mock(ExperimentsHelper::class.java)
        val registrationSdk = RegistrationServiceSdk2Test()
        val rxApi = spy(
            PassportRxApi(
                context,
                passportApi,
                checkAuthApi,
                experimentsHelper,
                registrationSdk,
                mockOpsProcessingScheduler!!
            )
        )
        doReturn(rxApi).`when`(PassportComponent.instance).passportRxApi
        return rxApi
    }

    protected fun mockLogin(passportApi: PassportApi) {
        doReturn(mutableListOf(TEST_AUTHORIZED_ACCOUNT, TEST_UNAUTHORIZED_ACCOUNT))
            .whenever(passportApi).getAccounts(any())
        doReturn(TEST_AUTHORIZED_ACCOUNT).whenever(passportApi).getAccount(any<PassportUid>())
        doReturn(TEST_TOKEN).whenever(passportApi).getToken(any())
        doReturn(TEST_AUTHORIZED_ACCOUNT).whenever(passportApi).currentAccount
    }

    protected fun mockAccountEventReceived(event: PassportAccountEvent, uid: PassportUid = TEST_UID): Completable {

        val context: Context = ApplicationProvider.getApplicationContext()
        val receiver = AccountsChangedReceiver()
        context.registerReceiver(receiver, IntentFilter())

        val intent = Intent().apply {
            action = event.value
            putExtra(PassportUid.Factory.KEY_ENVIRONMENT, uid.environment.integer)
            putExtra(PassportUid.Factory.KEY_UID, uid.value)
        }

        return Completable.fromAction { receiver.onReceive(context, intent) }
            .subscribeOn(mockMainScheduler)
            .doOnComplete { context.unregisterReceiver(receiver) }
    }

    protected fun mockCheckAuth(vararg successfulResponse: Boolean) {
        successfulResponse.forEach {
            mockWebServer.enqueue(MockResponse().apply {
                setResponseCode(if (it) 200 else 403)
            })
        }
    }

    protected companion object {
        val TEST_PASSPORT_FILTER = PassportFilter.Builder.Factory
            .createBuilder()
            .setPrimaryEnvironment(Passport.PASSPORT_ENVIRONMENT_TESTING)
            .build()
        val TEST_UID = PassportUid.Factory.from(Passport.PASSPORT_ENVIRONMENT_TESTING, 12345)
        val TEST_ANOTHER_UID = PassportUid.Factory.from(Passport.PASSPORT_ENVIRONMENT_TESTING, 54321)
        val TEST_AUTHORIZED_ACCOUNT = TestPassportAccount(12345)
        val TEST_ANOTHER_AUTHORIZED_ACCOUNT = TestPassportAccount(54321)
        val TEST_UNAUTHORIZED_ACCOUNT = TestPassportAccount(67890, false)
        val TEST_TOKEN = TestPassportToken("testPassportToken")
    }
}
