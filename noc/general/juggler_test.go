package slbcloghandler

import (
	"testing"

	"github.com/stretchr/testify/assert"
)

var emptyMsg []jugglerMsg

func TestJugglerReducerRepeat(t *testing.T) {
	var messages []jugglerMsg
	prevIndex := jugglerEventIndex{}
	openTime := 1600000000
	lastSentIndex := map[jugglerKey]uint32{}
	m := App{}

	event := eventsBalancers{balancerState: BalancerState{B1: BalancerOk}}
	for _, msg := range event.FormatJuggler() {
		msg.OpenTime = openTime
		messages = append(messages, msg)
	}

	newIndex := m.makeMessagesIndex(messages)
	sendMessages := m.reduceMessages(newIndex, prevIndex, lastSentIndex)
	expJugglerMsg := []jugglerMsg{
		{
			Description: "",
			Hostname:    B1,
			Instance:    "",
			Service:     "balancer_status",
			Status:      jugglerStatusOk,
			OpenTime:    openTime,
			Tags:        []string{"slbcloghandler", "type_balancer_status"},
		}}
	assert.ElementsMatch(t, sendMessages, expJugglerMsg)

	prevIndex = newIndex
	seen := 0
	for i := uint32(0); i < jugglerHashDiv; i++ {
		newIndex = m.makeMessagesIndex(messages)
		sendMessages = m.reduceMessages(newIndex, prevIndex, lastSentIndex)
		seen += len(sendMessages)
		if len(sendMessages) > 0 {
			assert.ElementsMatch(t, sendMessages, expJugglerMsg)
		}
	}
	assert.Equal(t, seen, 1)
}

func TestJugglerReducerStatusChange(t *testing.T) {
	var messages []jugglerMsg
	prevIndex := jugglerEventIndex{}
	openTime := 1600000000
	m := App{}
	lastSentIndex := map[jugglerKey]uint32{}

	jmsg := eventsBalancers{balancerState: BalancerState{B1: BalancerOk}}
	for _, msg := range jmsg.FormatJuggler() {
		msg.OpenTime = openTime
		messages = append(messages, msg)
	}

	newIndex := m.makeMessagesIndex(messages)

	sendMessages := m.reduceMessages(newIndex, prevIndex, lastSentIndex)
	assert.ElementsMatch(t, sendMessages, []jugglerMsg{
		{
			Description: "",
			Hostname:    B1,
			Instance:    "",
			Service:     "balancer_status",
			Status:      jugglerStatusOk,
			OpenTime:    openTime,
			Tags:        []string{"slbcloghandler", "type_balancer_status"},
		},
	},
	)
	prevIndex = newIndex

	jmsg = eventsBalancers{balancerState: BalancerState{B1: BalancerNoData}}
	for _, msg := range jmsg.FormatJuggler() {
		msg.OpenTime = openTime
		messages = append(messages, msg)
	}

	newIndex = m.makeMessagesIndex(messages)
	sendMessages = m.reduceMessages(newIndex, prevIndex, lastSentIndex)
	assert.ElementsMatch(t, sendMessages, []jugglerMsg{
		{
			Description: "no data",
			Hostname:    B1,
			Instance:    "",
			Service:     "balancer_status",
			Status:      jugglerStatusCrit,
			OpenTime:    openTime,
			Tags:        []string{"slbcloghandler", "type_balancer_status"},
		},
	},
	)
	prevIndex = newIndex

	// no changes no messages
	newIndex = m.makeMessagesIndex(messages)
	sendMessages = m.reduceMessages(newIndex, prevIndex, lastSentIndex)
	assert.ElementsMatch(t, sendMessages, emptyMsg)
	prevIndex = newIndex
}
