### AI-Assisted Take Home Assessment

#### Expense Settlement with Client Library

### Overview

You are tasked with developing a simple REST server and client library using AI-assisted
development practices. This assessment evaluates your ability to leverage AI tools effectively to
design, implement, and deploy a production-ready service, with a client library that is compatible
with its API.

The domain of the service is managing split expenses between members of a group.

Spend up to 2 hours on this take-home assessment.

## Project Requirements

#### Behaviors

 1. User sign up
 2. Authentication for existing user
 3. User profile management
 4. View user’s groups
 5. Group management
    * Add group
    * Add user to group as member
 6. Expense management
    * Add expense for group (paying user and amount + any metadata)
    * View expense history
    * Summarize balance by amount owed to members (assuming equal share in each
expense)

## Core Components

You must develop the following three components:

 1. Python Backend Service using a SQL database
    * API supporting the behaviors.
    * Database implementation + data modeling
    * Type safety guardrails and schema validation
    * Client library in Typescript.
 2. Typescript Frontend Application using a client library
    * Lightweight frontend UX demonstrating the behaviors.
    * Authentication handling
    * Use client library with the backend API for data persistence and business logic.
 3. Infrastructure Definitions
    * Infrastructure as Code using terraform
    * Design for resilience
    * Secret management
    * Observability configuration

## Deliverables

Please submit the following items collected in a zip file with your name:

 1.  Source code directories
    * All three components held in separate directories
    * Any automated testing code/config for each component
    * Configuration for local dev operation
 2. Documentation
    * README.md with local dev setup instructions
    * API documentation
    * Any architectural diagrams
    * Security consideration document
 3. AI Usage Report
    * Please name this AI_JOURNAL.md
    * Include which tools and models were used (Claude code, ChatGPT, Cursor,
Copilot, etc.)
    * Example prompts / iterations
    * Document any challenges you faced and how AI helped to solve them.
    * Document any tasks where manual intervention was needed and what you did
    * Optional: include AI tool logs

## Additional Notes

 - You MUST use any AI tools available to you
 - External libraries and frameworks are allowed
 - Focus on demonstrating iterative AI-assisted development
 - Partial implementations are acceptable if you run out of time and document why
 - Security note - ensure no secrets are included in your deliverables