@file:Suppress("UsePropertyAccessSyntax")

package com.yandex.tv.services.testapp

import androidx.test.platform.app.InstrumentationRegistry
import com.yandex.tv.services.common.ServiceException
import com.yandex.tv.services.common.ServiceSdk2
import com.yandex.tv.services.common.internal.AbstractServiceRemoteSdk
import com.yandex.tv.services.common.internal.IntrospectableTestServiceSdk2
import org.hamcrest.core.IsEqual
import org.hamcrest.core.IsInstanceOf
import org.junit.Assert.assertThat
import org.junit.Assert.fail
import org.junit.Test
import org.mockito.Mockito.any
import org.mockito.Mockito.spy
import org.mockito.Mockito.timeout
import org.mockito.Mockito.verify
import java.lang.ref.WeakReference
import java.util.concurrent.ExecutionException
import java.util.concurrent.TimeUnit

class SdkClientSideErrorsTest {

    @Test
    fun callSdk_returnsValue() {
        val context = InstrumentationRegistry.getInstrumentation().targetContext
        val sdk = TestServiceSdk2.Factory.create(context, "com.yandex.tv.services.testapp")

        val actual = sdk.getConstantString().get(1000, TimeUnit.MILLISECONDS)
        sdk.shutdownNow()
        assertThat(actual, IsEqual("constant_string"))
    }

    @Test
    fun submitAndShutdown_requestCompletedSdkDestroyed() {
        val context = InstrumentationRegistry.getInstrumentation().targetContext
        val sdk = deepSpyOnSdk(IntrospectableTestServiceSdk2.Factory.create(context, "com.yandex.tv.services.testapp"))

        val request = IntrospectableTestServiceSdk2.Request.GetConstantString()
        val calledBeforeShutdown = sdk.submit(request)
        sdk.shutdown()

        verify(sdk, timeout(1000).times(1)).doSubmit()
        verify(sdk, timeout(1000).times(1)).doDestroy()

        val actual = calledBeforeShutdown.get(1000, TimeUnit.MILLISECONDS)
        assertThat(actual, IsEqual("constant_string"))
    }

    @Test
    fun doubleSubmitAndShutdown_requestCompletedSdkDestroyed() {
        val context = InstrumentationRegistry.getInstrumentation().targetContext
        val sdk = deepSpyOnSdk(IntrospectableTestServiceSdk2.Factory.create(context, "com.yandex.tv.services.testapp"))

        val calledBeforeShutdown = sdk.submit(IntrospectableTestServiceSdk2.Request.GetConstantStringDelayed(100))
        Thread.sleep(50)
        val calledBeforeShutdown2 = sdk.submit(IntrospectableTestServiceSdk2.Request.GetConstantString())
        sdk.shutdown()

        verify(sdk, timeout(1000).times(2)).doSubmit()
        verify(sdk, timeout(1000).times(1)).doDestroy()

        val actual = calledBeforeShutdown.get(1000, TimeUnit.MILLISECONDS)
        assertThat(actual, IsEqual("constant_string"))
        val actual2 = calledBeforeShutdown2.get(1000, TimeUnit.MILLISECONDS)
        assertThat(actual2, IsEqual("constant_string"))
    }

    @Test
    fun submitAndShutdownNow_requestFailedWith_ERROR_CODE_ILLEGAL_SDK_STATE_sdkDestroyed() {
        val context = InstrumentationRegistry.getInstrumentation().targetContext
        val sdk = deepSpyOnSdk(IntrospectableTestServiceSdk2.Factory.create(context, "com.yandex.tv.services.testapp"))

        val request = IntrospectableTestServiceSdk2.Request.GetConstantString()
        val calledBeforeShutdownNow = sdk.submit(request)
        sdk.shutdownNow()

        verify(sdk, timeout(1000).times(1)).doSubmit()
        verify(sdk, timeout(1000).times(1)).doDestroy()

        try {
            calledBeforeShutdownNow.get(1000, TimeUnit.MILLISECONDS)
            fail("exception was expected, but not thrown")
        } catch (ee: ExecutionException) {
            val e = ee.cause as ServiceException
            assertThat(e.errorCode, IsEqual(ServiceException.ERROR_CODE_ILLEGAL_SDK_STATE))
        }
    }

