// Copyright 2021 Yandex LLC. All rights reserved.

package com.yandex.tv.services.passport

import android.os.Build
import org.mockito.kotlin.eq
import org.mockito.kotlin.never
import org.mockito.kotlin.times
import org.mockito.kotlin.verify
import org.junit.Test
import org.junit.runner.RunWith
import org.robolectric.RobolectricTestRunner
import org.robolectric.annotation.Config

@RunWith(RobolectricTestRunner::class)
@Config(sdk = [Build.VERSION_CODES.P], manifest = Config.NONE, application = PassportRxApiTestApp::class)
class AccountChangedReceiverTest : BasePassportApiTest() {

    @Test
    fun `account added event fired, set it current`() {
        val api = createRxApi(createPassportApi())
        mockAccountEventReceived(PassportAccountEvent.ACTION_ACCOUNT_ADDED, TEST_UID).blockingAwait()
        verify(api, times(1)).setCurrentAccount(eq(TEST_UID))
    }

    @Test
    fun `account removed event fired, current account removed, account refreshed`() {
        val passportApi = createPassportApi()
        mockLogin(passportApi)
        val api = createRxApi(passportApi)
        mockAccountEventReceived(PassportAccountEvent.ACTION_ACCOUNT_REMOVED, TEST_UID).blockingAwait()
        verify(api, times(1)).refreshCurrentAccount()
    }

    @Test
    fun `account removed event fired, not current account removed, nothing happens`() {
        val passportApi = createPassportApi()
        mockLogin(passportApi)
        val api = createRxApi(passportApi)
        mockAccountEventReceived(PassportAccountEvent.ACTION_ACCOUNT_REMOVED, TEST_ANOTHER_UID).blockingAwait()
        verify(api, never()).refreshCurrentAccount()
    }

    @Test
    fun `token changed event fired, current token changed, account refreshed`() {
        val passportApi = createPassportApi()
        mockLogin(passportApi)
        val api = createRxApi(passportApi)
        mockAccountEventReceived(PassportAccountEvent.ACTION_TOKEN_CHANGED, TEST_UID).blockingAwait()
        verify(api, times(1)).refreshCurrentAccount()
    }

    @Test
    fun `token changed event fired, not current token changed, nothing happens`() {
        val passportApi = createPassportApi()
        mockLogin(passportApi)
        val api = createRxApi(passportApi)
        mockAccountEventReceived(PassportAccountEvent.ACTION_TOKEN_CHANGED, TEST_ANOTHER_UID).blockingAwait()
        verify(api, never()).refreshCurrentAccount()
    }
}
