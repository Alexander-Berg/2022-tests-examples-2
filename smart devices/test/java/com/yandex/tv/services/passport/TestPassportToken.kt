package com.yandex.tv.services.passport

import com.yandex.passport.api.PassportToken

data class TestPassportToken(
        private val value: String
) : PassportToken {

    override fun getValue(): String {
        return value
    }
}
