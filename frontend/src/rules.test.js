import {test} from 'node:test';
import assert from 'node:assert/strict';
import {address,integer,timestamp,scheduleWindow,executionSucceeded} from './rules.js';
test('reject invalid wallet and unsafe amount',()=>{assert.throws(()=>address(''));assert.throws(()=>integer('1.5'));assert.throws(()=>integer('9007199254740992'));assert.equal(integer('2500'),2500);});
test('require complete timestamp',()=>{assert.throws(()=>timestamp(''));assert.equal(timestamp('2030-01-01T00:00:00Z'),1893456000);});
test('validate schedule before wallet signing',()=>{assert.deepEqual(scheduleWindow(2000,3000,1000),[2000,3000]);assert.throws(()=>scheduleWindow(1200,3000,1000),/five minutes/);assert.throws(()=>scheduleWindow(2000,1999,1000),/after/);assert.throws(()=>scheduleWindow(2000,2000+31536001,1000),/365 days/);});
test('receipt is not success without execution proof',()=>{assert.equal(executionSucceeded({}),false);assert.equal(executionSucceeded({consensus_data:{leader_receipt:{execution_result:'ERROR'}}}),false);assert.equal(executionSucceeded({consensus_data:{leader_receipt:{execution_result:'SUCCESS'}}}),true);});
