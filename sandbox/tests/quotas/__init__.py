import uuid
import random
import collections

import pytest

import sandbox.serviceq.types as qtypes


MOCKED_WINDOW_SIZE = 10


@pytest.fixture
def patch_api_consumption(monkeypatch):
    monkeypatch.setattr(qtypes.ComplexApiConsumption, "WINDOW_SIZE", 10)
    monkeypatch.setattr(qtypes.ComplexApiConsumption, "WEB_WINDOW_SIZE", 15)


class TestQuotas(object):
    Capatibilities = collections.namedtuple("Capatibilities", "cores ram")

    def test__dominanta_accounting_common(self, qserver):
        task = self.Capatibilities(12, 32 << 10)
        host = self.Capatibilities(32, 32 << 12)
        dominanta = qserver._Server__calculate_cpu_based_dominanta(task, host, False)
        expected = host.cores * 10
        assert dominanta == expected

    def test__dominanta_accounting_multislot(self, qserver):
        task = self.Capatibilities(2, 32 << 10)
        host = self.Capatibilities(32, 32 << 12)
        dominanta = qserver._Server__calculate_cpu_based_dominanta(task, host, True)
        expected = 80
        assert dominanta == expected

    def test__dominanta_accounting_multislot_minimal_slot(self, qserver):
        task = self.Capatibilities(1, 1 << 10)
        host = self.Capatibilities(24, (24 * 3) << 10)
        dominanta = qserver._Server__calculate_cpu_based_dominanta(task, host, True)
        expected = 10
        assert dominanta == expected

    def test__consumption_one_execution_1(self):
        qp = 80
        job_id = uuid.uuid4().bytes
        duration = 5
        real_duration = duration + 1
        start_time = 1
        cons = qtypes.Consumption(window_size=MOCKED_WINDOW_SIZE)
        assert cons == qtypes.Consumption.decode(cons.encode())

        #        |          |          |
        expected = (0, 0)
        assert cons.calculate(start_time) == expected
        cons.check_invariants()
        assert cons.recalculate() == expected
        assert cons.executing_jobs == []
        assert cons == qtypes.Consumption.decode(cons.encode())

        assert (cons.ram, cons.cpu, cons.hdd, cons.ssd) == (0, 0, 0, 0)
        cons.started(start_time, job_id, qp, duration, 100, 4, 1000, 2000)
        assert (cons.ram, cons.cpu, cons.hdd, cons.ssd) == (100, 4, 1000, 2000)
        cons.check_invariants()
        #        |          |<----     |
        assert cons.executing_jobs == [job_id]
        expected = (0, qp * duration)
        assert cons.recalculate() == expected
        assert cons.calculate(start_time) == expected
        assert cons.calculate(start_time) == expected
        cons.check_invariants()
        assert cons == qtypes.Consumption.decode(cons.encode())

        #        |         <|----      |
        expected = (qp, qp * (duration - 1))
        assert cons.recalculate(start_time + 1) == expected
        assert cons.calculate(start_time + 1) == expected
        cons.check_invariants()
        assert cons.recalculate() == expected
        assert cons == qtypes.Consumption.decode(cons.encode())

        #        |      <---|-         |
        expected = (qp * (duration - 1), qp)
        assert cons.calculate(start_time + duration - 1) == expected
        cons.check_invariants()
        assert cons.recalculate() == expected
        assert cons == qtypes.Consumption.decode(cons.encode())

        #        |     <----|          |
        expected = (qp * duration, 0)
        assert cons.calculate(start_time + duration) == expected
        cons.check_invariants()
        assert cons.recalculate() == expected
        assert cons.executing_jobs == [job_id]
        assert cons == qtypes.Consumption.decode(cons.encode())

        #        |    <-----|          |
        expected = (qp * real_duration, 0)
        assert cons.calculate(start_time + real_duration) == expected
        cons.check_invariants()
        assert cons.recalculate() == expected
        assert cons.executing_jobs == [job_id]
        assert cons == qtypes.Consumption.decode(cons.encode())

        cons.finished(start_time + real_duration, job_id)
        assert (cons.ram, cons.cpu, cons.hdd, cons.ssd) == (0, 0, 0, 0)
        cons.check_invariants()
        assert cons == qtypes.Consumption.decode(cons.encode())

        #        |   <----- |          |
        expected = (qp * real_duration, 0)
        assert cons.calculate(start_time + real_duration + 1) == expected
        cons.check_invariants()
        assert cons.recalculate() == expected
        assert cons.executing_jobs == []
        assert cons == qtypes.Consumption.decode(cons.encode())

        #        |<-----    |          |
        expected = (qp * real_duration, 0)
        assert cons.calculate(start_time + cons.window_size) == expected
        cons.check_invariants()
        assert cons.recalculate() == expected
        assert cons == qtypes.Consumption.decode(cons.encode())

        #       <|-----    |          |
        expected = (qp * (real_duration - 1), 0)
        assert cons.calculate(start_time + cons.window_size + 1) == expected
        cons.check_invariants()
        assert cons.recalculate() == expected
        assert cons == qtypes.Consumption.decode(cons.encode())

        #   <----|-        |          |
        expected = (qp, 0)
        assert cons.calculate(start_time + cons.window_size + real_duration - 1) == expected
        cons.check_invariants()
        assert cons.recalculate() == expected
        assert cons == qtypes.Consumption.decode(cons.encode())

        #  <-----|         |          |
        expected = (0, 0)
        assert cons.calculate(start_time + cons.window_size + real_duration) == expected
        cons.check_invariants()
        assert cons.recalculate() == expected
        assert cons == qtypes.Consumption.decode(cons.encode())
        # <----- |         |          |
        assert cons.calculate(start_time + cons.window_size + real_duration + 1) == expected
        cons.check_invariants()
        assert cons.recalculate() == expected
        assert cons == qtypes.Consumption.decode(cons.encode())

    def test__consumption_one_execution_2(self):
        qp = 80
        job_id = uuid.uuid4().bytes
        duration = 5
        real_duration = duration + 1
        start_time = 1
        cons = qtypes.Consumption(window_size=MOCKED_WINDOW_SIZE)

        cons.started(start_time, job_id, qp, duration, 0, 0, 0, 0)
        cons.check_invariants()
        #        |          |<----     |
        assert cons.executing_jobs == [job_id]
        expected = (0, qp * duration)
        assert cons.calculate(start_time) == expected
        cons.check_invariants()
        assert cons.recalculate() == expected

        #        |        <-|---       |
        expected = (qp * 2, qp * (duration - 2))
        assert cons.calculate(start_time + 2) == expected
        cons.check_invariants()
        assert cons.recalculate() == expected

        assert cons.executing_jobs == [job_id]
        cons.finished(start_time + real_duration, job_id)
        cons.check_invariants()
        assert cons.executing_jobs == []

        #        | <-----   |          |
        expected = (qp * real_duration, 0)
        assert cons.calculate(start_time + cons.window_size - 1) == expected
        cons.check_invariants()
        assert cons.recalculate() == expected

        #       <|-----    |          |
        expected = (qp * (real_duration - 1), 0)
        assert cons.calculate(start_time + cons.window_size + 1) == expected
        cons.check_invariants()
        assert cons.recalculate() == expected

        #   <----|-        |          |
        expected = (qp, 0)
        assert cons.calculate(start_time + cons.window_size + real_duration - 1) == expected
        cons.check_invariants()
        assert cons.recalculate() == expected

        # <----- |         |          |
        expected = (0, 0)
        assert cons.calculate(start_time + cons.window_size + real_duration + 1) == expected
        cons.check_invariants()
        assert cons.recalculate() == expected

    def test__consumption_one_execution_3(self):
        qp = 80
        job_id = uuid.uuid4().bytes
        duration = 5
        real_duration = duration + 1
        start_time = 1
        cons = qtypes.Consumption(window_size=MOCKED_WINDOW_SIZE)

        cons.started(start_time, job_id, qp, duration, 0, 0, 0, 0)
        cons.check_invariants()
        #        |          |<----     |
        assert cons.executing_jobs == [job_id]
        expected = (0, qp * duration)
        assert cons.calculate(start_time) == expected
        cons.check_invariants()
        assert cons.recalculate() == expected

        assert cons.executing_jobs == [job_id]
        cons.finished(start_time + real_duration, job_id)
        cons.check_invariants()
        assert cons.executing_jobs == []

        # <----- |         |          |
        expected = (0, 0)
        assert cons.calculate(start_time + cons.window_size + real_duration + 1) == expected
        cons.check_invariants()
        assert cons.recalculate() == expected

    def test__consumption_one_execution_4(self):
        qp = 80
        job_id = uuid.uuid4().bytes
        duration = 5
        real_duration = duration - 1
        start_time = 1
        cons = qtypes.Consumption(window_size=MOCKED_WINDOW_SIZE)

        cons.started(start_time, job_id, qp, duration, 0, 0, 0, 0)
        cons.check_invariants()
        #        |          |<----     |
        assert cons.executing_jobs == [job_id]
        expected = (0, qp * duration)
        assert cons.calculate(start_time) == expected
        cons.check_invariants()
        assert cons.recalculate() == expected

        #        |      <---|-         |
        expected = (qp * real_duration, qp)
        assert cons.calculate(start_time + real_duration) == expected
        cons.check_invariants()
        assert cons.recalculate() == expected

        #        |      <---|          |
        assert cons.executing_jobs == [job_id]
        cons.finished(start_time + real_duration, job_id)
        cons.check_invariants()
        expected = (qp * real_duration, 0)
        assert cons.calculate(start_time + real_duration) == expected
        cons.check_invariants()
        assert cons.recalculate() == expected
        assert cons.executing_jobs == []

        #        |     <--- |          |
        assert cons.calculate(start_time + real_duration + 1) == expected
        cons.check_invariants()
        assert cons.recalculate() == expected

    def test__consumption_one_execution_5(self):
        qp = 80
        job_id = uuid.uuid4().bytes
        duration = 12
        real_duration = duration + 1
        start_time = 1
        cons = qtypes.Consumption(window_size=MOCKED_WINDOW_SIZE)

        cons.started(start_time, job_id, qp, duration, 0, 0, 0, 0)
        cons.check_invariants()
        #               |          |<---------|--
        assert cons.executing_jobs == [job_id]
        expected = (0, qp * cons.window_size)
        assert cons.calculate(start_time) == expected
        cons.check_invariants()
        assert cons.recalculate() == expected

        #               |        <-|--------  |
        expected = (qp * 2, qp * (cons.window_size - 2))
        assert cons.calculate(start_time + 2) == expected
        cons.check_invariants()
        assert cons.recalculate() == expected

        #               |<---------|          |
        expected = (qp * cons.window_size, 0)
        assert cons.calculate(start_time + cons.window_size) == expected
        cons.check_invariants()
        assert cons.recalculate() == expected

        #            <--|----------|          |
        expected = (qp * cons.window_size, 0)
        assert cons.calculate(start_time + real_duration) == expected
        cons.check_invariants()
        assert cons.recalculate() == expected

        assert cons.executing_jobs == [job_id]
        cons.finished(start_time + real_duration, job_id)
        cons.check_invariants()
        assert cons.executing_jobs == []

        #           <---|--------- |          |
        expected = (qp * (cons.window_size - 1), 0)
        assert cons.calculate(start_time + real_duration + 1) == expected
        cons.check_invariants()
        assert cons.recalculate() == expected

        #   <-----------|-         |          |
        expected = (qp, 0)
        assert cons.calculate(start_time + cons.window_size + real_duration - 1) == expected
        cons.check_invariants()
        assert cons.recalculate() == expected

        #  <------------|          |          |
        expected = (0, 0)
        assert cons.calculate(start_time + cons.window_size + real_duration) == expected
        cons.check_invariants()
        assert cons.recalculate() == expected

        # <------------ |          |          |
        assert cons.calculate(start_time + cons.window_size + real_duration + 1) == expected
        cons.check_invariants()
        assert cons.recalculate() == expected

    def test__consumption_one_execution_6(self):
        qp = 80
        job_id = uuid.uuid4().bytes
        duration = 12
        real_duration = duration - 1
        start_time = 1
        cons = qtypes.Consumption(window_size=MOCKED_WINDOW_SIZE)

        cons.started(start_time, job_id, qp, duration, 0, 0, 0, 0)
        cons.check_invariants()
        #             |          |<---------|--
        assert cons.executing_jobs == [job_id]
        expected = (0, qp * cons.window_size)
        assert cons.calculate(start_time) == expected
        cons.check_invariants()
        assert cons.recalculate() == expected

        #            <|----------|          |
        expected = (qp * cons.window_size, 0)
        assert cons.recalculate(start_time + real_duration) == expected
        assert cons.calculate(start_time + real_duration) == expected
        cons.check_invariants()
        assert cons.recalculate() == expected

        assert cons.executing_jobs == [job_id]
        cons.finished(start_time + real_duration, job_id)
        cons.check_invariants()
        assert cons.executing_jobs == []

        #           <-|--------- |          |
        expected = (qp * (cons.window_size - 1), 0)
        assert cons.calculate(start_time + real_duration + 1) == expected
        cons.check_invariants()
        assert cons.recalculate() == expected

        #  <----------|          |          |
        expected = (0, 0)
        assert cons.calculate(start_time + cons.window_size + real_duration) == expected
        cons.check_invariants()
        assert cons.recalculate() == expected

        # <---------- |          |          |
        expected = (0, 0)
        assert cons.calculate(start_time + cons.window_size + real_duration + 1) == expected
        cons.check_invariants()
        assert cons.recalculate() == expected

    def test__consumption_one_execution_7(self):
        qp = 80
        job_id = uuid.uuid4().bytes
        duration = 12
        real_duration = duration - 1
        start_time = 1
        cons = qtypes.Consumption(window_size=MOCKED_WINDOW_SIZE)

        cons.started(start_time, job_id, qp, duration, 0, 0, 0, 0)
        cons.check_invariants()
        #             |          |<---------|--
        assert cons.executing_jobs == [job_id]
        expected = (0, qp * cons.window_size)
        assert cons.recalculate(start_time) == expected

        assert cons.executing_jobs == [job_id]
        cons.finished(start_time + real_duration, job_id)
        cons.check_invariants()
        assert cons.executing_jobs == []

        # <---------- |          |          |
        expected = (0, 0)
        assert cons.calculate(start_time + cons.window_size + real_duration + 1) == expected
        cons.check_invariants()
        assert cons.recalculate() == expected

    def test__consumption_one_execution_8(self):
        qp = 80
        job_id = uuid.uuid4().bytes
        duration = 0
        real_duration = 5
        start_time = 1
        cons = qtypes.Consumption(window_size=MOCKED_WINDOW_SIZE)

        cons.started(start_time, job_id, qp, duration, 0, 0, 0, 0)
        cons.check_invariants()
        # |          |          |
        expected = (0, qp * duration)
        assert cons.recalculate() == expected

        assert cons.executing_jobs == [job_id]
        cons.finished(start_time + real_duration, job_id)
        cons.check_invariants()
        assert cons.executing_jobs == []

        # |   <----  |          |
        expected = (qp * real_duration, 0)
        assert cons.calculate(start_time + real_duration + 2) == expected
        cons.check_invariants()
        assert cons.recalculate() == expected

    def test__consumption_two_executions_1(self):
        qp = 80
        job1_id = uuid.uuid4().bytes
        job2_id = uuid.uuid4().bytes
        duration = 1
        real_duration = 5
        start_time = 1
        cons = qtypes.Consumption(window_size=MOCKED_WINDOW_SIZE)

        #      |          |          |
        assert (cons.ram, cons.cpu, cons.hdd, cons.ssd) == (0, 0, 0, 0)
        cons.started(start_time, job1_id, qp, duration, 100, 4, 1000, 0)
        assert (cons.ram, cons.cpu, cons.hdd, cons.ssd) == (100, 4, 1000, 0)
        cons.check_invariants()
        #      |          |<         |
        assert cons.qp == (0, qp)
        expected = (0, qp * duration)
        assert cons.recalculate() == expected

        assert cons.executing_jobs == [job1_id]
        #      |     <----|          |
        cons.finished(start_time + real_duration, job1_id)
        assert (cons.ram, cons.cpu, cons.hdd, cons.ssd) == (0, 0, 0, 0)
        cons.check_invariants()
        assert cons.qp == (qp * real_duration, 0)
        assert cons.executing_jobs == []

        cons.started(start_time + real_duration + 1, job2_id, qp, duration, 200, 8, 0, 2000)
        assert (cons.ram, cons.cpu, cons.hdd, cons.ssd) == (200, 8, 0, 2000)
        cons.check_invariants()
        #      |    <---- |          |
        #      |          |<         |
        expected = (qp * real_duration, qp * duration)
        assert cons.qp == expected
        assert cons.recalculate(start_time + real_duration + 1) == expected

        cons.finished(start_time + real_duration * 2 + 1, job2_id)
        assert (cons.ram, cons.cpu, cons.hdd, cons.ssd) == (0, 0, 0, 0)
        cons.check_invariants()
        #     <|----      |          |
        #      |     <----|          |
        expected = (qp * (real_duration * 2 - 1), 0)
        assert cons.qp == expected
        assert cons.calculate(start_time + real_duration * 2 + 1) == expected
        cons.check_invariants()
        assert cons.recalculate() == expected

        #    <-|---       |          |
        #      |    <---- |          |
        expected = (qp * (real_duration * 2 - 2), 0)
        assert cons.calculate(start_time + real_duration * 2 + 2) == expected
        cons.check_invariants()
        assert cons.recalculate() == expected

        # <----|          |          |
        #      | <----    |          |
        expected = (qp * real_duration, 0)
        assert cons.calculate(start_time + real_duration * 2 + 5) == expected
        cons.check_invariants()
        assert cons.recalculate() == expected

    def test__consumption_two_executions_2(self):
        qp = 80
        job1_id = uuid.uuid4().bytes
        job2_id = uuid.uuid4().bytes
        duration = 0
        real_duration = 5
        start_time = 1
        cons = qtypes.Consumption(window_size=MOCKED_WINDOW_SIZE)

        #      |          |          |
        cons.started(start_time, job1_id, qp, duration, 0, 0, 0, 0)
        cons.check_invariants()
        #      |        <-|          |
        expected = (qp * 2, 0)
        assert cons.calculate(start_time + 2) == expected
        cons.check_invariants()
        #      |     <----|          |
        cons.finished(start_time + real_duration, job1_id)
        cons.check_invariants()
        #      |    <---- |          |
        #      |          |          |
        cons.started(start_time + real_duration + 1, job2_id, qp, duration, 0, 0, 0, 0)
        cons.check_invariants()
        expected = (qp * real_duration, 0)
        assert cons.recalculate(start_time + real_duration + 1) == expected
        assert cons.calculate(start_time + real_duration + 1) == expected
        cons.check_invariants()
        #      |  <----   |          |
        #      |        <-|          |
        expected = (qp * (real_duration + 2), 0)
        assert cons.calculate(start_time + real_duration + 3) == expected
        cons.check_invariants()
        #     <|----      |          |
        #      |     <----|          |
        expected = (qp * (real_duration * 2 - 1), 0)
        assert cons.calculate(start_time + real_duration + 6) == expected
        cons.check_invariants()
        cons.finished(start_time + real_duration + 6, job2_id)
        cons.check_invariants()
        assert cons.executing_jobs == []
        # <----|          |          |
        #      | <----    |          |
        expected = (qp * real_duration, 0)
        assert cons.calculate(start_time + real_duration + 10) == expected
        cons.check_invariants()

    def test__consumption_two_executions_3(self):
        qp1 = 80
        qp2 = 120
        job1_id = uuid.uuid4().bytes
        job2_id = uuid.uuid4().bytes
        duration1 = 2
        duration2 = 3
        real_duration1 = 5
        real_duration2 = 10
        start_time = 1
        cons = qtypes.Consumption(window_size=MOCKED_WINDOW_SIZE)

        #             |          |          |
        assert cons.executing_jobs == []
        assert (cons.ram, cons.cpu, cons.hdd, cons.ssd) == (0, 0, 0, 0)
        cons.started(start_time, job1_id, qp1, duration1, 100, 4, 1000, 0)
        assert (cons.ram, cons.cpu, cons.hdd, cons.ssd) == (100, 4, 1000, 0)
        cons.check_invariants()
        cons.started(start_time, job2_id, qp2, duration2, 200, 8, 0, 2000)
        assert (cons.ram, cons.cpu, cons.hdd, cons.ssd) == (300, 12, 1000, 2000)
        cons.check_invariants()
        assert sorted(cons.executing_jobs) == sorted([job1_id, job2_id])
        #             |          |<-        |
        #             |          |<--       |
        expected = (0, qp1 * duration1 + qp2 * duration2)
        assert cons.calculate(start_time) == expected
        cons.check_invariants()
        assert cons.recalculate() == expected
        #             |         <|-         |
        #             |         <|--        |
        expected = (qp1 + qp2, qp1 * (duration1 - 1) + qp2 * (duration2 - 1))
        assert cons.calculate(start_time + 1) == expected
        cons.check_invariants()
        assert cons.recalculate() == expected
        #             |     <----|          |
        #             |     <----|          |
        expected = ((qp1 + qp2) * real_duration1, 0)
        assert cons.calculate(start_time + real_duration1) == expected
        cons.check_invariants()
        assert cons.recalculate() == expected
        cons.finished(start_time + real_duration1, job1_id)
        assert (cons.ram, cons.cpu, cons.hdd, cons.ssd) == (200, 8, 0, 2000)
        cons.check_invariants()
        assert cons.executing_jobs == [job2_id]
        #             |<----     |          |
        #             |<---------|          |
        expected = (qp1 * real_duration1 + qp2 * real_duration2, 0)
        assert cons.calculate(start_time + real_duration2) == expected
        cons.check_invariants()
        assert cons.recalculate() == expected
        cons.finished(start_time + real_duration2, job2_id)
        assert (cons.ram, cons.cpu, cons.hdd, cons.ssd) == (0, 0, 0, 0)
        cons.check_invariants()
        #         <---|-         |          |
        #         <---|------    |          |
        expected = (qp1 + qp2 * 6, 0)
        assert cons.calculate(start_time + real_duration2 + 4) == expected
        cons.check_invariants()
        assert cons.recalculate() == expected
        #    <----    |         |          |
        #    <--------|-        |          |
        expected = (qp2, 0)
        assert cons.calculate(start_time + real_duration2 * 2 - 1) == expected
        cons.check_invariants()
        assert cons.recalculate() == expected
        #  <----      |         |          |
        #  <--------- |         |          |
        expected = (0, 0)
        assert cons.calculate(start_time + real_duration2 * 2 + 1) == expected
        cons.check_invariants()
        assert cons.recalculate() == expected

    def test__consumption_two_executions_4(self):
        qp1 = 80
        qp2 = 120
        job1_id = uuid.uuid4().bytes
        job2_id = uuid.uuid4().bytes
        duration1 = 2
        duration2 = 3
        real_duration1 = 5
        real_duration2 = 11
        start_time = 1
        cons = qtypes.Consumption(window_size=MOCKED_WINDOW_SIZE)

        #             |          |          |
        assert cons.executing_jobs == []
        cons.started(start_time, job1_id, qp1, duration1, 0, 0, 0, 0)
        cons.check_invariants()
        #             |          |<-        |
        cons.started(start_time + 1, job2_id, qp2, duration2, 0, 0, 0, 0)
        cons.check_invariants()
        assert sorted(cons.executing_jobs) == sorted([job1_id, job2_id])
        #             |         <|-         |
        #             |          |<--       |
        expected = (qp1, qp1 + qp2 * duration2)
        assert cons.calculate(start_time + 1) == expected
        cons.check_invariants()
        assert cons.recalculate() == expected
        #             |       <--|         |
        #             |        <-|-        |
        expected = (qp1 * 3 + qp2 * 2, qp2)
        assert cons.calculate(start_time + 3) == expected
        cons.check_invariants()
        assert cons.recalculate() == expected
        #             |     <----|          |
        #             |      <---|          |
        expected = (qp1 * real_duration1 + qp2 * 4, 0)
        assert cons.calculate(start_time + real_duration1) == expected
        cons.check_invariants()
        assert cons.recalculate() == expected
        cons.finished(start_time + real_duration1, job1_id)
        cons.check_invariants()
        assert cons.executing_jobs == [job2_id]
        #             |<----     |          |
        #             | <--------|          |
        expected = (qp1 * real_duration1 + qp2 * 9, 0)
        assert cons.calculate(start_time + real_duration1 * 2) == expected
        cons.check_invariants()
        assert cons.recalculate() == expected
        #            <|----      |          |
        #             |<---------|          |
        expected = (qp1 * 4 + qp2 * cons.window_size, 0)
        assert cons.calculate(start_time + real_duration1 * 2 + 1) == expected
        cons.check_invariants()
        assert cons.recalculate() == expected
        #           <-|---       |          |
        #            <|----------|          |
        expected = (qp1 * 3 + qp2 * cons.window_size, 0)
        assert cons.calculate(start_time + real_duration1 * 2 + 2) == expected
        cons.check_invariants()
        assert cons.recalculate() == expected
        cons.finished(start_time + real_duration1 * 2 + 2, job2_id)
        cons.check_invariants()
        assert cons.executing_jobs == []
        #          <--|--       |          |
        #           <-|-------- |          |
        expected = (qp1 * 2 + qp2 * (cons.window_size - 1), 0)
        assert cons.calculate(start_time + real_duration1 * 2 + 3) == expected
        cons.check_invariants()
        assert cons.recalculate() == expected
        #  <----      |         |          |
        #   <---------|-        |          |
        expected = (qp2, 0)
        assert cons.calculate(start_time + real_duration2 * 2 - 1) == expected
        cons.check_invariants()
        assert cons.recalculate() == expected
        # <----       |         |          |
        #  <----------|         |          |
        expected = (0, 0)
        assert cons.calculate(start_time + real_duration2 * 2) == expected
        cons.check_invariants()
        assert cons.recalculate() == expected

    def test__consumption_random(self):
        random_consumption = 100
        cons = qtypes.Consumption(window_size=random_consumption)
        duration_range = (1, cons.window_size)
        qp_range = (1, 100)
        Job = collections.namedtuple("Job", "job_id started duration")
        jobs = []
        for now in xrange(1, 1000):
            for _ in xrange(random.randint(0, 10)):
                job_id = uuid.uuid4().bytes
                job = Job(job_id, now, random.randint(*duration_range))
                jobs.append(job)
                cons.started(job.started, job_id, random.randint(*qp_range), job.duration, 0, 0, 0, 0)
                cons.check_invariants()
            for _ in xrange(random.randint(0, 10)):
                if not jobs:
                    break
                job_index = random.randint(0, len(jobs) - 1)
                job = jobs[job_index]
                if job.started < now:
                    cons.finished(now, job.job_id)
                    cons.check_invariants()
                    del jobs[job_index]
            if not random.randint(0, 100):
                cons.calculate(now)
                cons.check_invariants()


