# Հայերեն

## README-ի նպատակը
Այս README-ն օգտատիրոջ ուղեցույց է։ Այն ցույց է տալիս, թե GSD flow-ի մեջ ինչպես սկսել աշխատանքը agent-ի հետ տվյալ նախագծի համար։

Սկսելու համար կա միայն երկու սցենար.
- նախագիծը սկսվում է զրոյից
- նախագիծը արդեն գոյություն ունի

## Սցենար 1. Նախագիծը սկսվում է զրոյից
### Երբ ընտրել այս ճանապարհը
Ընտրեք այս ճանապարհը, եթե repository-ում դեռ չկա իրական codebase, կամ դուք ունեք միայն գաղափար, brief, notes կամ նախնական project information։

### Ինչ պետք է անի օգտատերը
1. Գրեք agent-ին, որ սա նոր նախագիծ է։
2. Տվեք այն, ինչ արդեն ունեք.
   - գաղափար կամ business goal
   - brief, notes, transcript կամ այլ files
   - known constraints, deadlines, required integrations
3. Եթե ինչ-որ բան դեռ չգիտեք, դա նորմալ է. պարզապես ասեք, ինչն է դեռ բաց։

### Ինչ skill պետք է գործարկվի
Օգտագործեք `$gsd-new-project`.

### Ինչ կանի agent-ը
- Կհավաքի արդեն առկա տեղեկությունը chat-ից և files-ից։
- Չի կրկնի արդեն պատասխանված հարցերը։
- Կհարցնի միայն այն, ինչ պետք է առաջ շարժվելու համար։
- Կկառուցի մեկնարկային project direction-ը GSD flow-ի համար։

### Ինչ է հաջորդ քայլը GSD flow-ում
- Եթե project idea-ն արդեն բավական հստակ է, հաջորդ քայլերը գնում են դեպի spec readiness։
- Եթե հետո պետք լինի տեխնիկական stack ընտրել, հաջորդ համապատասխան skill-ը կլինի `$gsd-select-stack`.
- Երբ readiness artifacts-ը բավարար լինեն, planning-ի հաջորդ հիմնական քայլը կլինի `$gsd-plan-milestone`.
- Երբ milestone-ը արդեն ստեղծված լինի, բացեք նոր Codex session և գործարկեք `$gsd-run-milestone` այդ milestone-ի վրա։
- `$gsd-run-milestone` orchestration flow-ը կվերցնի milestone-ի execution-ը իր վրա և կօգտագործի sub-agents milestone-ը ամբողջությամբ ավարտելու համար։

### Ինչպես գրել առաջին հաղորդագրությունը
- «Սա նոր նախագիծ է։ Ունեմ միայն գաղափար»։
- «Սա նոր նախագիծ է։ Ունեմ brief և notes, աշխատիր դրանց հիման վրա»։

## Սցենար 2. Նախագիծը արդեն գոյություն ունի
### Երբ ընտրել այս ճանապարհը
Ընտրեք այս ճանապարհը, եթե repository-ում արդեն կա codebase, modules, configs, scripts կամ այլ իրական project structure։

### Ինչ պետք է անի օգտատերը
1. Գրեք agent-ին, որ նախագիծը արդեն գոյություն ունի։
2. Ասեք, թե ձեր նպատակը որն է.
   - հասկանալ ներկայիս կառուցվածքը
   - onboarding անել repo-ն
   - պատրաստվել refactor, migration, upgrade կամ modernization-ի
3. Եթե կան կարևոր files, risky areas կամ known problems, նշեք դրանք։

### Որ skill-ը պետք է ընտրել
- Օգտագործեք `$gsd-map-codebase`, եթե պետք է factual repo map, structure understanding և grounded onboarding։
- Օգտագործեք `$gsd-map-codebase`, եթե խնդիրը վերաբերում է major refactor, migration, upgrade, modernization կամ architecture-level change-ին։

### Ինչ կանի agent-ը
- Կուսումնասիրի իրական repository state-ը։
- Կբացատրի նախագիծը պարզ և գործնական ձևով։
- Կասի, արդյոք բավական է սովորական mapping, թե պետք է serious mapping։
- Կձևակերպի անվտանգ հաջորդ քայլը GSD flow-ի մեջ։

