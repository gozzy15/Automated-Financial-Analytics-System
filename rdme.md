# Financial Data Intelligence Platform

A comprehensive financial analytics platform that automates stock market data collection, ETL processing, machine learning-based price prediction, interactive dashboard visualization, automated reporting, Google Drive integration, and email-based report distribution.

The system combines data engineering, data analytics, machine learning, and business intelligence into a single end-to-end financial analysis workflow.

## Project Overview

The **Financial Analytics System** is an end-to-end Python application designed to automate the collection, processing, analysis, visualization, and reporting of stock market data. It demonstrates how data engineering, machine learning, and business intelligence can be integrated into a single workflow for financial analysis.

The system extracts historical and live market data from financial data sources, processes the data through an ETL (Extract, Transform, Load) pipeline, stores the cleaned data in a SQLite database, and performs financial analysis using technical indicators and machine learning models. It then presents the results through interactive dashboards, automated reports, and email notifications.

The project includes two complementary dashboards:

* A **Streamlit dashboard** for simple, user-friendly exploration of financial data.
* A **Dash dashboard** for more advanced analytics, interactive visualizations, and portfolio insights.

To support automation, the application integrates with Google Drive for data storage and retrieval, generates Excel, CSV, and HTML reports, and can automatically distribute reports via email with file attachments.

The machine learning component uses a Random Forest regression model to forecast future stock prices, estimate expected returns, and generate basic trading signals such as **Buy**, **Hold**, and **Sell** based on predicted market movement.

Overall, this project demonstrates practical skills in:

* Data Engineering
* ETL Pipeline Development
* Financial Data Analysis
* Machine Learning
* Interactive Dashboard Development
* Data Visualization
* Database Design
* Reporting Automation
* Cloud Integration
* Python Application Development
