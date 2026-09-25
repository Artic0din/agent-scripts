// Run with dependency-cruiser and TypeScript available on PATH.
const assert = require('node:assert/strict');
const fs = require('node:fs');
const os = require('node:os');
const path = require('node:path');
const { spawnSync } = require('node:child_process');

const root = fs.mkdtempSync(path.join(os.tmpdir(), 'deep-modules-'));
try {
  fs.mkdirSync(path.join(root, 'src/packages/example/lib'), { recursive: true });
  fs.writeFileSync(path.join(root, 'tsconfig.json'), '{}');
  fs.copyFileSync(path.join(__dirname, 'dependency-cruiser.config.cjs'), path.join(root, '.dependency-cruiser.cjs'));
  fs.writeFileSync(path.join(root, 'src/packages/example/lib/types.ts'), 'export type Example = string;\n');
  fs.writeFileSync(path.join(root, 'src/packages/example/lib/declarations.d.ts'), 'export type Example = string;\n');
  fs.writeFileSync(path.join(root, 'src/packages/example/index.ts'), "export type { Example } from './lib/types';\n");
  for (const [target, expected] of [['./packages/example/lib/types', 1], ['./packages/example/lib/declarations', 1], ['./packages/example', 0]]) {
    fs.writeFileSync(path.join(root, 'src/app.ts'), `import type { Example } from '${target}';\nexport type App = Example;\n`);
    const result = spawnSync('depcruise', ['--config', '.dependency-cruiser.cjs', 'src'], { cwd: root, encoding: 'utf8' });
    assert.equal(result.status, expected, result.error?.message || result.stdout + result.stderr);
    if (expected) assert.match(result.stdout + result.stderr, /entrypoint-boundary-from-app/);
  }
  console.log('PASS: private type imports fail; public entry-point type imports pass');
} finally {
  fs.rmSync(root, { recursive: true, force: true });
}