### Ինչ է հաջորդ քայլը GSD flow-ում
- Եթե արդյունքը սովորական onboarding/map է, և readiness artifacts-ը բավարար են, հաջորդ planning step-ը կլինի `$gsd-plan-milestone`.
- Եթե mapping-ից հետո պետք է որոշել stack-ը, հաջորդ skill-ը կլինի `$gsd-select-stack`.
- Եթե serious mapping է պետք, նախ ավարտվում է `$gsd-map-codebase`, և միայն հետո որոշվում է milestone planning-ի շրջանակը։
- Երբ milestone-ը արդեն ստեղծված լինի, բացեք նոր Codex session և գործարկեք `$gsd-run-milestone`՝ ընտրելով այդ milestone-ը։
- Այդ պահից orchestration flow-ը կվերցնի milestone-ի իրականացումը իր վրա և sub-agents-ի օգնությամբ կտանի այն մինչև completion։

### Ինչպես գրել առաջին հաղորդագրությունը
- «Սա արդեն գոյություն ունեցող նախագիծ է։ Նախ արա `$gsd-map-codebase`»։
- «Սա արդեն գոյություն ունեցող նախագիծ է։ Պետք է modernization-ի համար `$gsd-map-codebase`»։

## Օգտատիրոջ համար պարզ կանոն
- Եթե նոր նախագիծ է, սկսեք `$gsd-new-project`-ով։
- Եթե արդեն գոյություն ունեցող նախագիծ է և պետք է հասկանալ repo-ն, սկսեք `$gsd-map-codebase`-ով։
- Եթե արդեն գոյություն ունեցող նախագիծ է և պետք է մեծ refactor կամ migration հասկանալ, սկսեք `$gsd-map-codebase`-ով։
- Եթե milestone-ը արդեն ստեղծված է, հաջորդ session-ում գործարկեք `$gsd-run-milestone` և ընտրեք այդ milestone-ը execution-ի համար։

# English

## Purpose Of This README
This README is a user guide. It tells you how to start working with the agent for this project inside the GSD flow.

There are only two starting scenarios:
- the project starts from scratch
- the project already exists

## Obsidian Vault Setup For GSD
GSD uses one shared Obsidian MCP vault root and one project namespace per repository.

Codex config should point MCPVault to the shared vault root only:

    [mcp_servers.obsidian]
    command = "npx"
    args = ["-y", "@bitbonsai/mcpvault@latest", "<shared-obsidian-vault-root>"]

Each project stores durable GSD memory under:

    projects/<vault-project-id>/

`<vault-project-id>` is normally the repository root folder name. During `$gsd-new-project` or `$gsd-map-codebase`, Codex records the resolved value in `PROJECT.md`.

Example:

    Repository:
    D:/path/to/example-project

    Vault namespace:
    <shared-obsidian-vault-root>/projects/example-project/

Do not create one MCP server per project unless explicitly needed.
Do not store milestone, phase, verification, roadmap, or live state files in Obsidian.

## Context Index For Faster Agent Work
GSD uses `.planning/CONTEXT_INDEX.md` as a compact task-routing guide for Codex.

The context index helps the agent avoid scanning the whole repository by recording:
- where to start for common task types
- what to inspect next
- what usually changes
- which validation checks to run
- which folders or files to avoid unless needed

Use `$gsd-map-codebase` for initial mapping, serious mapping, targeted context-index refresh, major structure changes, or whenever agents repeatedly inspect too much of the project.

For a project that has not started yet, the context index is not required until real structure exists.

## Updating GSD From The Blueprint

GSD is designed to be updated from a reusable blueprint without overwriting project-specific workflow data.

Use:

    $gsd-sync-blueprint audit-only|install|update <TARGET_REPOSITORY_PATH>

to audit a project repository from the current reusable blueprint source and then, only after explicit approval, install or update reusable GSD files from the blueprint.

