package ru.yandex.quasar.app.auth

import okhttp3.Call
import okhttp3.OkHttpClient
import okhttp3.Protocol
import okhttp3.Request
import okhttp3.Response
import okhttp3.ResponseBody
import org.junit.Assert.assertFalse
import org.junit.Assert.assertTrue
import org.junit.Test
import org.junit.runner.RunWith
import org.mockito.kotlin.any
import org.mockito.kotlin.doReturn
import org.mockito.kotlin.mock
import org.robolectric.RobolectricTestRunner
import ru.yandex.quasar.app.utils.NetworkConnectionWaiting
import ru.yandex.quasar.app.utils.scheduler.RetryScheduler
import ru.yandex.quasar.fakes.FakeCall
import ru.yandex.quasar.fakes.FakeExecutorService
import ru.yandex.quasar.protobuf.ModelObjects
import ru.yandex.quasar.core.utils.Observable
import java.io.IOException
import java.util.concurrent.ExecutorService
import javax.inject.Provider

@RunWith(RobolectricTestRunner::class)
class AuthRequestExecutorTest {

    @Test
    fun executeRequestEnqueuesExecution() {
        val request = createRequest()
        val call = FakeCall(request)
        val executorService = FakeExecutorService()
        val authRequestExecutor = createAuthRequestExecutor(
            { request },
            call,
            mock(),
            executorService)
        val failed = Array(1) { false }
        authRequestExecutor.addOnFailListener { failed[0] = true }
        authRequestExecutor.executeRequest()
        executorService.runAllJobs()
        assertTrue("Execution should be enqueued", call.isEnqueued())
        assertFalse("First execution should not fail", failed[0])
    }

    @Test
    fun executeRequestFailsOnSecondCall() {
        val request = createRequest()
        val call = FakeCall(request)
        val executorService = FakeExecutorService()
        val authRequestExecutor = createAuthRequestExecutor(
            { request },
            call,
            mock(),
            executorService)
        val failed = Array(1) { false }
        authRequestExecutor.addOnFailListener { failed[0] = true }
        authRequestExecutor.executeRequest()
        executorService.runAllJobs()
        authRequestExecutor.executeRequest()
        executorService.runAllJobs()
        assertTrue("Second execution should fail", failed[0])
    }

    @Test
    fun cancelCancelsRequestCallAndScheduler() {
        val request = createRequest()
        val call = FakeCall(request)
        val retryScheduler = RetrySchedulerMock()
        val executorService = FakeExecutorService()
        val authRequestExecutor = createAuthRequestExecutor({ request }, call, retryScheduler, executorService)
        authRequestExecutor.executeRequest()
        executorService.runAllJobs()
        authRequestExecutor.cancel()
        assertTrue(call.isCanceled())
        assertTrue(retryScheduler.cancelled)
    }

    @Test
    fun onFailureRequestFailsWhenCancelled() {
        val request = createRequest()
        val call = FakeCall(request)
        val retryScheduler = RetrySchedulerMock()
        val executorService = FakeExecutorService()
        val authRequestExecutor = createAuthRequestExecutor({ request }, call, retryScheduler, executorService)
        val failed = Array(1) { false }
        authRequestExecutor.addOnFailListener { failed[0] = true }
        authRequestExecutor.executeRequest()
        executorService .runAllJobs()
        authRequestExecutor.cancel()
        authRequestExecutor.onFailure(call, IOException())
        assertTrue("Request should fail on cancel", failed[0])
        assertFalse(retryScheduler.scheduled)
    }

    @Test
    fun onFailureRetriesRequest() {
        val request = createRequest()
        val call = FakeCall(request)
        val retryScheduler = RetrySchedulerMock()
        val executorService = FakeExecutorService()
        val authRequestExecutor = createAuthRequestExecutor({ request }, call, retryScheduler, executorService)
        val failed = Array(1) { false }
        authRequestExecutor.addOnFailListener { failed[0] = true }
        authRequestExecutor.executeRequest()
        executorService.runAllJobs()
        authRequestExecutor.onFailure(call, IOException())
        assertFalse("Request should be retried on failure", failed[0])
        assertTrue(retryScheduler.scheduled)
    }

    @Test
    fun onResponseFailsOnIncorrectUrl() {
        val incorrectUrl = "https://google.com"
        val request = createRequest(incorrectUrl)
        val call = FakeCall(request)
        val retryScheduler = RetrySchedulerMock()
        val executorService = FakeExecutorService()
        val authRequestExecutor = createAuthRequestExecutor({ request }, call, retryScheduler, executorService)
        val failed = Array(1) { false }
        authRequestExecutor.addOnFailListener { failed[0] = true }
        authRequestExecutor.executeRequest()
        executorService.runAllJobs()
        authRequestExecutor.onResponse(call, createResponse(200, request))
        assertTrue("Request should fail if redirect url and last request url are not equal",
            failed[0])
        assertFalse(retryScheduler.scheduled)
    }

    @Test
    fun onResponseFailsOnNonServerError() {
        val request = createRequest()
        val call = FakeCall(request)
        val retryScheduler = RetrySchedulerMock()
        val executorService = FakeExecutorService()
        val authRequestExecutor = createAuthRequestExecutor({ request }, call, retryScheduler, executorService)
        val failed = Array(1) { false }
        authRequestExecutor.addOnFailListener { failed[0] = true }
        authRequestExecutor.executeRequest()
        executorService.runAllJobs()
        authRequestExecutor.onResponse(call, createResponse(404, request))
        assertTrue("Request should fail on non server error", failed[0])
        assertFalse(retryScheduler.scheduled)
    }

