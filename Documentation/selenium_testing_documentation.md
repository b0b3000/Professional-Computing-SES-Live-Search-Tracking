# STT Selenium Testing Documentation

## Overview

This document outlines the structure and implementation of Selenium testing for the Flask web application. It provides information on the setup, configuration, and individual test cases to verify the application's functionality using automated browser tests.

## Table of Contents

1. [Project Structure](#project-structure)
2. [Setup and Installation](#setup-and-installation)
3. [Test Cases Overview](#test-cases-overview)
4. [Running the Tests](#running-the-tests)
5. [Expected Outcomes](#expected-outcomes)
6. [Troubleshooting](#troubleshooting)
7. [Contributing](#contributing)

## Project Structure

The Selenium tests are organized in the `selenium_testing` folder, located in the root directory of the project. The folder structure is as follows:

```
├── 3200
│   ├── bin
│   ├── include
│   ├── lib
│   ├── pyvenv.cfg
│   └── share
├── Base-Station
│   ├── base.py
│   ├── base_deprecated.py
│   ├── keys.txt
│   ├── requirements.txt
│   └── upload_deprecated.py
├── Documentation
│   ├── hardware_documentation.md
│   ├── projectmanagement_documentation
│   ├── selenium_testing_documentation.md
│   ├── technical_documentation.md
│   └── userinterface_documentation.md
├── README.md
├── Selenium-Testing
│   └── test_flask_app.py
├── Testing
│   ├── Azure_Testing
│   ├── Mapping-Tool
│   ├── Meshtastic-Testing
│   ├── Web-App
│   ├── base-3200-a
│   ├── dbconntest.py
│   └── fake_upload.py
├── Web-App
│   ├── __pycache__
│   └── app
├── __pycache__
│   ├── app.cpython-311.pyc
│   ├── get_key.cpython-311.pyc
│   ├── historical_database.cpython-311.pyc
│   ├── retrieve_from_containers.cpython-311.pyc
│   └── to_gpx.cpython-311.pyc
├── app.py
├── appREADME.md
├── application
│   ├── __init__.py
│   ├── __pycache__
│   ├── routes.py
│   ├── static
│   └── templates
├── base-3200-a.gpx
├── base-3200-b.gpx
├── base-station0.gpx
├── base-station1.gpx
├── config.py
├── get_key.py
├── historical_database.py
├── keys.txt
├── requirements.txt
├── retrieve_from_containers.py
├── search_data
│   ├── 20240913225854
│   ├── 20240913225854.zip
│   ├── 20240916103651
│   ├── 20240918121522
│   ├── 20240918121522.zip
│   └── 20240923152355
└── to_gpx.py
```

## Setup and Installation

### Prerequisites

- Python 3.x
- Selenium library
- A web driver (e.g., ChromeDriver or GeckoDriver)
- Flask application running locally on `http://127.0.0.1:5000`

### Installation Steps

1. **Install Python Packages:**

   Navigate to the root directory of the project and install the required Python packages:

   ```bash
   pip install -r requirements.txt
   pip install selenium
   ```

2. **Download and Install a Web Driver:**

   Download the appropriate web driver for your browser:

   - [ChromeDriver](https://sites.google.com/chromium.org/driver/)
   - [GeckoDriver (for Firefox)](https://github.com/mozilla/geckodriver/releases)

   Make sure the web driver is added to your system's PATH or specify the path in the test script.

3. **Start the Flask Application:**

   Make sure the Flask app is running locally before executing the Selenium tests:

   ```bash
   export FLASK_APP=app
   flask run
   ```

## Test Cases Overview

This section provides an overview of the different test cases implemented in each script:

### `test_flask_app.py`

- **Test Name:** `test_homepage_loads`
- **Description:** Verifies that the homepage loads successfully and the title is correct.
- **Steps:**
  1. Navigate to the homepage.
  2. Check if the page title is "My Flask App".
  3. Verify the presence of the main header element.
  
- **Expected Result:** The homepage should load, and the header element should be displayed.

### `test_login.py`

- **Test Name:** `test_valid_login`
- **Description:** Verifies that a user can log in with valid credentials.
- **Steps:**
  1. Navigate to the login page.
  2. Enter valid username and password.
  3. Click the login button.
  4. Check if redirected to the user dashboard.
  
- **Expected Result:** The user should be redirected to the dashboard after logging in.

### `test_navigation.py`

- **Test Name:** `test_navigation_links`
- **Description:** Checks if the navigation links work correctly.
- **Steps:**
  1. Click on the 'About' link in the navigation bar.
  2. Verify if the URL changes to `/about`.
  3. Check if the 'Contact' link navigates to the correct page.

- **Expected Result:** All navigation links should work as expected.

## Running the Tests

### Using `unittest`

1. Navigate to the `selenium_testing` folder:

   ```bash
   cd selenium_testing
   ```

2. Run individual test scripts:

   ```bash
   python test_flask_app.py
   ```

3. Run all tests in the folder:

   ```bash
   python -m unittest discover
   ```

### Using `pytest`

To run all Selenium tests using `pytest`, execute the following command from the root directory:

```bash
pytest selenium_testing/
```

## Expected Outcomes

The following are the expected outcomes for each test case:

- All pages load correctly.
- Forms submit and validate inputs as expected.
- Navigation links work and redirect to the correct pages.

## Troubleshooting

- **Issue:** `WebDriverException: Message: 'chromedriver' executable needs to be in PATH.`
  - **Solution:** Ensure that `chromedriver` is in your system's PATH or specify the full path in the test script.

- **Issue:** `ConnectionRefusedError: [Errno 111] Connection refused`
  - **Solution:** Make sure the Flask app is running locally on `http://127.0.0.1:5000` before starting the tests.

- **Issue:** Selenium tests are running but not interacting with the elements.
  - **Solution:** Verify that the elements exist in the DOM and that the correct locators (ID, class, XPath, etc.) are used.

## Contributing

If you would like to contribute to the Selenium testing suite, please follow these guidelines:

1. Add new test cases in a separate script file within the `selenium_testing` folder.
2. Ensure all new tests pass before submitting a pull request.
3. Update this documentation to include details about new test cases.

---

Feel free to modify this template to fit your project’s requirements! Let me know if you need more detailed descriptions or additional sections.