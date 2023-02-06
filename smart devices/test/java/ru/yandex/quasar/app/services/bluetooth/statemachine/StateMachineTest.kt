package ru.yandex.quasar.app.services.bluetooth.statemachine

import junit.framework.Assert.assertEquals
import org.junit.Test
import org.junit.runner.RunWith
import org.robolectric.RobolectricTestRunner
import ru.yandex.quasar.app.services.bluetooth.statemachine.StateMachine.State
import ru.yandex.quasar.app.services.bluetooth.statemachine.StateMachine.Message

@RunWith(RobolectricTestRunner::class)
class StateMachineTest {
    companion object {
        val SWITCH_TO_1 = 1
        val SWITCH_TO_2 = 2
        val SWITCH_TO_3 = 3
        val SWITCH_TO_4 = 4
        val SWITCH_TO_5 = 5
        val ENTER_1 = 11
        val ENTER_2 = 12
        val ENTER_3 = 13
        val ENTER_4 = 14
        val ENTER_5 = 15
        val EXIT_1 = 21
        val EXIT_2 = 22
        val EXIT_3 = 23
        val EXIT_4 = 24
        val EXIT_5 = 25
    }
    val sm = StateMachine()
    val s1 = TestState1()
    val s2 = TestState2()
    val s3 = TestState3()
    val s4 = TestState4()
    val s5 = TestState5()
    val log = mutableListOf<Pair<Int, State>>()

    open inner class TestState: State() {
        override fun processMessage(msg: Message): Boolean {
            log.add(msg.code to this)
            return true
        }
    }

    inner class TestState1: TestState() {
        override fun processMessage(msg: Message): Boolean {
            super.processMessage(msg)
            return when (msg.code) {
                SWITCH_TO_2 -> {
                    sm.switchTo(s2)
                    true
                }
                else -> {
                    false
                }
            }
        }

        override fun onEnter() {
            log.add(ENTER_1 to this)
        }

        override fun onExit() {
            log.add(EXIT_1 to this)
        }
    }

    inner class TestState2: TestState() {
        override fun processMessage(msg: Message): Boolean {
            super.processMessage(msg)
            return when (msg.code) {
                SWITCH_TO_1 -> {
                    sm.switchTo(s1)
                    true
                }
                else -> {
                    false
                }
            }
        }

        override fun onEnter() {
            log.add(ENTER_2 to this)
        }

        override fun onExit() {
            log.add(EXIT_2 to this)
        }
    }

    inner class TestState3: TestState() {
        override fun onEnter() {
            log.add(ENTER_3 to this)
        }

        override fun onExit() {
            log.add(EXIT_3 to this)
        }
    }

    inner class TestState4: TestState() {
        override fun onEnter() {
            log.add(ENTER_4 to this)
        }

        override fun onExit() {
            log.add(EXIT_4 to this)
        }
    }

    inner class TestState5: TestState() {
        override fun onEnter() {
            log.add(ENTER_5 to this)
        }

        override fun onExit() {
            log.add(EXIT_5 to this)
        }
    }

    @Test
    fun given_twoStates_when_sendingCommands_then_stateIsSwitched() {
        sm.addState(s1)
        sm.addState(s2)
        sm.setInitialState(s1)
        sm.processMessage(Message(SWITCH_TO_2))
        sm.processMessage(Message(SWITCH_TO_1))

        assertEquals(listOf(
                ENTER_1 to s1,
                SWITCH_TO_2 to s1,
                EXIT_1 to s1,
                ENTER_2 to s2,
                SWITCH_TO_1 to s2,
                EXIT_2 to s2,
                ENTER_1 to s1
            ), log
        )
    }

    @Test
    fun given_3LevelTreeOfStates_when_switchingBetweenLeafs_then_correspondingEnterExitMethodsAreCalled() {
        sm.addState(s5)
        sm.addState(s4, s5)
        sm.addState(s3, s5)
        sm.addState(s2, s4)
        sm.addState(s1, s3)
        sm.setInitialState(s1)
        sm.processMessage(Message(SWITCH_TO_2))

        assertEquals(listOf(
                ENTER_5 to s5,
                ENTER_3 to s3,
                ENTER_1 to s1,
                SWITCH_TO_2 to s1,
                EXIT_1 to s1,
                EXIT_3 to s3,
                ENTER_4 to s4,
                ENTER_2 to s2
            ), log
        )
    }

    @Test
    fun given_parentAndAncestor_when_currentStateIsParent_then_switchingToAncestorWorks() {
        sm.addState(s1)
        sm.addState(s2, s1)
        sm.setInitialState(s1)
        sm.processMessage(Message(SWITCH_TO_2))

        assertEquals(listOf(
            ENTER_1 to s1,
            SWITCH_TO_2 to s1,
            ENTER_2 to s2
        ), log)
    }

    @Test
    fun given_parentAndAncestor_when_currentStateIsAncestor_then_switchingToParentWorks() {
        sm.addState(s1)
        sm.addState(s2, s1)
        sm.setInitialState(s2)
        sm.processMessage(Message(SWITCH_TO_1))

        assertEquals(listOf(
                ENTER_1 to s1,
                ENTER_2 to s2,
                SWITCH_TO_1 to s2,
                EXIT_2 to s2
        ), log)
    }
}
