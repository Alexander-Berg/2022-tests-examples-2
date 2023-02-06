package mcutils

import (
	"testing"
	"time"

	"github.com/stretchr/testify/require"

	"a.yandex-team.ru/noc/macros/macrospb"
)

func TestExtraElements(t *testing.T) {
	base := make([]string, 0)
	sample := make([]string, 0)
	res := ExtraElements(base, sample)
	require.Nil(t, res)

	base = nil
	sample = nil
	res = ExtraElements(base, sample)
	require.Nil(t, res)

	base = nil
	sample = []string{"a", "b"}
	res = ExtraElements(base, sample)
	require.Equal(t, []string{"a", "b"}, res)

	base = []string{"a", "b"}
	sample = nil
	res = ExtraElements(base, sample)
	require.Nil(t, res)

	base = []string{"a", "b"}
	sample = []string{"c", "a"}
	res = ExtraElements(base, sample)
	require.Equal(t, []string{"c"}, res)
}

func TestMakeArrayChanges(t *testing.T) {
	oldArr := make([]string, 0)
	newArr := make([]string, 0)
	res := MakeArrayChanges(oldArr, newArr)
	require.Nil(t, res)

	oldArr = nil
	newArr = nil
	res = MakeArrayChanges(oldArr, newArr)
	require.Nil(t, res)

	oldArr = nil
	newArr = []string{"a", "b"}
	res = MakeArrayChanges(oldArr, newArr)
	require.NotNil(t, res)
	require.Equal(t, []string{"a", "b"}, res.Added)
	require.Nil(t, res.Removed)

	oldArr = []string{"a", "b"}
	newArr = nil
	res = MakeArrayChanges(oldArr, newArr)
	require.NotNil(t, res)
	require.Nil(t, res.Added)
	require.Equal(t, []string{"a", "b"}, res.Removed)

	oldArr = []string{"a", "b"}
	newArr = []string{"a", "b"}
	res = MakeArrayChanges(oldArr, newArr)
	require.Nil(t, res)

	oldArr = []string{"a", "b", "k"}
	newArr = []string{"c", "a", "s"}
	res = MakeArrayChanges(oldArr, newArr)
	require.NotNil(t, res)
	require.Equal(t, []string{"c", "s"}, res.Added)
	require.Equal(t, []string{"b", "k"}, res.Removed)
}

