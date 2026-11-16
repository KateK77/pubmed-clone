// Screenshot-only actor memory. Never contains DOM, database or oracle observations.
export function taskEnvelope(test, notes, viewport, origin) {
  // All frozen task fields are retained verbatim, including every workflow/criterion.
  return JSON.stringify({frozen_test:test,precondition_notes:notes,viewport,allowed_origin:origin})
}

export function initialInput(task, image) {
  return [{role:'user',content:[{type:'input_text',text:task},
    {type:'input_image',image_url:'data:image/png;base64,'+image,detail:'original'}]}]
}

export function nextInput(task, earlierTurns, lastOutput, screenshots) {
  // Explicit non-reasoning sessions: retain latest native call/output pairing, all
  // executed action text and all model observations; older screenshots stay on disk.
  // An unexpected hidden-reasoning item is not silently dropped or replayed against
  // an edited prefix. Stop for compatibility review instead (no automatic retry).
  if(lastOutput.some(item=>item.type==='reasoning')) throw new Error('Unexpected reasoning state in none-effort mode; context optimization requires review')
  const calls=lastOutput.filter(item=>item.type==='computer_call')
  if(calls.length!==screenshots.length || calls.some(call=>!screenshots.some(s=>s.call_id===call.call_id))) throw new Error('Native call/screenshot pairing mismatch')
  return [{role:'user',content:task},
    ...(earlierTurns.length?[{role:'user',content:'Prior native action/observation ledger (observations are not verified verdicts): '+JSON.stringify(earlierTurns)}]:[]),
    ...lastOutput,...screenshots]
}

export function ledgerTurn(output) {
  return output.filter(x=>x.type==='computer_call'||x.type==='message').map(x=>x.type==='computer_call'
    ? {call_id:x.call_id,actions:x.actions}
    : {observation:x.content?.filter(y=>y.type==='output_text').map(y=>y.text).join('\n')||''})
}

export function tokenEstimate(usage, prices) {
  const input=usage.input_tokens,output=usage.output_tokens
  const cached=usage.input_tokens_details?.cached_tokens||0
  if(!Number.isInteger(input)||input<0||!Number.isInteger(output)||output<0||!Number.isInteger(cached)||cached<0||cached>input) throw new Error('Invalid provider usage')
  return {cached_input_tokens:cached,
    uncached_upper_usd:(input*prices.input+output*prices.output)/1e6,
    cache_adjusted_estimate_usd:((input-cached)*prices.input+cached*prices.cached_input+output*prices.output)/1e6}
}
