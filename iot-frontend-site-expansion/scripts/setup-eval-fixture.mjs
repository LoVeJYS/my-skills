import { cpSync, existsSync, readFileSync, mkdirSync, symlinkSync, writeFileSync } from 'node:fs'
import { dirname, isAbsolute, relative, resolve } from 'node:path'
import { fileURLToPath } from 'node:url'
import { spawnSync } from 'node:child_process'

const options = parseArgs(process.argv.slice(2))
const evalId = Number(options['eval-id'])
const source = resolve(options.source || process.cwd())
const output = options.output ? resolve(options.output) : ''
const skillRoot = resolve(dirname(fileURLToPath(import.meta.url)), '..')

if (!Number.isInteger(evalId) || evalId < 1 || evalId > 6) fail('--eval-id 必须是 1 到 6 的整数')
if (!output) fail('--output 必填')
if (existsSync(output)) fail(`输出路径必须不存在，脚本不会覆盖或删除: ${output}`)
if (!existsSync(resolve(source, '.git'))) fail('--source 必须是 Git 仓库根目录')
const relativeOutput = relative(source, output)
if (relativeOutput === '' || (!relativeOutput.startsWith('..') && !isAbsolute(relativeOutput))) fail('--output 不能位于源仓库内部')

const baseline = options.baseline || git(source, ['rev-parse', 'HEAD']).trim()
run('git', ['cat-file', '-e', `${baseline}^{commit}`], source)
run('git', ['clone', '--no-hardlinks', '--local', source, output], process.cwd())
run('git', ['checkout', '--detach', baseline], output)
copySkill(output)
linkDependencies(output)

if (evalId === 6) setupDirtyWorkspace(output)

console.log(`Eval fixture 已创建: eval=${evalId}, baseline=${baseline.slice(0, 12)}, path=${output}`)
console.log(`Skill 已复制到 fixture: .kiro/skills/iot-frontend-site-expansion`)
console.log('源仓库未修改；所有任务、构建和提交只能在该 fixture 中运行。')

function copySkill(repo) {
  const destination = resolve(repo, '.kiro/skills/iot-frontend-site-expansion')
  mkdirSync(dirname(destination), { recursive: true })
  cpSync(skillRoot, destination, { recursive: true })
}

function linkDependencies(repo) {
  const sourceModules = resolve(source, 'node_modules')
  const destinationModules = resolve(repo, 'node_modules')
  if (!existsSync(sourceModules)) {
    console.warn('WARN: 源仓库没有 node_modules；fixture 构建前需使用受信 registry 按 lockfile 准备依赖')
    return
  }
  symlinkSync(sourceModules, destinationModules, process.platform === 'win32' ? 'junction' : 'dir')
}

function setupDirtyWorkspace(repo) {
  const packagePath = resolve(repo, 'package.json')
  const packageJson = JSON.parse(readFileSync(packagePath, 'utf8'))
  packageJson.evalFixtureDirty = true
  writeFileSync(packagePath, `${JSON.stringify(packageJson, null, 2)}\n`)

  const envPath = resolve(repo, 'config/env/.env.test')
  const current = readFileSync(envPath, 'utf8')
  writeFileSync(envPath, `${current.endsWith('\n') ? current : `${current}\n`}# eval fixture staged change\n`)
  run('git', ['add', '--', 'config/env/.env.test'], repo)
}

function git(cwd, args) {
  const result = spawnSync('git', args, { cwd, encoding: 'utf8' })
  if (result.status !== 0) fail(result.stderr || `git ${args.join(' ')} 执行失败`)
  return result.stdout || ''
}

function run(command, args, cwd) {
  const result = spawnSync(command, args, { cwd, encoding: 'utf8', stdio: 'inherit' })
  if (result.status !== 0) fail(`${command} ${args.join(' ')} 执行失败`)
}

function fail(message) {
  console.error(`ERROR: ${message}`)
  process.exit(1)
}

function parseArgs(args) {
  const result = {}
  for (let index = 0; index < args.length; index += 1) {
    const arg = args[index]
    if (!arg.startsWith('--')) continue
    const separator = arg.indexOf('=')
    if (separator >= 0) result[arg.slice(2, separator)] = arg.slice(separator + 1)
    else if (args[index + 1] && !args[index + 1].startsWith('--')) {
      result[arg.slice(2)] = args[index + 1]
      index += 1
    } else result[arg.slice(2)] = 'true'
  }
  return result
}
