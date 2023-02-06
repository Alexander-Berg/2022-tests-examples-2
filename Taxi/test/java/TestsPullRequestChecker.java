import org.junit.Test;
import ru.yandex.eats.bitbucket.check.pull.requests.PullRequestChecker;
import ru.yandex.eats.bitbucket.check.pull.requests.Verdict;

import static org.junit.Assert.*;


public class TestsPullRequestChecker {
    @Test
    public void testTitleCheck() {
        assertTrue(PullRequestChecker.isTitleCorrect("feat mysql support: new field value"));
        assertFalse(PullRequestChecker.isTitleCorrect("feat: new field value"));
        assertTrue(PullRequestChecker.isTitleCorrect("bug mysql: new field value"));
        assertFalse(PullRequestChecker.isTitleCorrect("feature mysql support: new field value"));
        assertTrue(PullRequestChecker.isTitleCorrect("Revert \"feat mysql support: new field value\""));
    }

    @Test
    public void testDescriptionCheck() {
        assertTrue(PullRequestChecker.isDescriptionCorrect("Relates: EDADEV-666"));
        assertTrue(PullRequestChecker.isDescriptionCorrect("Relates: EDADEV-666, EDADEV-42"));
        assertTrue(PullRequestChecker.isDescriptionCorrect("Relates: https://st.yandex-team.ru/EDADEV-666"));
        assertTrue(PullRequestChecker.isDescriptionCorrect(
                "Relates: https://st.yandex-team.ru/EDADEV-666, https://st.yandex-team.ru/EDADEV-42"
        ));
        assertFalse(PullRequestChecker.isDescriptionCorrect("Relates: EDADEV-666, \nEDADEV-42"));
        assertFalse(PullRequestChecker.isDescriptionCorrect(""));
    }

    @Test
    public void testRefBranch() {
        assertTrue(PullRequestChecker.isRefDevelop("refs/heads/develop"));
        assertFalse(PullRequestChecker.isRefDevelop("refs/heads/master"));
    }

    @Test
    public void testMergeCommitMessageCheck() {
        assert PullRequestChecker.checkMergeCommitMessage(
                ""
        ) == Verdict.EMPTY_MESSAGE;

        assert PullRequestChecker.checkMergeCommitMessage(
                "feat vendor: test vendor"
        ) == Verdict.WRONG_LENGTH;

        assert PullRequestChecker.checkMergeCommitMessage(
                "feat vendor: test vendor\n" +
                        "\n"
        ) == Verdict.WRONG_LENGTH;

        assert PullRequestChecker.checkMergeCommitMessage(
                "feat vendor: test vendor\n" +
                        "\n" +
                        "Some test PR"
        ) == Verdict.RELATES_LINE_NEEDED;

        assert PullRequestChecker.checkMergeCommitMessage(
                "feat vendor: test vendor\n" +
                        "\n" +
                        "some test PR\n" +
                        "Relates: EDADEV-666"
        ) == Verdict.SUCCESS;

        assert PullRequestChecker.checkMergeCommitMessage(
                "feat vendor: test vendor\n" +
                        "\n" +
                        "Some test PR.\n" +
                        "Contains some test changes.\n" +
                        "Relates: EDADEV-666"
        ) == Verdict.SUCCESS;
    }
}