    @Test
    fun onResponseRetriesOnServerError() {
        val request = createRequest()
        val call = FakeCall(request)
        val retryScheduler = RetrySchedulerMock()
        val executorService = FakeExecutorService()
        val authRequestExecutor = createAuthRequestExecutor({ request }, call, retryScheduler, executorService)
        val failed = Array(1) { false }
        authRequestExecutor.addOnFailListener { failed[0] = true }
        executorService.runAllJobs()
        authRequestExecutor.executeRequest()
        authRequestExecutor.onResponse(call, createResponse(500, request))
        assertFalse("Request should be retried on server error", failed[0])
        assertTrue(retryScheduler.scheduled)
    }

    @Test
    fun onResponseSucceedsOnCorrectUrl() {
        val request = createRequest()
        val call = FakeCall(request)
        val retryScheduler = RetrySchedulerMock()
        val executorService = FakeExecutorService()
        val authRequestExecutor = createAuthRequestExecutor({ request }, call, retryScheduler, executorService)
        val succeed = Array(1) { false }
        authRequestExecutor.addOnSuccessListener { succeed[0] = true }
        authRequestExecutor.executeRequest()
        executorService.runAllJobs()
        authRequestExecutor.onResponse(call, createResponse(200, request))
        assertTrue("Request should succeed on code 200 and correct final url", succeed[0])
        assertFalse(retryScheduler.scheduled)
    }

    @Test
    fun requestIsRetriedOnAuthServerException() {
        val request = createRequest()
        val call = FakeCall(request)
        val retryScheduler = RetrySchedulerMock()
        val executorService = FakeExecutorService()
        val authRequestExecutor = createAuthRequestExecutor(
            { throw AuthServerException("Status 500") }, call, retryScheduler, executorService)
        authRequestExecutor.executeRequest()
        executorService.runAllJobs()
        assertTrue(retryScheduler.scheduled)
    }

    @Test
    fun requestFailsOnRuntimeExceptionInRequestProvider() {
        val request = createRequest()
        val call = FakeCall(request)
        val retryScheduler = RetrySchedulerMock()
        val executorService = FakeExecutorService()
        val authRequestExecutor = createAuthRequestExecutor(
            { throw RuntimeException() }, call, retryScheduler, executorService)
        val failed = Array(1) { false }
        authRequestExecutor.addOnFailListener { failed[0] = true }
        authRequestExecutor.executeRequest()
        executorService.runAllJobs()
        assertTrue("Request should fail on non server error", failed[0])
        assertFalse(retryScheduler.scheduled)
    }

    @Test
    fun when_noConnection_then_executionIsNotEnqueued() {
        val request = createRequest()
        val call = FakeCall(request)
        val executorService = FakeExecutorService()
        val authRequestExecutor = createAuthRequestExecutor(
            { request },
            call,
            mock(),
            executorService,
            false
        )
        val failed = Array(1) { false }
        authRequestExecutor.addOnFailListener { failed[0] = true }
        authRequestExecutor.executeRequest()
        executorService.runAllJobs()
        assertFalse("Execution should be enqueued", call.isEnqueued())
        assertFalse("First execution should not fail", failed[0])
    }

    @Test
    fun when_executionCancelledWithNoConnection_then_failCallbackCalled() {
        val request = createRequest()
        val call = FakeCall(request)
        val executorService = FakeExecutorService()
        val authRequestExecutor = createAuthRequestExecutor(
            { request },
            call,
            mock(),
            executorService,
            false
        )
        val failed = Array(1) { false }
        authRequestExecutor.addOnFailListener { failed[0] = true }
        authRequestExecutor.executeRequest()
        executorService.runAllJobs()
        authRequestExecutor.cancel()
        assertFalse("Execution should be enqueued", call.isEnqueued())
        assertTrue("Auth request executor should fail", failed[0])
    }

    private fun createRequest(url: String = "https://ya.ru"): Request {
        return Request.Builder().url(url).build()
    }

    private fun createAuthRequestExecutor(
        request: () -> Request,
        call: Call,
        retryScheduler: RetryScheduler,
        executorService: ExecutorService,
        withConnection: Boolean = true,
        redirectUrl: String = "https://ya.ru"
    ): AuthRequestExecutor {
        val httpClient = mock<OkHttpClient> {
            on { newCall(any()) }.doReturn(call)
        }
        val networkObservable =
            Observable<ModelObjects.NetworkStatus?> {}
        val wifiStatus = ModelObjects.WifiStatus.newBuilder()
            .setStatus(ModelObjects.WifiStatus.Status.CONNECTED)
            .setSignal(ModelObjects.WifiStatus.Signal.EXCELLENT).build()
        val networkStatus = ModelObjects.NetworkStatus.newBuilder()
            .setStatus(ModelObjects.NetworkStatus.Status.CONNECTED)
            .setWifiStatus(wifiStatus).build()
        if (withConnection) {
            networkObservable.receiveValue(networkStatus)
        }
        return AuthRequestExecutor(
            "token",
            "uid",
            Provider { httpClient },
            mock(),
            request,
            NetworkConnectionWaiting(networkObservable),
            redirectUrl,
            retryScheduler,
            executorService)
    }

    private fun createResponse(code: Int, request: Request): Response {
        return Response.Builder()
            .code(code)
            .request(request)
            .protocol(Protocol.HTTP_2)
            .message("Message")
            .body(ResponseBody.create(null, ""))
            .build()
    }

    private class RetrySchedulerMock :
        RetryScheduler(mock(), 0L, 0L) {

        var scheduled = false
            private set

        override fun shouldRetry(): Boolean {
            return true
        }

        override fun schedule(task: () -> Unit) {
            scheduled = true
        }
    }
}