class TestUsageMetrics(object):
    def test__empty_metrics(self):
        cons = qtypes.Consumption()
        metrics = cons.calculate_usage_metrics(0, flush=False)
        assert metrics == [qtypes.UsageMetric((0, 0, 0))]
        assert metrics is cons.calculate_usage_metrics(0, flush=False)
        assert metrics is cons.calculate_usage_metrics(0, flush=True)
        assert metrics is not cons.calculate_usage_metrics(0, flush=True)

    def test__single_job_in_hour_metrics(self):
        cons = qtypes.Consumption()
        job_id = uuid.uuid4().bytes
        qp = 80
        cons.started(0, job_id, qp, 0, 0, 0, 0, 0)
        assert cons.calculate_usage_metrics(0) == [qtypes.UsageMetric((0, 0, 0))]
        now = qtypes.USAGE_METRICS_GRANULARITY - 1
        assert cons.calculate_usage_metrics(now, flush=False) == [qtypes.UsageMetric((0, now, qp * now))]
        cons.finished(now, job_id)
        assert cons.calculate_usage_metrics(now) == [qtypes.UsageMetric((0, now, qp * now))]
        assert cons.calculate_usage_metrics(now) == [qtypes.UsageMetric((now, now, 0))]

    def test__single_job_cross_hour_metrics(self):
        gran = qtypes.USAGE_METRICS_GRANULARITY
        cons = qtypes.Consumption()
        job_id = uuid.uuid4().bytes
        qp = 80
        cons.started(0, job_id, qp, 0, 0, 0, 0, 0)
        assert cons.calculate_usage_metrics(gran - 1, flush=False) == [
            qtypes.UsageMetric((0, gran - 1, qp * (gran - 1))),
        ]
        assert cons.calculate_usage_metrics(gran, flush=False) == [
            qtypes.UsageMetric((0, gran - 1, qp * gran)),
            qtypes.UsageMetric((gran, gran, 0)),
        ]
        assert cons.calculate_usage_metrics(gran + 1, flush=False) == [
            qtypes.UsageMetric((0, gran - 1, qp * gran)),
            qtypes.UsageMetric((gran, gran + 1, qp)),
        ]
        now = gran + gran // 2
        cons.finished(now, job_id)
        metrics = cons.calculate_usage_metrics(now)
        assert metrics == [
            qtypes.UsageMetric((0, gran - 1, qp * gran)),
            qtypes.UsageMetric((gran, now, qp * (now - gran))),
        ]

    def test__two_jobs_in_hour_metrics(self):
        gran = qtypes.USAGE_METRICS_GRANULARITY
        cons = qtypes.Consumption()
        job1_id = uuid.uuid4().bytes
        job2_id = uuid.uuid4().bytes
        qp1 = 80
        qp2 = 120
        cons.started(0, job1_id, qp1, 0, 0, 0, 0, 0)
        now = gran // 4
        assert cons.calculate_usage_metrics(now, flush=False) == [
            qtypes.UsageMetric((0, now, qp1 * now)),
        ]
        cons.started(now, job2_id, qp2, 0, 0, 0, 0, 0)
        later = now + gran // 4
        assert cons.calculate_usage_metrics(later, flush=False) == [
            qtypes.UsageMetric((0, later, qp1 * later + qp2 * (later - now))),
        ]
        cons.finished(later, job1_id)
        assert cons.calculate_usage_metrics(later, flush=False) == [
            qtypes.UsageMetric((0, later, qp1 * later + qp2 * (later - now))),
        ]
        later2 = later + gran // 4
        cons.finished(later2, job2_id)
        assert cons.calculate_usage_metrics(later2, flush=False) == [
            qtypes.UsageMetric((0, later2, qp1 * later + qp2 * (later2 - now))),
        ]

    def test__two_jobs_cross_hour_metrics(self):
        gran = qtypes.USAGE_METRICS_GRANULARITY
        cons = qtypes.Consumption()
        job1_id = uuid.uuid4().bytes
        job2_id = uuid.uuid4().bytes
        qp1 = 80
        qp2 = 120
        cons.started(0, job1_id, qp1, 0, 0, 0, 0, 0)
        now = gran // 2
        assert cons.calculate_usage_metrics(now, flush=False) == [
            qtypes.UsageMetric((0, now, qp1 * now)),
        ]
        cons.started(now, job2_id, qp2, 0, 0, 0, 0, 0)
        later = now + gran
        assert cons.calculate_usage_metrics(later, flush=False) == [
            qtypes.UsageMetric((0, gran - 1, qp1 * gran + qp2 * (gran - now))),
            qtypes.UsageMetric((gran, later, (qp1 + qp2) * (later - gran))),
        ]
        cons.finished(later, job1_id)
        assert cons.calculate_usage_metrics(later, flush=False) == [
            qtypes.UsageMetric((0, gran - 1, qp1 * gran + qp2 * (gran - now))),
            qtypes.UsageMetric((gran, later, (qp1 + qp2) * (later - gran))),
        ]
        later2 = later + gran // 4
        cons.finished(later2, job2_id)
        assert cons.calculate_usage_metrics(later2, flush=False) == [
            qtypes.UsageMetric((0, gran - 1, qp1 * gran + qp2 * (gran - now))),
            qtypes.UsageMetric((gran, later2, qp1 * (later - gran) + qp2 * (later2 - gran))),
        ]


