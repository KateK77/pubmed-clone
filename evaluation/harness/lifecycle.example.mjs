// Implement against the isolated evaluation environment, not public production.
// prepare must reset synthetic app state for EACH frozen test before returning ready:true.
// Never use prepare to perform the user workflow under test.
export async function prepare({test,config}) {
  return {ready:false,reason:`Local reset/preconditions for ${test.id} must be explicitly implemented before execution.`}
}
// Supported ready:true fields: start_url, instructions, secrets, storage_state,
// viewport:{width,height}, extra_pages:["http://127.0.0.1:8125/"]. Extra pages must
// be pre-approved exact local origins; initial selected page remains the app.
// The model must request native Ctrl+Tab to view/read the synthetic mailbox.
// Optional: independent read-only verification, never returned to the CUA actor.
// Must provide reviewed_by and concrete evidence for PASS/FAIL. Without this hook,
// native completion stays BLOCKED/pending review, never auto-PASS.
// export async function verify({test,context,prepared,result,config}) {...}
// Optional local synthetic-data cleanup, must not touch real user data.
// export async function cleanup({test,prepared,config}) {...}
