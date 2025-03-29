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

# What I built
## Database
I chose to store the questions and screener data in Postgres. A large part of this decision was made due to my familiarity with postgres right now, which meant that it would be easy to get going. However, I think it's a reasonable choice for this system to store at least the screener data. For the screener itself, since we're likely not going to modify the shape of that frequently, the highly structured nature of SQL isn't a huge drawback, and gaining ACID compliant transactions is nice. Some NoSQL databases also offer that, but they tend to try to be more available than consistent, where relational databases tend to try to be more consistent. 

We could store answers there too, but we'd have to handle a lot more data as this gets used more and use data partitioning to horizontally scale it. Access patterns would decide how we would need to partition the data. My first guess would be that we'd want to do it by user, so all of a single user's answers are on the same partition. However, if we're never retrieving a specific users answers, and are usually trying to get things like "What was the average answer to this question," we'd want to be partitioning it differently. It might be better to store answers somewhere like DynamoDB, where availability is of a higher concern.

## Backend
I used the flask framework to build an API server in python. I've built apps with Python in flask before and figured it would be a great way to get started and build it quickly. I built a controller layer to handle the API endpoints, a provider layer to help abstract away database choices, and a resource layer to actually deal with the database directly. I used flask-sqlalchemy in order to easily handle the SQLAlchemy sessions with flask applicaton context. I used flask-cors to handle our CORS list (even though it's actually just allowing everything right now), and flask-migrate to do our database schema migrations. And I chose marshmallow as an input/API request data validation tool.

## Frontend
I used Parcel to build a React based web app in typescript. I don't have a lot of frontend experience, so using a tool like parcel that has great documentation and guides for building a react app was very helpful for me. I evaluated it briefly vs Vite and Rsbuild, and found Parcel to seem the easiest to get started with and found the documentation the clearest. I didn't feel that I needed the speed of Vite or Rsbuild. Again, since I don't have a ton of experience and figured that custom behavior and looks was not super important, I searched for a library to create the actual survey component and found SurveyJS to be very well documented and full featured. So all I really needed to do was put together an app that could call the backend endpoints and convert the json into the shape that SurveyJS needed.

## API Contract
`GET /screener/<screener-id>`
This endpoint returns the json for the screener. The JSON returned looks like:
<details>
  <summary>Example JSON</summary>

```{
  "id": "abcd-123",
  "name": "BPDS",
  "disorder": "Cross-Cutting",
  "content": {
    "sections": [
      {
        "type": "standard",
        "title": "During the past TWO (2) WEEKS, how much (or how often) have you been bothered by the following problems?",
        "answers": [
          {
            "title": "Not at all",
            "value": 0
          },
          {
            "title": "Rare, less than a day or two",
            "value": 1
          },
          {
            "title": "Several days",
            "value": 2
          },
          {
            "title": "More than half the days",
            "value": 3
          },
          {
            "title": "Nearly every day",
            "value": 4
          }
        ],
        "questions": [
          {
            "question_id": "question_a",
            "title": "Little interest or pleasure in doing things?"
          },
          {
            "question_id": "question_b",
            "title": "Feeling down, depressed, or hopeless?"
          },
          {
            "question_id": "question_c",
            "title": "Sleeping less than usual, but still have a lot of energy?"
          },
          {
            "question_id": "question_d",
            "title": "Starting lots more projects than usual or doing more risky things than usual?"
          },
          {
            "question_id": "question_e",
            "title": "Feeling nervous, anxious, frightened, worried, or on edge?"
          },
          {
            "question_id": "question_f",
            "title": "Feeling panic or being frightened?"
          },
          {
            "question_id": "question_g",
            "title": "Avoiding situations that make you feel anxious?"
          },
          {
            "question_id": "question_h",
            "title": "Drinking at least 4 drinks of any kind of alcohol in a single day?"
          }
        ]
      }
    ],
    "display_name": "BDS"
  },
  "full_name": "Blueprint Diagnostic Screener"
}
```
</details>

`POST /screener/<screener-id>/answers`
This endpoint expects the answers to be sent and returns a list of the assessments to use based on the answers
<details>
<summary>Expected Request JSON:</summary>

```
{
    "answers": (required) [
        {
            "value": (required) Integer,
            "question_id": (required) String
        }, ...
    ]
}
```
An example:
```
{
  "answers": [
    {
      "value": 1,
      "question_id": "question_a"
    },
    {
      "value": 0,
      "question_id": "question_b"
    },
    {
      "value": 2,
      "question_id": "question_c"
    },
    {
      "value": 3,
      "question_id": "question_d"
    },
    {
      "value": 1,
      "question_id": "question_e"
    },
    {
      "value": 0,
      "question_id": "question_f"
    },
    {
      "value": 1,
      "question_id": "question_g"
    },
    {
      "value": 0,
      "question_id": "question_h"
    }
  ]
}
```
</details>
<details>
<summary>Response JSON</summary>

```
{
  "results": (required) String[] // Note that the only possible values in this list are: "ASRM", "PHQ-9", "ASSIST"
}
```
An Example:
```
{
  "results": ["ASRM", "PHQ-9"]
}
```
</details>

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