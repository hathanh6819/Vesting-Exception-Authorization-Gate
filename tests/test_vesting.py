import hashlib
import json
import pytest
from datetime import datetime, timezone

def address(value):
    from genlayer.py.types import Address
    return Address(value)

def warp(vm, timestamp):
    vm.warp(datetime.fromtimestamp(timestamp, timezone.utc).isoformat())

BEN = '0x2222222222222222222222222222222222222222'
OUT = '0x3333333333333333333333333333333333333333'
T = 1893456000
POLICY = 'Permit an early release only when the DAO explicitly cancels the milestone without continuing obligations.'

@pytest.fixture
def setup(direct_vm, direct_deploy):
    warp(direct_vm, T)
    c = direct_deploy('contracts/vesting_exception_gate.py')
    assert c.create_schedule(address(BEN), 10000, T, T+10000, 2500, 'dao/decisions', POLICY) == 1
    return c, direct_vm

def document(vm, **changes):
    from genlayer.py.types import Address
    address = Address(vm._contract_address) if isinstance(vm._contract_address, bytes) else vm._contract_address
    data = dict(contract=str(address.as_hex).lower(), schedule_id=1, beneficiary=BEN, decision_id='cancel-1', statement='The DAO explicitly cancels this milestone permanently. No continuing obligations remain.')
    data.update(changes)
    return json.dumps(data).encode()

def prepare(c, vm, body=None, digest=None, status=200, findings=None):
    body = document(vm) if body is None else body
    assert isinstance(c.record_cancellation(1, 'cancel-1', 'a'*40, 'decision.json', digest or hashlib.sha256(body).hexdigest(), T+5000), int)
    vm.clear_mocks()
    vm.mock_web(r'raw\.githubusercontent\.com', dict(status=status, body=body.decode()))
    vm.mock_llm('Evaluate a DAO', json.dumps(findings if findings is not None else dict(cancellation_explicit=True, policy_covered=True, conflicting_obligations=False)))

def act(c, vm, method, *args):
    if method == 'transfer':
        args = (address(args[0]), *args[1:])
    with vm.prank(address(BEN)):
        from genlayer.gl.vm import UserError
        try:
            return getattr(c, method)(*args)
        except UserError as error:
            return str(error)

def conserve(c):
    s = c.get_schedule(1)
    assert c.get_info()['treasury'] + s['amount']-s['released'] + int(c.balance_of(address(BEN))) + int(c.balance_of(address(OUT))) == 1000000000

def test_happy_consume_transfer_replay(setup):
    c, vm = setup
    prepare(c, vm)
    assert act(c, vm, 'assess_exception', 1, 1) == 'ELIGIBLE'
    assert len(c.get_schedule(1)['receipt']) == 64
    assert act(c, vm, 'consume_exception', 1, 1) == 2500
    before = c.get_schedule(1)
    assert 'NOT_AUTHORIZED' in act(c, vm, 'consume_exception', 1, 1)
    assert c.get_schedule(1) == before
    assert act(c, vm, 'transfer', OUT, 100) == 'TRANSFERRED'
    assert int(c.balance_of(address(OUT))) == 100
    conserve(c)

@pytest.mark.parametrize('kind', ['digest', 'beneficiary_identity', 'contract_identity', 'schedule_identity', 'decision_identity', 'oversized', 'malformed', 'unavailable', 'model'])
def test_fail_closed(setup, kind):
    c, vm = setup
    kwargs = {'digest': dict(digest='f'*64), 'beneficiary_identity': dict(body=document(vm, beneficiary=OUT)), 'contract_identity': dict(body=document(vm, contract='0x'+'4'*40)), 'schedule_identity': dict(body=document(vm, schedule_id=2)), 'decision_identity': dict(body=document(vm, decision_id='other')), 'oversized': dict(body=b'x'*16001), 'malformed': dict(body=b'not-json'), 'unavailable': dict(status=503), 'model': dict(findings={'cancellation_explicit':'true'})}[kind]
    prepare(c, vm, **kwargs)
    assert act(c, vm, 'assess_exception', 1, 1) == 'UNRESOLVED'
    before = c.get_schedule(1)
    assert 'NOT_AUTHORIZED' in act(c, vm, 'consume_exception', 1, 1)
    assert c.get_schedule(1) == before
    conserve(c)

@pytest.mark.parametrize('cancel,covered,conflict,expected', [(True,True,True,'CONFLICT'), (False,True,False,'INELIGIBLE'), (True,False,False,'INELIGIBLE')])
def test_semantic_rejections(setup, cancel, covered, conflict, expected):
    c, vm = setup
    prepare(c, vm, findings=dict(cancellation_explicit=cancel,policy_covered=covered,conflicting_obligations=conflict))
    assert act(c, vm, 'assess_exception', 1, 1) == expected
    assert 'NOT_AUTHORIZED' in act(c, vm, 'consume_exception', 1, 1)
    conserve(c)

