from _pytest import runner
from py.log import Producer

from taxi_xdist import report
from taxi_xdist import workermanage


class IntegrationTestsScheduling:
    def __init__(self, config, log=None):
        self.numnodes = len(workermanage.parse_spec_config(config))
        self.node2collection = {}
        self.node2pending = {}
        self.pending = []
        self.collection = None
        if log is None:
            self.log = Producer('loadsched')
        else:
            self.log = log.loadsched
        self.config = config

    @property
    def nodes(self):
        """A list of all nodes in the scheduler."""
        return list(self.node2pending.keys())

    @property
    def collection_is_completed(self):
        """Boolean indication initial test collection is complete.
        This is a boolean indicating all initial participating nodes
        have finished collection.  The required number of initial
        nodes is defined by ``.numnodes``.
        """
        return len(self.node2collection) >= self.numnodes

    @property
    def tests_finished(self):
        """Return True if all tests have been executed by the nodes."""
        if not self.collection_is_completed:
            return False
        if self.pending:
            return False
        for pending in self.node2pending.values():
            if len(pending) >= 2:
                return False
        return True

    @property
    def has_pending(self):
        """Return True if there are pending test items
        This indicates that collection has finished and nodes are
        still processing test items, so this can be thought of as
        "the scheduler is active".
        """
        if self.pending:
            return True
        for pending in self.node2pending.values():
            if pending:
                return True
        return False

    def add_node(self, node):
        """Add a new node to the scheduler.
        From now on the node will be allocated chunks of tests to
        execute.
        Called by the ``DSession.worker_workerready`` hook when it
        successfully bootstraps a new node.
        """
        assert node not in self.node2pending
        self.node2pending[node] = []

    def add_node_collection(self, node, collection):
        """Add the collected test items from a node
        The collection is stored in the ``.node2collection`` map.
        Called by the ``DSession.worker_collectionfinish`` hook.
        """
        assert node in self.node2pending
        if self.collection_is_completed:
            # A new node has been added later, perhaps an original one died.
            # .schedule() should have
            # been called by now
            assert self.collection
            if collection != self.collection:
                other_node = next(iter(self.node2collection.keys()))
                msg = report.report_collection_diff(
                    self.collection,
                    collection,
                    other_node.gateway.id,
                    node.gateway.id,
                )
                self.log(msg)
                return
        self.node2collection[node] = list(collection)

    def mark_test_complete(self, node, item_index, duration=0):
        """Mark test item as completed by node
        The duration it took to execute the item is used as a hint to
        the scheduler.
        This is called by the ``DSession.worker_testreport`` hook.
        """
        self.node2pending[node].remove(item_index)
        self.schedule()

    def check_schedule(self, node, duration=0):
        """Maybe schedule new items on the node
        If there are any globally pending nodes left then this will
        check if the given node should be given any more tests.  The
        ``duration`` of the last test is optionally used as a
        heuristic to influence how many tests the node is assigned.
        """
        if node.shutting_down:
            return None

        if self.pending:
            node_pending = self.node2pending[node]
            if not node_pending:
                self._send_tests(node, 1)
        return None

    def remove_node(self, node):
        """Remove a node from the scheduler
        This should be called either when the node crashed or at
        shutdown time.  In the former case any pending items assigned
        to the node will be re-scheduled.  Called by the
        ``DSession.worker_workerfinished`` and
        ``DSession.worker_errordown`` hooks.
        Return the item which was being executing while the node
        crashed or None if the node has no more pending items.
        """
        pending = self.node2pending.pop(node)
        if not pending:
            return None

        # The node crashed, reassing pending items
        crashitem = self.collection[pending.pop(0)]
        self.pending.extend(pending)
        self.schedule()
        return crashitem

    def schedule(self):
        """Initiate distribution of the test collection
        Initiate scheduling of the items across the nodes.  If this
        gets called again later it behaves the same as calling
        ``.check_schedule()`` on all nodes so that newly added nodes
        will start to be used.
        This is called by the ``DSession.worker_collectionfinish`` hook
        if ``.collection_is_completed`` is True.
        """
        assert self.collection_is_completed

        if self.collection is None:
            # XXX allow nodes to have different collections
            if not self._check_nodes_have_same_collection():
                self.log('**Different tests collected, aborting run**')
                return

            # Collections are identical, create the index of pending items.
            self.collection = list(self.node2collection.values())[0]
            self.pending[:] = range(len(self.collection))

        if not self.collection:
            return

        for node in self.nodes:
            self.check_schedule(node)

    def _send_tests(self, node, num):
        assert num == 1
        if not self.pending:
            return
        tests_per_node = self.pending[:num]
        if tests_per_node:
            del self.pending[:num]
            self.node2pending[node].extend(tests_per_node)
            node.send_runtest_some(tests_per_node)

    def _check_nodes_have_same_collection(self):
        """Return True if all nodes have collected the same items.
        If collections differ, this method returns False while logging
        the collection differences and posting collection errors to
        pytest_collectreport hook.
        """
        node_collection_items = list(self.node2collection.items())
        first_node, col = node_collection_items[0]
        same_collection = True
        for node, collection in node_collection_items[1:]:
            msg = report.report_collection_diff(
                col,
                collection,
                first_node.gateway.id,
                node.gateway.id,
            )
            if msg:
                same_collection = False
                self.log(msg)
                if self.config is not None:
                    rep = runner.CollectReport(
                        node.gateway.id, 'failed',
                        longrepr=msg, result=[])
                    self.config.hook.pytest_collectreport(report=rep)

        return same_collection
