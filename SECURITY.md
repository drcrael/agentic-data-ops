# Security model

The default execution mode has no inference and no network side effects. Workbook content is never executable control input. Trusted administrators configure providers and rules; attributed humans supply resolutions. LLM output has no tool-execution capability.

Local-only checks occur at gateway preflight and at the HTTP provider boundary. Only literal loopback addresses count as local. Redirects and inherited HTTP proxies are disabled. Raw remote context requires an explicit separate grant; otherwise only allowlisted metadata is built. Input and response size limits are enforced.

API keys come from named environment variables at request time. Do not put secrets in model names, field names, YAML metadata or provider URLs. Credentials/query strings in provider URLs are rejected. Reports are sensitive operational artifacts even when they contain no raw rows.

Use trusted model servers. A loopback endpoint is a transport property, not proof of the server's internals. For stronger isolation, deploy with an OS/network egress deny policy and filesystem access controls. Configuration and resolution files are administrative interfaces and must not come from untrusted workbook content.

Report security issues privately to the repository owner through an available private GitHub contact/security-reporting channel. Do not include real datasets, credentials or sensitive findings in public issues.