class TestApiQuotas(object):
    def test__api_consumption_table_rotation(self):
        consumption = qtypes.ApiConsumption(10, 100)
        user_name = "test_user"
        consumption.add_user(user_name)
        current_consumption = 0
        global_time = 0
        for delta in range(1, 11):
            global_time += 1
            current_consumption += delta
            consumption.rotate_table(global_time)
            consumption.add_consumption(user_name, global_time, delta)
            assert consumption.consumption[user_name][0] == current_consumption

        for delta in range(1, 10):
            global_time += 1
            current_consumption -= delta
            consumption.rotate_table(global_time)
            assert consumption.consumption[user_name][0] == current_consumption

        current_consumption -= 10
        assert current_consumption == 0
        global_time += 1
        consumption.rotate_table(global_time)
        assert user_name not in consumption.consumption

    @pytest.mark.usefixtures("patch_api_consumption")
    def test__complex_api_consumption_table_rotation(self):
        consumption = qtypes.ComplexApiConsumption()
        current_api_consumption = 0
        current_web_consumption = 0
        global_time = 0
        user_name = "test_user"

        def add_and_check_consumption(api_delta, web_delta, current_api_consumption, current_web_consumption):
            consumption.api_consumption.add_consumption(user_name, global_time, api_delta)
            consumption.web_api_consumption.add_consumption(user_name, global_time, web_delta)
            assert consumption.api_consumption.consumption[user_name][0] == current_api_consumption
            assert consumption.web_api_consumption.consumption[user_name][0] == current_web_consumption

        for delta in range(1, 11):
            global_time += 1
            current_api_consumption += delta
            current_web_consumption += delta
            consumption._rotate_table(global_time)
            add_and_check_consumption(delta, delta, current_api_consumption, current_web_consumption)

        for api_delta, web_delta in zip(range(1, 6), range(11, 16)):
            global_time += 1
            current_api_consumption -= api_delta
            current_web_consumption += web_delta
            consumption._rotate_table(global_time)
            add_and_check_consumption(0, web_delta, current_api_consumption, current_web_consumption)

        for api_delta, web_delta in zip(range(6, 10), range(1, 5)):
            global_time += 1
            current_api_consumption -= api_delta
            current_web_consumption -= web_delta
            consumption._rotate_table(global_time)
            add_and_check_consumption(0, 0, current_api_consumption, current_web_consumption)

        global_time += 1
        current_api_consumption -= 10
        current_web_consumption -= 5
        assert current_api_consumption == 0
        consumption._rotate_table(global_time)
        assert user_name not in consumption.api_consumption.consumption

        for delta in range(6, 15):
            global_time += 1
            current_web_consumption -= delta
            consumption._rotate_table(global_time)
            assert user_name not in consumption.api_consumption.consumption
            assert consumption.web_api_consumption.consumption[user_name][0] == current_web_consumption

        global_time += 1
        current_web_consumption -= 15
        assert current_web_consumption == 0
        consumption._rotate_table(global_time)
        assert user_name not in consumption.api_consumption.consumption
        assert user_name not in consumption.web_api_consumption.consumption


