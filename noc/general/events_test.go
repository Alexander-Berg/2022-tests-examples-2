package slbcloghandler

import (
	"testing"
	"time"

	"github.com/stretchr/testify/assert"
)

const (
	B1           = "balancer1"
	B2           = "balancer2"
	B1Loc        = "unknown"
	Service1Name = "serviceololo"
	Service1Ip1  = "2a02:6b8::1"
	Service1Ip2  = "2a02:6b8::2"
	RS1          = "2a02:6b8:1234::1"
	RS2          = "2a02:6b8:1234::2"
	RS3          = "2a02:6b8:1234::3"
	RS4          = "2a02:6b8:1234::4"
)

// constant
var emptyEvents = []mainEvent(nil)
var emptyEventsBalancers = eventsBalancers{balancerState: BalancerState{B1: BalancerOk, B2: BalancerOk}}
var emptyEventsBalancers2 = eventsBalancers{balancerState: BalancerState{B1: BalancerOk, B2: BalancerNoData}}
var emptyEventsRsDuplicates = eventsRsDuplicates{Text: ""}
var emptyEventsVipDuplicates = eventsVipDuplicates{Text: ""}

type gSta struct {
	Vips []gVip
	Host string
}

type gVip struct {
	IP     string
	Port   int
	Quorum int
	Qstate int
	Rss    []gRs
}

type gRs struct {
	IP    string
	Alive int
}

func makeSta(conf gSta) BalancerStat {
	r := BalancerStat{Status: StatusOk}
	r.Host = conf.Host
	r.Server.TS = int(time.Now().Unix())
	for _, vip := range conf.Vips {
		var rsss []Rs
		for _, rs := range vip.Rss {
			rsss = append(rsss, Rs{IP: rs.IP, Alive: rs.Alive, Port: 80})
		}
		vipPort := 389
		if vip.Port != 0 {
			vipPort = vip.Port
		}
		r.Server.Conf = append(r.Server.Conf, Conf{
			Rs:          rsss,
			Vip:         vip.IP,
			Port:        vipPort,
			Quorum:      vip.Quorum,
			QuorumState: vip.Qstate,
			Protocol:    "TCP", Af: "INET6", QuorumUp: "/etc/keepalived/quorum-handler2.sh up " + vip.IP + ",b-100,1"})
	}
	return r
}

func assertEvents(snapshot map[balancer]CurrentBalancerState, expectedEvents CurrentEvents, t *testing.T) {
	okBalancerQuorum = 2
	conf := NewConfig()
	conf.PushAPI = false
	conf.API = false
	conf.Solomon = &SolomonConfig{}
	conf.Analyzer = &AnalyzerConfig{
		FlapCalculationLength: 5,
		FlapDivider:           24,
		CalcInterval:          5,
		FlapMaxThreshold:      10,
		FlapAvgThreshold:      1,
	}
	app, err := NewApp(&conf)
	if err != nil {
		t.Error(err)
	}
	app.Iteration = 1
	app.expectedBalancers = expectedBalancers{B1: ExpBalancerOk, B2: ExpBalancerOk}
	fakeServiceName := servicenameToVs{}
	fakeServiceName[Service1Name] = []vs{Service1Ip1, Service1Ip2}
	app.UpdateServiceNameFromMap(fakeServiceName)
	for _, balancerData := range snapshot {
		app.UpdateBalancerStateStructures(balancerData.State)
	}
	app.setSnapshot(snapshot)
	app.tickEvents()
	expectedEvents.LastUpdate = app.CurrentEvents.LastUpdate
	assert.Equal(t, expectedEvents, *app.CurrentEvents)
}

func TestAllDown(t *testing.T) {
	state := gSta{
		Host: B1,
		Vips: []gVip{
			{IP: Service1Ip1, Qstate: 0, Quorum: 1, Rss: []gRs{{IP: RS1, Alive: 0}}},
			{IP: Service1Ip2, Qstate: 0, Quorum: 1, Rss: []gRs{{IP: RS1, Alive: 0}}},
		}}

	snapshot := map[balancer]CurrentBalancerState{}
	snapshot[B1] = CurrentBalancerState{State: makeSta(state), Status: StatusOk}
	expectedEvents := CurrentEvents{
		VipIPDown: []mainEvent{
			eventsVsDownFull{
				eventsVsDown:  eventsVsDown{Vs: Service1Ip1},
				balancersDown: balancers{B1}},
			eventsVsDownFull{
				eventsVsDown:  eventsVsDown{Vs: Service1Ip2},
				balancersDown: balancers{B1}}},
		FqdnDown: []mainEvent{eventsServicenameDownFull{
			eventsServicenameDown: eventsServicenameDown{Servicename: Service1Name},
			vsDown:                vss{Service1Ip1, Service1Ip2}}},
		BalancerNodata: emptyEventsBalancers2,
		RsEvents: []mainEvent{eventsRsDiscrepancy{
			Location:    B1Loc,
			Status:      EventStatusError,
			Servicename: Service1Name,
			PercUp:      0,
			RssDown:     map[string]bool{RS1: true},
		}},
		RsDupEvents:  emptyEventsRsDuplicates,
		VipDupEvents: emptyEventsVipDuplicates,
	}

	assertEvents(snapshot, expectedEvents, t)
}

