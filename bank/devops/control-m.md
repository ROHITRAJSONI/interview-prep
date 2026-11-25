# Control-M

## Q: How have you used Control-M to orchestrate batch jobs, and how do you handle job dependencies and failures?
### Solution
Control-M schedules and orchestrates enterprise batch: Spring Batch jobs, shell scripts, file transfers and database procedures across hosts. Jobs are organized into **folders** with calendars (business days, month-end, holiday calendars).

- **Dependencies:** **in/out conditions** (job A adds a condition when it finishes OK; job B waits for it), plus **file watchers** for "start when the upstream file lands".
- **Failure handling:** a job ends NOT OK on a non-zero exit code. Your code must return proper exit codes, which in Spring Batch means mapping `ExitStatus` to the process exit code. Configure automatic **reruns** (count and interval), **On-Do actions** (notify, set a condition, trigger a recovery job), and **SLA management** (alert if the critical path is going to miss its deadline, e.g. the regulatory submission window).
- Make jobs **restartable and idempotent**: Spring Batch's JobRepository resumes from the failed step/chunk.

## Q: Control-M vs Airflow (or AWS Step Functions): how do they compare?
### Solution
- **Control-M:** a commercial, enterprise-wide scheduler with a GUI. Strong at calendars, cross-platform (mainframe, Unix, Windows), SLAs, auditing and operations teams. Common in banks. Jobs-as-code via the Automation API (JSON).
- **Airflow:** open source, DAGs written as Python code, with a huge operator ecosystem. Data-engineering focused. You run and scale it yourself (or use MWAA).
- **Step Functions:** serverless AWS workflows with native service integrations. Best for event-driven, cloud-native orchestration and sagas.

Choose by where the workloads run and who operates them. Many firms run Control-M for legacy and enterprise batch, and Airflow/Step Functions for new cloud data pipelines.