def test_recovery(setup):
    c, vm = setup
    prepare(c, vm, status=503)
    assert act(c, vm, 'assess_exception', 1, 1) == 'UNRESOLVED'
    vm.clear_mocks()
    vm.mock_web(r'raw\.githubusercontent\.com', dict(status=200,body=document(vm).decode()))
    vm.mock_llm('Evaluate a DAO', json.dumps(dict(cancellation_explicit=True,policy_covered=True,conflicting_obligations=False)))
    assert act(c, vm, 'assess_exception', 1, 1) == 'ELIGIBLE'
    assert act(c, vm, 'consume_exception', 1, 1) == 2500
    conserve(c)

def test_revision_revoke_expiry(setup):
    c, vm = setup
    prepare(c, vm)
    assert act(c, vm, 'assess_exception', 1, 1) == 'ELIGIBLE'
    c.revoke_decision(1)
    assert 'STALE_REVISION' in act(c, vm, 'consume_exception', 1, 1)
    prepare(c, vm)
    assert act(c, vm, 'assess_exception', 1, 3) == 'ELIGIBLE'
    warp(vm, T+5000)
    assert 'EXPIRED' in act(c, vm, 'consume_exception', 1, 3)
    conserve(c)

def test_normal_claim_after_early_release(setup):
    c, vm = setup
    prepare(c, vm)
    act(c, vm, 'assess_exception', 1, 1)
    act(c, vm, 'consume_exception', 1, 1)
    warp(vm, T+1000)
    assert 'NOTHING_RELEASABLE' in act(c, vm, 'claim_vested', 1)
    warp(vm, T+10000)
    assert act(c, vm, 'claim_vested', 1) == 7500
    conserve(c)

def test_claim_race_recomputes_remaining(setup):
    c, vm = setup
    prepare(c, vm)
    act(c, vm, 'assess_exception', 1, 1)
    warp(vm, T+1000)
    assert act(c, vm, 'claim_vested', 1) == 1000
    assert act(c, vm, 'consume_exception', 1, 1) == 1500
    conserve(c)

def test_unauthorized_writes(setup):
    c, vm = setup
    before = c.get_schedule(1)
    from genlayer.gl.vm import UserError
    with pytest.raises(UserError, match='ONLY_BENEFICIARY'):
        c.claim_vested(1)
    assert 'ONLY_DAO' in act(c, vm, 'revoke_decision', 1)
    assert 'INSUFFICIENT_BALANCE' in act(c, vm, 'transfer', OUT, 1)
    assert c.get_schedule(1) == before
    conserve(c)

def test_validator_rejects_changed_findings(setup, monkeypatch):
    c, vm = setup
    prepare(c, vm)
    assert act(c, vm, 'assess_exception', 1, 1) == 'ELIGIBLE'
    import genlayer.gl.vm as gl_vm
    monkeypatch.setattr(gl_vm, 'spawn_sandbox', lambda fn: gl_vm.Return(fn()))
    assert vm.run_validator() is True
    vm.clear_mocks()
    vm.mock_web(r'raw\.githubusercontent\.com', dict(status=200,body=document(vm).decode()))
    vm.mock_llm('Evaluate a DAO', json.dumps(dict(cancellation_explicit=True,policy_covered=True,conflicting_obligations=True)))
    assert vm.run_validator() is False

@pytest.mark.parametrize('index,value', [(1,0),(2,T-1),(3,T),(4,0),(4,10001),(5,'../bad/repo'),(6,'short')])
def test_invalid_schedule_preserves_treasury(setup,index,value):
    from genlayer.gl.vm import UserError
    c, vm = setup
    before = c.get_info()
    args = [address(OUT),10000,T,T+10000,2500,'dao/decisions',POLICY]
    args[index] = value
    with pytest.raises(UserError):
        c.create_schedule(*args)
    assert c.get_info() == before
    conserve(c)

@pytest.mark.parametrize('index,value', [(0,''),(1,'f'*39),(2,'../decision.json'),(3,'f'*63),(4,T),(4,T+604801)])
def test_invalid_decision_preserves_schedule(setup,index,value):
    from genlayer.gl.vm import UserError
    c, vm = setup
    before = c.get_schedule(1)
    args = ['cancel-1','a'*40,'decision.json','f'*64,T+5000]
    args[index] = value
    with pytest.raises(UserError):
        c.record_cancellation(1,*args)
    assert c.get_schedule(1) == before
    conserve(c)
