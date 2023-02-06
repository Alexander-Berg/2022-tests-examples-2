package com.yandex.launcher.core.notification

import android.content.Context
import org.mockito.kotlin.*
import com.yandex.launcher.updaterapp.BaseRobolectricTest
import com.yandex.launcher.updaterapp.contract.IEventListener
import com.yandex.launcher.updaterapp.contract.events.*
import com.yandex.launcher.updaterapp.contract.models.Update
import com.yandex.launcher.updaterapp.core.notification.UpdaterManagerProxyNotifier
import com.yandex.launcher.updaterapp.core.notification.constants.ErrorCode
import org.hamcrest.Matchers.equalTo
import org.hamcrest.Matchers.instanceOf
import org.hamcrest.MatcherAssert.assertThat
import org.junit.Before
import org.junit.Test

class UpdaterManagerProxyNotifierTest : BaseRobolectricTest() {

    private var listener = EventListenerStub()
    private lateinit var context: Context
    private lateinit var notifier: UpdaterManagerProxyNotifier

    @Before
    override fun setUp() {
        super.setUp()

        context = spy(app)
        notifier = UpdaterManagerProxyNotifier.getInstance(context)
        notifier.listeners = mock {
            on { beginBroadcast() }.thenReturn(1)
            on { getBroadcastItem(any()) }.thenReturn(listener)
        }
    }

    @Test
    fun `onCheckForUpdatesError sends event`() {
        notifier.onCheckForUpdatesError("test", ErrorCode.UNKNOWN)

        assertThat(listener.events.first().event, instanceOf(CheckForUpdatesErrorEvent::class.java))
        assertThat(listener.events.size, equalTo(1))
    }

    @Test
    fun `broadcast send events to listeners`() {
        notifier.broadcast(UpdatedEvent(null))

        assertThat(listener.events.first().event, instanceOf(UpdatedEvent::class.java))
        assertThat(listener.events.size, equalTo(1))
    }

    @Test
    fun `onInstallStarted sends event`() {
        notifier.onInstallStarted(Update("a", "p", "d", "1", 1))

        assertThat(listener.events.first().event, instanceOf(InstallStartedEvent::class.java))
        assertThat(listener.events.size, equalTo(1))
    }

    @Test
    fun `onInstallInProgress sends event`() {
        notifier.onInstallInProgress(Update("a", "p", "d", "1", 1), "-", 1, true)

        assertThat(listener.events.first().event, instanceOf(InstallInProgressEvent::class.java))
        assertThat(listener.events.size, equalTo(1))
    }

    @Test
    fun `onInstalled sends event`() {
        notifier.onInstalled(Update("a", "p", "d", "1", 1), null)

        assertThat(listener.events.first().event, instanceOf(InstalledEvent::class.java))
        assertThat(listener.events.size, equalTo(1))
    }

    @Test
    fun `onInstallError sends event`() {
        notifier.onInstallError(Update("a", "p", "d", "1", 1), null, ErrorCode.UNKNOWN)

        assertThat(listener.events.first().event, instanceOf(InstallErrorEvent::class.java))
        assertThat(listener.events.size, equalTo(1))
    }

    @Test
    fun `onUpdated sends event`() {
        notifier.onUpdated(Update("a", "p", "d", "1", 1), null)

        assertThat(listener.events.first().event, instanceOf(UpdatedEvent::class.java))
        assertThat(listener.events.size, equalTo(1))
    }

    @Test
    fun `onUpdateError sends event`() {
        notifier.onUpdateError(Update("a", "p", "d", "1", 1), null, ErrorCode.INVALID_PACKAGE)

        assertThat(listener.events.first().event, instanceOf(UpdateErrorEvent::class.java))
        assertThat(listener.events.size, equalTo(1))
    }

    @Test
    fun `onNetworkUnavailable sends event`() {
        notifier.onNetworkUnavailable(0)

        assertThat(listener.events.first().event, instanceOf(NetworkUnavailableEvent::class.java))
        assertThat(listener.events.size, equalTo(1))
    }

    @Test
    fun `onVerificationStarted sends event`() {
        notifier.onVerificationStarted(Update("a", "p", "d", "1", 1))

        assertThat(listener.events.first().event, instanceOf(VerificationStartedEvent::class.java))
        assertThat(listener.events.size, equalTo(1))
    }

    @Test
    fun `onVerificationSuccess sends event`() {
        notifier.onVerificationSuccess(Update("a", "p", "d", "1", 1))

        assertThat(listener.events.first().event, instanceOf(VerificationSuccessEvent::class.java))
        assertThat(listener.events.size, equalTo(1))
    }

    @Test
    fun `onVerificationFailed sends event`() {
        notifier.onVerificationFailed(Update("a", "p", "d", "1", 1), false)

        assertThat(listener.events.first().event, instanceOf(VerificationFailedEvent::class.java))
        assertThat(listener.events.size, equalTo(1))
    }

    @Test
    fun `onOtaInstallFailed sends event`() {
        notifier.onOtaInstallFailed(Update("a", "p", "d", "1", 1), ErrorCode.NOT_DOWNLOADED)

        assertThat(listener.events.first().event, instanceOf(OtaInstallFailedEvent::class.java))
        assertThat(listener.events.size, equalTo(1))
    }

    @Test
    fun `onUpdateAvailable sends event`() {
        notifier.onUpdateAvailable(Update("a", "p", "d", "1", 1), null, null)

        assertThat(listener.events.first().event, instanceOf(UpdateAvailableEvent::class.java))
        assertThat(listener.events.size, equalTo(1))
    }

    @Test
    fun `onDownloaded sends event`() {
        notifier.onDownloaded(Update("a", "p", "d", "1", 1))

        assertThat(listener.events.first().event, instanceOf(DownloadedEvent::class.java))
        assertThat(listener.events.size, equalTo(1))
    }

    @Test
    fun `onDownloadProgressChange sends event`() {
        notifier.onDownloadProgressChange(emptyList(), null)

        assertThat(listener.events.first().event, instanceOf(DownloadProgressChangeEvent::class.java))
        assertThat(listener.events.size, equalTo(1))
    }

    @Test
    fun `onDownloadCancelled sends event`() {
        notifier.onDownloadCancelled(Update("a", "p", "d", "1", 1), "-", ErrorCode.DOWNLOAD_CANCELLED)

        assertThat(listener.events.first().event, instanceOf(DownloadCancelledEvent::class.java))
        assertThat(listener.events.size, equalTo(1))
    }

    @Test
    fun `onDownloadError sends event`() {
        notifier.onDownloadError(Update("a", "p", "d", "1", 1), "-", ErrorCode.UNKNOWN)

        assertThat(listener.events.first().event, instanceOf(DownloadErrorEvent::class.java))
        assertThat(listener.events.size, equalTo(1))
    }

    @Test
    fun `onUpdateInProgress sends event`() {
        notifier.onUpdateInProgress(Update("a", "p", "d", "1", 1), null)

        assertThat(listener.events.first().event, instanceOf(UpdateInProgressEvent::class.java))
        assertThat(listener.events.size, equalTo(1))
    }

}

class EventListenerStub : IEventListener {
    val events = mutableListOf<BoxedEvent>()

    override fun asBinder() = null

    override fun onEvent(event: BoxedEvent?) {
        event?.let { events.add(event) }
    }
}
