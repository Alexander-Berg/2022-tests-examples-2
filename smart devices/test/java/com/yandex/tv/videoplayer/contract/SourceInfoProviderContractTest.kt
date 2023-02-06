package com.yandex.tv.videoplayer.contract

import android.content.ContentResolver
import android.database.MatrixCursor
import android.media.tv.TvContract
import android.media.tv.TvInputManager
import android.net.Uri
import android.os.Build
import android.os.Bundle
import androidx.test.core.app.ApplicationProvider
import org.mockito.kotlin.any
import org.mockito.kotlin.anyOrNull
import org.mockito.kotlin.doReturn
import org.mockito.kotlin.eq
import org.mockito.kotlin.mock
import org.mockito.kotlin.spy
import org.mockito.kotlin.times
import org.mockito.kotlin.verify
import org.mockito.kotlin.whenever
import com.yandex.tv.common.contract.inputsources.SourceInfoProviderContract
import com.yandex.tv.common.contract.inputsources.SourceInfoProviderContract.EpgSync
import com.yandex.tv.common.utility.test.injectContentProviderSpy
import com.yandex.tv.live.providers.SourceInfoProvider
import org.hamcrest.Matchers.equalTo
import org.hamcrest.Matchers.not
import org.hamcrest.MatcherAssert.assertThat
import org.junit.AfterClass
import org.junit.BeforeClass
import org.junit.Test
import org.junit.runner.RunWith
import org.mockito.MockedStatic
import org.mockito.Mockito
import org.robolectric.Robolectric
import org.robolectric.RobolectricTestRunner
import org.robolectric.android.controller.ContentProviderController
import org.robolectric.annotation.Config

@RunWith(RobolectricTestRunner::class)
@Config(sdk = [Build.VERSION_CODES.P], application = TvAppContractTestApp::class)
class SourceInfoProviderContractTest {

    private var controller: ContentProviderController<out SourceInfoProvider>? = null
    private var providerSpy: SourceInfoProvider? = null
    private var providerContentResolverSpy: ContentResolver? = null

    private fun prepareContentProvider() {
        controller = Robolectric.buildContentProvider(TestSourceInfoProvider::class.java)
            .also { controller ->
                providerSpy = spy(controller.get())
                    .also { provider ->
                        injectContentProviderSpy(controller, provider)
                    }
            }
    }

    private fun createContentProvider() {
        controller?.create(SourceInfoProviderContract.AUTHORITY)
    }

    private fun spyContentProviderInternals() {
        controller?.get()?.also { provider ->
            val providerContextSpy = spy(provider.context)
            val tvInputManagerMock = mock<TvInputManager>()
                providerContentResolverSpy = spy(providerContextSpy?.contentResolver)
            whenever(tvInputManagerMock.tvInputList).doReturn(emptyList())
            whenever(providerContextSpy?.contentResolver).doReturn(providerContentResolverSpy)
            whenever(providerContextSpy?.getSystemService(any())).doReturn(tvInputManagerMock)
            whenever(provider.context).doReturn(providerContextSpy)
            whenever(provider.writePermission).doReturn(null)
            whenever(provider.readPermission).doReturn(null)
        }
    }

    private fun destroyContentProvider() {
        controller?.shutdown()
        providerContentResolverSpy = null
    }

    @Test
    fun `get tv input info, info obtained`() {
        prepareContentProvider()
        createContentProvider()
        spyContentProviderInternals()

        ApplicationProvider.getApplicationContext<TvAppContractTestApp>()
            .contentResolver
            .query(SourceInfoProviderContract.buildInputUri(TEST_INPUT_ID), null, null, null, null)
            .use {
                val channelsUriIdx = it!!.getColumnIndex(SourceInfoProviderContract.INPUT_CHANNELS_URI)
                val programsUriIdx = it.getColumnIndex(SourceInfoProviderContract.INPUT_PROGRAMS_URI)
                assertThat(it.count, equalTo(1))
                assertThat(it.moveToFirst(), equalTo(true))
                assertThat(it.getString(channelsUriIdx), equalTo(TEST_CHANNELS_URI.toString()))
                assertThat(it.getString(programsUriIdx), equalTo(TEST_PROGRAMS_URI.toString()))
            }

        destroyContentProvider()
    }

