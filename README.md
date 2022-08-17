<img src="https://cdn.weareasterisk.com/product-assets/gavel/banner.png" width="450" height="150" alt="Gavel banner">

**Gavel** is a project expo judging system. Documentation can be found at the link below.

# [Gavel Documentation](https://gavel.weareasterisk.com/)

Freetail changes:
- Pipelines normally make a deployment to freetail-gavel, whose URL is https://judging.hacktx.com. To make a deployment for a custom Gavel instance, run a pipeline with the `GAVEL_ENV` variable set to `freetail-<your desired name>`. You can access the instance from Deployments > Environments on the GitLab project navigation pane.
- To create an environment, cancel the deploy job and trigger the create job. Once the create job is finished, trigger a deploy job so that files created in the CI/CD Pipeline are pushed to Elastic Beanstalk.
