package com.yandex.launcher.updaterapp.updatermanager

import com.yandex.launcher.updaterapp.BaseRobolectricTest
import com.yandex.launcher.updaterapp.contract.IExceptionCallback
import org.hamcrest.Matchers.equalTo
import org.hamcrest.Matchers.hasItem
import org.hamcrest.Matchers.not
import org.hamcrest.MatcherAssert.assertThat
import org.junit.Test

/**
 * Test contract rules from [UpdaterManager]
 */
class UpdaterManagerTest : BaseRobolectricTest() {

    @Test
    fun `all UpdaterManager's methods should not return void or primitives`() {
        val ignoreMethods = listOf("asBinder")
        UpdaterManager::class.java.methods.forEach { method ->
            val methodName = method.name
            if (ignoreMethods.contains(methodName)) {
                return@forEach
            }

            assertThat("method=$methodName returns void", method.returnType, not(equalTo(Void.TYPE)))
            if (methodName != "getContractVersion") { // exception from rule
                assertThat("method=$methodName returns int", method.returnType, not(equalTo(Integer.TYPE)))
            }
            assertThat("method=$methodName returns boolean", method.returnType, not(equalTo(java.lang.Boolean.TYPE)))
            assertThat("method=$methodName returns long", method.returnType, not(equalTo(java.lang.Long.TYPE)))
            assertThat("method=$methodName returns short", method.returnType, not(equalTo(java.lang.Short.TYPE)))
            assertThat("method=$methodName returns byte", method.returnType, not(equalTo(java.lang.Byte.TYPE)))
            assertThat("method=$methodName returns float", method.returnType, not(equalTo(java.lang.Float.TYPE)))
            assertThat("method=$methodName returns double", method.returnType, not(equalTo(java.lang.Double.TYPE)))
            assertThat("method=$methodName returns char", method.returnType, not(equalTo(Character.TYPE)))
        }
    }

    @Test
    fun `all UpdaterManager's methods should contains IExceptionCallback as param`() {
        val ignoreMethods = listOf("asBinder")
        UpdaterManager::class.java.methods.forEach { method ->
            val methodName = method.name
            if (ignoreMethods.contains(methodName)) {
                return@forEach
            }


            assertThat("method=$methodName not contains IExceptionCallback as param", method.parameterTypes.toList(), hasItem(IExceptionCallback::class.java))
        }
    }
}
