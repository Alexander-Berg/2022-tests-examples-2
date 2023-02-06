// Copyright 2021 Yandex LLC. All rights reserved.

package com.yandex.tv.services.passport

import android.os.Build
import com.yandex.passport.api.PassportAccount
import io.reactivex.rxjava3.core.Single
import org.hamcrest.MatcherAssert.assertThat
import org.hamcrest.Matchers.equalTo
import org.junit.Ignore
import org.junit.Test
import org.junit.runner.RunWith
import org.mockito.kotlin.any
import org.mockito.kotlin.anyOrNull
import org.mockito.kotlin.atLeastOnce
import org.mockito.kotlin.doReturn
import org.mockito.kotlin.eq
import org.mockito.kotlin.never
import org.mockito.kotlin.times
import org.mockito.kotlin.verify
import org.mockito.kotlin.whenever
import org.robolectric.RobolectricTestRunner
import org.robolectric.annotation.Config
import retrofit2.HttpException
import java.lang.Thread.sleep
import java.util.concurrent.TimeUnit

@RunWith(RobolectricTestRunner::class)
@Config(sdk = [Build.VERSION_CODES.P], manifest = Config.NONE, application = PassportRxApiTestApp::class)
class PassportRxApiTest : BasePassportApiTest() {

    @Test
    fun `not logged in, initialized, current account is null`() {
        val passportApi = createPassportApi()
        val api = createRxApi(passportApi)
        api.getCurrentAccountDetails()
            .test()
            .awaitCount(1)
            .assertValue { !it.isPresent }
    }

    @Test
    fun `not logged in, not initialized, current cached account is null`() {
        Single.fromCallable { try { sleep(10000) } catch (ignored: InterruptedException) { } }
            .subscribeOn(mockOpsProcessingScheduler)
            .subscribe()
        val passportApi = createPassportApi()
        val api = createRxApi(passportApi)
        val account = api.getCurrentCachedAccountDetails()
        assertThat(account, equalTo(null))
    }

    @Test
    fun `not logged in, not initialized, current account is not obtained`() {
        Single.fromCallable { try { sleep(10000) } catch (ignored: InterruptedException) { } }
            .subscribeOn(mockOpsProcessingScheduler)
            .subscribe()
        val passportApi = createPassportApi()
        val api = createRxApi(passportApi)
        api.getCurrentAccountDetails()
            .subscribeOn(mockMainScheduler)
            .test()
            .awaitDone(5, TimeUnit.SECONDS)
            .assertNotComplete()
    }

    @Test
    fun `logged in, initialize, current account is not null`() {
        val passportApi = createPassportApi()
        mockLogin(passportApi)
        val api = createRxApi(passportApi)
        api.getCurrentAccountDetails()
            .test()
            .awaitCount(1)
            .assertValue { it.isPresent && it.get().account == TEST_AUTHORIZED_ACCOUNT}
    }

    @Test
    fun `logged in, initialize, current account obtained, account changed fired`() {
        val passportApi = createPassportApi()
        mockLogin(passportApi)
        val api = createRxApi(passportApi)
        api.observeCurrentAccountDetails()
            .test()
            .awaitCount(1)
            .assertValue { it.isPresent && it.get().account == TEST_AUTHORIZED_ACCOUNT && it.get().token == TEST_TOKEN }
    }

    @Test
    fun `logged in and initialized, refresh account and await, account refreshed`() {
        val passportApi = createPassportApi()
        mockLogin(passportApi)
        val api = createRxApi(passportApi)
        api.refreshCurrentAccountAndAwait()
            .test()
            .awaitCount(1)
            .assertValue { it.isPresent && it.get().account == TEST_AUTHORIZED_ACCOUNT && it.get().token == TEST_TOKEN }
    }

