package genstash

import (
	"errors"
	"strconv"
	"strings"
	"testing"

	"github.com/stretchr/testify/require"

	"a.yandex-team.ru/noc/alexandria/stash/genstash"
)

func TestStashInit(t *testing.T) {
	stash, err := genstash.InitStash()
	require.NoError(t, err)
	require.NotEmpty(t, stash)
}

func TestStashConsistency(t *testing.T) {
	stash, _ := genstash.InitStash()
	err := MatchersSoftsConsistency(stash)

	require.NoError(t, err)
	require.NotEmpty(t, stash)
}

func TestStashConsistencyExtended(t *testing.T) {
	stash, _ := genstash.InitStash()
	err := MatchersSoftsConsistencyExtended(stash)

	require.NoError(t, err)
	require.NotEmpty(t, stash)
}

func MatchersSoftsConsistency(stash genstash.Stash) error {
	var errs errstrings
	for _, v := range stash.Matchers {
		if _, ok := stash.Softs[*v.SoftID]; !ok {
			errtext := "Matcher and Soft consistency is not full. [Matcher_index : Soft_id]: [" + strconv.Itoa(v.Index) + " : " + *v.SoftID + "]"
			errs.append(errtext)
		}
	}
	return errs.sumError()
}

func MatchersSoftsConsistencyExtended(stash genstash.Stash) error {
	var errs errstrings
	for _, v := range stash.Matchers {
		for _, a := range v.Acceptable {
			if _, ok := stash.Softs[*a]; !ok {
				errtext := "Mentioned Acceptable soft does not exist. [Matcher_index : Soft_id]: [" + strconv.Itoa(v.Index) + " : " + *a + "]"
				errs.append(errtext)
			}
		}
		for _, d := range v.Dangerous {
			if _, ok := stash.Softs[*d]; !ok {
				errtext := "Mentioned Dangerous soft does not exist. [Matcher_index : Soft_id]: [" + strconv.Itoa(v.Index) + " : " + *d + "]"
				errs.append(errtext)
			}
		}
	}
	return errs.sumError()
}

type errstrings []string

func (e *errstrings) sumError() error {
	if len(*e) > 0 {
		return errors.New(strings.Join(*e, "; "))
	}
	return nil
}

func (e *errstrings) append(errtext string) {
	*e = append(*e, errtext)
}