Blueprint sync updates reusable assets such as skills, templates, managed `AGENTS.md` blocks, and the reusable guidance blocks in hybrid starter surfaces.

Blueprint sync must preserve project-owned artifacts, including:

    .planning/STATE.md
    .planning/ROADMAP.md
    .planning/CONTEXT_INDEX.md
    .planning/milestones/**
    .planning/phases/**
    .planning/verification/**
    project-local .codex outputs

For `PROJECT.md` and `.planning/CODEBASE_MAP.md`, sync may create the starter file only when missing. If the file exists, sync may update only the marked `GSD-BLUEPRINT` guidance block and must preserve all `GSD-PROJECT` content.

`README.md` and existing `.planning/STATE.md` are project-owned. Sync must not create or update a target project README and must never update existing runtime state.

## Scenario 1. Project From Scratch
### When To Choose This Path
Choose this path if the repository does not contain a real codebase yet, or if you only have an idea, a brief, notes, or early project information.

### What The User Should Do
1. Tell the agent that this is a new project.
2. Provide whatever you already have:
   - idea or business goal
   - brief, notes, transcript, or other files
   - known constraints, deadlines, required integrations
3. If some parts are still unknown, just say what is still open.

### Which Skill Should Be Used
Use `$gsd-new-project`.

### What The Agent Will Do
- It will gather the information that already exists in chat and files.
- It will not repeat questions that are already answered.
- It will ask only for the information needed to move forward.
- It will build the starting project direction inside the GSD flow.

### What The Next Step Is In The GSD Flow
- If the project idea is already clear enough, the next work moves toward spec readiness.
- If technical stack selection is needed later, the next relevant skill is `$gsd-select-stack`.
- When the readiness artifacts are current enough, the next main planning step is `$gsd-plan-milestone`.
- After the milestone has been created, open a new Codex session and run `$gsd-run-milestone` on that milestone.
- The `$gsd-run-milestone` orchestration flow will take over execution and use sub-agents to complete the milestone end to end.

### How To Write The First Message
- “This is a new project. I only have an idea.”
- “This is a new project. I have a brief and notes. Work from those.”

## Scenario 2. Existing Project
### When To Choose This Path
Choose this path if the repository already contains a real codebase, modules, configs, scripts, or other project structure.

### What The User Should Do
1. Tell the agent that the project already exists.
2. Say what your goal is:
   - understand the current structure
   - onboard the repo
   - prepare for a refactor, migration, upgrade, or modernization
3. If there are important files, risky areas, or known problems, point them out.

### Which Skill Should Be Used
- Use `$gsd-map-codebase` for factual repo mapping, grounded onboarding, serious transformation-oriented mapping, or context-index routing refresh.

### What The Agent Will Do
- It will inspect the real repository state.
- It will explain the project in a plain, practical way.
- It will choose the right mapping depth and slices inside the unified mapping workflow.
- It will define the safe next step in the GSD flow.

### What The Next Step Is In The GSD Flow
- If mapping is complete enough and the readiness artifacts are current enough, the next planning step is `$gsd-plan-milestone`.
- If stack choice is still needed after mapping, the next skill is `$gsd-select-stack`.
- If serious mapping is needed, `$gsd-map-codebase` performs the deeper current-state mapping itself through bounded mapping sub-agents and updates `CODEBASE_MAP.md` and `CONTEXT_INDEX.md`.
- Mapping does not create milestones for mapping or hand mapping work to `$gsd-run-milestone`.

### How To Write The First Message
- “This is an existing project. First run `$gsd-map-codebase`.”
- “This is an existing project. We need `$gsd-map-codebase` for modernization.”

## Simple Rule For The User
- If it is a new project, start with `$gsd-new-project`.
- If it is an existing project and you need to understand the repo, start with `$gsd-map-codebase`.
- If it is an existing project and you need to understand a major refactor or migration, start with `$gsd-map-codebase`.
- Use `$gsd-run-milestone` only after normal implementation milestone planning has created an implementation milestone.

# Русский

## Назначение Этого README
Этот README - пользовательское руководство. Он показывает, как начать работу с агентом для данного проекта внутри GSD flow.

Есть только два стартовых сценария:
- проект начинается с нуля
- проект уже существует

## Сценарий 1. Проект С Нуля
### Когда Выбирать Этот Путь
Выбирайте этот путь, если repository еще не содержит реальный codebase, или если у вас пока есть только идея, brief, notes или ранняя project information.

### Что Должен Сделать Пользователь
1. Сообщите агенту, что это новый проект.
2. Передайте все, что у вас уже есть:
   - идея или business goal
   - brief, notes, transcript или другие files
   - known constraints, deadlines, required integrations
3. Если часть информации еще неизвестна, просто скажите, что пока остается открытым.

### Какой Skill Нужно Использовать
Используйте `$gsd-new-project`.

### Что Сделает Агент
- Он соберет уже существующую информацию из чата и files.
- Он не будет повторять вопросы, на которые уже есть ответы.
- Он спросит только то, что нужно для движения дальше.
- Он выстроит стартовое project direction внутри GSD flow.

### Какой Следующий Шаг В GSD Flow
- Если project idea уже достаточно ясна, следующая работа идет в сторону spec readiness.
- Если позже понадобится выбор technical stack, следующий relevant skill - `$gsd-select-stack`.
- Когда readiness artifacts будут достаточно актуальны, следующим основным planning step будет `$gsd-plan-milestone`.
- После того как milestone уже создан, откройте новую Codex session и запустите `$gsd-run-milestone` для этого milestone.
- Orchestration flow через `$gsd-run-milestone` возьмет execution на себя и завершит milestone целиком с помощью sub-agents.

### Как Написать Первое Сообщение
- «Это новый проект. У меня есть только идея.»
- «Это новый проект. У меня есть brief и notes. Работай от них.»

## Сценарий 2. Существующий Проект
### Когда Выбирать Этот Путь
Выбирайте этот путь, если repository уже содержит реальный codebase, modules, configs, scripts или другую project structure.

### Что Должен Сделать Пользователь
1. Сообщите агенту, что проект уже существует.
2. Скажите, в чем именно цель:
   - понять текущую структуру
   - сделать onboarding по repo
   - подготовиться к refactor, migration, upgrade или modernization
3. Если есть важные files, risky areas или known problems, укажите их.

### Какой Skill Нужно Использовать
- Используйте `$gsd-map-codebase`, если нужен factual repo map, понимание структуры и grounded onboarding.
- Используйте `$gsd-map-codebase`, если запрос связан с major refactor, migration, upgrade, modernization или другим architecture-level change.

### Что Сделает Агент
- Он изучит реальное состояние repository.
- Он объяснит проект простым и практичным языком.
- Он скажет, достаточно ли обычного mapping или нужен serious mapping.
- Он определит безопасный следующий шаг внутри GSD flow.

### Какой Следующий Шаг В GSD Flow
- Если результатом стал обычный onboarding/map и readiness artifacts уже достаточно актуальны, следующий planning step - `$gsd-plan-milestone`.
- Если после mapping все еще нужно выбрать stack, следующий skill - `$gsd-select-stack`.
- Если нужен serious mapping, сначала завершается `$gsd-map-codebase`, и только потом определяется scope для milestone planning.
- После того как milestone уже создан, откройте новую Codex session и запустите `$gsd-run-milestone`, выбрав этот milestone.
- После этого orchestration flow берет milestone execution на себя и доводит его до completion через sub-agents.

### Как Написать Первое Сообщение
- «Это существующий проект. Сначала запусти `$gsd-map-codebase`.»
- «Это существующий проект. Для modernization нужен `$gsd-map-codebase`.»

## Простое Правило Для Пользователя
- Если это новый проект, начинайте с `$gsd-new-project`.
- Если это существующий проект и нужно понять repo, начинайте с `$gsd-map-codebase`.
- Если это существующий проект и нужно разобраться с крупным refactor или migration, начинайте с `$gsd-map-codebase`.
- Если milestone уже создан, в новой Codex session запускайте `$gsd-run-milestone` и выбирайте этот milestone для execution.
