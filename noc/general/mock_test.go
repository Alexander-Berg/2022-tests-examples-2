package errorbooster

import (
	"context"
	"testing"

	"github.com/stretchr/testify/mock"
	"github.com/stretchr/testify/require"

	"a.yandex-team.ru/kikimr/public/sdk/go/persqueue"
)

type writerMock struct {
	mock.Mock

	ack    chan persqueue.WriteResponse
	closed chan struct{}
}

func (m *writerMock) setup() {
	m.ack = make(chan persqueue.WriteResponse)
	m.closed = make(chan struct{})
}

func (m *writerMock) tearDown() {
	close(m.ack)
	close(m.closed)
}

func (m *writerMock) Init(ctx context.Context) (*persqueue.WriterInit, error) {
	args := m.Called(ctx)
	return args.Get(0).(*persqueue.WriterInit), args.Error(1)
}

func (m *writerMock) Write(d *persqueue.WriteMessage) error {
	args := m.Called(d)
	return args.Error(0)
}

func (m *writerMock) Close() error {
	args := m.Called()
	return args.Error(0)
}

func (m *writerMock) C() <-chan persqueue.WriteResponse {
	return m.ack
}

func (m *writerMock) Closed() <-chan struct{} {
	return m.closed
}

func (m *writerMock) Stat() persqueue.WriterStat {
	args := m.Called()
	return args.Get(0).(persqueue.WriterStat)
}

func TestMockImplements(t *testing.T) {
	require.Implements(t, (*persqueue.Writer)(nil), (*writerMock)(nil))
}