    @Test
    fun `get token for uid, token obtained`() {
        val passportApi = createPassportApi()
        mockLogin(passportApi)
        val api = createRxApi(passportApi)
        api.getToken(TEST_UID)
            .test()
            .awaitCount(1)
            .assertValue(TEST_TOKEN)
    }

    @Test
    fun `get account for uid, account obtained`() {
        val passportApi = createPassportApi()
        mockLogin(passportApi)
        val api = createRxApi(passportApi)
        api.getAccount(TEST_UID)
            .test()
            .awaitCount(1)
            .assertValue(TEST_AUTHORIZED_ACCOUNT)
    }

    @Test
    fun `logged in and initialized, get current token, token obtained`() {
        val passportApi = createPassportApi()
        mockLogin(passportApi)
        val api = createRxApi(passportApi)
        api.getCurrentToken()
            .test()
            .awaitCount(1)
            .assertValue { it.isPresent && it.get() == TEST_TOKEN.value }
    }

    @Ignore("The test fails in pull requests but passes locally")
    @Test
    fun `logged in and initialized, set current account, account set`() {
        val passportApi = createPassportApi()
        mockLogin(passportApi)
        val api = createRxApi(passportApi)
        val accountChangeObserver = api.observeCurrentAccountDetails()
            .skip(1) //skip initial login
            .test()
        api.setCurrentAccount(TEST_UID)
            .subscribeOn(mockMainScheduler)
            .subscribe()
        accountChangeObserver
            .awaitCount(1)
            .assertValue { it.isPresent && it.get().account == TEST_AUTHORIZED_ACCOUNT && it.get().token == TEST_TOKEN }
    }

    @Test
    fun `logged in and initialized, get authorized accounts, accounts obtained`() {
        val passportApi = createPassportApi()
        mockLogin(passportApi)
        val api = createRxApi(passportApi)
        api.getAuthorizedAccounts(TEST_PASSPORT_FILTER)
            .test()
            .awaitCount(1)
            .assertValue { it.size == 1 && it[0] == TEST_AUTHORIZED_ACCOUNT}
    }

    @Test
    fun `logged in and initialized, drop token, token dropped`() {
        val passportApi = createPassportApi()
        mockLogin(passportApi)
        val api = createRxApi(passportApi)
        api.dropToken(TEST_TOKEN.value)
            .test()
            .awaitCount(1)
            .assertComplete()
        verify(passportApi).dropToken(eq(TEST_TOKEN.value))
    }

    @Test
    @Ignore
    fun `logged in and initialized, remove account, account removed and new picked`() {
        val passportApi = createPassportApi()
        mockLogin(passportApi)
        val api = createRxApi(passportApi)
        doReturn(mutableListOf(TEST_ANOTHER_AUTHORIZED_ACCOUNT)).whenever(passportApi).getAccounts(any())
        api.removeAccount(TEST_UID)
            .test()
            .awaitCount(1)
            .assertComplete()
        verify(passportApi, atLeastOnce()).removeAccount(eq(TEST_UID))
        verify(api, atLeastOnce()).setCurrentAccount(TEST_ANOTHER_UID)
        verify(api, atLeastOnce()).refreshCurrentAccountAndAwait()
        api.getCurrentAccountDetails()
            .test()
            .awaitCount(1)
            .assertValue { it.isPresent && it.get().account == TEST_ANOTHER_AUTHORIZED_ACCOUNT }
    }

    @Test
    @Ignore
    fun `logged in and initialized, remove inactive account, account removed`() {
        val passportApi = createPassportApi()
        mockLogin(passportApi)
        val api = createRxApi(passportApi)
        doReturn(mutableListOf(TEST_AUTHORIZED_ACCOUNT)).whenever(passportApi).getAccounts(any())
        api.removeAccount(TEST_ANOTHER_UID)
            .test()
            .awaitCount(1)
            .assertComplete()
        verify(passportApi, atLeastOnce()).removeAccount(eq(TEST_ANOTHER_UID))
        verify(api, never()).setCurrentAccount(any())
        verify(api, atLeastOnce()).refreshCurrentAccountAndAwait()
        api.getCurrentAccountDetails()
            .test()
            .awaitCount(1)
            .assertValue { it.isPresent && it.get().account == TEST_AUTHORIZED_ACCOUNT }
    }

