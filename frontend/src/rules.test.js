import {test} from 'node:test';
import assert from 'node:assert/strict';
import {address,integer,timestamp,executionSucceeded} from './rules.js';
test('reject invalid wallet and unsafe amount',()=>{assert.throws(()=>address(''));assert.throws(()=>integer('1.5'));assert.throws(()=>integer('9007199254740992'));assert.equal(integer('2500'),2500);});
test('require complete timestamp',()=>{assert.throws(()=>timestamp(''));assert.equal(timestamp('2030-01-01T00:00:00Z'),1893456000);});
test('receipt is not success without execution proof',()=>{assert.equal(executionSucceeded({}),false);assert.equal(executionSucceeded({consensus_data:{leader_receipt:{execution_result:'ERROR'}}}),false);assert.equal(executionSucceeded({consensus_data:{leader_receipt:{execution_result:'SUCCESS'}}}),true);});
