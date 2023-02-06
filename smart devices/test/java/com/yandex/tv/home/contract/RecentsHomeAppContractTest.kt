package com.yandex.tv.home.contract

import android.content.Context
import android.os.Build
import android.os.Bundle
import androidx.test.core.app.ApplicationProvider
import com.yandex.tv.common.contract.home.ChannelType
import com.yandex.tv.common.contract.home.HomeAppRecentsContract
import com.yandex.tv.common.utility.test.assertBundlesEqual
import com.yandex.tv.home.di.homeAppModule
import com.yandex.tv.home.passport.HomeAccountManagerFacade
import com.yandex.tv.home.recent.RecentContentProvider
import com.yandex.tv.home.utils.commonTestModule
import org.junit.After
import org.junit.Before
import org.junit.Test
import org.junit.runner.RunWith
import org.koin.android.ext.koin.androidContext
import org.koin.core.context.startKoin
import org.koin.core.context.stopKoin
import org.koin.test.KoinTest
import org.mockito.Mockito.times
import org.mockito.kotlin.anyOrNull
import org.mockito.kotlin.argumentCaptor
import org.mockito.kotlin.eq
import org.mockito.kotlin.spy
import org.mockito.kotlin.verify
import org.robolectric.Robolectric
import org.robolectric.RobolectricTestRunner
import org.robolectric.android.controller.ContentProviderController
import org.robolectric.annotation.Config
import org.robolectric.shadows.ShadowSQLiteOpenHelper

private const val TEST_CHANNEL_NUMBER = 42
private const val TEST_CHANNEL_NAME = "test_name"
private const val TEST_CHANNEL_FAVORITE = true
private const val TEST_CHANNEL_THUMBNAIL = "test_thumb_url"
private const val TEST_CHANNEL_URI = "test_channel_uri"
private const val TEST_CHANNEL_INPUT_ID = "test_input_id"
private val TEST_CHANNEL_TYPE = ChannelType.SATELLITE

@RunWith(RobolectricTestRunner::class)
@Config(sdk = [Build.VERSION_CODES.P], application = HomeAppContractTestApp::class, shadows = [ShadowSQLiteOpenHelper::class])
class RecentsHomeAppContractTest: KoinTest {

    private var controller: ContentProviderController<RecentContentProvider>? = null
    private var providerSpy: RecentContentProvider? = null

    private fun prepareContentProvider() {
        controller = Robolectric.buildContentProvider(RecentContentProvider::class.java)
            .also { controller ->
                providerSpy = spy(controller.get())
                    .also { provider ->
                        com.yandex.tv.common.utility.test.injectContentProviderSpy(controller, provider)
                    }
            }
    }

    private fun createContentProvider() {
        controller?.create(HomeAppRecentsContract.AUTHORITY)
    }

    private fun destroyContentProvider() {
        controller?.shutdown()
    }

    private fun createTestChannel(): Bundle {
        return Bundle().apply {
            putInt(HomeAppRecentsContract.EXTRA_RECENT_DISPLAY_NUMBER, TEST_CHANNEL_NUMBER)
            putString(HomeAppRecentsContract.EXTRA_RECENT_CHANNEL_TITLE, TEST_CHANNEL_NAME)
            putBoolean(HomeAppRecentsContract.EXTRA_RECENT_CHANNEL_FAVORITE, TEST_CHANNEL_FAVORITE)
            putString(HomeAppRecentsContract.EXTRA_RECENT_CHANNEL_THUMBNAIL_URL, TEST_CHANNEL_THUMBNAIL)
            putString(HomeAppRecentsContract.EXTRA_RECENT_CHANNEL_CONTENT_URL, TEST_CHANNEL_URI)
            putString(HomeAppRecentsContract.EXTRA_RECENT_CHANNEL_INPUT_ID, TEST_CHANNEL_INPUT_ID)
            putInt(HomeAppRecentsContract.EXTRA_RECENT_MAIN_COLOR, 0)
            putString(HomeAppRecentsContract.EXTRA_RECENT_CHANNEL_TYPE, TEST_CHANNEL_TYPE.name)
        }
    }

    private fun insertTestChannel(extras: Bundle) {
        ApplicationProvider.getApplicationContext<Context>()
            .contentResolver
            .call(HomeAppRecentsContract.buildRecentUri(), HomeAppRecentsContract.METHOD_PUT_LAST_CHANNEL, null, extras)
    }

    @Before
    fun setUp() {
        startKoin {
            androidContext(ApplicationProvider.getApplicationContext())
            modules(listOf(homeAppModule, commonTestModule, deeplinkTestModule))
        }
        HomeAccountManagerFacade.onAppCreate(ApplicationProvider.getApplicationContext())
    }

    @After
    fun tearDown() {
        stopKoin()
    }

    @Test
    fun `put last channel, channel saved`() {
        prepareContentProvider()
        createContentProvider()

        val insertedChannel = createTestChannel()
        insertTestChannel(insertedChannel)

        verify(providerSpy, times(1))?.call(eq(HomeAppRecentsContract.METHOD_PUT_LAST_CHANNEL), anyOrNull(), anyOrNull())
        val channelCaptor = argumentCaptor<Bundle>()
        verify(providerSpy, times(1))?.putLastRecentChannel(channelCaptor.capture())

        assertBundlesEqual(channelCaptor.firstValue, insertedChannel)

        destroyContentProvider()
    }

    @Test
    fun `last channel inserted, get last channel, channel obtained`() {
        prepareContentProvider()
        createContentProvider()

        val insertedChannel = createTestChannel()
        insertTestChannel(insertedChannel)

        val channel = ApplicationProvider.getApplicationContext<Context>()
            .contentResolver
            .call(HomeAppRecentsContract.buildRecentUri(), HomeAppRecentsContract.METHOD_GET_LAST_CHANNEL, null, null)

        verify(providerSpy, times(1))?.call(eq(HomeAppRecentsContract.METHOD_GET_LAST_CHANNEL), anyOrNull(), anyOrNull())
        verify(providerSpy, times(1))?.getLastRecentChannel()

        assertBundlesEqual(channel, insertedChannel)

        destroyContentProvider()
    }
}
