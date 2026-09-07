# SSO 与客户端配置安全

## Vite 暴露边界

所有 `VITE_*` 变量都应按客户端可见配置处理，因为它们可能被写入浏览器 bundle。变量名包含 `SECRET` 不会使它成为真正秘密。

因此：

- 不在最终回复、日志、eval 结果或 commit message 中输出 Gateway key 原值；
- 不默认跨区域复制 `VITE_GATEWAY_SECRET_KEY` 或 `VITE_GATEWAY_APP_KEY`；
- 只有用户提供值或明确授权从指定参考环境复用时才写入；
- 如果 `VITE_GATEWAY_SECRET_KEY` 实际具备服务端密钥权限，应停止前端扩散，建议迁移签名到服务端并轮换已有值；
- 如果它只是公开 client key，应由项目明确记录其非秘密性质，避免误导。

本 Skill 不擅自进行后端迁移，也不猜测替代值。

## dotenv 中的 `#`

未加引号的 `#` 可能被 dotenv 当作注释：

```dotenv
VITE_SSO_GETTOKEN=https://example.com/#/getLoginToken
```

应写成：

```dotenv
VITE_SSO_GETTOKEN="https://example.com/#/getLoginToken"
```

验证不能只依赖 build 成功。应通过 Vite `loadEnv` 或等价解析器检查最终值未截断，同时避免打印完整配置值。

## SSO 空值影响

`VITE_SSO_CLIENTID` 和 `VITE_SSO_GETTOKEN` 可以在新增站点阶段暂时为空，但交付必须明确：

- 构建通过不代表登录可用；
- 登录跳转、token 中转页和登出可能不可用；
- 依赖 GETTOKEN 域名推断环境的功能可能 fallback 或判断失败。

只提示真正为空的键。后补时只改用户提供的键，不覆盖另一个已有值。

## 值处理

- SSO client ID 通常不是秘密，但仍避免无必要地回显完整值。
- GETTOKEN 是回调 URL，可以在用户明确提供时写入；包含 `#` 时必须加双引号。
- Gateway key 在报告中只显示“已配置/未配置/来源已授权”，不显示内容。
