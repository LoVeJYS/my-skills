import { existsSync, readFileSync } from 'node:fs'
import { resolve } from 'node:path'
import { loadEnv } from 'vite'

const root = process.cwd()
const options = parseArgs(process.argv.slice(2))
const errors = []
const warnings = []
let checks = 0

const mode = options.mode
const env = options.env
const cloudId = options['cloud-id']
const displayName = options['display-name']
const middleGateway = options['middle-gateway']
const referenceEnv = options['reference-env']
const envPascal = toPascalCase(env || '')

check(['new', 'sso'].includes(mode), '--mode 必须是 new 或 sso')
check(Boolean(env) && /^[a-z][a-z0-9-]*$/.test(env), '--env 必须符合 [a-z][a-z0-9-]*')
check(existsSync(resolve(root, 'package.json')), '当前目录必须是仓库根目录')

if (errors.length === 0) {
  verifyEnvironmentAndBuild()
  if (mode === 'new') verifyNewSite()
  if (mode === 'sso') verifySsoContract()
}

for (const warning of warnings) console.warn(`WARN: ${warning}`)
if (errors.length > 0) {
  for (const error of errors) console.error(`ERROR: ${error}`)
  console.error(`站点验证失败: ${errors.length} 项错误，${checks} 项检查`)
  process.exit(1)
}
console.log(`站点验证通过: mode=${mode}, env=${env}, checks=${checks}`)

