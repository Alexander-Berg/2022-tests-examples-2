package com.yandex.tv.services.passport

import android.app.Application
import android.content.Context
import android.os.Build
import android.os.Bundle
import androidx.test.core.app.ApplicationProvider
import com.yandex.tv.services.passport.gift.GiftAliceFlow
import com.yandex.tv.services.passport.gift.api.GiftAlicePromoDetails
import com.yandex.tv.services.passport.gift.api.GiftAliceStatusModel
import io.reactivex.rxjava3.core.Completable
import io.reactivex.rxjava3.core.Observable
import io.reactivex.rxjava3.core.Single
import org.junit.After
import org.junit.Assert.assertEquals
import org.junit.Assert.assertThrows
import org.junit.Before
import org.junit.Test
import org.junit.runner.RunWith
import org.mockito.Mockito
import org.mockito.Mockito.times
import org.mockito.Mockito.verify
import org.mockito.kotlin.any
import org.mockito.kotlin.never
import org.robolectric.RobolectricTestRunner
import org.robolectric.Shadows
import org.robolectric.annotation.Config
import java.util.*

@RunWith(RobolectricTestRunner::class)
@Config(sdk = [Build.VERSION_CODES.P], manifest = Config.NONE)
class PassportProviderTest {

    private val passportRxApi: PassportRxApi = Mockito.mock(PassportRxApi::class.java)
    private val giftAliceFlow: GiftAliceFlow = Mockito.mock(GiftAliceFlow::class.java)

    @Before
    fun setup() {
        Mockito.reset(passportRxApi)
    }

    @After
    fun tearDown() {

    }

    @Test
    fun `no permissions, call onAuthentication, throw SecurityException`() {
        val context = getAppContextWithoutPermissions()
        Mockito.`when`(passportRxApi.observeCurrentAccountDetails()).thenReturn(Observable.empty())
        val passportProvider = createPassportProvider(context, passportRxApi)

        assertThrows(SecurityException::class.java) {
            passportProvider.call(PassportProviderContract.METHOD_ON_INVALID_AUTHENTICATION, null, null)
        }
    }

    @Test
    fun `no permissions, call getCurrentAccount, throw SecurityException`() {
        val context = getAppContextWithoutPermissions()
        Mockito.`when`(passportRxApi.observeCurrentAccountDetails()).thenReturn(Observable.empty())
        val passportProvider = createPassportProvider(context, passportRxApi)

        assertThrows(SecurityException::class.java) {
            passportProvider.call(PassportProviderContract.METHOD_GET_CURRENT_ACCOUNT, null, null)
        }
    }

    @Test
    fun `no permissions, call getGift, throw SecurityException`() {
        val context = getAppContextWithoutPermissions()
        Mockito.`when`(passportRxApi.observeCurrentAccountDetails()).thenReturn(Observable.empty())
        Mockito.`when`(giftAliceFlow.getGiftInfo()).thenReturn(Single.just(GiftAliceStatusModel()))
        val passportProvider = createPassportProvider(context, passportRxApi, giftAliceFlow)

        assertThrows(SecurityException::class.java) {
            passportProvider.call(PassportProviderContract.METHOD_GET_ALICE_GIFT, null, null)
        }
    }

    @Test
    fun `no permissions, call refreshCurrentAccount, throw SecurityException`() {
        val context = getAppContextWithoutPermissions()
        Mockito.`when`(passportRxApi.observeCurrentAccountDetails()).thenReturn(Observable.empty())
        val passportProvider = createPassportProvider(context, passportRxApi)

        assertThrows(SecurityException::class.java) {
            passportProvider.call(PassportProviderContract.METHOD_REFRESH_CURRENT_ACCOUNT, null, null)
        }
    }

    @Test
    fun `have permission, call getCurrentAccount, no exception`() {
        val context = getAppContext()
        Mockito.`when`(passportRxApi.observeCurrentAccountDetails()).thenReturn(Observable.just(Optional.empty()))
        Mockito.`when`(passportRxApi.getCurrentAccountDetails()).thenReturn(Single.just(Optional.empty()))
        val passportProvider = createPassportProvider(context, passportRxApi)

        passportProvider.call(PassportProviderContract.METHOD_GET_CURRENT_ACCOUNT, null, null)
    }

