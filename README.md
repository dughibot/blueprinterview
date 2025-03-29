# Getting Started:
1. Clone this repository
2. Make sure you have Docker installed on your machine
3. From the root directory, run `docker compose up`
4. Go to http://localhost:8000 to access the screener

# Problem Description:
The goal for this project was to build a miniature version of a web app that could be used to help a clinician choose which standardized clinical assessments to assign to a patient. 
I wanted to build a frontend that could present the user with a basic survey with what are essentially likert style questions that then sent the user's answers to a backend API server that looked at those answers and returned a list of assessments to give. 
The backend API needed the ability to serve up the JSON describing a screener, as well as the ability to process the answers to the questions in that screener.

The next steps for a project like this would probably be to actually save the returned list somewhere, instead of returning it to the frontend. We'd then want to build a way for the clinician to access the results and approve the assessments to be given. Alternatively, we could let the frontend just give those assessments to the patient directly and immediately. It depends on how sure we are about the scoring for our diagnostic screener.


# How to Actually Deploy in Prod:
## Database:
My top choice for this would be to run Postgres on AWS Aurora.

## Frontend:
In AWS, my top choice would probably be on Elastic Beanstalk or Amplify. I don't have a strong frontend background, so I don't have as much background on this

## Backend:
We could do this a number of ways. One of the most modern would be to run it on an EKS cluster. With this being part of a larger service/infrastructure, that would likely be my top choice in AWS.
Another option would be to modify the code so that there is an obvious entrypoint for AWS lambda and then use that to handle our API requests. We could do that using a tool like Chalice or Zappa, or we could drop the flask framework so that the backend is no longer a webserver, but just handling the request information passed to it from API Gateway (or whatever we use for routing) and returning responses that way. The upside of this vs EKS is that lambda is serverless and handles your autoscaling for you, but you can run into issues with cold starts being slow and application size limits. Also, if you ever need a job to run for longer than 15 minutes, that's impossible on lambda. It should be fine for handling small endpoints, however. 
The most traditional AWS way would be to deploy this to EC2 instances wrapped in an autoscaling group behind a load balancer. If this is the only thing we're building, I would probably choose this, because Kubernetes is overkill. However, more likely, this API service can be its own little pod that just runs this container on a larger EKS cluster that runs all of our services.

## Networking/Routing:
First, we'd want to set up a hosted zone in route53 for our website. We could point it at API Gateway which would handle routing our calls to the right services within EKS or lambda or EC2, wherever we decide to host the code.
We might want to set up CDNs with Cloudfront as well, but that's probably unneccessary to begin with.

## Monitoring:
We definitely need to set up logging and alerting around this. I omitted pretty much all of that, because I decided getting it working and tackling some frontend was more important. I have very little actual frontend experience, so I knw building a webapp for this was going to take me some time to get working properly, at determined that monitoring and good logging could be handled later.
I'd probably want to set up something like sentry to error monitoring. We could just use cloudwatch logs and set up alerts and graphs based on those, but searching for logs in cloudwatch is terribly slow, so setting up an ELK stack for our logs would be advisable. We could also use a different hosted solution like Datadog or Splunk. Setting up Prometheus and Grafana for monitoring would be great too.

## Infrastructure management:
I'd use terraform to manage creation and modification to all of these hosted infrastructure solutions.

## Security:
We'd want to make sure all of our services and database are locked down within a VPC so that public access is limited.
Obviously having our database password tracked in git (and just set to "password") is bad, and we would not want to do that. Using AWS secrets manager or Vault are great ways to store our passwords. As long as I'm going all in on AWS, I'd choose that to keep things natively within the ecosystem.
On a totally different security note, we'd want to improve our CORS list instead of just allowing everything, we'd want to make sure to greenlist just our app(s).
Other than that, security is not my forte, and so I'm sure there are pieces that I'm missing, but I'm not sure about them.


# Things I left out that are not mentioned above:
## Tests
 I didn't write any tests. This was a small enough project that manual testing was easy enough to do, and I prioritized getting a working frontend over writing tests for the backend/writing tests at all. Ideally, we'd want a suite of unit tests to check that the API functions answers endpoint handled normal happy paths and error and edge cases. Some of those cases would be:
 ### In the answers endpoint:
- answers such that no assessments are recommended
- answers such that each assessment is recommended
- answers such that all assessments are recommended
- an invalid screener id
- missing answers to questions in the screener
- answers with invalid values
- answers to questions that don't exist
- if answers score in such a way that put the user on the border of needing a particular assessment
- answer such that one assessment is recommended due to multiple different reasons (check that the assessment is only in the API response once)
### The screener endpoint:
- getting a valid screener
- invalid screener id

Ideally these tests mock out postgres and an API client so that we're just testing the API controller. We should also have unit tests for the provider layer with postgres mocked out, and also integration and regression tests with everyting all together.

Pytest is a good framework for python testing. I'm not sure what I'd use for the frontend testing; I'm sure there are good frameworks for it though.

## Misc.
I'd probably want to put in some sort of tools for API contract management/creating documentation. Swagger is a very popular choice, but I have only dabbled a little with it.

I'd also want to use some sort of schema tool for API responses instead of just the API requests. Marshmallow is a popular tool in python for this; but I'd want to take some time to build a solution that allows us to follow DRY principles a little more easily.

I'd also want to move the mapping from domain scores -> assessment names into the database as well. That would allow us to add more assessments more easily.

The database schema should definitely also be changed a bit depending on how we want to possibly build new screeners. This is built such that answers belong to a specific section, but we may want to allow them to be re-used in different sections. The questions are allowed to be repeated in multiple different sections, but that could be undesirable, especially when we start building screeners with multiple sections. There's not currently a good way to prevent a single screener from asking the same question twice in different sections. That may be okay, but would mean modifying our answers to handle the idea of an answer to a question being scoped to a specific section.

I mainly used docker and docker compose as a tool to make getting this running locally very simple. While we'd probably want to use Docker containers to deploy code in EKS for sure, I didn't focus heavily on those containers, and so there are a lot of improvements to be made there. A super obvious problem with our current backend container, for example, is that it upgrades the database schema and tries to load data into it everytime you start the container with the default command. You'd never do that in prod. You want your db upgrades, data migrations, and code deploys to be separate. They can all be in one automated pipeline, but you don't want them to be all in one shell script that runs when a backend container starts up.

I also did not put any environment configurations in this. You need the code to be able to be run in different environments without them affecting each other. The database URI, especially, needs to be environment specific and should default to a dev or local version so that you only ever connect to the prod database when you really want to.