# Voice Conversation Mode

When this command is invoked, you enter **voice conversation mode**. Follow these rules strictly:

## Core Loop

You are now in a continuous voice conversation. After EVERY response you give, you MUST:

1. **Speak your response** — Call `mcp__voice__voice_speak` with your response text
2. **Listen for the next input** — Call `mcp__voice__voice_listen` immediately after speaking
3. **Process the transcript** — Handle whatever the user said
4. **Repeat from step 1**

This loop continues until the user says "exit voice mode", "stop listening", or "end conversation".

## Behavior Rules

- **NEVER stop the loop on your own.** After every response, speak it and listen again.
- **If voice_listen returns a timeout** (empty transcript), call `voice_listen` AGAIN immediately. The user may have missed the window or pressed the hotkey to re-trigger. Do NOT drop back to text mode on a timeout — try listening again up to 3 times before asking (via voice_speak) "Are you still there?" and listening one more time.
- **If voice_listen returns a transcript**, process it normally regardless of source (direct or hotkey).
- **Keep responses concise for voice.** Aim for 1-3 sentences unless the user asks for detail.
- **Don't narrate your tool calls.** Just do it and give the result.
- **Use voice_speak for ALL responses.** Every single thing you say to the user must go through voice_speak.

## Starting the Loop

When activated, immediately:
1. Call `mcp__voice__voice_speak` with "Voice mode active. I'm listening."
2. Call `mcp__voice__voice_listen` to start the first listening window
3. Enter the core loop

## Continuous Mode

If the user says "enable continuous listening" or "always listen":
1. Call `mcp__voice__voice_mode` with mode "continuous"
2. Continue the core loop — voice_listen will now return transcripts whenever speech is detected, no hotkey needed

To go back: call `mcp__voice__voice_mode` with mode "push-to-talk"

## Exiting Voice Mode

When the user says any exit phrase:
- Call `voice_speak` with "Exiting voice mode. Back to text."
- Call `voice_mode` with mode "off"
- Stop the loop
- Return to normal text interaction
