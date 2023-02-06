package commands

import (
	"context"
	"errors"
	"fmt"
	"os"

	"github.com/spf13/cobra"

	"a.yandex-team.ru/security/yadi/yadi/internal/cli"
)

var testCmd = &cobra.Command{
	Use:   "test [flags] [/path/to/dependencies/file|...]",
	Short: "Test for any known vulnerabilities",
	Long:  "Identifies project dependencies and checks if there are any known vulnerabilities.",
	RunE:  runTestCmd,
}

func init() {
	RootCmd.AddCommand(testCmd)
}

func runTestCmd(cmd *cobra.Command, args []string) error {
	var targets []string
	if len(opts.Targets) > 0 && len(args) == 0 {
		targets = cli.ValidateTargets(opts.Targets, true)
	} else if opts.Recursive {
		dirs := args
		if len(dirs) == 0 {
			dirs = []string{"."}
		}

		for _, dir := range dirs {
			targets = append(targets, cli.FindTargets(dir)...)
		}
	} else {
		candidates := args
		explicit := true
		if len(candidates) == 0 {
			candidates = projectFiles
			explicit = false
		}

		targets = cli.ValidateTargets(candidates, explicit)
	}

	if len(targets) == 0 {
		return errors.New("can't find any targets to analyze")
	}

	outer, err := cli.IssuesFormatter(opts.Format)
	if err != nil {
		return err
	}
	defer func() { _ = outer.Close() }()

	ctx := context.Background()
	haveIssues, err := cli.AnalyzeTargets(ctx, cli.DepsOptions{
		FuzzySearch: true,
		ResolveMode: cli.FetcherFlags(opts.Local, opts.Remote),
		Targets:     targets,
		IssueOutput: outer,
	})
	if err != nil {
		return err
	}

	if haveIssues {
		os.Exit(opts.ExitStatus)
	}

	if opts.Format != "json" {
		// TODO(buglloc): fix this bullshit!
		fmt.Println("No issues found.")
	}
	return nil
}
