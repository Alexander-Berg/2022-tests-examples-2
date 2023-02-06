package slbcloghandler

import (
	"testing"

	"github.com/stretchr/testify/assert"
)

func TestEqual(t *testing.T) {
	a := rsFqdnDBItem{ip: "127.0.0.1", fqdn: "localhost"}
	ad := rsFqdnDBItem{ip: "127.0.0.1", fqdn: "localhost"}
	b := rsFqdnDBItem{ip: "127.0.0.2", fqdn: "localhost2"}
	assert.True(t, a.compare(&ad))
	assert.True(t, a.compare(&a))
	assert.False(t, a.compare(&b))
	assert.False(t, b.compare(&ad))
}

func toDBItem(data []rsFqdnDBItem) []dbItem {
	res := []dbItem{}
	for _, i := range data {
		res = append(res, &i)
	}
	return res
}

func TestDiff(t *testing.T) {
	prevItems := rsFqdnDBItems{pos: 0, items: []rsFqdnDBItem{
		{ip: "127.0.0.1", fqdn: "localhost"},
		{ip: "127.0.0.2", fqdn: "localhost2"},
	}}
	newItem := rsFqdnDBItems{pos: 0, items: []rsFqdnDBItem{
		{ip: "127.0.0.1", fqdn: "localhost"},
		{ip: "127.0.0.3", fqdn: "localhost2"},
	}}
	prevIndex := prevItems.makeIndex()
	newIndex := newItem.makeIndex()
	updateRows, deleteRows := makeDiff(prevIndex, newIndex)
	assert.Equal(t, toDBItem([]rsFqdnDBItem{{ip: "127.0.0.3", fqdn: "localhost2"}}), updateRows)
	assert.Equal(t, toDBItem([]rsFqdnDBItem{{ip: "127.0.0.2", fqdn: "localhost2"}}),
		deleteRows)
}
