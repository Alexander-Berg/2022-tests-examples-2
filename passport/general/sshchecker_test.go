package sshchecker

import (
	"testing"

	"github.com/stretchr/testify/require"
)

func TestParseResponse(t *testing.T) {
	response := `{"links": {}, "page": 1, "limit": 50, "result": [{"keys": [{"key": "ssh-rsa AAAAB3NzaC1yc2EAAAADAQABAAABAQDU5KSk6dwxaxGPNVGODo2d2LijMwWP201oNor1oau1U+gB1aVFaJpC5WGv7SVOqnqMpomW58y7wUrGXVlYInk9fbXXYFWqiWX6uwTQAL4Se5FdYtGCaT6lHq0Zhr24BzwoPyis5hweva+xadbZYGRbYocNMLpDXpzTYdvPB0f6tJcvjE3xwxdJB5oSpZqzJOnlR6SeMFhtuDDtH49brNNYrYRDXzf4MDX+jZWLP/2w1uxNujd/lVzXao/pYm+JxKAaqfekvu8FhIP5LpxzRILpDwfuyd5JpDa4Jbd3+aWDg7iXHqxjalBE8Evrvium7zSCCJ6Fk1XTErrS1aSyVOqh"}, {"key": "ssh-rsa AAAAB3NzaC1yc2EAAAADAQABAAABAQCc5Qxxpx4v7LVkSw5rZQY2aAAMLC7QY4+B09G7Lt74NlgV+dx98AddkcQbm+QaUPgpVQCeLCQJNCCJKzfBuIRl3+YlzyXeF8Vc4KZdaW3nYHNSdIvTCOSomLOAmCM82bBdx06P2VhJJiPetJaklQmfI2wOJlxrguvo7voObrNfYKDm3GWj/1r4+igIsOGW119/7uETRxCo64/66kSz0U48Ik8PQ2p27IbjIPCLRKSdl1ZMNMI7Kx9eAAxXFZfVth/xzSwJQPMGs2FLNFmATTPSAVvQI8+xqVAStPwX3CyyGdDLHMobbVo1fToEsmku7wDv57aDZDDJX4ZGKFwPexo3"}], "login": "dyor"}, {"keys": [{"key": "ssh-rsa AAAAB3NzaC1yc2EAAAADAQABAAABAQDiaMj8sW6KLfOGMbnxZ9RX5LI6+yXWNsHd+DuJKAdGPT526HyfUKoFYV4a/SWTXqq0sPOGZvgphFUZ0VhteZ2dOKNPPrDYumtB/DfBMbT0Q32vCAfKc6ggPkGOdtNzZRZg92SfAzMLvlDguBfqgN+z/Jraa7QpqzpaYd2aoG7GWAlT+ViK3VrbeL5R9Jzts5qP92baq+gZ1MBtmjCKXON/tG9NfJXPEImUduHE4e0uaLF0ZWQXPr6iLR4WC1OR+QyYFnhVmmFAiG1Z5T8o6WGb210gE7oaDhUeZAD3CZseT6vyZSyvBpeREI89kBOV44KlO1ExhIBFblWk07Jlvl9j cerevra@yandex-team.ru"}], "login": "cerevra"}], "total": 2, "pages": 1}`

	keys, err := parseResponse([]byte(response))
	require.NoError(t, err)
	require.Len(t, keys, 2)
	require.Contains(t, keys, "dyor")
	require.Len(t, keys["dyor"], 2)
	require.Contains(t, keys, "cerevra")
	require.Len(t, keys["cerevra"], 1)

	_, err = parseResponse([]byte(`{}`))
	require.Error(t, err)
	require.Equal(t, "no one ssh key in memory", err.Error())
}

func TestGetHeaderFields(t *testing.T) {
	_, err := getHeaderFields("")
	require.Error(t, err)
	require.Equal(t, "missing header", err.Error())

	_, err = getHeaderFields("aa aa")
	require.Error(t, err)
	require.Equal(t, "format: <login> <timestamp> <base64(sign)>", err.Error())

	fields, err := getHeaderFields("aa bb cc")
	require.NoError(t, err)
	require.Len(t, fields, 3)
	require.Equal(t, "aa", fields[0])
	require.Equal(t, "bb", fields[1])
	require.Equal(t, "cc", fields[2])
}
