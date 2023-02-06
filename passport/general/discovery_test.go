package kannel

import (
	"context"
	"math"
	"sync"
	"testing"
	"time"

	"a.yandex-team.ru/passport/infra/daemons/yasmsd/internal/logs"
)

// Номер телефона в РФ для тестов (не для реальной отправки!)
// В зависимости от номера результат может быть различен.
const RussianTestPhone = "+71234567890"

const GateYandexGMS = "gms"

func TestAbsDiff(t *testing.T) {
	check := func(l, r, expected uint64) {
		actual := absDiff(l, r)
		if actual != expected {
			t.Errorf(`absDiff(%d, %d), expected: %d, actual: %d`, l, r, expected, actual)
		}
	}

	check(0, 0, 0)
	check(math.MaxUint64, 0, math.MaxUint64)
	check(0, math.MaxUint64, math.MaxUint64)
	check(math.MaxUint64, math.MaxUint64, 0)

	check(10, 12, 2)
	check(12, 10, 2)
}

func TestKannelDiscovery(t *testing.T) {
	var err error

	host1 := "kannel-d1"
	host2 := "kannel-d2"

	service := NewKannelDiscovery(getKannelConfig(host1, host2), nil)

	kannel1 := service.kannels[0]
	kannel2 := service.kannels[1]

	if kannel1.host != host1 {
		t.Errorf("expected: '%s'", host1)
	}
	if kannel2.host != host2 {
		t.Errorf("expected: '%s'", host2)
	}

	reset := func() {
		kannel1.ping = true
		kannel1.status, err = kannelTestStatus(host1)
		if err != nil {
			t.Fatal(err)
		}

		kannel2.ping = true
		kannel2.status, err = kannelTestStatus(host2)
		if err != nil {
			t.Fatal(err)
		}
	}

	check := func(expected, id string) {
		actual := service.Discovery(GateYandexGMS)
		if actual != expected {
			t.Errorf("service.discovery(...) for id: '%s', expected: '%s', actual: '%s'", id, expected, actual)
		}
	}

	//
	// все kannel online, очереди на 1 меньше порога, работает случайный выбор
	//

	reset()

	// очереди на диске
	kannel1.status.stored = KannelQueueSizeThreshold
	kannel2.status.stored = 1

	// очереди ram
	kannel1.status.queued = 1
	kannel2.status.queued = KannelQueueSizeThreshold

	// очереди гейтов
	kannel1.status.gates[GateYandexGMS].queued = KannelQueueSizeThreshold
	kannel2.status.gates[GateYandexGMS].queued = 1

	var h1, h2 int
	for i := 0; i < 100; i++ {
		actual := service.Discovery(GateYandexGMS)
		if actual == host1 {
			h1++
		} else if actual == host2 {
			h2++
		} else {
			t.Errorf("expected valid host")
		}
	}

	if h1 == 0 || h2 == 0 {
		t.Errorf("expected at least once discovery")
	}

	//
	// упал хост или kannel закрыли от нагрузки
	//

	reset()
	kannel1.ping = false
	check(host2, "kannel1.ping = false")

	reset()
	kannel2.ping = false
	check(host1, "kannel2.ping = false")

	//
	// упали все хосты
	//

	reset()
	kannel1.ping = false
	kannel2.ping = false
	check("", "all kannels ping offline")

	//
	// один из хостов не получил обновление статуса kannel
	//

	reset()
	kannel1.status = nil
	check(host2, "kannel1.status = nil")

	reset()
	kannel2.status = nil
	check(host1, "kannel2.status = nil")

	//
	// все хосты не получили обновление статуса kannel
	//

	reset()
	kannel1.status = nil
	kannel2.status = nil
	check("", "all kannels status offline")

	//
	// хост отдает статус kannel, но статус offline
	//

	reset()
	kannel1.status.online = false
	check(host2, "kannel1.status.online = false")

	reset()
	kannel2.status.online = false
	check(host1, "kannel2.status.online = false")

	//
	// гейт offline
	//

	reset()
	kannel1.status.gates[GateYandexGMS].online = false
	check(host2, "kannel1.gms offline")

	reset()
	kannel2.status.gates[GateYandexGMS].online = false
	check(host1, "kannel2.gms offline")

	//
	// на одном из хостов kannel очередь на hdd больше порога
	//

	reset()
	kannel1.status.stored = KannelQueueSizeThreshold * 2
	kannel2.status.stored = KannelQueueSizeThreshold
	check(host2, "kannel1.stored threshold")

	reset()
	kannel1.status.stored = KannelQueueSizeThreshold
	kannel2.status.stored = KannelQueueSizeThreshold * 2
	check(host1, "kannel2.stored threshold")

	//
	// на одном из хостов kannel очередь ram больше порога
	//

	reset()
	kannel1.status.queued = KannelQueueSizeThreshold * 2
	kannel2.status.queued = KannelQueueSizeThreshold
	check(host2, "kannel1.queued threshold")

	reset()
	kannel1.status.queued = KannelQueueSizeThreshold
	kannel2.status.queued = KannelQueueSizeThreshold * 2
	check(host1, "kannel2.queued threshold")

	//
	// на одном из хостов kannel очередь гейта больше порога
	//

	reset()
	kannel1.status.gates[GateYandexGMS].queued = KannelQueueSizeThreshold * 2
	kannel2.status.gates[GateYandexGMS].queued = KannelQueueSizeThreshold
	check(host2, "kannel1.gates.queued threshold")

	reset()
	kannel1.status.gates[GateYandexGMS].queued = KannelQueueSizeThreshold
	kannel2.status.gates[GateYandexGMS].queued = KannelQueueSizeThreshold * 2
	check(host1, "kannel2.gates.queued threshold")
}

func TestKannelDiscoveryComplex(t *testing.T) {
	kannel1 := NewTestKannel(kannelTestStatusXMLPath())
	defer kannel1.Close()

	kannel2 := NewTestKannel(kannelTestStatusXMLPath())
	defer kannel2.Close()

	loggers := logs.NewNullLogs()

	service := NewKannelDiscovery(getKannelConfig(kannel1.URL, kannel2.URL), loggers)

	var wg sync.WaitGroup
	ctx, cancel := context.WithCancel(context.Background())

	wg.Add(1)
	service.Monitor(ctx, &wg)
	time.Sleep(KannelPingInterval)

	host := service.Discovery(GateYandexGMS)
	if len(host) == 0 {
		t.Error("expected hostname")
	} else if !(host == kannel1.URL || host == kannel2.URL) {
		t.Errorf("expected: %s or %s", kannel1.URL, kannel2.URL)
	}

	cancel()
	wg.Wait()
	loggers.Close()
}
