"""Catalog of practice topics, grouped by category.

Each topic id matches a question-bank file: bank/<category>/<topic_id>.md
"""

from dataclasses import dataclass


@dataclass(frozen=True)
class Topic:
    id: str
    name: str
    category: str


CATEGORIES = {
    "languages": "Languages & Frameworks",
    "aws": "AWS Cloud",
    "design": "Design & Concurrency",
    "data": "Data & Messaging",
    "devops": "DevOps & Tools",
}

_RAW = {
    "languages": [
        ("java", "Java (8 / 11 / 17)"),
        ("spring-boot", "Spring Boot"),
        ("spring-cloud", "Spring Cloud"),
        ("spring-ai", "Spring AI"),
        ("vertx", "Vert.x"),
        ("quarkus", "Quarkus"),
        ("javascript", "JavaScript"),
        ("groovy", "Groovy"),
    ],
    "aws": [
        ("ecs", "AWS ECS"),
        ("lambda", "AWS Lambda"),
        ("bedrock", "AWS Bedrock"),
        ("eventbridge", "AWS EventBridge"),
        ("sqs", "AWS SQS"),
        ("cloudwatch", "AWS CloudWatch"),
        ("secrets-manager", "AWS Secrets Manager"),
        ("appconfig", "AWS AppConfig / Config"),
        ("s3", "AWS S3"),
        ("parameter-store", "AWS SSM Parameter Store"),
        ("dynamodb", "DynamoDB"),
    ],
    "design": [
        ("microservices", "Microservices Architecture"),
        ("multithreading", "Multithreading & Concurrency"),
        ("design-patterns", "Design Patterns"),
        ("dependency-injection", "Dependency Injection (Dagger, Guice)"),
    ],
    "data": [
        ("kafka", "Apache Kafka"),
        ("rabbitmq", "RabbitMQ"),
        ("mysql", "MySQL"),
        ("oracle", "Oracle"),
        ("mongodb", "MongoDB"),
        ("documentdb", "Amazon DocumentDB"),
        ("couchbase", "Couchbase / CouchDB"),
    ],
    "devops": [
        ("maven", "Maven"),
        ("gradle", "Gradle"),
        ("git", "Git"),
        ("bitbucket", "Bitbucket"),
        ("jira-confluence", "Jira & Confluence"),
        ("control-m", "Control-M"),
        ("pentaho", "Pentaho"),
        ("cucumber", "Cucumber / BDD"),
    ],
}

TOPICS: dict[str, Topic] = {
    tid: Topic(tid, name, cat) for cat, items in _RAW.items() for tid, name in items
}


def by_category() -> dict[str, list[Topic]]:
    out: dict[str, list[Topic]] = {c: [] for c in CATEGORIES}
    for t in TOPICS.values():
        out[t.category].append(t)
    return out


def resolve(token: str) -> list[Topic]:
    """Turn a user token into topics: a topic id, a category id, a list index, or 'all'."""
    token = token.strip().lower()
    if not token:
        return []
    if token == "all":
        return list(TOPICS.values())
    if token in TOPICS:
        return [TOPICS[token]]
    if token in CATEGORIES:
        return by_category()[token]
    if token.isdigit():
        ordered = list(TOPICS.values())
        i = int(token) - 1
        if 0 <= i < len(ordered):
            return [ordered[i]]
    # loose match on name, e.g. "spring boot" or "sqs"
    matches = [t for t in TOPICS.values() if token in t.name.lower() or token in t.id]
    return matches