    @Test
    fun `get tv input channels, tv contract query called`() {
        prepareContentProvider()
        createContentProvider()
        spyContentProviderInternals()

        ApplicationProvider.getApplicationContext<TvAppContractTestApp>()
            .contentResolver
            .query(SourceInfoProviderContract.buildInputChannelsUri(TEST_INPUT_ID), null, null, null, null)

        verify(providerContentResolverSpy, times(1))
            ?.query(eq(TEST_CHANNELS_URI), anyOrNull(), anyOrNull(), anyOrNull(), anyOrNull())

        destroyContentProvider()
    }

    @Test
    fun `get tv input channels's programs, tv contract query called`() {
        prepareContentProvider()
        createContentProvider()
        spyContentProviderInternals()

        val channelProgramsUri = SourceInfoProviderContract.buildChannelProgramsUri(TEST_INPUT_ID, TEST_CHANNEL_ID, null, null)
        ApplicationProvider.getApplicationContext<TvAppContractTestApp>()
            .contentResolver
            .query(channelProgramsUri, null, null, null, null)

        verify(providerContentResolverSpy, times(1))
            ?.query(eq(TEST_CHANNEL_PROGRAM_URI), anyOrNull(), anyOrNull(), anyOrNull(), anyOrNull())

        destroyContentProvider()
    }

    @Test
    fun `get tv input stat, info obtained`() {
        prepareContentProvider()
        createContentProvider()
        spyContentProviderInternals()

        val testType = "testType"
        val outputColumns = arrayOf(TvContract.Channels.COLUMN_TYPE)
        whenever(providerContentResolverSpy?.query(eq(TEST_CHANNELS_URI), anyOrNull(), anyOrNull(), anyOrNull(), anyOrNull(), anyOrNull()))
            .thenReturn(MatrixCursor(outputColumns).apply {
                addRow(arrayOf(testType))
            })

        val inputStatUri = SourceInfoProviderContract.buildChannelsStatUri(TEST_INPUT_ID)
        ApplicationProvider.getApplicationContext<TvAppContractTestApp>()
            .contentResolver
            .query(inputStatUri, null, null, null, null)
            .use {
                val typeIdx = it!!.getColumnIndex(TvContract.Channels.COLUMN_TYPE)
                val countIdx = it.getColumnIndex(SourceInfoProviderContract.STAT_COLUMN_CHANNELS_COUNT)
                assertThat(it.count, equalTo(1))
                assertThat(it.moveToFirst(), equalTo(true))
                assertThat(it.getString(typeIdx), equalTo(testType))
                assertThat(it.getInt(countIdx), equalTo(1))
            }

        destroyContentProvider()
    }

    @Test
    fun `set epg sync success status, successful set`() {
        prepareContentProvider()
        createContentProvider()

        val epgSyncUri = EpgSync.buildUri()
        val args = Bundle().apply {
            putString(EpgSync.COLUMN_INPUT, TEST_INPUT_ID)
            putString(EpgSync.COLUMN_STATUS, EpgSync.SYNC_STATUS_FINISHED)
        }
        ApplicationProvider.getApplicationContext<TvAppContractTestApp>()
            .contentResolver
            .call(epgSyncUri, EpgSync.UPDATE_STATUS_METHOD, null, args)

        ApplicationProvider.getApplicationContext<TvAppContractTestApp>()
            .contentResolver
            .query(epgSyncUri, null, null, null, null)
            .use {
                val idIdx = it!!.getColumnIndex(EpgSync.COLUMN_INPUT)
                val statusIdx = it.getColumnIndex(EpgSync.COLUMN_STATUS)
                val errorIdx = it.getColumnIndex(EpgSync.COLUMN_ERROR_CODE)
                assertThat(it.count, equalTo(1))
                assertThat(it.moveToFirst(), equalTo(true))
                assertThat(it.getString(idIdx), equalTo(TEST_INPUT_ID))
                assertThat(it.getString(statusIdx), equalTo(EpgSync.SYNC_STATUS_FINISHED))
                assertThat(it.getInt(errorIdx), equalTo<Int>(0))
            }

        destroyContentProvider()
    }

