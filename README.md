## Finance WebApp

### Description

C$50 Finance is a web application that allows users to manage portfolios of stocks. Users can:

*   Register for an account and log in.
*   Look up real-time stock prices using the IEX API.
*   Virtually buy and sell stocks using a starting balance of \$10,000.
*   View their portfolio, including a summary of their holdings, the current value of each stock, and their total portfolio value.
*   Track their transactions in a history table.
*   Add a personal touch feature such as the ability to change passwords or add cash to their account.

### Features

*   User registration and login
*   Real-time stock quotes
*   Virtual stock trading
*   Portfolio tracking and history
*   Personal touch features

### Technologies Used

*   **Flask framework:** Web application framework
*   **SQLite database:** Relational database management system
*   **CS50’s SQL module:** Python library for interacting with SQLite databases
*   **Jinja templating engine:** Templating engine for rendering HTML
*   **Bootstrap:** Front-end framework for styling and layout
*   **IEX API:** Financial data provider for real-time stock quotes

### Installation

1.  Download the distribution code from the CS50x 2024 website.
2.  Install the necessary packages listed in `requirements.txt`.
3.  Run the Flask server using `flask run`.

### Usage

1.  Register for an account using the registration form.
2.  Log in to your account.
3.  Use the search bar to look up stock quotes.
4.  Buy and sell stocks using the provided forms.
5.  View your portfolio and transaction history on the index page.
6.  Explore the personal touch feature you implemented.

### Testing

1.  **Manual Testing:** Thoroughly test the application by performing various actions, including:
    *   Registering a new user and verifying that the portfolio page loads with the correct information.
    *   Requesting a quote using a valid stock symbol.
    *   Purchasing one stock multiple times, verifying that the portfolio displays correct totals.
    *   Selling all or some of a stock, again verifying the portfolio.
    *   Verifying that your history page shows all transactions for your logged in user.

2.  **Automated Testing:** Use the `check50` tool to run automated tests on your code.

3.  **Edge Case Testing:** Test for unexpected usage, such as:

    *   Inputting alphabetical strings into forms when only numbers are expected.
    *   Inputting zero or negative numbers into forms when only positive numbers are expected.
    *   Inputting floating-point values into forms when only integers are expected.
    *   Trying to spend more cash than a user has.
    *   Trying to sell more shares than a user has.
    *   Inputting an invalid stock symbol.
    *   Including potentially dangerous characters like `'` and `;` in SQL queries.

4.  **HTML Validation:** Check the validity of your HTML by clicking the "I ♥ VALIDATOR" button in the footer of each page.

### Troubleshooting

*   **"ImportError: No module named ‘application’"**: Make sure you are running `flask run` in the correct directory (the directory containing `app.py`).

*   **"OSError: \[Errno 98] Address already in use"**: This error occurs when the Flask server is already running. Kill the existing process using `ctrl-c` or `fuser -k 8080/tcp`.

### Credits

This project is based on the **C$50 Finance problem set** developed by the **CS50 team at Harvard University**. Special thanks to **David J. Malan** (malan@harvard.edu) for leading the CS50x 2024 course.

This project utilizes several technologies and libraries:

*   **Flask framework**
*   **SQLite database**
*   **CS50's SQL module**
*   **Jinja templating engine**
*   **Bootstrap**
*   **IEX API**