    @Test
    @Ignore
    fun `logged in and initialized, remove last account, account removed and no accounts left`() {
        val passportApi = createPassportApi()
        mockLogin(passportApi)
        val api = createRxApi(passportApi)
        doReturn(mutableListOf<PassportAccount>()).whenever(passportApi).getAccounts(any())
        api.removeAccount(TEST_UID)
            .test()
            .awaitCount(1)
            .assertComplete()
        verify(passportApi, atLeastOnce()).removeAccount(eq(TEST_UID))
        verify(api, never()).setCurrentAccount(any())
        verify(api, atLeastOnce()).refreshCurrentAccountAndAwait()
        api.getCurrentAccountDetails()
            .test()
            .awaitCount(1)
            .assertValue { !it.isPresent }
    }

    @Test
    fun `logged in and initialized, check auth successful, nothing changes`() {
        val passportApi = createPassportApi()
        mockLogin(passportApi)
        val api = createRxApi(passportApi)

        mockCheckAuth(true)
        api.checkAuth(TEST_UID).blockingAwait()

        verify(api, never()).dropToken(anyOrNull())
        verify(api, never()).removeAccount(anyOrNull(), any())
    }

    @Test
    fun `logged in and initialized, check auth unsuccessful, token refreshed`() {
        val passportApi = createPassportApi()
        mockLogin(passportApi)
        val api = createRxApi(passportApi)

        mockCheckAuth(false)
        try {
            api.checkAuth(TEST_UID).blockingAwait()
        } catch (e: HttpException) {
            assertThat(e.code(), equalTo(403))
        }

        verify(api, times(1)).dropToken(anyOrNull())
        verify(api, never()).removeAccount(anyOrNull(), any())
    }

    @Test
    fun `logged in and initialized, check auth unsuccessful, token not refreshed, account removed, new picked`() {
        val passportApi = createPassportApi()
        mockLogin(passportApi)
        val api = createRxApi(passportApi)

        mockCheckAuth(false, false)
        try {
            api.checkAuth(TEST_UID).blockingAwait()
        } catch (e: HttpException) {
            assertThat(e.code(), equalTo(403))
        }

        verify(api, times(1)).dropToken(anyOrNull())
        verify(api, never()).removeAccount(anyOrNull(), any())
    }

    @Test
    fun `account added, account event processed`() {
        val passportApi = createPassportApi()
        mockLogin(passportApi)
        val api = createRxApi(passportApi)

        mockAccountEventReceived(PassportAccountEvent.ACTION_ACCOUNT_ADDED).subscribe()

        api.observeAccountEvents()
            .test()
            .awaitCount(1)
            .assertValue(PassportAccountEvent.ACTION_ACCOUNT_ADDED)
    }

    @Test
    fun `account removed, account event processed`() {
        val passportApi = createPassportApi()
        mockLogin(passportApi)
        val api = createRxApi(passportApi)

        mockAccountEventReceived(PassportAccountEvent.ACTION_ACCOUNT_REMOVED).subscribe()

        api.observeAccountEvents()
            .test()
            .awaitCount(1)
            .assertValue(PassportAccountEvent.ACTION_ACCOUNT_REMOVED)
    }

    @Test
    fun `token changed, account event processed`() {
        val passportApi = createPassportApi()
        mockLogin(passportApi)
        val api = createRxApi(passportApi)

        mockAccountEventReceived(PassportAccountEvent.ACTION_TOKEN_CHANGED).subscribe()

        api.observeAccountEvents()
            .test()
            .awaitCount(1)
            .assertValue(PassportAccountEvent.ACTION_TOKEN_CHANGED)
    }
}
