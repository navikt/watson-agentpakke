# watson-agentpakke

Agentpakke for Team Holmes / Watson-porteføljen. Distribueres til nav-pilot med
`nav-pilot install --source navikt/watson-agentpakke`.

## Innhold

| Type      | Navn                                                                           |
| --------- | ------------------------------------------------------------------------------ |
| agent     | `vaktmester` — rullerende ukentlig vakt for Holmes-teamet                       |
| agent     | `nav-pilot` — lokal skygge av upstream-agenten med Holmes-tilpasninger           |
| skill     | `analytics-taxonomy` — Nav analytics-taksonomi (Umami)                          |
| skill     | `explain-diff-html` — forklar en kodeendring/diff/PR som HTML                   |
| skill     | `repo-activity-research` — oppsummer endringer i Watson-repoene                 |
| skill     | `unleash-feature-toggle` — opprett/rydd opp feature toggles i Holmes-porteføljen |
| skill     | `watson-setup` — sett opp watson-developer-lokalmiljø fra scratch               |
| extension | `auto-format` — kjører `pnpm format:fix` i `watson-sak-frontend` etter endringer |

## Bygger videre på nav-pilot

`.nav-pilot/agentpakke.lock.json` peker på `navikt/copilot` (pakka `nav-pilot`),
pinnet til en commit-sha. Låsefila har et flatt `items`-kart over både arvede og
Watson-spesifikke elementer som følger med ved installasjon. `agents/nav-pilot.agent.md`
og `instructions/output-style.instructions.md` skygger upstream-elementer ved
samme navn.

`items`-kartet utelater med vilje `deliberate-ai-use`-skillen og -instruksjonen.
Når upstream har flere elementer med samme navn, beholder kartet `accessibility`
som instruksjon, `kafka` som agent og `security-owasp` som instruksjon.

For å oppdatere til en nyere revisjon av `navikt/copilot`, oppdater SHA i lockfila.
Synkroniser `items`-kartet mot upstream uten å miste Watson-elementene, og gå gjennom
de to skyggefilene mot samme commit. Gjennomfør dette manuelt. Repoet har ingen
CI for basisoppdateringer.

```bash
gh api repos/navikt/copilot/commits/main --jq .sha
nav-pilot list --source navikt/copilot --items --json
```

## Installere i et repo

```bash
nav-pilot install watson-agentpakke --source navikt/watson-agentpakke --repo
```

Dette skriver `.nav-pilot/agentpakke.lock.json` i konsumentrepoet med kilde og
revisjon. Commit den filen slik at hele teamet installerer fra samme revisjon.

## Eierskap

Team Holmes eier og vedlikeholder denne pakka. Endringer i `vaktmester`,
Watson-skillene eller `auto-format` skjer her, ikke i `watson-developer`.
