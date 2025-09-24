# Ikigai Coding Challenge

## Welcome Message

Hi Candidates!

Welcome to the Ikigai Coding Challenge! This is a take-home exercise, and upon receiving this email, **you will have roughly/more than 48 hours to submit your solution**. Please fork this repository into your own github account and begin working on the solution.

## Instructions

It is strongly recommended that you read the questions in the README carefully. You should have all the information you need to complete this refactoring exercise. If you encounter any ambiguities, please make logical assumptions and ensure these assumptions are clearly stated when you submit your solution.

## Submission Process

Once you're done, please email us the repository link to your solution. We will evaluate the submission and inform you of the results. If your solution is accepted, we'll schedule a live coding session with you (1 hour) to discuss your solution and enhance it with additional requirements. If your solution is not accepted, we will let you know why we rejected the submission.

## Resources

You're encouraged to google or make use of any AI solutions available.

## Technical Requirements

### Language Options
The exercise will be available in:
- Java
- Kotlin
- C#
- Python
- TypeScript (Node.js)

### System Requirements
- **TypeScript (Node.js)**: Please ensure to have node >= 16.16.0 installed beforehand
- **Java**: Please have Java >= 17 version ready

## Repository

**Repository Link:** https://github.com/ikigai-digital/time-deposit-take-home-kata

## Challenge Requirements

### Overview
A junior developer implemented some domain logic in a time deposit system but did not complete the API functionality. Your task is to refactor the existing codebase to implement all required functionalities based on the provided business requirements, ensuring no breaking changes occur.

### API Endpoints
- **Create a RESTful API endpoint** for updating the balances of all time deposits in the database
- **Create a RESTful API endpoint** to get all time deposits
- **Get API Response Schema:**
  - `id`
  - `planType`
  - `balance`
  - `days`
  - `withdrawals`
- Choose any API framework you prefer

### Database Setup
Store all time deposit plans in a database with the following tables:

#### `timeDeposits` Table
- `id`: Integer (primary key)
- `planType`: String (required)
- `days`: Integer (required)  
- `balance`: Decimal (required)

#### `withdrawals` Table
- `id`: Integer (primary key)
- `timeDepositId`: Integer (Foreign Key, required)
- `amount`: Decimal (required)
- `date`: Date (required)

### Interest Calculation Logic
Implement monthly interest calculation based on plan type:

- **Basic plan**: 1% interest
- **Student plan**: 3% interest (no interest after 1 year)
- **Premium plan**: 5% interest (interest starts after 45 days)
- **Important**: No interest for the first 30 days for all plans

### Refactoring Constraints
- **DO NOT** introduce breaking changes to the shared `TimeDeposit` class
- **DO NOT** modify the `updateBalance` method signature
- Ensure your design is extensible for future complexities in interest calculations
- The existing `TimeDepositCalculator.updateBalance` method is functioning correctly and must remain unchanged after refactoring

### Code Quality Requirements
- Adhere to **SOLID principles**, design patterns, and clean code practices
- Embrace **Hexagonal Architecture**, Clean Architecture, or other suitable architectural patterns
- Use **atomic commits**
- Implement **test containers**
- Include clear instructions on how to run the application

### Additional Requirements
- Your final solution should include **exactly two API endpoints** (no additional endpoints)
- Do not create pull requests or new branches in the ikigai-digital repository
- Work in your forked repository
- No need to handle invalid input/exceptions
- Email the link to your public GitHub repository

## Important Deadline

**⚠️ Submission deadline: September 26th by 11:30 PM HK time**