    @Test
    fun callShutdownSdk_throws_ERROR_CODE_ILLEGAL_SDK_STATE() {
        val context = InstrumentationRegistry.getInstrumentation().targetContext
        val sdk = TestServiceSdk2.Factory.create(context, "com.yandex.tv.services.testapp")
        sdk.shutdown()

        try {
            sdk.getConstantString().get(1000, TimeUnit.MILLISECONDS)
            fail("exception was expected, but not thrown")
        } catch (ee: ExecutionException) {
            val e = ee.cause as ServiceException
            assertThat(e.errorCode, IsEqual(ServiceException.ERROR_CODE_ILLEGAL_SDK_STATE))
        }
    }

    @Test
    fun callNonExistentServiceSdk_throws_ERROR_CODE_CANNOT_BIND_SERVICE() {
        val context = InstrumentationRegistry.getInstrumentation().targetContext
        val sdk = NonExistentServiceSdk2.Factory.create(context, "com.yandex.tv.services.testapp")

        try {
            sdk.anyMethod().get(1000, TimeUnit.MILLISECONDS)
            sdk.shutdownNow()
            fail("exception was expected, but not thrown")
        } catch (ee: ExecutionException) {
            val e = ee.cause as ServiceException
            assertThat(e.errorCode, IsEqual(ServiceException.ERROR_CODE_CANNOT_BIND_SERVICE))
        }
    }

    @Test
    fun callDeniedServiceSdk_throws_ERROR_CODE_CANNOT_BIND_SERVICE() {
        val context = InstrumentationRegistry.getInstrumentation().targetContext
        val sdk = DeniedServiceSdk2.Factory.create(context, "com.yandex.tv.services.testapp")

        try {
            sdk.anyMethod().get(1000, TimeUnit.MILLISECONDS)
            sdk.shutdownNow()
            fail("exception was expected, but not thrown")
        } catch (ee: ExecutionException) {
            val e = ee.cause as ServiceException
            assertThat(e.errorCode, IsEqual(ServiceException.ERROR_CODE_CANNOT_BIND_SERVICE))
            assertThat(e.cause, IsInstanceOf(SecurityException::class.java))
        }
    }

    @Test
    fun callNonExistentMethod_throws_ERROR_CODE_IPC_CONTRACT_VIOLATION() {
        val context = InstrumentationRegistry.getInstrumentation().targetContext
        val sdk = TestServiceSdk2.Factory.create(context, "com.yandex.tv.services.testapp")

        try {
            sdk.nonExistentMethod().get(1000, TimeUnit.MILLISECONDS)
            sdk.shutdownNow()
            fail("exception was expected, but not thrown")
        } catch (ee: ExecutionException) {
            val e = ee.cause as ServiceException
            assertThat(e.errorCode, IsEqual(ServiceException.ERROR_CODE_IPC_CONTRACT_VIOLATION))
        }
    }

    @Test
    fun callSdkWithGarbageCollectedContext_throws_ERROR_CODE_ILLEGAL_SDK_STATE() {
        val context = InstrumentationRegistry.getInstrumentation().targetContext
        val sdk = TestServiceSdk2.Factory.create(context, "com.yandex.tv.services.testapp")

        // clear weak reference to context
        val weakContextField = AbstractServiceRemoteSdk::class.java.getDeclaredField("context")
        weakContextField.isAccessible = true
        val weakContext = weakContextField.get(sdk) as WeakReference<*>
        weakContext.clear()

        try {
            sdk.getConstantString().get(1000, TimeUnit.MILLISECONDS)
            sdk.shutdownNow()
            fail("exception was expected, but not thrown")
        } catch (ee: ExecutionException) {
            val e = ee.cause as ServiceException
            assertThat(e.errorCode, IsEqual(ServiceException.ERROR_CODE_ILLEGAL_SDK_STATE))
        }
    }

