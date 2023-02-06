package commands

import (
	"github.com/spf13/cobra"
)

var testCmd = &cobra.Command{
	Use:   "test",
	Short: "test for any known vulnerabilities",
}

func init() {
	rootCmd.AddCommand(testCmd)
}
