# Devops & Process

## Best Practices

1. git hygiene: regular git commits and pushes and branches for experiments and bug fixes, delete or reuse branches locally and remotely when merged (everyone should delete old branches locally too)
2. style-guide with linting rules/config plus linters in your IDE and .git hooks to warn of linting failures
3. build pipeline, unittesting
4. merge requests for code that someone else may interact with and needs to understand
5. documentation of whatever manual QA testing is done
6. documentation of whatever ML cross validation testing is done (in a hyperparam table)
6. automating any of the manual QA tests that are easy to automate
7. measuring unittest code coverage automatically with badges on the `README.md`
8. README on every repository with instructions on how to install/deploy/run it
9. weekly meetings to triage and prioritize tasks/features/bugs
10. go-no-go meetings with all devs before all releases to anyone outside Viva-Translate employees
10. a list of manual q/a test protocols that everyone can work through before releases (each person on the team takes one test and does it). Everyone on the team needs to be familiar with the app enough to be able to do at least one manual qa test.

## Front-End

### Linting

https://www.npmjs.com/package/eslint-config-airbnb

```bash
npx install-peerdeps --dev eslint-config-airbnb
```

## Model Management Platforms

### Managed

1. MLflow
2. Metaflow
3. Neptune - end-to-end, minus logging
4. Azure Machine Learning
4. Domino Data Science Platform - end-to-end, minus logging
    Google Cloud AI Platform

5. Amazon SageMaker

### Self-hosted