func TestAppendArrayChanges(t *testing.T) {
	baseLog := &macrospb.ArrayChange{
		Added:   []string{"a", "b", "c"},
		Removed: []string{"d", "e", "f"},
	}
	newLog := &macrospb.ArrayChange{
		Added:   []string{"e", "g", "k"},
		Removed: []string{"a", "x", "y", "c", "z"},
	}
	resLog := AppendArrayChanges(baseLog, newLog)
	require.NotNil(t, resLog)
	require.ElementsMatch(t, []string{"b", "g", "k"}, resLog.Added)
	require.ElementsMatch(t, []string{"d", "f", "x", "y", "z"}, resLog.Removed)

	baseLog = &macrospb.ArrayChange{
		Added:   []string{},
		Removed: []string{"e"},
	}
	newLog = &macrospb.ArrayChange{
		Added:   []string{"e", "g", "k"},
		Removed: []string{},
	}
	resLog = AppendArrayChanges(baseLog, newLog)
	require.NotNil(t, resLog)
	require.ElementsMatch(t, []string{"g", "k"}, resLog.Added)
	require.Equal(t, []string{}, resLog.Removed)

	baseLog = &macrospb.ArrayChange{
		Added:   []string{},
		Removed: []string{"e"},
	}
	newLog = &macrospb.ArrayChange{
		Added:   []string{"e", "g", "k"},
		Removed: nil,
	}
	resLog = AppendArrayChanges(baseLog, newLog)
	require.NotNil(t, resLog)
	require.ElementsMatch(t, []string{"g", "k"}, resLog.Added)
	require.Equal(t, []string{}, resLog.Removed)

	baseLog = &macrospb.ArrayChange{
		Added:   nil,
		Removed: nil,
	}
	newLog = &macrospb.ArrayChange{
		Added:   nil,
		Removed: nil,
	}
	resLog = AppendArrayChanges(baseLog, newLog)
	require.NotNil(t, resLog)
	require.Nil(t, resLog.Added)
	require.Nil(t, resLog.Removed)

	baseLog = &macrospb.ArrayChange{
		Added:   nil,
		Removed: nil,
	}
	newLog = &macrospb.ArrayChange{
		Added:   []string{"e", "g", "k"},
		Removed: []string{},
	}
	resLog = AppendArrayChanges(baseLog, newLog)
	require.NotNil(t, resLog)
	require.ElementsMatch(t, []string{"e", "g", "k"}, resLog.Added)
	require.Equal(t, []string{}, resLog.Removed)

	baseLog = &macrospb.ArrayChange{
		Added:   nil,
		Removed: nil,
	}
	newLog = &macrospb.ArrayChange{
		Added:   []string{"e", "g", "k"},
		Removed: nil,
	}
	resLog = AppendArrayChanges(baseLog, newLog)
	require.NotNil(t, resLog)
	require.ElementsMatch(t, []string{"e", "g", "k"}, resLog.Added)
	require.Nil(t, resLog.Removed)

	baseLog = &macrospb.ArrayChange{
		Added:   nil,
		Removed: []string{"k", "x", "y"},
	}
	newLog = &macrospb.ArrayChange{
		Added:   []string{"e", "g", "k"},
		Removed: nil,
	}
	resLog = AppendArrayChanges(baseLog, newLog)
	require.NotNil(t, resLog)
	require.ElementsMatch(t, []string{"e", "g"}, resLog.Added)
	require.ElementsMatch(t, []string{"x", "y"}, resLog.Removed)

	baseLog = &macrospb.ArrayChange{
		Added:   []string{"a", "b"},
		Removed: []string{"c", "d"},
	}
	newLog = &macrospb.ArrayChange{
		Added:   nil,
		Removed: nil,
	}
	resLog = AppendArrayChanges(baseLog, newLog)
	require.NotNil(t, resLog)
	require.ElementsMatch(t, []string{"a", "b"}, resLog.Added)
	require.ElementsMatch(t, []string{"c", "d"}, resLog.Removed)

	baseLog = &macrospb.ArrayChange{
		Added:   []string{"a", "b"},
		Removed: []string{"c", "d"},
	}
	newLog = &macrospb.ArrayChange{
		Added:   []string{},
		Removed: []string{},
	}
	resLog = AppendArrayChanges(baseLog, newLog)
	require.NotNil(t, resLog)
	require.ElementsMatch(t, []string{"a", "b"}, resLog.Added)
	require.ElementsMatch(t, []string{"c", "d"}, resLog.Removed)

	baseLog = nil
	newLog = &macrospb.ArrayChange{
		Added:   []string{"e", "g", "k"},
		Removed: []string{"a", "x", "y", "c", "z"},
	}
	resLog = AppendArrayChanges(baseLog, newLog)
	require.NotNil(t, resLog)
	require.ElementsMatch(t, []string{"e", "g", "k"}, resLog.Added)
	require.ElementsMatch(t, []string{"a", "x", "y", "c", "z"}, resLog.Removed)

	baseLog = &macrospb.ArrayChange{
		Added:   []string{"e", "g", "k"},
		Removed: []string{"a", "x", "y", "c", "z"},
	}
	newLog = nil
	resLog = AppendArrayChanges(baseLog, newLog)
	require.NotNil(t, resLog)
	require.ElementsMatch(t, []string{"e", "g", "k"}, resLog.Added)
	require.ElementsMatch(t, []string{"a", "x", "y", "c", "z"}, resLog.Removed)

	baseLog = nil
	newLog = nil
	resLog = AppendArrayChanges(baseLog, newLog)
	require.Nil(t, resLog)
}