func TestQuarterDown(t *testing.T) {
	state := gSta{
		Host: B1,
		Vips: []gVip{
			{IP: Service1Ip1, Qstate: 1, Quorum: 1, Port: 80, Rss: []gRs{
				{IP: RS1, Alive: 1},
				{IP: RS2, Alive: 0},
				{IP: RS3, Alive: 0},
				{IP: RS4, Alive: 0},
			}},
			{IP: Service1Ip2, Qstate: 1, Quorum: 1, Port: 80, Rss: []gRs{
				{IP: RS1, Alive: 1},
				{IP: RS2, Alive: 0},
				{IP: RS3, Alive: 0},
				{IP: RS4, Alive: 0},
			}},
			{IP: Service1Ip1, Qstate: 1, Quorum: 1, Port: 443, Rss: []gRs{
				{IP: RS1, Alive: 1},
				{IP: RS2, Alive: 0},
				{IP: RS3, Alive: 0},
				{IP: RS4, Alive: 0},
			}},
			{IP: Service1Ip2, Qstate: 1, Quorum: 1, Port: 443, Rss: []gRs{
				{IP: RS1, Alive: 1},
				{IP: RS2, Alive: 0},
				{IP: RS3, Alive: 0},
				{IP: RS4, Alive: 0},
			}},
		}}

	snapshot := map[balancer]CurrentBalancerState{}
	snapshot[B1] = CurrentBalancerState{State: makeSta(state), Status: StatusOk}
	expectedEvents := CurrentEvents{
		VipIPDown: []mainEvent{
			eventsVsDownFull{
				eventsVsDown:  eventsVsDown{Vs: Service1Ip1},
				balancersDown: []balancer{B1}},
			eventsVsDownFull{
				eventsVsDown:  eventsVsDown{Vs: Service1Ip2},
				balancersDown: []balancer{B1}}},
		FqdnDown: []mainEvent{eventsServicenameDownFull{
			eventsServicenameDown: eventsServicenameDown{Servicename: Service1Name},
			vsDown:                vss{Service1Ip1, Service1Ip2}}},
		BalancerNodata: emptyEventsBalancers2,
		RsEvents: []mainEvent{eventsRsDiscrepancy{
			Location:    B1Loc,
			Servicename: Service1Name,
			PercUp:      25,
			RssDown:     map[string]bool{RS2: true, RS3: true, RS4: true},
		}},
		RsDupEvents:  emptyEventsRsDuplicates,
		VipDupEvents: emptyEventsVipDuplicates,
	}
	assertEvents(snapshot, expectedEvents, t)
}

func TestAllUp(t *testing.T) {
	state := gSta{
		Host: B1,
		Vips: []gVip{
			{IP: Service1Ip1, Qstate: 1, Quorum: 1, Rss: []gRs{{IP: RS1, Alive: 1}}},
			{IP: Service1Ip2, Qstate: 1, Quorum: 1, Rss: []gRs{{IP: RS1, Alive: 1}}},
		}}

	snapshot := map[balancer]CurrentBalancerState{}
	snapshot[B1] = CurrentBalancerState{State: makeSta(state), Status: StatusOk}
	expectedEvents := CurrentEvents{
		VipIPDown: emptyEvents,
		FqdnDown: []mainEvent{eventsServicenameDownOk{eventsServicenameDown: eventsServicenameDown{Servicename: Service1Name},
			vsUp: vss{Service1Ip1, Service1Ip2}}},
		BalancerNodata: emptyEventsBalancers2,
		RsEvents: []mainEvent{
			eventsRsDiscrepancy{
				Location:    B1Loc,
				Servicename: Service1Name,
				PercUp:      100,
				Status:      EventStatusOk,
				RssDown:     map[string]bool{},
			},
		},
		RsDupEvents:  emptyEventsRsDuplicates,
		VipDupEvents: emptyEventsVipDuplicates,
	}

	assertEvents(snapshot, expectedEvents, t)
}

