package com.yandex.tv.services.passport

import android.accounts.Account
import com.yandex.passport.api.Passport
import com.yandex.passport.api.PassportAccount
import com.yandex.passport.api.PassportStash
import com.yandex.passport.api.PassportUid
import java.util.*

class TestPassportAccount(
        uidValue: Long,
        private val authorized: Boolean = true
) : PassportAccount {

    private val uid: PassportUid

    init {
        uid = PassportUid.Factory.from(Passport.PASSPORT_ENVIRONMENT_TESTING, uidValue)
    }

    override fun equals(other: Any?): Boolean {
        if (other !is TestPassportAccount) return false
        if (uid.environment != other.uid.environment) return false
        if (uid.value != other.uid.value) return false
        if (authorized != other.authorized) return false
        return true
    }

    override fun hashCode(): Int {
        var result = uid.hashCode()
        result = result * 31 + if (authorized) 1 else 0
        return result
    }

    override fun getUid(): PassportUid {
        return uid
    }

    override fun getPrimaryDisplayName(): String {
        return "test account"
    }

    override fun getSecondaryDisplayName(): String? {
        return null
    }

    override fun getAvatarUrl(): String? {
        return null
    }

    override fun isAvatarEmpty(): Boolean {
        return true
    }

    override fun getNativeDefaultEmail(): String? {
        return null
    }

    override fun isYandexoid(): Boolean {
        return false
    }

    override fun isBetaTester(): Boolean {
        return false
    }

    override fun isAuthorized(): Boolean {
        return authorized
    }

    override fun getStash(): PassportStash {
        return PassportStash { null }
    }

    override fun getAndroidAccount(): Account {
        return Account(uid.toString(), "test")
    }

    override fun isMailish(): Boolean {
        return false
    }

    override fun getSocialProviderCode(): String? {
        return null
    }

    override fun hasPlus(): Boolean {
        return false
    }

    override fun isPhonish(): Boolean {
        return false
    }

    override fun isSocial(): Boolean {
        return false
    }

    override fun isPdd(): Boolean {
        return false
    }

    override fun isLite(): Boolean {
        return false
    }

    override fun getFirstName(): String? {
        return null
    }

    override fun getLastName(): String? {
        return null
    }

    override fun getBirthday(): Date? {
        return null
    }

    override fun getPublicId(): String? {
        return null
    }
}
