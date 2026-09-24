# watson-agentpakke

Agentpakke for Team Holmes / Watson-porteføljen. Distribueres til nav-pilot med
`nav-pilot install --source navikt/watson-agentpakke`.

## Innhold

| Type      | Navn                                                                          |
| --------- | ------------------------------------------------------------------------------ |
| agent     | `vaktmester` — rullerende ukentlig vakt for Holmes-teamet                       |
| skill     | `analytics-taxonomy` — Nav analytics-taksonomi (Umami)                         |
| skill     | `explain-diff-html`  — forklar en kodeendring/diff/PR som HTML                  |
| skill     | `repo-activity-research` — oppsummer endringer i Watson-repoene                |
| skill     | `unleash-feature-toggle` — opprett/rydd opp feature toggles i Holmes-porteføljen|
| skill     | `watson-setup` — sett opp watson-developer-lokalmiljø fra scratch              |
| extension | `auto-format` — kjører `pnpm format:fix` i `watson-sak-frontend` etter endringer|

## Bygger videre på nav-pilot

`.nav-pilot/agentpakke.lock.json` peker på `navikt/copilot` (pakka `nav-pilot`),
pinnet til en commit-sha. Alt som ligger der (agenter som `nav-pilot`,
`security-champion`, `aksel` osv., skills, instruksjoner, prompts og hooks)
følger med når noen installerer denne pakka. Denne pakka legger bare til det
Watson-spesifikke på toppen, og skygger ingenting fra basen.

For å oppdatere til en nyere revisjon av `navikt/copilot`:

```bash
nav-pilot validate --source navikt/copilot   # finn ønsket sha
# oppdater sha i .nav-pilot/agentpakke.lock.json, commit og push
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