    @Test
    fun `have permission, call refreshCurrentAccount, no exception`() {
        val context = getAppContext()
        Mockito.`when`(passportRxApi.observeCurrentAccountDetails()).thenReturn(Observable.empty())
        Mockito.`when`(passportRxApi.refreshCurrentAccountAndAwait()).thenReturn(Single.just(Optional.empty()))
        Mockito.`when`(passportRxApi.dropToken(null)).thenReturn(Completable.complete())
        val passportProvider = createPassportProvider(context, passportRxApi)

        passportProvider.call(PassportProviderContract.METHOD_REFRESH_CURRENT_ACCOUNT, null, null)
    }

    @Test
    fun `have permission, call onAuthenticationInvalid, no exception`() {
        val context = getAppContext()
        Mockito.`when`(passportRxApi.observeCurrentAccountDetails()).thenReturn(Observable.just(Optional.empty()))
        Mockito.`when`(passportRxApi.getCurrentAccountDetails()).thenReturn(Single.just(Optional.empty()))
        val passportProvider = createPassportProvider(context, passportRxApi)

        passportProvider.call(PassportProviderContract.METHOD_ON_INVALID_AUTHENTICATION, null, null)
    }

    @Test
    fun `have last account, call getCurrentAccount, return last account`() {
        val optAwt1 = createOptionalAccountWithToken(uid = 111, token = "token")
        val optAwt2 = createOptionalAccountWithToken(uid = 222, token = "token2")
        Mockito.`when`(passportRxApi.observeCurrentAccountDetails())
                .thenReturn(Observable.just(optAwt1, optAwt2))
        Mockito.`when`(passportRxApi.getCurrentAccountDetails())
                .thenReturn(Single.just(optAwt2))

        val context = getAppContext()
        val passportProvider = createPassportProvider(context, passportRxApi)

        val bundle = passportProvider.call(PassportProviderContract.METHOD_GET_CURRENT_ACCOUNT, null, null)
        val actualAccount = PassportAccount.fromBundle(bundle)

        val expectedAccount = optAwt2.get().toPassportAccount()
        assertEquals(expectedAccount, actualAccount)
    }

    @Test
    fun `have last account, call getGift, return last account`() {
        val gift = GiftAliceStatusModel().apply {
            available = true
            details = GiftAlicePromoDetails().apply { subscriptionName = "yandex.plus" }
        }
        Mockito.`when`(passportRxApi.observeCurrentAccountDetails()).thenReturn(Observable.empty())
        Mockito.`when`(giftAliceFlow.getGiftInfo()).thenReturn(Single.just(gift))

        val context = getAppContext()
        val passportProvider = createPassportProvider(context, passportRxApi, giftAliceFlow)

        val bundle = passportProvider.call(PassportProviderContract.METHOD_GET_ALICE_GIFT, null, null)
        val actualGift = GiftAliceDetails.fromBundle(bundle)

        val expectedGift = gift.details?.toGiftDetails(context)
        assertEquals(expectedGift, actualGift)
    }

    @Test
    fun `no last account, call getCurrentAccount, return null`() {
        Mockito.`when`(passportRxApi.observeCurrentAccountDetails())
                .thenReturn(Observable.just(Optional.empty()))
        Mockito.`when`(passportRxApi.getCurrentAccountDetails())
                .thenReturn(Single.just(Optional.empty()))

        val context = getAppContext()
        val passportProvider = createPassportProvider(context, passportRxApi)

        val bundle = passportProvider.call(PassportProviderContract.METHOD_GET_CURRENT_ACCOUNT, null, null)
        val actualAccount = PassportAccount.fromBundle(bundle)

        assertEquals(null, actualAccount)
    }

    @Test
    fun `empty GiftAliceStatusModel, call getGift, return null`() {
        Mockito.`when`(passportRxApi.observeCurrentAccountDetails()).thenReturn(Observable.empty())
        Mockito.`when`(giftAliceFlow.getGiftInfo()).thenReturn(Single.just(GiftAliceStatusModel()))

        val context = getAppContext()
        val passportProvider = createPassportProvider(context, passportRxApi, giftAliceFlow)

        val bundle = passportProvider.call(PassportProviderContract.METHOD_GET_ALICE_GIFT, null, null)
        val actualGift = GiftAliceDetails.fromBundle(bundle)

        assertEquals(null, actualGift)
    }