function verifyEnvironmentAndBuild() {
  const envPath = `config/env/.env.${env}`
  const vitePath = `config/vite.config.${env}.ts`
  check(existsSync(resolve(root, envPath)), `${envPath} 不存在`)
  check(existsSync(resolve(root, vitePath)), `${vitePath} 不存在`)
  if (!existsSync(resolve(root, envPath))) return

  const rawEnv = readText(envPath)
  const parsedEnv = loadEnv(env, resolve(root, 'config/env'), '')
  verifyGetTokenQuoting(rawEnv, parsedEnv)

  if (!parsedEnv.VITE_SSO_CLIENTID) warnings.push('VITE_SSO_CLIENTID 为空，SSO 登录尚不可用')
  if (!parsedEnv.VITE_SSO_GETTOKEN) warnings.push('VITE_SSO_GETTOKEN 为空，token 回调、登出或环境识别可能不可用')

  if (mode === 'new') {
    check(parsedEnv.VITE_CLOUD_ID === String(cloudId), `VITE_CLOUD_ID 应为 ${cloudId}`)
    check(Boolean(parsedEnv.VITE_SSO_URL), 'VITE_SSO_URL 不能为空')
    check(Boolean(parsedEnv.VITE_GATEWAY_SECRET_KEY), 'VITE_GATEWAY_SECRET_KEY 不能为空')
    check(Boolean(parsedEnv.VITE_GATEWAY_APP_KEY), 'VITE_GATEWAY_APP_KEY 不能为空')
  }

  const packageJson = parseJson('package.json')
  const buildCommand = packageJson?.scripts?.[`build:${env}`] || ''
  check(Boolean(buildCommand), `缺少 build:${env}`)
  check(buildCommand.includes(`--config ./config/vite.config.${env}.ts`), `build:${env} 未指向正确 Vite config`)
  check(new RegExp(`--mode\\s+${escapeRegex(env)}(?:\\s|$)`).test(buildCommand), `build:${env} 未加载正确 mode`)

  const viteSource = readText(vitePath)
  check(new RegExp(`mode:\\s*['"]${escapeRegex(env)}['"]`).test(viteSource), `${vitePath} 固定 mode 不正确`)
  check(/envDir:\s*['"]\.\/config\/env['"]/.test(viteSource), `${vitePath} 缺少正确 envDir`)

  if (mode === 'new') {
    const checkBuildCommand = packageJson?.scripts?.[`checkInstallBuild:${env}`] || ''
    check(checkBuildCommand === `node ./scripts/checkInstallBuild.cjs --env=${env}`, `checkInstallBuild:${env} 命令不正确`)
    const checkBuildSource = readText('scripts/checkInstallBuild.cjs')
    const escapedEnv = escapeRegex(env)
    const envKeyPattern = env.includes('-') ? `['"]${escapedEnv}['"]` : `(?:['"]${escapedEnv}['"]|${escapedEnv})`
    const mappingPattern = new RegExp(`${envKeyPattern}\\s*:\\s*['"]npm run build:${escapedEnv}['"]`)
    check(mappingPattern.test(checkBuildSource), `checkInstallBuild.cjs 缺少 ${env} 映射`)
  }
}

function verifyNewSite() {
  check(/^\d+$/.test(cloudId || ''), '--cloud-id 必须是非负整数')
  check(Boolean(displayName), '--display-name 必填')
  if (displayName) check(![env, env.toUpperCase()].includes(displayName.trim()), '--display-name 不能使用 env 占位值')
  check(validateGatewayRoot(middleGateway), '--middle-gateway 必须是无凭据、无路径、无 query/hash 的 HTTPS origin')
  check(Boolean(referenceEnv) && /^[a-z][a-z0-9-]*$/.test(referenceEnv), '--reference-env 必填')
  check(validateConfigSource(options['sso-url-source']), '--sso-url-source 必须是 provided 或 reuse:<env>')
  check(validateConfigSource(options['gateway-config-source']), '--gateway-config-source 必须是 provided 或 reuse:<env>')

  const templateSyncPage = options['template-sync-page']
  const selfPages = parseCsv(options['self-pages'])
  check(Boolean(templateSyncPage), '--template-sync-page 必填')
  check(selfPages.length > 0, '--self-pages 必须包含动态发现的自描述页面')

  verifyApiServices()
  verifyDirectMap()
  if (templateSyncPage) verifyTemplateSync(templateSyncPage)
  if (selfPages.length > 0) verifySelfDescribedPages(selfPages)
}

function verifySsoContract() {
  const parsedEnv = loadEnv(env, resolve(root, 'config/env'), '')
  const selected = parseSsoKeys(options['sso-keys'])
  check(selected.length > 0, '--sso-keys 必须至少包含一个 SSO 键')
  const allowClear = options['allow-clear'] === 'true'
  const contracts = [
    { key: 'VITE_SSO_CLIENTID', expected: 'expected-client-id', preserved: 'preserved-client-id' },
    { key: 'VITE_SSO_GETTOKEN', expected: 'expected-gettoken', preserved: 'preserved-gettoken' },
  ]

  for (const contract of contracts) {
    const isSelected = selected.includes(contract.key)
    const optionName = isSelected ? contract.expected : contract.preserved
    const provided = hasOption(optionName)
    check(provided, `--${optionName} 必须提供，以证明 ${contract.key} ${isSelected ? '符合用户输入' : '保持不变'}`)
    if (!provided) continue
    const expectedValue = options[optionName]
    if (isSelected && expectedValue === '' && !allowClear) check(false, `清空 ${contract.key} 必须显式传入 --allow-clear=true`)
    check((parsedEnv[contract.key] || '') === expectedValue, `${contract.key} 与 ${isSelected ? '期望值' : '修改前保留值'}不一致`)
  }
}

function verifyGetTokenQuoting(rawEnv, parsedEnv) {
  const rawGetToken = rawEnv.match(/^VITE_SSO_GETTOKEN=(.*)$/m)?.[1] ?? ''
  if (!rawGetToken.includes('#')) return
  const quoted = rawGetToken.startsWith('"') && rawGetToken.endsWith('"')
  check(quoted, 'VITE_SSO_GETTOKEN 包含 # 时必须使用双引号')
  if (quoted) check(parsedEnv.VITE_SSO_GETTOKEN === rawGetToken.slice(1, -1), 'Vite 解析后的 GETTOKEN 与完整双引号值不一致')
}

function verifyApiServices() {
  const source = readText('src/constants/api.ts')
  const typeBody = source.match(/interface\s+ConstantsType\s*\{([\s\S]*?)\n\}/)?.[1] || ''
  const groups = [...typeBody.matchAll(/^\s*(\w+):\s*Record<string, string>/gm)].map((match) => match[1])
  check(groups.length > 0, '未能从 ConstantsType 动态发现服务组')

  const referenceCloudId = loadEnv(referenceEnv, resolve(root, 'config/env'), '').VITE_CLOUD_ID
  check(Boolean(referenceCloudId), `参考环境 ${referenceEnv} 缺少 VITE_CLOUD_ID`)

  for (const group of groups) {
    const block = extractPropertyBlock(source, group)
    if (!block) {
      check(false, `无法解析服务组 ${group}`)
      continue
    }
    const existingIds = [...block.matchAll(/^\s*(\d+)\s*:/gm)].map((match) => match[1])
    const supportsProduction = existingIds.some((id) => !['0', '4', '8'].includes(id))
    const value = getServiceValue(block, cloudId)

    if (supportsProduction) {
      check(Boolean(value), `生产服务组 ${group} 缺少 cloudId ${cloudId}`)
      if (value && middleGateway) {
        const newUrl = safeUrl(value)
        check(Boolean(newUrl) && newUrl.origin === middleGateway, `${group}[${cloudId}] 未使用指定中台 origin`)
        const referenceValue = getServiceValue(block, referenceCloudId)
        const referenceUrl = safeUrl(referenceValue)
        check(Boolean(referenceUrl), `参考环境 ${referenceEnv} 在服务组 ${group} 中缺少可解析 URL`)
        if (newUrl && referenceUrl) check(newUrl.pathname === referenceUrl.pathname, `${group}[${cloudId}] 的服务路径后缀与 ${referenceEnv} 不一致`)
      }
    } else {
      check(!value, `dev/test-only 服务组 ${group} 不应包含 cloudId ${cloudId}`)
    }
  }
}

function verifyDirectMap() {
  const source = readText('src/apis/request/index.ts')
  const block = extractNamedObject(source, 'protocolSyncSiteCloudIdMap')
  check(Boolean(block), '未找到 protocolSyncSiteCloudIdMap；请按真实调用链确认是否仍需要该映射')
  if (!block) return
  const key = escapeRegex(env)
  const valuePattern = new RegExp(`^\\s*(?:['"]${key}['"]|${key})\\s*:\\s*['"]${escapeRegex(cloudId)}['"]`, 'm')
  check(valuePattern.test(block), `protocolSyncSiteCloudIdMap 缺少 ${env} -> ${cloudId}`)
  if (env.includes('-')) check(new RegExp(`^\\s*['"]${key}['"]\\s*:`, 'm').test(block), `带连字符 env ${env} 必须使用字符串对象键`)
}

function verifyTemplateSync(path) {
  const page = readText(path)
  const types = readText('src/views/template-sync/constant.ts')
  const statusField = `sync${envPascal}`
  check(Boolean(page), `${path} 不存在`)
  check(hasEnvOption(page, env), `${path} 缺少 env option: ${env}`)
  check(page.includes(displayName), `${path} 缺少正式展示名: ${displayName}`)
  check(countOccurrences(page, `row.${statusField} === 0`) >= 2, `${path} 的编辑和删除条件未分别包含 ${statusField}`)

  for (const suffix of ['', 'Time', 'UserNo']) {
    const field = `${statusField}${suffix}`
    check(new RegExp(`prop:\\s*['"]${escapeRegex(field)}['"]`).test(page), `${path} 缺少 ${field} 列`)
    check(new RegExp(`\\b${escapeRegex(field)}\\s*:`).test(types), `Task 类型缺少 ${field}`)
  }

  const propIndex = page.search(new RegExp(`prop:\\s*['"]${escapeRegex(statusField)}['"]`))
  if (propIndex >= 0)
    check(page.slice(propIndex, propIndex + 700).includes(`row.${statusField} === 2`), `${statusField} formatter 没有读取本列的部分同步状态`)
  check(/site\s*===\s*['"]eu['"]/.test(page), `${path} 缺少既有 EU 文件分支`)
  if (env !== 'eu') check(!new RegExp(`site\\s*===\\s*['"]${escapeRegex(env)}['"]`).test(page), `${env} 不应复制 EU-only 文件分支`)
}

function verifySelfDescribedPages(pages) {
  const field = `sync${envPascal}`
  for (const path of pages) {
    const source = readText(path)
    check(Boolean(source), `${path} 不存在`)
    check(hasEnvOption(source, env), `${path} 缺少 env option: ${env}`)
    check(source.includes(displayName), `${path} 缺少正式展示名: ${displayName}`)
    check(countOccurrences(source, `row.${field}`) >= 2, `${path} 未同时覆盖未同步条件和汇总状态 ${field}`)
    check(/site\s*===\s*['"]eu['"]/.test(source), `${path} 缺少既有 EU 文件分支`)
    if (env !== 'eu') check(!new RegExp(`site\\s*===\\s*['"]${escapeRegex(env)}['"]`).test(source), `${path} 不应为 ${env} 复制文件分支`)
  }
}

function validateGatewayRoot(value) {
  if (!value) return false
  const url = safeUrl(value)
  return (
    Boolean(url) &&
    url.protocol === 'https:' &&
    !url.username &&
    !url.password &&
    !url.search &&
    !url.hash &&
    url.pathname === '/' &&
    value === url.origin
  )
}

function validateConfigSource(value) {
  return /^(provided|reuse:[a-z][a-z0-9-]*)$/.test(value || '')
}

function getServiceValue(block, id) {
  if (!id) return ''
  return block.match(new RegExp(`^\\s*${escapeRegex(String(id))}\\s*:\\s*['"]([^'"]+)['"]`, 'm'))?.[1] || ''
}

function safeUrl(value) {
  try {
    return value ? new URL(value) : null
  } catch {
    return null
  }
}

function parseSsoKeys(value) {
  const allowed = new Set(['VITE_SSO_CLIENTID', 'VITE_SSO_GETTOKEN'])
  const keys = parseCsv(value)
  for (const key of keys) check(allowed.has(key), `不支持的 SSO 键: ${key}`)
  return keys.filter((key) => allowed.has(key))
}

function hasOption(name) {
  return Object.prototype.hasOwnProperty.call(options, name)
}

function countOccurrences(source, value) {
  return source.split(value).length - 1
}

function hasEnvOption(source, value) {
  const escaped = escapeRegex(value)
  return new RegExp(`(?:value\\s*=\\s*['"]${escaped}['"]|value\\s*:\\s*['"]${escaped}['"])`).test(source)
}

function extractPropertyBlock(source, property) {
  const match = new RegExp(`\\b${escapeRegex(property)}\\s*:\\s*\\{`).exec(source)
  return match ? extractBalancedBlock(source, source.indexOf('{', match.index)) : ''
}

function extractNamedObject(source, name) {
  const match = new RegExp(`\\b${escapeRegex(name)}\\b[^=]*=\\s*\\{`).exec(source)
  return match ? extractBalancedBlock(source, source.indexOf('{', match.index)) : ''
}

function extractBalancedBlock(source, openingIndex) {
  let depth = 0
  for (let index = openingIndex; index < source.length; index += 1) {
    if (source[index] === '{') depth += 1
    if (source[index] === '}') {
      depth -= 1
      if (depth === 0) return source.slice(openingIndex + 1, index)
    }
  }
  return ''
}

function check(condition, message) {
  checks += 1
  if (!condition) errors.push(message)
}

function parseJson(path) {
  try {
    return JSON.parse(readText(path))
  } catch (error) {
    check(false, `${path} 无法解析: ${error.message}`)
    return null
  }
}

function readText(path) {
  const fullPath = resolve(root, path)
  return existsSync(fullPath) ? readFileSync(fullPath, 'utf8') : ''
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

function parseCsv(value) {
  return (value || '')
    .split(',')
    .map((item) => item.trim())
    .filter(Boolean)
}

function toPascalCase(value) {
  return value
    .split('-')
    .filter(Boolean)
    .map((part) => part.charAt(0).toUpperCase() + part.slice(1))
    .join('')
}

function escapeRegex(value) {
  return value.replace(/[.*+?^${}()|[\]\\]/g, '\\$&')
}
