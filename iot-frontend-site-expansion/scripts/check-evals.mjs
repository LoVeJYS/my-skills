import { existsSync, readFileSync } from 'node:fs'
import { dirname, resolve } from 'node:path'
import { fileURLToPath } from 'node:url'
const scriptDir = dirname(fileURLToPath(import.meta.url))
const skillRoot = resolve(scriptDir, '..')
const skillName = readFileSync(resolve(skillRoot, 'SKILL.md'), 'utf8')
  .match(/^name:\s*(.+)$/m)?.[1]
  ?.trim()
const errors = []
const evals = readJson(resolve(skillRoot, 'evals/evals.json'))
if (evals?.skill_name !== skillName) errors.push('evals.json 的 skill_name 与 SKILL.md name 不一致')
if (!Array.isArray(evals?.evals) || evals.evals.length === 0) errors.push('evals.json 必须包含非空 evals 数组')
const ids = new Set()
for (const item of evals?.evals || []) {
  const prefix = `eval ${item.id ?? 'unknown'}`
  if (!Number.isInteger(item.id)) errors.push(`${prefix}: id 必须是整数`)
  if (ids.has(item.id)) errors.push(`${prefix}: id 重复`)
  ids.add(item.id)
  if (typeof item.prompt !== 'string' || !item.prompt.includes(skillName)) errors.push(`${prefix}: 功能 prompt 必须明确点名 ${skillName}`)
  if (typeof item.expected_output !== 'string' || item.expected_output.trim() === '') errors.push(`${prefix}: expected_output 不能为空`)
  if (!Array.isArray(item.expectations) || item.expectations.length === 0) errors.push(`${prefix}: expectations 必须是非空数组`)
  if (!Array.isArray(item.assertions) || item.assertions.length === 0) errors.push(`${prefix}: assertions 必须是非空数组`)
  if (JSON.stringify(item.expectations) !== JSON.stringify(item.assertions))
    errors.push(`${prefix}: expectations 与 assertions 必须完全一致，以兼容当前 schema 和 grader`)
  if (!Array.isArray(item.files)) errors.push(`${prefix}: files 必须是数组`)
  for (const assertion of item.assertions || []) {
    if (typeof assertion !== 'string' || assertion.trim() === '') errors.push(`${prefix}: assertion 必须是非空字符串`)
  }
  for (const file of item.files || []) {
    if (!existsSync(resolve(skillRoot, file))) errors.push(`${prefix}: 输入文件不存在: ${file}`)
  }
}
const triggerEvals = readJson(resolve(skillRoot, 'evals/trigger-evals.json'))
if (!Array.isArray(triggerEvals) || triggerEvals.length < 8) errors.push('trigger-evals.json 至少需要 8 条样本')
const positive = (triggerEvals || []).filter((item) => item.should_trigger === true)
const negative = (triggerEvals || []).filter((item) => item.should_trigger === false)
if (positive.length === 0 || negative.length === 0) errors.push('trigger eval 必须同时包含应触发和不应触发样本')
for (const [index, item] of (triggerEvals || []).entries()) {
  if (typeof item.query !== 'string' || item.query.trim() === '') errors.push(`trigger ${index}: query 不能为空`)
  if (typeof item.should_trigger !== 'boolean') errors.push(`trigger ${index}: should_trigger 必须是 boolean`)
  if (item.should_trigger && !item.query.includes(skillName)) errors.push(`trigger ${index}: 显式触发正例必须点名 ${skillName}`)
}
if (errors.length > 0) {
  for (const error of errors) console.error(`ERROR: ${error}`)
  process.exit(1)
}
console.log(`Eval 校验通过: ${evals.evals.length} 条功能 eval，${triggerEvals.length} 条 trigger eval，双字段兼容`)
function readJson(path) {
  try {
    return JSON.parse(readFileSync(path, 'utf8'))
  } catch (error) {
    errors.push(`${path} 无法解析: ${error.message}`)
    return null
  }
}
