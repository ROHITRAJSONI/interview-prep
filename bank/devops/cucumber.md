# Cucumber / BDD

## Q: How do you structure Cucumber tests so they stay maintainable?
### Solution
- Write features in **business language**, one behaviour per scenario. Use declarative steps ("Given a customer with a blocked card"), not UI-click scripts.
- Use `Background` for shared setup, `Scenario Outline` + `Examples` for data variations, and tags (`@smoke`, `@regression`, `@wip`) to select suites.
- Keep step definitions thin. They delegate to page objects / API clients / domain helpers, so wording changes don't break the logic.
- Share state between steps via **dependency injection** (cucumber-spring, or PicoContainer's per-scenario `World` object), not static fields, so scenarios can run in parallel.
- Make each scenario independent: create its own data and clean up afterwards.

## Q: How do you integrate Cucumber with Spring Boot and run it in CI?
### Solution
```java
@Suite
@IncludeEngines("cucumber")
@SelectClasspathResource("features")
@ConfigurationParameter(key = GLUE_PROPERTY_NAME, value = "com.acme.steps")
class RunCucumberTest {}

@CucumberContextConfiguration
@SpringBootTest(webEnvironment = RANDOM_PORT)
class CucumberSpringConfig {}
```
Use the JUnit Platform engine (cucumber-junit-platform-engine), one `@CucumberContextConfiguration` class, and **Testcontainers** for real DB/Kafka dependencies. In CI, run them with the failsafe plugin in the `verify` phase, publish the HTML/JSON reports, and enable parallel execution (`cucumber.execution.parallel.enabled=true`), which is only safe once state is per scenario.
