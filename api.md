为了在生产环境中仅允许内部人员访问 API，你需要在多层面引入访问控制和网络隔离措施。以下是推荐的做法：

---

## ✅ 1. 使用反向代理 (推荐)

在 `Nginx`、`Traefik`、`HAProxy` 等反向代理中配置仅允许可信 IP 访问 `/api` 路径：

```nginx
server {
  listen 80;
  server_name api.example.com;

  location / {
    proxy_pass http://127.0.0.1:8000;
    # 允许内部 IP 访问
    allow 10.0.0.0/8;
    allow 192.168.0.0/16;
    deny all;
  }
}
```

对于公开的接口路径，可以单独配置无需限制访问 ([reddit.com][1], [fastapi.tiangolo.com][2])。

🏅 **优点**：高效、借助成熟的代理层配置，不改动应用代码。

---

## ✅ 2. 在应用层做 IP 白名单

如果你并不通过代理做控制，还可以在 FastAPI 中写中间件拦截：

```python
from fastapi import FastAPI, Request, status
from fastapi.responses import JSONResponse

WHITELIST = ["10.0.0.5", "192.168.1.100"]

app = FastAPI()

@app.middleware("http")
async def ip_whitelist(request: Request, call_next):
    client_ip = request.client.host
    if client_ip not in WHITELIST:
        return JSONResponse(status_code=status.HTTP_403_FORBIDDEN, content={"detail": f"{client_ip} not allowed"})
    return await call_next(request)
```

若部署在代理后，别忘了使用 `ProxyHeadersMiddleware` 或从 `X-Forwarded-For` 中获取真实 IP ([stackoverflow.com][3])。

📌 **缺点**：代码维护增加，性能略有影响。

---

## ✅ 3. 结合工具库 — `FastAPI Guard`

如果你还需要防暴力攻击、黑名单、地理IP控制等，推荐使用社区安全中间件：

* 支持 IP 白名单/黑名单、速率限制、自动封禁
* 集成 Cloud IP 检测、Geolocation、日志等 ([reddit.com][4])

```python
from fastapi import FastAPI
from fastapi_guard import FastAPIGuard

app = FastAPI()
guard = FastAPIGuard()
guard.init_app(app)
# 配置策略...
```

---

## ✅ 4. 额外安全加固策略

| 场景      | 做法                               |   |
| ------- | -------------------------------- | - |
| HTTPS   | 使用 TLS 证书并通过代理终端接收               |   |
| 身份认证    | 为每个内部用户使用 JWT/OAuth2 验证          |   |
| 速率限制    | 使用 `fastapi-limiter` 或代理层限制请求频率  |   |
| 防火墙/安全组 | 同时配置云服务的网络策略屏蔽外部访问               |   |

---

## 🧩 综合推荐做法（生产）

1. **前端代理层控制入口路径访问**。通过 `Nginx` 或云 LB 限制只有内部 IP 能访问 `/api/v1/*`。
2. **在应用层加 IP 白名单中间件**，作为“最后一道校验”。
3. **根据需求启用安全中间件**，如 `FastAPI Guard` 做防暴力、黑名单等。
4. **确保 HTTPS + 身份认证 + 速率限制** 同时上线。

---

## 小结

* ✅ **反向代理+网络策略**是最优先和高效的方式。
* ✅ **应用层中间件**提供二次保护。
* ✅ 借助现成安全库，更快覆盖复杂需求。
* ✅ 其他措施（HTTPS、认证、限流、安全组）不应缺失。

如果你提供更多背景（如是否部署云环境、是否有公用网关），我可以帮你给出更符合你架构的具体配置建议！

[1]: https://www.reddit.com/r/FastAPI/comments/172mz4o/how_would_you_control_how_users_can_access_your/?utm_source=chatgpt.com "How would you control how users can access your API? (Credential ..."
[2]: https://fastapi.tiangolo.com/deployment/concepts/?utm_source=chatgpt.com "Deployments Concepts - FastAPI"
[3]: https://stackoverflow.com/questions/66867814/fastapi-how-to-allow-endpoint-access-for-specific-ip-only?utm_source=chatgpt.com "FastAPI how to allow endpoint access for specific IP only?"
[4]: https://www.reddit.com/r/Python/comments/1ilhbkk/fastapi_guard_a_fastapi_extension_to_secure_your/?utm_source=chatgpt.com "FastAPI Guard - A FastAPI extension to secure your APIs : r/Python"