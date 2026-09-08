export function address(value){if(!/^0x[0-9a-fA-F]{40}$/.test(value))throw Error('Enter a valid contract or wallet address.');return value;}
export function integer(value){if(!/^\d+$/.test(value)||!Number.isSafeInteger(Number(value)))throw Error('Enter a non-negative safe integer.');return Number(value);}
export function timestamp(value){const n=Date.parse(value);if(!Number.isFinite(n))throw Error('Complete the date and time.');return Math.floor(n/1000);}
export function executionSucceeded(receipt){const raw=receipt?.consensus_data?.leader_receipt;const list=(Array.isArray(raw)?raw:raw?[raw]:[]).filter(x=>x.vote!=='idle');return list.length>0&&list.every(x=>x.execution_result==='SUCCESS');}
