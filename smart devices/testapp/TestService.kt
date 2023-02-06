package com.yandex.tv.services.testapp

import android.app.Service
import android.content.Intent
import android.os.IBinder
import kotlin.system.exitProcess

class TestService : Service() {

	private val testServiceApi: TestServiceApi by lazy {
		object : TestServiceApi {
			override fun getConstantString(): String {
				return "constant_string"
			}

			override fun crash() {
				// prevents showing "App crashed" dialog on API 25
				exitProcess(-1)
			}
		}
	}

	override fun onBind(intent: Intent?): IBinder {
		return TestServiceBinder(testServiceApi)
	}

}
