## What this project is

A Proof of Concept analytics workspace for hospital operations, built to 
demonstrate how AI-assisted natural-language querying can make clinical and 
billing data accessible without SQL knowledge.

This repo contains the data layer: curated MySQL views and KPI queries covering 
appointment volume, cancellation rates, revenue trends, billing breakdowns, 
and provider performance. The SQL layer feeds structured data to an AI query 
interface, enabling non-technical stakeholders to ask questions in plain English 
and receive data-backed answers.

**Business problem solved:** Hospital operations teams couldn't easily query 
performance data without engineering support. This workspace made KPI data 
self-serve and repeatable.

**Tech stack:** MySQL, SQL views, KPI query library
**AI layer:** Natural-language interface over structured views
