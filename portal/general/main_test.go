package runtimeconfig

import (
	"testing"
	"time"

	"github.com/stretchr/testify/assert"
	"github.com/stretchr/testify/require"

	"a.yandex-team.ru/portal/avocado/libs/utils/advsync"
	"a.yandex-team.ru/portal/avocado/libs/utils/fs"
	"a.yandex-team.ru/portal/avocado/libs/utils/log3"
)

func TestLinearFileSelector(t *testing.T) {
	selector := NewLinearFileSelector("a", "b", "c", "d")
	type event struct {
		fsEvent      fs.Event
		shouldUpdate bool
	}
	type stateCheckStruct struct {
		events        []event
		expectedFile  string
		expectedError error
	}
	checks := []stateCheckStruct{
		{
			events:        []event{},
			expectedFile:  "",
			expectedError: NoSelectedFileError{},
		},
		{
			events: []event{
				event{
					fsEvent: fs.Event{
						Name: "b",
						Op:   fs.Create,
					},
					shouldUpdate: true,
				},
				event{
					fsEvent: fs.Event{
						Name: "c",
						Op:   fs.Create,
					},
					shouldUpdate: true,
				},
				event{
					fsEvent: fs.Event{
						Name: "b",
						Op:   fs.Create,
					},
					shouldUpdate: false,
				},
			},
			expectedFile:  "c",
			expectedError: nil,
		},
		{
			events: []event{
				event{
					fsEvent: fs.Event{
						Name: "a",
						Op:   fs.Create,
					},
					shouldUpdate: false,
				},
				event{
					fsEvent: fs.Event{
						Name: "c",
						Op:   fs.Remove,
					},
					shouldUpdate: true,
				},
			},
			expectedFile:  "b",
			expectedError: nil,
		},
		{
			events: []event{
				event{
					fsEvent: fs.Event{
						Name: "d",
						Op:   fs.Create,
					},
					shouldUpdate: true,
				},
				event{
					fsEvent: fs.Event{
						Name: "d",
						Op:   fs.Create,
					},
					shouldUpdate: true,
				},
			},
			expectedFile:  "d",
			expectedError: nil,
		},
		{
			events: []event{
				event{
					fsEvent: fs.Event{
						Name: "a",
						Op:   fs.Remove,
					},
					shouldUpdate: false,
				},
				event{
					fsEvent: fs.Event{
						Name: "d",
						Op:   fs.Remove,
					},
					shouldUpdate: true,
				},
				event{
					fsEvent: fs.Event{
						Name: "b",
						Op:   fs.Remove,
					},
					shouldUpdate: true,
				},
			},
			expectedFile:  "",
			expectedError: NoSelectedFileError{},
		},
	}
	for _, check := range checks {
		for _, event := range check.events {
			shouldUpdate := selector.ShouldUpdate(event.fsEvent)
			require.Equal(t, event.shouldUpdate, shouldUpdate)
		}
		selected, err := selector.GetSelectedFile()
		require.Equal(t, check.expectedFile, selected)
		require.Equal(t, check.expectedError, err)
	}
}

func newTestUpdateable() *testUpdateable {
	return &testUpdateable{
		updateWaiter: advsync.NewUntil(),
	}
}

type testUpdateable struct {
	data         []byte
	updateWaiter advsync.Until
}

func (u *testUpdateable) Update(data []byte) error {
	u.data = data
	if u.updateWaiter != nil {
		u.updateWaiter.Fulfill()
	}
	return nil
}

func (u *testUpdateable) awaitUpdate() {
	u.updateWaiter.Wait()
	u.updateWaiter.Prolong()
}

func (u *testUpdateable) assertNotUpdated() {
	select {
	case <-u.updateWaiter.Done():
		panic("updateable got updated despite expectations")
	default:
	}
}

func advanceTime() {
	time.Sleep(time.Millisecond)
}

func TestFileWatcher(t *testing.T) {
	updateable := newTestUpdateable()
	updateable2 := newTestUpdateable()
	selector := NewLinearFileSelector("/a", "/b")
	selector2 := NewLinearFileSelector("/c")
	// logger := log3.NewLoggerStub()
	logger, err := log3.NewLogger(log3.WithCritHandler(nil))
	require.NoError(t, err)

	theTime := time.Now()
	a := fs.NewVirtualFile([]byte("a"), fs.NewVirtualFileInfo("/a", theTime))
	b := fs.NewVirtualFile([]byte("b"), fs.NewVirtualFileInfo("/b", theTime))
	c := fs.NewVirtualFile([]byte("c"), fs.NewVirtualFileInfo("/c", theTime))
	a2 := fs.NewVirtualFile([]byte("a2"), fs.NewVirtualFileInfo("/a", theTime))

	vfs, err := fs.NewVirtualFileSystem()
	require.NoError(t, err)

	fileWatcher, err := NewFileWatcher(vfs, logger, nil, nil)
	require.NoError(t, err)
	go fileWatcher.Serve()

	err = fileWatcher.Add(NewConfig("test", updateable, selector))
	require.NoError(t, err)
	err = fileWatcher.Add(NewConfig("test2", updateable2, selector2))
	require.NoError(t, err)

	advanceTime()
	updateable.assertNotUpdated()

	err = vfs.AddFile(a)
	require.NoError(t, err)
	err = vfs.AddFile(c)
	require.NoError(t, err)

	updateable.awaitUpdate()
	updateable2.awaitUpdate()

	assert.Equal(t, []byte("a"), updateable.data)
	assert.Equal(t, []byte("c"), updateable2.data)

	err = vfs.AddFile(b)
	require.NoError(t, err)

	advanceTime()
	updateable.awaitUpdate()
	updateable2.assertNotUpdated()

	assert.Equal(t, []byte("b"), updateable.data)

	vfs.DeleteFile("/a")

	advanceTime()
	updateable.assertNotUpdated()
	updateable2.assertNotUpdated()

	err = vfs.AddFile(a2)
	require.NoError(t, err)
	advanceTime()
	updateable.assertNotUpdated()
	updateable2.assertNotUpdated()

	vfs.DeleteFile("/b")
	advanceTime()
	updateable.awaitUpdate()
	updateable2.assertNotUpdated()
	assert.Equal(t, []byte("a2"), updateable.data)
	assert.Equal(t, []byte("c"), updateable2.data)

	err = fileWatcher.Close()
	require.NoError(t, err)
}
