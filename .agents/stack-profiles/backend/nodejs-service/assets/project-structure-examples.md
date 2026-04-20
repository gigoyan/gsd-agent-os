# Node.js Profile Examples

These examples are intended for user-facing explanation during stack selection and for maintainers generating project-local templates later.

## Example: `authoring_mode=javascript-esm`

```json
{
  "type": "module",
  "scripts": {
    "dev": "node --watch src/server.js",
    "test": "node --test",
    "lint": "eslint ."
  }
}
```

```js
import Fastify from 'fastify';

const app = Fastify({ logger: true });
app.get('/health', async () => ({ ok: true }));
await app.listen({ port: 3000 });
```

## Example: `authoring_mode=typescript-node-next`

```json
{
  "type": "module",
  "scripts": {
    "test": "node --test",
    "typecheck": "tsc --noEmit",
    "build": "tsc -p tsconfig.json"
  }
}
```

```json
{
  "compilerOptions": {
    "module": "nodenext",
    "target": "ES2022"
  }
}
```

## Example: `service_architecture=feature-first-layered`

```text
src/
  app/
    server.js
  config/
    env.js
  modules/
    users/
      routes.js
      service.js
      repository.js
      schema.js
    billing/
      routes.js
      service.js
      repository.js
  shared/
    errors/
    logging/
test/
  integration/
  unit/
```

Why a user might choose it:
- easiest modular structure for most product APIs
- each business area is easy to find
- still keeps transport and data code separated

## Example: `service_architecture=strict-layered`

```text
src/
  presentation/
    http/
  application/
  domain/
  data/
  config/
test/
```

Why a user might choose it:
- clear technical layer boundaries
- fits teams already used to layer-based systems

Main downside:
- one feature may be split across several folders

## Example: `service_architecture=hexagonal`

```text
src/
  core/
    user/
      use-cases/
      entities/
  ports/
    user-repository.js
    mailer.js
  adapters/
    http/
    db/
    queue/
  config/
test/
  core/
  adapters/
```

Why a user might choose it:
- core logic can be tested without the web server or database
- integrations are easier to swap later

Main downside:
- more files and more ceremony

## Example: `http_framework=fastify`

```js
const route = {
  schema: {
    response: {
      200: {
        type: 'object',
        properties: {
          ok: { type: 'boolean' }
        },
        required: ['ok']
      }
    }
  }
};

app.get('/health', route, async () => ({ ok: true }));
```

Why a user might choose it:
- explicit contracts for API boundaries
- strong default fit for JSON APIs

## Example: `http_framework=express`

```js
const router = Router();

router.get('/health', async (_req, res, next) => {
  try {
    res.json({ ok: true });
  } catch (error) {
    next(error);
  }
});
```

Why a user might choose it:
- familiar middleware model
- broad ecosystem and team familiarity

## Example: `repo_shape=npm-workspaces-monorepo`

```text
package.json
apps/
  api/
    package.json
  worker/
    package.json
packages/
  shared-config/
    package.json
  domain-types/
    package.json
```

Why a user might choose it:
- multiple deployables
- internal shared packages

Main downside:
- more coordination and boundary discipline
