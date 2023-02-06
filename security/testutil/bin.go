package testutil

import (
	"bytes"
	"encoding/json"
	"fmt"
	"os"
	"os/exec"
)

type DownloadedModule struct {
	Path     string
	Version  string
	Info     string
	GoMod    string
	Zip      string
	Dir      string
	Sum      string
	GoModSum string
}

func GoDownload(pkg string, env []string) (*DownloadedModule, error) {
	args := []string{"mod", "download", "-json", pkg}
	stdout, err := GoExec(args, env)
	if err != nil {
		return nil, err
	}

	var out DownloadedModule
	if err := json.Unmarshal(stdout, &out); err != nil {
		return nil, fmt.Errorf("reading json: %v", err)
	}

	return &out, nil
}

func GoGet(pkg string, env []string) ([]byte, error) {
	args := []string{"get", "-d", pkg}
	return GoExec(args, env)
}

func GoExec(args []string, env []string) ([]byte, error) {
	cmd := exec.Command("go", args...)
	var stdout, stderr bytes.Buffer
	cmd.Env = append(os.Environ(), env...)
	cmd.Stdout = &stdout
	cmd.Stderr = &stderr
	if err := cmd.Run(); err != nil {
		var goErr struct {
			Error string
		}

		if jErr := json.Unmarshal(stdout.Bytes(), &goErr); jErr == nil && goErr.Error != "" {
			return nil, fmt.Errorf("%v: %s", err, goErr.Error)
		}

		return nil, fmt.Errorf("%v\n%s", err, stderr.String())
	}

	return stdout.Bytes(), nil
}
