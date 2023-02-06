package ru.yandex.quasar.fakes

import android.webkit.ValueCallback
import ru.yandex.quasar.app.auth.AuthErrorType
import ru.yandex.quasar.app.webview.cookie.CookieHelping

class FakeCookieHelper(
    var setupsSuccessfully: Boolean
) : CookieHelping {
    override fun setupTechnicalCookies(url: String, callback: ValueCallback<Boolean>) {
        callback.onReceiveValue(setupsSuccessfully)
    }

    override fun setupAuthCookies(url: String, onSuccess: () -> Unit, onFail: (errorType: AuthErrorType) ->  Unit) {
        if (setupsSuccessfully)
            onSuccess()
        else
            onFail(AuthErrorType.GENERAL_ERROR)
    }

    override fun resetAuthCookies(url: String) {
        // TODO: implement when will be needed
    }

    override fun isObsoleteCookiesResponse(httpStatusCode: Int, getHttpHeader: (key: String) -> String?): Boolean {
        // TODO: implement when will be needed
        return false
    }

}
