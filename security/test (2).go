package commands

import (
	"errors"
	"fmt"

	"github.com/spf13/cobra"

	"a.yandex-team.ru/security/libs/go/simplelog"
	"a.yandex-team.ru/security/yadi/yadi-arc/pkg/manager/yamake"
)

var testOpts = struct {
	BatchSize int
}{
	BatchSize: 20,
}

var testCmd = &cobra.Command{
	Use:   "test [flags] target",
	Short: "Test Arcadia projects for any known vulnerabilities",
	RunE: func(_ *cobra.Command, args []string) error {
		var target string
		switch len(args) {
		case 0:
			target = "."
		case 1:
			target = args[0]
		default:
			return errors.New("please provide exactly one target")
		}

		simplelog.Info("search targets")
		targets, err := yamake.FindTargets(rootOpts.ArcadiaRoot, target)
		if err != nil {
			return err
		}

		if len(targets) == 0 {
			return fmt.Errorf("no targets in path: %s", target)
		}

		simplelog.Info(fmt.Sprintf("found %d targets", len(targets)))
		pm, err := yamake.NewManager(targets, yamake.ManagerOpts{
			ArcadiaPath: rootOpts.ArcadiaRoot,
			BatchSize:   testOpts.BatchSize,
		})
		if err != nil {
			return err
		}

		if rootOpts.ListOnly {
			return doList(pm)
		}
		return doAnalyzeProject(pm)
	},
}

func init() {
	flags := testCmd.PersistentFlags()
	flags.IntVar(&testOpts.BatchSize, "batch-size", testOpts.BatchSize, "batch size for 'ya make'")
}