func TestAppendLog(t *testing.T) {
	baseName := "_A_"
	newName := "_B_"

	baseTicket := "NOCDEV-239"
	newTicket := "NOCDEV-136"

	newComment := "Some new comment"

	baseAdmins := macrospb.ArrayChange{
		Added:   []string{"person1 added", "person2 added", "department3 added"},
		Removed: []string{"person1 removed", "person2 removed", "department3 removed"},
	}
	newAdmins := macrospb.ArrayChange{
		Added:   []string{"person1 removed", "person8 added", "department9 added"},
		Removed: []string{"person2561 added", "person2 added", "department3 added"},
	}

	baseApprovers := macrospb.ArrayChange{
		Added:   []string{"person1 added", "department3 added"},
		Removed: []string{"department3 removed"},
	}
	newApprovers := macrospb.ArrayChange{
		Added:   []string{"department3 removed", "department9 added"},
		Removed: nil,
	}

	newOwnerService := "new owner service"

	baseChildren := macrospb.ArrayChange{
		Added:   []string{"child1 added", "child2 added", "child3 added"},
		Removed: nil,
	}
	newChildren := macrospb.ArrayChange{
		Added:   nil,
		Removed: []string{"child1 removed", "child2 removed", "child3 added"},
	}

	baseProjectIDs := macrospb.ArrayChange{
		Added:   nil,
		Removed: []string{"projectID1 removed", "projectID2 removed", "projectID3 removed"},
	}
	newProjectIDs := macrospb.ArrayChange{
		Added:   nil,
		Removed: []string{"projectID4 removed", "projectID5 removed", "projectID6 removed"},
	}

	baseSecured := false
	newSecured := true

	baseLog := &macrospb.GoMacroLog{
		MacroID:      239,
		Username:     "somebody",
		Timestamp:    time.Now(),
		Action:       macrospb.ActionEdited,
		Aggregated:   false,
		Name:         &baseName,
		Ticket:       &baseTicket,
		Comment:      nil,
		Admins:       &baseAdmins,
		Approvers:    &baseApprovers,
		OwnerService: nil,
		Children:     &baseChildren,
		ProjectIDs:   &baseProjectIDs,
		Secured:      &baseSecured,
	}
	newLog := &macrospb.GoMacroLog{
		MacroID:      239,
		Username:     "somebody",
		Timestamp:    time.Now().Add(10 * time.Hour),
		Action:       macrospb.ActionEdited,
		Aggregated:   false,
		Name:         &newName,
		Ticket:       &newTicket,
		Comment:      &newComment,
		Admins:       &newAdmins,
		Approvers:    &newApprovers,
		OwnerService: &newOwnerService,
		Children:     &newChildren,
		ProjectIDs:   &newProjectIDs,
		Secured:      &newSecured,
	}

	resLog, err := AppendLog(baseLog, newLog)
	require.NoError(t, err)
	require.Equal(t, uint32(239), resLog.MacroID)
	require.Empty(t, resLog.Username)
	require.Equal(t, macrospb.ActionEdited, resLog.Action)
	require.True(t, resLog.Aggregated)
	require.NotNil(t, resLog.Name)
	require.Equal(t, newName, *resLog.Name)
	require.NotNil(t, resLog.Ticket)
	require.Equal(t, newTicket, *resLog.Ticket)
	require.NotNil(t, resLog.Comment)
	require.Equal(t, newComment, *resLog.Comment)
	require.NotNil(t, resLog.Admins)
	require.ElementsMatch(t, []string{"person1 added", "person8 added", "department9 added"}, resLog.Admins.Added)
	require.ElementsMatch(t, []string{"person2 removed", "department3 removed", "person2561 added"}, resLog.Admins.Removed)
	require.NotNil(t, resLog.Approvers)
	require.ElementsMatch(t, []string{"person1 added", "department3 added", "department9 added"}, resLog.Approvers.Added)
	require.Equal(t, []string{}, resLog.Approvers.Removed)
	require.NotNil(t, resLog.OwnerService)
	require.Equal(t, newOwnerService, *resLog.OwnerService)
	require.NotNil(t, resLog.Children)
	require.ElementsMatch(t, []string{"child1 added", "child2 added"}, resLog.Children.Added)
	require.ElementsMatch(t, []string{"child1 removed", "child2 removed"}, resLog.Children.Removed)
	require.NotNil(t, resLog.ProjectIDs)
	require.Nil(t, resLog.ProjectIDs.Added)
	require.ElementsMatch(t, []string{
		"projectID1 removed", "projectID2 removed", "projectID3 removed",
		"projectID4 removed", "projectID5 removed", "projectID6 removed",
	}, resLog.ProjectIDs.Removed)
	require.NotNil(t, resLog.Secured)
	require.Equal(t, newSecured, *resLog.Secured)

	resLog, err = AppendLog(nil, newLog)
	require.NoError(t, err)
	require.Equal(t, newLog.MacroID, resLog.MacroID)
	require.Equal(t, newLog.Username, resLog.Username)
	require.Equal(t, newLog.Action, resLog.Action)
	require.Equal(t, newLog.Aggregated, resLog.Aggregated)
	require.NotNil(t, resLog.Name)
	require.Equal(t, newName, *resLog.Name)
	require.NotNil(t, resLog.Ticket)
	require.Equal(t, newTicket, *resLog.Ticket)
	require.NotNil(t, resLog.Comment)
	require.Equal(t, newComment, *resLog.Comment)
	require.NotNil(t, resLog.Admins)
	require.ElementsMatch(t, []string{"person1 removed", "person8 added", "department9 added"}, resLog.Admins.Added)
	require.ElementsMatch(t, []string{"person2561 added", "person2 added", "department3 added"}, resLog.Admins.Removed)
	require.NotNil(t, resLog.Approvers)
	require.ElementsMatch(t, []string{"department3 removed", "department9 added"}, resLog.Approvers.Added)
	require.Nil(t, resLog.Approvers.Removed)
	require.NotNil(t, resLog.OwnerService)
	require.Equal(t, newOwnerService, *resLog.OwnerService)
	require.NotNil(t, resLog.Children)
	require.Nil(t, resLog.Children.Added)
	require.ElementsMatch(t, []string{"child1 removed", "child2 removed", "child3 added"}, resLog.Children.Removed)
	require.NotNil(t, resLog.ProjectIDs)
	require.Nil(t, resLog.ProjectIDs.Added)
	require.ElementsMatch(t, []string{"projectID4 removed", "projectID5 removed", "projectID6 removed"}, resLog.ProjectIDs.Removed)
	require.NotNil(t, resLog.Secured)
	require.Equal(t, newSecured, *resLog.Secured)

	resLog, err = AppendLog(baseLog, nil)
	require.NoError(t, err)
	require.Equal(t, baseLog.MacroID, resLog.MacroID)
	require.Equal(t, baseLog.Username, resLog.Username)
	require.Equal(t, baseLog.Action, resLog.Action)
	require.Equal(t, baseLog.Aggregated, resLog.Aggregated)
	require.NotNil(t, resLog.Name)
	require.Equal(t, baseName, *resLog.Name)
	require.NotNil(t, resLog.Ticket)
	require.Equal(t, baseTicket, *resLog.Ticket)
	require.Nil(t, resLog.Comment)
	require.NotNil(t, resLog.Admins)
	require.ElementsMatch(t, []string{"person1 added", "person2 added", "department3 added"}, resLog.Admins.Added)
	require.ElementsMatch(t, []string{"person1 removed", "person2 removed", "department3 removed"}, resLog.Admins.Removed)
	require.NotNil(t, resLog.Approvers)
	require.ElementsMatch(t, []string{"person1 added", "department3 added"}, resLog.Approvers.Added)
	require.ElementsMatch(t, []string{"department3 removed"}, resLog.Approvers.Removed)
	require.Nil(t, resLog.OwnerService)
	require.NotNil(t, resLog.Children)
	require.ElementsMatch(t, []string{"child1 added", "child2 added", "child3 added"}, resLog.Children.Added)
	require.Nil(t, resLog.Children.Removed)
	require.NotNil(t, resLog.ProjectIDs)
	require.Nil(t, resLog.ProjectIDs.Added)
	require.ElementsMatch(t, []string{"projectID1 removed", "projectID2 removed", "projectID3 removed"}, resLog.ProjectIDs.Removed)
	require.NotNil(t, resLog.Secured)
	require.Equal(t, baseSecured, *resLog.Secured)

	baseLog.Action = macrospb.ActionCreated
	resLog, err = AppendLog(baseLog, newLog)
	require.Nil(t, resLog)
	require.EqualError(t, err, "failed to append logs: only edit logs may be appended")

	baseLog.Action = macrospb.ActionEdited
	newLog.Action = macrospb.ActionDeleted
	resLog, err = AppendLog(baseLog, newLog)
	require.Nil(t, resLog)
	require.EqualError(t, err, "failed to append logs: only edit logs may be appended")

	newLog.Action = macrospb.ActionEdited
	baseLog.MacroID = 2239
	resLog, err = AppendLog(baseLog, newLog)
	require.Nil(t, resLog)
	require.EqualError(t, err, "failed to append logs: only logs of the same macro may be appended")
}

