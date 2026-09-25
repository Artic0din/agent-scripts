// Run from a project with dependency-cruiser and TypeScript installed, or via npm exec.
const assert = require('node:assert/strict');
const fs = require('node:fs');
const os = require('node:os');
const path = require('node:path');
const { spawnSync } = require('node:child_process');
const localBinary = path.resolve('node_modules/.bin/depcruise');
const command = fs.existsSync(localBinary) ? localBinary : 'depcruise';
assert.equal(require('./dependency-cruiser.config.cjs').forbidden.length, 4);

const root = fs.mkdtempSync(path.join(os.tmpdir(), 'deep-modules-'));
try {
  fs.mkdirSync(path.join(root, 'src/packages/example/lib'), { recursive: true });
  fs.copyFileSync(path.join(__dirname, 'dependency-cruiser.config.cjs'), path.join(root, '.dependency-cruiser.cjs'));
  fs.writeFileSync(path.join(root, 'src/packages/example/lib/types.ts'), 'export type Example = string;\n');
  fs.writeFileSync(path.join(root, 'src/packages/example/lib/declarations.d.ts'), 'export type Example = string;\n');
  fs.writeFileSync(path.join(root, 'src/packages/example/index.ts'), "export type { Example } from './lib/types';\n");
  for (const [target, expected] of [['./packages/example/lib/types', 1], ['./packages/example/lib/declarations', 1], ['./packages/example', 0]]) {
    fs.writeFileSync(path.join(root, 'src/app.ts'), `import type { Example } from '${target}';\nexport type App = Example;\n`);
    const result = spawnSync(command, ['--config', '.dependency-cruiser.cjs', 'src'], { cwd: root, encoding: 'utf8' });
    assert.equal(result.status, expected, result.error?.message || result.stdout + result.stderr);
    if (expected) assert.match(result.stdout + result.stderr, /entrypoint-boundary-from-app/);
  }
  fs.writeFileSync(path.join(root, 'src/packages/root.ts'), "export type { Example } from './example/lib/types';\n");
  const rootImport = spawnSync(command, ['--config', '.dependency-cruiser.cjs', 'src'], { cwd: root, encoding: 'utf8' });
  assert.equal(rootImport.status, 1, rootImport.error?.message || rootImport.stdout + rootImport.stderr);
  assert.match(rootImport.stdout + rootImport.stderr, /entrypoint-boundary-from-app/);
  fs.unlinkSync(path.join(root, 'src/packages/root.ts'));
  fs.writeFileSync(path.join(root, 'tsconfig.boundaries.json'), JSON.stringify({ compilerOptions: { paths: { '@example/*': ['./src/packages/example/*'] } } }));
  fs.writeFileSync(path.join(root, 'src/alias.ts'), "export type { Example } from '@example/lib/types';\n");
  const aliased = spawnSync(command, ['--config', '.dependency-cruiser.cjs', '--ts-config', 'tsconfig.boundaries.json', 'src'], { cwd: root, encoding: 'utf8' });
  assert.equal(aliased.status, 1, aliased.error?.message || aliased.stdout + aliased.stderr);
  assert.match(aliased.stdout + aliased.stderr, /entrypoint-boundary-from-app/);
  fs.unlinkSync(path.join(root, 'src/alias.ts'));
  fs.mkdirSync(path.join(root, 'src/packages/example/tests'), { recursive: true });
  fs.mkdirSync(path.join(root, 'src/packages/other/tests'), { recursive: true });
  fs.writeFileSync(path.join(root, 'src/packages/example/tests/fixture.ts'), 'export const fixture = 1;\n');
  fs.writeFileSync(path.join(root, 'src/packages/other/tests/fixture.ts'), 'export const fixture = 2;\n');
  for (const [target, expected] of [['./fixture', 0], ['../../other/tests/fixture', 1]]) {
    fs.writeFileSync(path.join(root, 'src/packages/example/tests/check.ts'), `export { fixture } from '${target}';\n`);
    const result = spawnSync(command, ['--config', '.dependency-cruiser.cjs', 'src'], { cwd: root, encoding: 'utf8' });
    assert.equal(result.status, expected, result.error?.message || result.stdout + result.stderr);
    if (expected) assert.match(result.stdout + result.stderr, /tests-through-entrypoints/);
  }
  fs.unlinkSync(path.join(root, 'src/packages/example/tests/check.ts'));
  fs.writeFileSync(path.join(root, 'src/cycle-a.ts'), "import './cycle-b';\n");
  fs.writeFileSync(path.join(root, 'src/cycle-b.ts'), "import './cycle-a';\n");
  const cycle = spawnSync(command, ['--config', '.dependency-cruiser.cjs', 'src'], { cwd: root, encoding: 'utf8' });
  assert.equal(cycle.status, 0, cycle.error?.message || cycle.stdout + cycle.stderr);
  console.log('PASS: private type and foreign fixture imports fail; public entry points and own fixtures pass');
} finally {
  fs.rmSync(root, { recursive: true, force: true });
}
