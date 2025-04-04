"use client";

import { Model } from "survey-core";
import { Survey } from "survey-react-ui";
import { useCallback, useState, useEffect } from "react";

const backendUrlBase = "http://localhost:8080/screener";

interface QuestionJson {
  question_id: string;
  title: string;
}

interface AnswerOptionJson {
  title: string;
  value: string;
}

interface SectionJson {
  type: string;
  title: string;
  questions: QuestionJson[];
  answers: AnswerOptionJson[];
}

interface ContentJson {
  display_name: string;
  sections: SectionJson[];
}

interface ScreenerJson {
  id: string;
  disorder: string;
  name: string;
  full_name: string;
  content: ContentJson;
}

export default function SurveyComponent() {
  const survey = new Model();
  const [surveyJson, setSurveyJson] = useState<ScreenerJson | null>(null);

  const surveyComplete = useCallback(getSurveyResults, []);

  useEffect(() => {
    fetchSurveyJson(setSurveyJson);
  }, []);

  if (!surveyJson) {
    return <div>Loading survey...</div>;
  }

  survey.title = surveyJson.full_name;
  survey.autoAdvanceEnabled = true;
  survey.autoAdvanceAllowComplete = false;
  survey.showProgressBar = true;
  survey.firstPageIsStartPage = true;
  survey.startSurveyText = "Let's Begin";
  survey.completedHtml = "<h3>Thank you for completing the screener!<h3>";
  const startPage = survey.addNewPage("startPage");
  const opener = startPage.addNewQuestion("html");
  opener.html = `<h3> Welcome to the ${surveyJson.full_name}! <br /> <br /> Please answer the following questions to the best of your ability. </h3>`;

  surveyJson.content.sections.forEach((section: SectionJson) => {
    section.questions.forEach((question: QuestionJson) => {
      const questionPage = survey.addNewPage(`${question.question_id}Page`);
      const fullPanel = questionPage.addNewPanel(
        `${question.question_id}Panel`
      );
      fullPanel.title = section.title;
      const surveyQuestion = fullPanel.addNewQuestion(
        "rating",
        question.question_id
      );
      surveyQuestion.title = question.title;
      surveyQuestion.displayMode = "buttons";
      surveyQuestion.isRequired = true;
      surveyQuestion.rateValues = section.answers.map(
        (answerOption: AnswerOptionJson) => {
          return { value: answerOption.value, text: answerOption.title };
        }
      );
    });
  });

  const s2 = new Model(survey.toJSON());
  s2.onComplete.add(surveyComplete);

  return <Survey model={s2} />;
}

async function fetchSurveyJson(setSurveyJson: CallableFunction) {
  try {
    const response = await fetch(`${backendUrlBase}/abcd-123`, {
      method: "GET",
      headers: {
        "Content-Type": "application/json",
      },
    });
    if (response.ok) {
      const data = await response.json();
      setSurveyJson(data);
    } else {
      alert("Failed to load survey data. Please try again later.");
    }
  } catch (error) {
    alert(`An error occurred while fetching the survey data. ${error}`);
  }
}

async function getSurveyResults(survey: Model) {
  const answerData = Object.entries(survey.data).reduce(
    (prevVal: object[], [qid, ans]) =>
      prevVal.concat({ question_id: qid, value: ans }),
    []
  );

  fetch(`${backendUrlBase}/abcd-123/answers`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json;",
    },
    body: JSON.stringify({ answers: answerData }),
  })
    .then((response: Response) => {
      if (response.ok) {
        response
          .json()
          .then((results) => alert(JSON.stringify(results.results)));
      } else {
        alert("Something went wrong! Please try again later.");
      }
    })
    .catch((error) => {
      alert(`Something went wrong! Please try again later. ${error}`);
    });
}