func TestMergeLogs(t *testing.T) {
	baseName := "_A_"
	newName := "_B_"
	thirdName := "_A_"

	baseTicket := "NOCDEV-239"
	thirdTicket := "NOCDEV-1112"

	newComment := "Some new comment"

	baseAdmins := macrospb.ArrayChange{
		Added:   []string{"person1 added", "person2 added", "department3 added"},
		Removed: []string{"person1 removed", "person2 removed", "department3 removed"},
	}
	newAdmins := macrospb.ArrayChange{
		Added:   []string{"person1 removed", "person8 added", "department9 added"},
		Removed: []string{"person2561 added", "person2 added", "department3 added"},
	}
	thirdAdmins := macrospb.ArrayChange{
		Added:   []string{"person2561 added", "person2 removed", "department3 removed"},
		Removed: []string{"person1 added", "person8 added", "department9 added"},
	}

	baseApprovers := macrospb.ArrayChange{
		Added:   nil,
		Removed: []string{"person1 removed", "person2 removed", "department3 removed"},
	}
	thirdApprovers := macrospb.ArrayChange{
		Added:   []string{"person1 removed", "person8 added", "department9 added"},
		Removed: nil,
	}

	newOwnerService := "new owner service"

	baseChildren := macrospb.ArrayChange{
		Added:   []string{"child1 added", "child2 added", "child3 added"},
		Removed: nil,
	}
	newChildren := macrospb.ArrayChange{
		Added:   nil,
		Removed: []string{"child1 removed", "child2 removed", "child3 added"},
	}
	thirdChildren := macrospb.ArrayChange{
		Added:   nil,
		Removed: []string{"child1 added", "child2 added"},
	}

	baseProjectIDs := macrospb.ArrayChange{
		Added:   nil,
		Removed: []string{"projectID1 removed", "projectID2 removed", "projectID3 removed"},
	}
	newProjectIDs := macrospb.ArrayChange{
		Added:   nil,
		Removed: []string{"projectID4 removed", "projectID5 removed", "projectID6 removed"},
	}

	baseSecured := false
	newSecured := true

	logs := []*macrospb.GoMacroLog{
		{
			MacroID:    239,
			Username:   "first person",
			Timestamp:  time.Now(),
			Action:     macrospb.ActionEdited,
			Aggregated: false,
			Name:       &baseName,
			Ticket:     &baseTicket,
			Admins:     &baseAdmins,
			Approvers:  &baseApprovers,
			Children:   &baseChildren,
			ProjectIDs: &baseProjectIDs,
			Secured:    &baseSecured,
		},
		{
			MacroID:      239,
			Username:     "second person",
			Timestamp:    time.Now(),
			Action:       macrospb.ActionEdited,
			Aggregated:   false,
			Name:         &newName,
			Comment:      &newComment,
			Admins:       &newAdmins,
			Approvers:    nil,
			OwnerService: &newOwnerService,
			Children:     &newChildren,
			ProjectIDs:   &newProjectIDs,
			Secured:      &newSecured,
		},
		{
			MacroID:    239,
			Username:   "third person",
			Timestamp:  time.Now(),
			Action:     macrospb.ActionEdited,
			Aggregated: false,
			Name:       &thirdName,
			Ticket:     &thirdTicket,
			Admins:     &thirdAdmins,
			Approvers:  &thirdApprovers,
			Children:   &thirdChildren,
		},
	}

	resLog, err := MergeLogs(logs)
	require.NoError(t, err)
	require.NotNil(t, resLog)
	require.NoError(t, err)
	require.Equal(t, uint32(239), resLog.MacroID)
	require.Empty(t, resLog.Username)
	require.Equal(t, macrospb.ActionEdited, resLog.Action)
	require.True(t, resLog.Aggregated)
	require.NotNil(t, resLog.Name)
	require.Equal(t, thirdName, *resLog.Name)
	require.NotNil(t, resLog.Ticket)
	require.Equal(t, thirdTicket, *resLog.Ticket)
	require.NotNil(t, resLog.Comment)
	require.Equal(t, newComment, *resLog.Comment)
	require.NotNil(t, resLog.Admins)
	require.Equal(t, []string{}, resLog.Admins.Added)
	require.Equal(t, []string{}, resLog.Admins.Removed)
	require.NotNil(t, resLog.Approvers)
	require.ElementsMatch(t, []string{"person8 added", "department9 added"}, resLog.Approvers.Added)
	require.ElementsMatch(t, []string{"person2 removed", "department3 removed"}, resLog.Approvers.Removed)
	require.NotNil(t, resLog.OwnerService)
	require.Equal(t, newOwnerService, *resLog.OwnerService)
	require.NotNil(t, resLog.Children)
	require.Equal(t, []string{}, resLog.Children.Added)
	require.ElementsMatch(t, []string{"child1 removed", "child2 removed"}, resLog.Children.Removed)
	require.NotNil(t, resLog.ProjectIDs)
	require.Nil(t, resLog.ProjectIDs.Added)
	require.ElementsMatch(t, []string{
		"projectID1 removed", "projectID2 removed", "projectID3 removed",
		"projectID4 removed", "projectID5 removed", "projectID6 removed",
	}, resLog.ProjectIDs.Removed)
	require.NotNil(t, resLog.Secured)
	require.Equal(t, newSecured, *resLog.Secured)

	logs[0].MacroID = 2239
	resLog, err = MergeLogs(logs)
	require.Nil(t, resLog)
	require.EqualError(t, err, "failed to append logs: only logs of the same macro may be appended")
}
