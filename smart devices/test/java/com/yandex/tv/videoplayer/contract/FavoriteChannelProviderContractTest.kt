package com.yandex.tv.videoplayer.contract

import android.content.ContentValues
import android.database.Cursor
import android.os.Build
import androidx.test.core.app.ApplicationProvider
import com.yandex.tv.common.contract.inputsources.FavoriteChannelsProviderContract
import com.yandex.tv.common.utility.test.injectContentProviderSpy
import com.yandex.tv.live.providers.FavoritesProvider
import org.hamcrest.MatcherAssert.assertThat
import org.hamcrest.Matchers.equalTo
import org.junit.Test
import org.junit.runner.RunWith
import org.mockito.kotlin.spy
import org.robolectric.Robolectric
import org.robolectric.RobolectricTestRunner
import org.robolectric.android.controller.ContentProviderController
import org.robolectric.annotation.Config

private const val TEST_CHANNEL_INPUT_ID = "test_channel_input_id"
private const val TEST_CHANNEL_URI = "test_channel_uri"

@RunWith(RobolectricTestRunner::class)
@Config(sdk = [Build.VERSION_CODES.P], application = TvAppContractTestApp::class)
class FavoriteChannelProviderContractTest {

    private var controller: ContentProviderController<FavoritesProvider>? = null
    private var providerSpy: FavoritesProvider? = null

    private fun prepareContentProvider() {
        controller = Robolectric.buildContentProvider(FavoritesProvider::class.java)
            .also { controller ->
                providerSpy = spy(controller.get())
                    .also { provider ->
                        injectContentProviderSpy(controller, provider)
                    }
            }
    }

    private fun createContentProvider() {
        controller?.create(FavoriteChannelsProviderContract.AUTHORITY)
    }

    private fun destroyContentProvider() {
        controller?.shutdown()
    }

    private fun createTestChannel(): ContentValues {
        return ContentValues(2).apply {
            put(FavoriteChannelsProviderContract.COLUMN_CHANNEL_INPUT, TEST_CHANNEL_INPUT_ID)
            put(FavoriteChannelsProviderContract.COLUMN_CHANNEL_URI, TEST_CHANNEL_URI)
        }
    }

    private fun insertTestChannel(channel: ContentValues) {
        ApplicationProvider.getApplicationContext<TvAppContractTestApp>()
            .contentResolver
            .insert(FavoriteChannelsProviderContract.buildUri(), channel)
    }

    private fun queryTestChannel(): Cursor? {
        return ApplicationProvider.getApplicationContext<TvAppContractTestApp>()
            .contentResolver
            .query(FavoriteChannelsProviderContract.buildUri(), null, null, null, null)
    }

    private fun removeTestChannel() {
        ApplicationProvider.getApplicationContext<TvAppContractTestApp>()
            .contentResolver
            .delete(FavoriteChannelsProviderContract.buildUri(), null, null)
    }

    @Test
    fun `no favorites, put favorite channel, channel is stored`() {
        prepareContentProvider()
        createContentProvider()
        val testChannel = createTestChannel()
        insertTestChannel(testChannel)

        queryTestChannel()!!.use {
            val channelInputIdx = it.getColumnIndex(FavoriteChannelsProviderContract.COLUMN_CHANNEL_INPUT)
            val channelUriIdx = it.getColumnIndex(FavoriteChannelsProviderContract.COLUMN_CHANNEL_URI)
            assertThat(it.count, equalTo(1))
            assertThat(it.moveToFirst(), equalTo(true))
            assertThat(it.getString(channelInputIdx), equalTo(TEST_CHANNEL_INPUT_ID))
            assertThat(it.getString(channelUriIdx), equalTo(TEST_CHANNEL_URI))
        }

        destroyContentProvider()
    }

    @Test
    fun `favorites not empty, remove favorite channels, channels are removed`() {
        prepareContentProvider()
        createContentProvider()
        val testChannel = createTestChannel()
        insertTestChannel(testChannel)
        removeTestChannel()

        queryTestChannel()!!.use {
            assertThat(it.count, equalTo(0))
        }

        destroyContentProvider()
    }
}
