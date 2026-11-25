# AWS ECS

## Q: Fargate vs EC2 launch type: how do you choose, and how does a rolling deployment work?
### Solution
**Fargate:** no instances to manage, you pay per task vCPU/memory, and isolation is per task. It's the default choice for most microservices. **EC2:** cheaper at steady high utilization (Reserved/Spot instances), and needed for GPUs, daemon tasks, special kernels, or very large tasks. You manage the AMIs, patching and cluster capacity providers.

**Rolling deploy:** you register a new task definition revision and update the service. `minimumHealthyPercent`/`maximumPercent` control how many old and new tasks run at once. New tasks must pass the **ALB target group health check** before old ones are drained (deregistration delay). Enable the **deployment circuit breaker with rollback** so a bad image automatically reverts. For blue/green with traffic shifting and a test listener, use the CodeDeploy deployment controller.

## Q: Task role vs execution role in ECS. What's the difference?
### Solution
- **Execution role:** used by the ECS agent to *start* the task: pull the image from ECR, write logs to CloudWatch, fetch secrets referenced in the task definition (`secrets` from Secrets Manager / SSM).
- **Task role:** assumed by *your application code* at runtime. The SDK gets credentials from the container credentials endpoint and uses them to call S3, DynamoDB, SQS, etc.

A common bug: you give S3 permissions to the execution role, and the app still gets AccessDenied. Least privilege means one task role per service, scoped to its own resources.
