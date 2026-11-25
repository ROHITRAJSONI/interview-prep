# AWS SSM Parameter Store

## Q: How do you load Parameter Store values into a Spring Boot app, and what about throttling?
### Solution
Use `spring-cloud-aws-starter-parameter-store` with `spring.config.import=aws-parameterstore:/myapp/prod/`. Parameters under the path become properties (`/myapp/prod/db.url` → `db.url`). `SecureString` values are decrypted with KMS; the task role needs `ssm:GetParametersByPath` plus `kms:Decrypt`.

Throttling: the standard throughput limit is low (about 40 TPS by default). Read **once at startup** with `GetParametersByPath` (batched), never per request. Enable **higher throughput** if needed, cache with a refresh interval, or use the Parameters and Secrets Lambda extension in Lambda.

## Q: Standard vs Advanced parameters?
### Solution
- **Standard:** free, up to 4 KB values, 10,000 parameters per account/region, no policies.
- **Advanced:** charged per parameter, up to 8 KB, 100,000 parameters, and **parameter policies** (expiration, notifications like "notify 15 days before expiry", no-change notifications). Can be shared across accounts via RAM.

Organize by hierarchy (`/{app}/{env}/{key}`) and write IAM policies on path prefixes, so each service can only read its own tree.
