---
name: fleet-maintenance
description: "Disabled Mac-fleet workflow retained as migration source until Ryan's real inventory, profiles, and host routes are defined."
---

# Fleet Maintenance

This workflow is disabled.
Do not connect to or mutate any Mac through this skill.

The bundled scripts and references preserve upstream implementation ideas only.
They assume Peter-specific inventory paths, host profiles, services, credentials, and package ownership that do not exist in Ryan's verified environment.

Enable this skill only after a separate customisation establishes and validates:

- Ryan-owned inventory and snapshot paths;
- current host identities, SSH aliases, and reachability boundaries;
- desired profiles, package owners, repositories, and Xcode policy;
- the credential workflow available on every target host;
- focused tests for every retained mutation script.

Until then, use the applicable single-machine maintenance skill for an explicitly selected local Mac.
