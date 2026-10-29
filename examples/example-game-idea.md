# Example game idea: "Lantern Hollow"

[Back to README](../README.md) · Next: [example design](example-game-design.md) · [example session](example-workflow.md)

This is the kind of request a user gives. It is deliberately informal; the Game Director fills gaps
with documented defaults.

```text
/pixel-art-game-studio I want a cozy top-down pixel-art game called Lantern Hollow.
You are a new lamplighter arriving in a small valley town where the lanterns have
started going out one by one. There is a town and a forest. I want maybe three
characters who feel like real people with their own worries, dialogue where my
choices matter, a day/night cycle (lanterns matter at night!), a couple of quests,
and saving. Keyboard and controller. Warm, slightly melancholic mood. No combat.
```

What the Director extracts (and what it defaults):

| Aspect | Value | Source |
| --- | --- | --- |
| Genre | Cozy narrative exploration | user |
| Camera | Top-down | user |
| Platform | Desktop (Windows/macOS/Linux) | default |
| Engine | Godot 4 if installed, otherwise documented alternative | default |
| Resolution | 320x180 logical, integer scaling | default |
| Core loop | Explore, talk, relight lanterns, uncover why they go out | user + director |
| Systems | Dialogue with choices, flags, relationships, quests, inventory (small), day/night, save/load | user |
| Combat | None | user |
| Milestone 1 | Town only, one NPC, one lantern quest, save/reload | director |

The Director does not ask about font, palette size, or menu layout; those get defaults in the design
documents and can be changed later by feedback.
