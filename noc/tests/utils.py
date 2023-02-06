import commitreload
import rollback
import branchstash
import ifreload


def run_commit_reload(noreload: bool = False, *filepaths):
    commitreload.commit_reload(filepaths, not noreload)


def run_rollback(commit: str):
    rollback.rollback(commit)


def run_branchstash():
    branchstash.stash_to_branch()


def run_ifreload():
    ifreload.main()