// NOCDEV-2522
func Test1RsDownEverywhere(t *testing.T) {
	stateB1 := gSta{
		Host: B1,
		Vips: []gVip{
			{IP: Service1Ip1, Qstate: 1, Quorum: 1, Rss: []gRs{{IP: RS1, Alive: 0}}},
			{IP: Service1Ip2, Qstate: 1, Quorum: 1, Rss: []gRs{{IP: RS2, Alive: 1}}}},
	}
	stateB2 := gSta{
		Host: B2,
		Vips: []gVip{
			{IP: Service1Ip1, Qstate: 1, Quorum: 1, Rss: []gRs{{IP: RS1, Alive: 0}}},
			{IP: Service1Ip2, Qstate: 1, Quorum: 1, Rss: []gRs{{IP: RS2, Alive: 1}}}},
	}

	snapshot := map[balancer]CurrentBalancerState{}
	snapshot[B1] = CurrentBalancerState{State: makeSta(stateB1), Status: StatusOk}
	snapshot[B2] = CurrentBalancerState{State: makeSta(stateB2), Status: StatusOk}
	expectedEvents := CurrentEvents{
		VipIPDown: emptyEvents,
		FqdnDown: []mainEvent{eventsServicenameDownOk{eventsServicenameDown: eventsServicenameDown{Servicename: Service1Name},
			vsUp: vss{Service1Ip1, Service1Ip2}}},
		BalancerNodata: emptyEventsBalancers,
		RsEvents: []mainEvent{
			eventsRsDiscrepancy{
				Location:    B1Loc,
				Servicename: Service1Name,
				PercUp:      50,
				Status:      EventStatusError,
				RssDown:     map[string]bool{RS1: true},
			},
		},
		RsDupEvents:  emptyEventsRsDuplicates,
		VipDupEvents: emptyEventsVipDuplicates,
	}

	assertEvents(snapshot, expectedEvents, t)
}

func TestAllDownOnOneBalancer(t *testing.T) {
	stateB1 := gSta{
		Host: B1,
		Vips: []gVip{
			{IP: Service1Ip1, Qstate: 1, Quorum: 1, Rss: []gRs{{IP: RS1, Alive: 1}}},
			{IP: Service1Ip2, Qstate: 1, Quorum: 1, Rss: []gRs{{IP: RS2, Alive: 1}}}},
	}
	stateB2 := gSta{
		Host: B2,
		Vips: []gVip{
			{IP: Service1Ip1, Qstate: 0, Quorum: 1, Rss: []gRs{{IP: RS1, Alive: 0}}},
			{IP: Service1Ip2, Qstate: 0, Quorum: 1, Rss: []gRs{{IP: RS2, Alive: 0}}}},
	}

	snapshot := map[balancer]CurrentBalancerState{}
	snapshot[B1] = CurrentBalancerState{State: makeSta(stateB1), Status: StatusOk}
	snapshot[B2] = CurrentBalancerState{State: makeSta(stateB2), Status: StatusOk}
	expectedEvents := CurrentEvents{
		VipIPDown: []mainEvent{
			eventsVsDownPartial{
				eventsVsDown:  eventsVsDown{Vs: Service1Ip1},
				balancersUp:   []balancer{B1},
				balancersDown: []balancer{B2}},
			eventsVsDownPartial{
				eventsVsDown:  eventsVsDown{Vs: Service1Ip2},
				balancersUp:   []balancer{B1},
				balancersDown: []balancer{B2}}},
		FqdnDown: []mainEvent{eventsServicenameDownOk{eventsServicenameDown: eventsServicenameDown{Servicename: Service1Name},
			vsUp: vss{Service1Ip1, Service1Ip2}}},
		BalancerNodata: emptyEventsBalancers,
		RsEvents: []mainEvent{
			eventsRsDiscrepancy{
				Location:    B1Loc,
				Servicename: Service1Name,
				PercUp:      100,
				Status:      EventStatusOk,
				RssDown:     map[string]bool{},
			},
		},
		RsDupEvents:  emptyEventsRsDuplicates,
		VipDupEvents: emptyEventsVipDuplicates,
	}

	assertEvents(snapshot, expectedEvents, t)
}
