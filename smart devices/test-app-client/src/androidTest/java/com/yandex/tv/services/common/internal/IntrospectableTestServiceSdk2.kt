package com.yandex.tv.services.common.internal

import android.content.Context
import android.content.Intent
import android.content.ServiceConnection
import android.os.Bundle
import android.os.IBinder
import com.yandex.tv.services.common.ServiceException
import com.yandex.tv.services.common.ServiceFuture
import com.yandex.tv.services.testapp.ITestService
import com.yandex.tv.services.testapp.TestServiceSdk2

open class IntrospectableTestServiceSdk2 private constructor(context: Context, serviceName: String, bindIntent: Intent) :
        AbstractServiceRemoteSdk<ITestService>(context, serviceName, bindIntent) {

    object Factory {
        fun create(context: Context, targetPackageName: String): IntrospectableTestServiceSdk2 {
            return IntrospectableTestServiceSdk2(
                    context,
                    "IntrospectableTestService",
                    Intent().apply {
                        setPackage(targetPackageName)
                        action = "com.yandex.tv.action.BIND_TEST_SERVICE"
                    }
            )
        }
    }

    abstract class Request {
        open fun execute(service: ITestService, asyncResult: IAsyncResult) {
            execute()
        }
        open fun execute() {}

        open class GetConstantString : Request() {
            override fun execute(service: ITestService, asyncResult: IAsyncResult) {
                service.getConstantString(asyncResult)
                super.execute(service, asyncResult)
            }
        }

        open class Crash : Request() {
            override fun execute(service: ITestService, asyncResult: IAsyncResult) {
                service.crash(asyncResult)
                super.execute(service, asyncResult)
            }
        }

        open class GetConstantStringDelayed(private val delayMs: Long) : Request() {
            override fun execute(service: ITestService, asyncResult: IAsyncResult) {
                Thread.sleep(delayMs)
                service.getConstantString(asyncResult)
                super.execute(service, asyncResult)
            }
        }
    }

    fun submit(request: Request): ServiceFuture<String> {
        SdkLog.d(serviceName, "[Service] <arbitrary request> call")
        val future = CompletableServiceFuture<String>()
        class RequestImpl : IAsyncResult.Stub(), ServiceRequest<ITestService> {
            override fun onSuccess(__bundle: Bundle?) {
                if (__bundle == null) {
                    SdkLog.e(serviceName, "[Service] <arbitrary request> returned null bundle")
                    onError(ServiceException(ServiceException.ERROR_CODE_IPC_CONTRACT_VIOLATION, "TestService.getConstantString returned null bundle"))
                    return
                }
                __bundle.classLoader = TestServiceSdk2::class.java.classLoader
                future.complete(__bundle.getString(null))
                SdkLog.d(serviceName, "[Service] <arbitrary request> done")
            }

            override fun onError(e: ServiceException?) {
                var e: ServiceException? = e
                if (e == null) {
                    SdkLog.e(serviceName, "[Service] <arbitrary request> returned null exception")
                    e = ServiceException(ServiceException.ERROR_CODE_IPC_CONTRACT_VIOLATION, "IntrospectableServiceSdk.<arbitrary request> returned null exception")
                }
                future.completeExceptionally(e)
                SdkLog.d(serviceName, "[Service] <arbitrary request> done")
            }

            override fun execute(service: ITestService) {
                request.execute(service, this)
            }
        }
        submit(RequestImpl())
        return future
    }

    override fun doSubmit(request: ServiceRequest<ITestService>?) {
        super.doSubmit(request)
        doSubmit()
    }

    open fun doSubmit() {

    }

    override fun getTypedService(service: IBinder): ITestService {
        return ITestService.Stub.asInterface(service)
    }

    public override fun doOnConnected(service: IBinder?) {
        super.doOnConnected(service)
    }

    public override fun doOnDisconnected() {
        super.doOnDisconnected()
    }

    public override fun doOnAutoReconnectTimeout() {
        super.doOnAutoReconnectTimeout()
    }

    public override fun doShutdown() {
        super.doShutdown()
    }

    public override fun doDestroy() {
        super.doDestroy()
    }

    fun getInternalConnection(): ServiceConnection {
        return AbstractServiceRemoteSdk::class.java
            .getDeclaredField("connection")
            .apply { isAccessible = true }
            .get(this) as ServiceConnection
    }

}