    @Test
    fun `call refreshCurrentAccount, call PassportApi#refreshCurrentAccountAndAwait()`() {
        val passportApiSpy = Mockito.spy(passportRxApi)
        Mockito.doReturn(Observable.empty<Optional<AccountWithToken>>())
                .`when`(passportApiSpy).observeCurrentAccountDetails()
        Mockito.doReturn(Single.just(Optional.empty<AccountWithToken>()))
                .`when`(passportApiSpy).refreshCurrentAccountAndAwait()

        val context = getAppContext()
        val passportProvider = createPassportProvider(context, passportApiSpy)

        passportProvider.call(PassportProviderContract.METHOD_REFRESH_CURRENT_ACCOUNT, null, null)

        verify(passportApiSpy, times(1)).refreshCurrentAccountAndAwait()
    }

    @Test
    fun `call onAuthenticationInvalid, call PassportApi#removeAccount(uid, forceRemove)`() {
        val optAwt1 = createOptionalAccountWithToken(uid = 111, token = "token")
        Mockito.`when`(passportRxApi.observeCurrentAccountDetails()).thenReturn(Observable.just(optAwt1))
        Mockito.`when`(passportRxApi.getCurrentAccountDetails()).thenReturn(Single.just(optAwt1))
        Mockito.`when`(passportRxApi.refreshCurrentAccountAndAwait()).thenReturn(Single.just(optAwt1))
        Mockito.`when`(passportRxApi.removeAccount(any(), any())).thenReturn(Completable.complete())

        val context = getAppContext()
        val passportProvider = createPassportProvider(context, passportRxApi)

        val bundle = Bundle()
        bundle.putString(PassportProviderContract.INVALID_UID, optAwt1.get().account.uid.value.toString())
        passportProvider.call(PassportProviderContract.METHOD_ON_INVALID_AUTHENTICATION, null, bundle)

        verify(passportRxApi, times(1)).removeAccount(optAwt1.get().account.uid, true)
    }

    @Test
    fun `call onAuthenticationInvalid with wrong token, PassportApi#removeAccount should not be called`() {
        val optAwt1 = createOptionalAccountWithToken(uid = 111, token = "token")
        Mockito.`when`(passportRxApi.observeCurrentAccountDetails()).thenReturn(Observable.just(optAwt1))
        Mockito.`when`(passportRxApi.getCurrentAccountDetails()).thenReturn(Single.just(optAwt1))
        Mockito.`when`(passportRxApi.refreshCurrentAccountAndAwait()).thenReturn(Single.just(optAwt1))
        Mockito.`when`(passportRxApi.removeAccount(any(), any())).thenReturn(Completable.complete())

        val context = getAppContext()
        val passportProvider = createPassportProvider(context, passportRxApi)

        val bundle = Bundle()
        bundle.putString(PassportProviderContract.INVALID_UID, "some_other_uid")
        passportProvider.call(PassportProviderContract.METHOD_ON_INVALID_AUTHENTICATION, null, bundle)

        verify(passportRxApi, never()).removeAccount(optAwt1.get().account.uid, true)
    }

    private fun createPassportProvider(context: Context, passportRxApi: PassportRxApi, giftFlow: GiftAliceFlow = giftAliceFlow): PassportProvider {
        return PassportProvider().apply {
            lateInit(PassportProviderImpl(context, passportRxApi, giftFlow))
        }
    }

    private fun getAppContext(): Context {
        val context = ApplicationProvider.getApplicationContext<Application>()
        val shadowApp = Shadows.shadowOf(context)
        shadowApp.grantPermissions(PassportProviderContract.PERMISSION_READ_CURRENT_ACCOUNT)
        return context
    }

    private fun getAppContextWithoutPermissions(): Context {
        return ApplicationProvider.getApplicationContext<Application>()
    }

    private fun createOptionalAccountWithToken(uid: Long, token: String? = null): Optional<AccountWithToken> {
        return Optional.of(AccountWithToken(
                TestPassportAccount(uid),
                token?.let { TestPassportToken(it) })
        )
    }

}
