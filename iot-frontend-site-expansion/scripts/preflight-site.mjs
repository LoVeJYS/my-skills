import { existsSync, readFileSync, readdirSync } from 'node:fs'
import { resolve } from 'node:path'
import { spawnSync } from 'node:child_process'
const root = process.cwd()
const options = parseArgs(process.argv.slice(2))
const errors = []
const warnings = []
const mode = options.mode
const env = options.env
if (!['new', 'sso'].includes(mode)) errors.push('--mode 必须是 new 或 sso')
if (!env || !/^[a-z][a-z0-9-]*$/.test(env)) errors.push('--env 必须符合 [a-z][a-z0-9-]*')
if (!existsSync(resolve(root, 'package.json'))) errors.push('当前目录不是 iot-platform-web 仓库根目录')
const packageJson = readJson('package.json')
const statusEntries = getStatusEntries()
const stagedEntries = statusEntries.filter((entry) => entry.index !== ' ' && entry.index !== '?')
const targetPaths = getTargetPaths(mode, env)
const dirtyTargets = statusEntries.filter((entry) => targetPaths.includes(entry.path))
if (dirtyTargets.length > 0) errors.push(`目标文件在任务前已有改动: ${dirtyTargets.map((entry) => entry.path).join(', ')}`)
if (stagedEntries.length > 0) {
  warnings.push(`暂存区已有内容；可以继续调查和修改干净目标文件，但创建本次提交前必须处理: ${stagedEntries.map((entry) => entry.path).join(', ')}`)
}
if (mode === 'new' && env) validateNewMode()
if (mode === 'sso' && env) validateSsoMode()
const hooksPath = git(['config', '--get', 'core.hooksPath'], true).trim() || '.git/hooks'
const preCommitPath = resolve(root, hooksPath, 'pre-commit')
if (!existsSync(preCommitPath)) warnings.push(`当前没有实际 pre-commit hook: ${hooksPath}/pre-commit`)
for (const warning of warnings) console.warn(`WARN: ${warning}`)
if (errors.length > 0) {
  for (const error of errors) console.error(`ERROR: ${error}`)
  process.exit(1)
}
console.log(
  `预检通过: mode=${mode}, env=${env}, targets=${targetPaths.length}, staged=${stagedEntries.length}, preCommitHook=${existsSync(preCommitPath)}`,
)
function validateNewMode() {
  const cloudId = options['cloud-id']
  const gateway = options['middle-gateway']
  const displayName = options['display-name']
  const referenceEnv = options['reference-env']
  const targetFiles = parseCsv(options['target-files'])
  if (!/^\d+$/.test(cloudId || '')) errors.push('--cloud-id 必须是非负整数')
  if (!displayName || displayName.trim() === '') errors.push('--display-name 必须是正式站点名称')
  else if ([env, env.toUpperCase()].includes(displayName.trim())) errors.push('--display-name 不能使用 env 或其大写形式作为占位值')
  validateGatewayRoot(gateway)
  validateConfigSource('sso-url-source')
  validateConfigSource('gateway-config-source')
  if (!referenceEnv || !/^[a-z][a-z0-9-]*$/.test(referenceEnv)) errors.push('--reference-env 必填且必须是合法 env')
  else if (!existsSync(resolve(root, `config/env/.env.${referenceEnv}`))) errors.push(`参考环境不存在: config/env/.env.${referenceEnv}`)
  if (targetFiles.length === 0) errors.push('--target-files 必须包含调查后动态确认的目标文件列表')
  const envFile = `config/env/.env.${env}`
  const viteFile = `config/vite.config.${env}.ts`
  if (existsSync(resolve(root, envFile))) errors.push(`env 已存在: ${envFile}`)
  if (existsSync(resolve(root, viteFile))) errors.push(`Vite 配置已存在: ${viteFile}`)
  if (packageJson?.scripts?.[`build:${env}`]) errors.push(`构建入口已存在: build:${env}`)
  if (packageJson?.scripts?.[`checkInstallBuild:${env}`]) errors.push(`检查构建入口已存在: checkInstallBuild:${env}`)
  const requestSource = readText('src/apis/request/index.ts')
  if (hasObjectKey(requestSource, env)) errors.push(`请求映射中已存在 env: ${env}`)
  if (/^\d+$/.test(cloudId || '')) {
    const occupiedBy = findCloudIdOwners(cloudId)
    if (occupiedBy.length > 0) errors.push(`cloudId ${cloudId} 已被占用: ${occupiedBy.join(', ')}`)
  }
}
function validateSsoMode() {
  const envFile = `config/env/.env.${env}`
  const ssoKeys = parseSsoKeys(options['sso-keys'])
  if (!existsSync(resolve(root, envFile))) errors.push(`SSO 后补所需 env 不存在: ${envFile}`)
  if (!packageJson?.scripts?.[`build:${env}`]) errors.push(`SSO 后补所需构建入口不存在: build:${env}`)
  if (ssoKeys.length === 0) errors.push('--sso-keys 必须至少包含 VITE_SSO_CLIENTID 或 VITE_SSO_GETTOKEN')
}
function validateGatewayRoot(value) {
  if (!value) {
    errors.push('--middle-gateway 必填')
    return
  }
  try {
    const url = new URL(value)
    if (url.protocol !== 'https:') errors.push('--middle-gateway 必须使用 HTTPS')
    if (url.username || url.password) errors.push('--middle-gateway 不得包含用户名或密码')
    if (url.search || url.hash) errors.push('--middle-gateway 不得包含 query 或 hash')
    if (url.pathname !== '/' || value !== url.origin) errors.push('--middle-gateway 必须是无路径且无末尾 / 的 origin')
  } catch {
    errors.push('--middle-gateway 不是合法 URL')
  }
}
function validateConfigSource(optionName) {
  const value = options[optionName]
  if (!value || !/^(provided|reuse:[a-z][a-z0-9-]*)$/.test(value)) {
    errors.push(`--${optionName} 必须是 provided 或 reuse:<env>`)
  }
}
function findCloudIdOwners(cloudId) {
  const owners = []
  const envDir = resolve(root, 'config/env')
  if (existsSync(envDir)) {
    for (const name of readdirSync(envDir)) {
      if (!name.startsWith('.env.')) continue
      const content = readFileSync(resolve(envDir, name), 'utf8')
      const match = content.match(/^VITE_CLOUD_ID\s*=\s*["']?(\d+)/m)
      if (match?.[1] === cloudId) owners.push(`config/env/${name}`)
    }
  }
  const apiSource = readText('src/constants/api.ts')
  const keyPattern = new RegExp(`^\\s*${escapeRegex(cloudId)}\\s*:`, 'm')
  if (keyPattern.test(apiSource) && owners.length === 0) owners.push('src/constants/api.ts（孤立映射）')
  return owners
}
function getTargetPaths(currentMode, currentEnv) {
  if (!currentEnv) return []
  if (currentMode === 'sso') return [`config/env/.env.${currentEnv}`]
  const defaults = [
    `config/env/.env.${currentEnv}`,
    `config/vite.config.${currentEnv}.ts`,
    'package.json',
    'scripts/checkInstallBuild.cjs',
    'src/constants/api.ts',
    'src/apis/request/index.ts',
  ]
  return [...new Set([...defaults, ...parseCsv(options['target-files']).map(normalizePath)])]
}
function parseSsoKeys(value) {
  const allowed = new Set(['VITE_SSO_CLIENTID', 'VITE_SSO_GETTOKEN'])
  const keys = parseCsv(value)
  for (const key of keys) if (!allowed.has(key)) errors.push(`不支持的 SSO 键: ${key}`)
  return keys.filter((key) => allowed.has(key))
}
function parseCsv(value) {
  return (value || '')
    .split(',')
    .map((item) => item.trim())
    .filter(Boolean)
}
function getStatusEntries() {
  return git(['status', '--porcelain=v1', '--untracked-files=all'])
    .split(/\r?\n/)
    .filter(Boolean)
    .map((line) => ({ index: line[0], worktree: line[1], path: normalizeStatusPath(line.slice(3)) }))
}
function normalizeStatusPath(path) {
  const renameTarget = path.includes(' -> ') ? path.split(' -> ').at(-1) : path
  return normalizePath(renameTarget.replace(/^"|"$/g, ''))
}
function normalizePath(path) {
  return path.replaceAll('\\', '/').replace(/^\.\//, '')
}
function hasObjectKey(source, key) {
  const escaped = escapeRegex(key)
  return new RegExp(`^\\s*(?:['"]${escaped}['"]|${escaped})\\s*:`, 'm').test(source)
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
function git(args, allowFailure = false) {
  const result = spawnSync('git', args, { cwd: root, encoding: 'utf8' })
  if (result.status !== 0 && !allowFailure) {
    console.error(result.stderr || `git ${args.join(' ')} 执行失败`)
    process.exit(result.status || 1)
  }
  return result.stdout || ''
}
function readJson(path) {
  try {
    return JSON.parse(readText(path))
  } catch (error) {
    errors.push(`${path} 无法解析: ${error.message}`)
    return null
  }
}
function readText(path) {
  const fullPath = resolve(root, path)
  return existsSync(fullPath) ? readFileSync(fullPath, 'utf8') : ''
}
function escapeRegex(value) {
  return value.replace(/[.*+?^${}()|[\]\\]/g, '\\$&')
}