    @Test
    fun `set epg sync error status, successful set`() {
        prepareContentProvider()
        createContentProvider()

        val epgSyncUri = EpgSync.buildUri()
        val args = Bundle().apply {
            putString(EpgSync.COLUMN_INPUT, TEST_INPUT_ID)
            putString(EpgSync.COLUMN_STATUS, EpgSync.SYNC_STATUS_ERROR)
            putInt(EpgSync.COLUMN_ERROR_CODE, EpgSync.ERROR_NO_CHANNELS)
        }
        ApplicationProvider.getApplicationContext<TvAppContractTestApp>()
            .contentResolver
            .call(epgSyncUri, EpgSync.UPDATE_STATUS_METHOD, null, args)

        ApplicationProvider.getApplicationContext<TvAppContractTestApp>()
            .contentResolver
            .query(epgSyncUri, null, null, null, null)
            .use {
                val idIdx = it!!.getColumnIndex(EpgSync.COLUMN_INPUT)
                val statusIdx = it.getColumnIndex(EpgSync.COLUMN_STATUS)
                val errorIdx = it.getColumnIndex(EpgSync.COLUMN_ERROR_CODE)
                assertThat(it.count, equalTo(1))
                assertThat(it.moveToFirst(), equalTo(true))
                assertThat(it.getString(idIdx), equalTo(TEST_INPUT_ID))
                assertThat(it.getString(statusIdx), equalTo(EpgSync.SYNC_STATUS_ERROR))
                assertThat(it.getInt(errorIdx), equalTo(EpgSync.ERROR_NO_CHANNELS))
            }

        destroyContentProvider()
    }

    @Test
    fun `get hdmi info, info obtained`() {
        prepareContentProvider()
        createContentProvider()
        spyContentProviderInternals()

        val hdmiUri = SourceInfoProviderContract.Hdmi.buildHdmiInfoUri()

        ApplicationProvider.getApplicationContext<TvAppContractTestApp>()
            .contentResolver
            .query(hdmiUri, null, null, null, null)
            .use {
                val inputStateIdx = it!!.getColumnIndexOrThrow(SourceInfoProviderContract.Hdmi.COLUMN_HDMI_INPUT_STATE)
                val isHiddenIdx = it.getColumnIndexOrThrow(SourceInfoProviderContract.Hdmi.COLUMN_HDMI_HIDDEN_STATUS)
                val deviceNameIdx = it.getColumnIndexOrThrow(SourceInfoProviderContract.Hdmi.COLUMN_HDMI_DEVICE_NAME)
                val portNameIdx = it.getColumnIndexOrThrow(SourceInfoProviderContract.Hdmi.COLUMN_HDMI_PORT_NAME)
                val arcStatusIdx = it.getColumnIndexOrThrow(SourceInfoProviderContract.Hdmi.COLUMN_HDMI_ARC_STATUS)
                val inputIdIdx = it.getColumnIndexOrThrow(SourceInfoProviderContract.Hdmi.COLUMN_HDMI_INPUT_ID)
                assertThat(portNameIdx, not(-1))
                assertThat(deviceNameIdx, not(-1))
                assertThat(isHiddenIdx, not(-1))
                assertThat(inputStateIdx, not(-1))
                assertThat(inputIdIdx, not(-1))
                assertThat(arcStatusIdx, not(-1))
            }

        destroyContentProvider()
    }

    companion object {

        const val TEST_INPUT_ID = "test_input_id"
        const val TEST_CHANNEL_ID = "42"

        private val TEST_CHANNELS_URI = Uri.parse("content://android.media.tv/channel")
            .buildUpon()
            .appendQueryParameter("input", TEST_INPUT_ID)
            .appendQueryParameter("browsable_only", "false")
            .build()
        private val TEST_PROGRAMS_URI = Uri.parse("content://android.media.tv/program")
            .buildUpon()
            .appendQueryParameter("input", TEST_INPUT_ID)
            .build()
        private val TEST_CHANNEL_PROGRAM_URI = Uri.parse("content://test_channel_program_uri")


        private var mockedTvContract: MockedStatic<TvContract>? = null

        @BeforeClass
        @JvmStatic
        fun mockSdk() {
            mockedTvContract = Mockito.mockStatic(TvContract::class.java).apply {
                `when`<Uri> { TvContract.buildChannelsUriForInput(anyOrNull()) }.thenReturn(TEST_CHANNELS_URI)
                `when`<Uri> { TvContract.buildProgramsUriForChannel(anyOrNull<Long>()) }.thenReturn(TEST_CHANNEL_PROGRAM_URI)
                `when`<Uri> { TvContract.buildProgramsUriForChannel(anyOrNull<Uri>()) }.thenReturn(TEST_CHANNEL_PROGRAM_URI)
            }
        }

        @AfterClass
        @JvmStatic
        fun unmockSdk() {
            mockedTvContract?.close()
        }
    }
}
