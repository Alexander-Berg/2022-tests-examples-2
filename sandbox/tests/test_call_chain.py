from sandbox.projects.release_machine.components.config_core.jg.lib import call_chain


def test__call_chain__jmespath__getattr():

    cc = call_chain.CallChainMem().something

    assert cc.call_chain
    assert len(cc.call_chain) == 1
    assert cc.call_chain[0] == ("something", call_chain.CALL_CHAIN_ACTION_GETATTR)


def test__call_chain__jmespath__getitem():

    cc = call_chain.CallChainMem()["something"]

    assert cc.call_chain
    assert len(cc.call_chain) == 1
    assert cc.call_chain[0] == ("something", call_chain.CALL_CHAIN_ACTION_GETITEM)


def test__call_chain__jmespath__resource_hack():

    cc1 = call_chain.CallChainMem().resources["?type == 'SOMETHING'"][0].id
    cc2 = call_chain.CallChainMem().resources["SOMETHING"][0].id

    assert cc1.jmespath == cc2.jmespath


def test__call_chain__jmespath__resource_hack__should_not_be_applied():

    cc1 = call_chain.CallChainMem().potato["?type == 'SOMETHING'"][0].id
    cc2 = call_chain.CallChainMem().potato["SOMETHING"][0].id

    assert cc1.jmespath != cc2.jmespath

    cc1 = call_chain.CallChainMem().resources["?type == '0'"].id
    cc2 = call_chain.CallChainMem().resources[0].id

    assert cc1.jmespath != cc2.jmespath
