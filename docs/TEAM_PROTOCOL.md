# Team Protocol: @job_hunter + @cc

## Shared goals
- Maximize quality opportunities.
- Minimize user effort.
- Maintain proactive daily cadence.

## Message contract
`job_hunter -> cc`
- opportunities[]
- fit_explanations[]
- source_health

`cc -> user`
- priorities[]
- next_steps[]
- follow-ups[]

## Failure policy
- If source fetch fails, return partial results + source error note.
- If no jobs fit threshold, broaden query and retry once.