    @Test
    fun crashService_serviceReconnected() {
        val context = InstrumentationRegistry.getInstrumentation().targetContext
        val sdk = deepSpyOnSdk(IntrospectableTestServiceSdk2.Factory.create(context, "com.yandex.tv.services.testapp"))

        val request = IntrospectableTestServiceSdk2.Request.Crash()
        sdk.submit(request)
        verify(sdk, timeout(1000).times(1)).doOnConnected(any())
        verify(sdk, timeout(1000).times(1)).doOnDisconnected()

        // wait a bit and check service gets connected again
        verify(sdk, timeout(5000).times(2)).doOnConnected(any())
        sdk.shutdownNow()
    }

    // todo: enable after fix https://st.yandex-team.ru/TVANDROID-5429
    // @Test
    fun bindServiceThenForceStopApp_serviceReconnected() {
        val context = InstrumentationRegistry.getInstrumentation().targetContext
        val sdk = deepSpyOnSdk(IntrospectableTestServiceSdk2.Factory.create(context, "com.yandex.tv.services.testapp"))

        sdk.submit(IntrospectableTestServiceSdk2.Request.GetConstantString())
        verify(sdk, timeout(1000).times(1)).doOnConnected(any())

        forceStop("com.yandex.tv.services.testapp")
        verify(sdk, timeout(1000).times(1)).doOnDisconnected()

        // wait a bit and check service gets connected again
        verify(sdk, timeout(5000).times(2)).doOnConnected(any())
        sdk.shutdownNow()
    }

    // todo: enable after fix https://st.yandex-team.ru/TVANDROID-5429
    //@Test
    fun submitRequestWhileAppForceStopped_serviceReconnectedRequestExecuted() {
        val context = InstrumentationRegistry.getInstrumentation().targetContext
        val sdk = deepSpyOnSdk(IntrospectableTestServiceSdk2.Factory.create(context, "com.yandex.tv.services.testapp"))

        sdk.submit(IntrospectableTestServiceSdk2.Request.GetConstantString())
        verify(sdk, timeout(1000).times(1)).doOnConnected(any())

        forceStop("com.yandex.tv.services.testapp")
        verify(sdk, timeout(1000).times(1)).doOnDisconnected()
        val future = sdk.submit(IntrospectableTestServiceSdk2.Request.GetConstantString())

        // wait a bit and check service gets connected again
        verify(sdk, timeout(5000).times(2)).doOnConnected(any())
        val actual = future.get(1000, TimeUnit.MILLISECONDS)
        assertThat(actual, IsEqual("constant_string"))
        sdk.shutdownNow()
    }

    @Test
    fun shutdownAfterExternalDisconnect_noException() {
        val context = InstrumentationRegistry.getInstrumentation().targetContext
        val sdk = IntrospectableTestServiceSdk2.Factory.create(context, "com.yandex.tv.services.testapp")

        // trigger binding
        val future = sdk.submit(IntrospectableTestServiceSdk2.Request.GetConstantString())
        future.get(1000, TimeUnit.MILLISECONDS)

        // simulate external unbind, like it happens when ServiceConnection leak is detected
        context.unbindService(sdk.getInternalConnection())

        sdk.shutdownNow()
    }

    private fun <T : ServiceSdk2> deepSpyOnSdk(sdk: T): T {
        val spy = spy(sdk)

        val handlerField = AbstractServiceRemoteSdk::class.java.getDeclaredField("executionHandler")
        handlerField.isAccessible = true
        val handler = handlerField.get(sdk)

        val sdkField = handler.javaClass.getDeclaredField("this$0")
        sdkField.isAccessible = true
        sdkField.set(handler, spy)

        return spy
    }

    private fun forceStop(packageName: String) {
        InstrumentationRegistry.getInstrumentation().uiAutomation
                .executeShellCommand("am force-stop $packageName")
                .close()
    }

}
