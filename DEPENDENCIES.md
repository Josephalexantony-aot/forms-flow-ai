# Dependencies Details

In the following document, we’ll describe the details of dependencies of various components in the **formsflow.ai** solution.

## 1. forms-flow-analytics

   To  build interactive dashboards and gain insights.

  | Component | Version|  
  | ---       | -----   |
  |  Redash   | 24.04.0 |

<br>

## 2. forms-flow-api

   REST API to formsflow.ai integration components

   | Component | Version |  
   | ---       | -----   |
   |  Python   |  3.13.2 |
   | Flask     |  3.1.0  |
   |  Postgres |  11.0   |

  <br>
  
## 3. forms-flow-bpm

   For workflow and decision automation<br>

   | Component | Version|  
   | ---       | -----  |
   |  Camunda  |  7.21.0 |
   |  SpringBoot  | 3.3.5 |
   | Postgres    | Latest |
  <br>
  
## 4. forms-flow-forms

   To  build data management applications<br>

   | Component | Version|  
   | ---       | -----   |
   |   Formio | 3.2.0 |
   |   Mongo | 5.0 |
   <br>

## 5. forms-flow-idm

   Identity Management<br>

   | Component | Version|  
   | ---       | -----   |
   | Keycloak  | 7.0  and above   |
   <br>

#### NOTE

* If you are using keycloak version **11.0 and above**, you can use the keycloak import script  [mentioned here](https://github.com/AOT-Technologies/forms-flow-ai/blob/master/forms-flow-idm/keycloak/imports/formsflow-ai-realm.json) .
* If you are in keycloak version **7.0 and above**, refer our [guide](https://github.com/AOT-Technologies/forms-flow-ai/blob/master/forms-flow-idm/keycloak/README.md#create-realm) on how to manually setup keycloak roles/users .
   <br>

## 6. forms-flow-web

   Delivers progressive web application<br>

   | Component | Version |
   |  --- | --- |
   | React  | 17.0.2 |
   | Formio | 4.21.4 |
   <br>

## 7. forms-flow-web-root-config

   To create new front-end modules<br>

   | Component | Version |
   |  --- | --- |
   | React  | 17.0.2 |
   | Formio | 4.21.4 |
   | Webpack| 5.94.0|
   <br>