class TestQuotaPoolsType(object):
    def test__quota_pools__empty(self):
        pools = qtypes.QuotaPools()
        assert len(pools.pools) == 0
        assert pools.pools.index == {}
        data = pools.encode()
        assert data == [[], {}, {}]
        assert qtypes.QuotaPools.decode(data) == pools

    def test__quota_pools__add(self):
        pools = qtypes.QuotaPools()
        assert pools.add("POOL1", ["TAG1", "TAG2"]) == 0
        with pytest.raises(ValueError):
            pools.add("POOL1", ["TAG3", "TAG4"])
        assert pools.add("POOL2", ["TAG3", "TAG4"]) == 1
        assert pools.add("POOL3", ["TAG1", "TAG3"]) == 2
        for tags in (["TAG1", "TAG2"], ["TAG1"], ["TAG1", "TAG2", "TAG3"]):
            with pytest.raises(ValueError):
                pools.add("POOL4", tags)
        assert len(pools.pools.index) == 3
        for i, pool in enumerate(("POOL1", "POOL2", "POOL3")):
            assert pools.pools[i] == pool and pools.pools.index[pool] == i
        assert "POOL4" not in pools.pools

    def test__quota_pools__update(self):
        pools = qtypes.QuotaPools()
        assert pools.add("POOL1", ["TAG1", "TAG2"]) == 0
        assert pools.add("POOL2", ["TAG3", "TAG4"]) == 1
        assert pools.add("POOL3", ["TAG1", "TAG3"]) == 2
        with pytest.raises(ValueError):
            pools.update("POOL1", ["TAG1", "TAG3"])
        with pytest.raises(ValueError):
            pools.update("POOL2", ["TAG3", "TAG4", "TAG1"])
        pools.update("POOL1", ["TAG1", "TAG2", "TAG4"])
        pools.update("POOL1", ["TAG1", "TAG2", "TAG5"])
        assert pools.default(None) == qtypes.DEFAULT_QUOTA
        pool1_index = pools.pools.index["POOL1"]
        assert pools.default(pool1_index) == 0
        pools.update("POOL1", default_quota=42)
        assert pools.default(pool1_index) == 42

    def test__quota_pools__match_tags(self):
        pools = qtypes.QuotaPools()
        pool1_index = pools.add("POOL1", ["TAG1", "TAG2"])
        pool2_index = pools.add("POOL2", ["TAG3", "TAG4"])
        pool3_index = pools.add("POOL3", ["TAG1", "TAG3"])
        assert pools.match_pool(["TAG"]) is None
        assert pools.match_pool(["TAG1"]) is None
        assert pools.match_pool(["TAG1", "TAG2", "TAG3"]) == pool1_index
        assert pools.match_pool(["TAG3", "TAG1"]) == pool3_index
        assert pools.match_pool(["TAG3", "TAG4"]) == pool2_index
        assert pools.match_pool(None) is None
