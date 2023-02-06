package com.yandex.tv.services.testapp

import android.app.Service
import android.content.Intent
import android.os.IBinder

class DeniedService : Service() {

	private val deniedServiceApi: DeniedServiceApi by lazy {
		object : DeniedServiceApi {
			override fun anyMethod() {
				// noop
			}
		}
	}

	override fun onBind(intent: Intent?): IBinder {
		return DeniedServiceBinder(deniedServiceApi)
	}

}
