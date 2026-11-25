# Groovy

## Q: Where have you used Groovy alongside Java, and what are its main differences?
### Solution
Typical uses: **Gradle build scripts**, **Jenkins pipelines** (Jenkinsfile), **Spock** tests, and scripting/glue.

Differences from Java: optional typing (`def`), dynamic dispatch by default, closures as first-class values, GStrings (`"Hi ${name}"`), safe navigation (`a?.b`), the Elvis operator (`x ?: 'default'`), native list/map literals, operator overloading, the `==` operator calls `equals()`, and the "Groovy truth" (empty collections and strings are false).

Senior point: dynamic typing hides errors until runtime. Use `@CompileStatic`/`@TypeChecked` in performance- or correctness-critical code. Also, a Jenkins pipeline runs CPS-transformed Groovy, so some normal Groovy (certain closures, non-serializable objects) fails there. That's what `@NonCPS` is for.

## Q: Why use Spock over JUnit for Java code?
### Solution
Spock gives readable BDD-style blocks (`given/when/then`), built-in mocking (`1 * repo.save(_)`), and **data-driven tests** with `where:` tables. When an assertion fails, power assertions show the value of every sub-expression.

```groovy
def "fee is #fee for amount #amount"() {
    expect:
    calculator.fee(amount) == fee
    where:
    amount | fee
    100    | 1.0
    10000  | 50.0
}
```
Trade-offs: the team has to learn Groovy, IDE refactoring is weaker than for Java, and with JUnit 5 `@ParameterizedTest` plus AssertJ the gap is smaller.
