# Sub/Swap Marketplace
A platform that allows workers to request subs for their shifts. It'a a marketplace that prices requests based on how inconvenient they are to fulfill. Currently only supports Princeton Computer Science Lab Teaching Assistants. Instructions on how to use the platform: https://subswap.herokuapp.com/about

# Development Instructions
1. Setup a python virtual environment:
    ```
    python3 -m venv env
    # activate based on OS
    ```
2. Install the dependencies:
    `pip install -r requirements.txt`
3. Set the following environment variables:

    ```
    export CONFIG_TYPE="development"
    export FLASK_APP=app.py
    export SECRET_KEY="your_secret_key_here"
    ```
    Alternatively, you can create an `.env` file in the root directory and define the variables there.

4. Initialize the database with mock data by running `flask init_db`. You can edit `subapp/dbscript.py` to change how this data is created and add your own netID to the test users.

5. Start the application using `python app.py` or `flask run`. You will only be able to use hot-reload if you start the app using the first command.

# Admin Features
Currently the application supports adding the schedule for COS126 and 2xx Lab TAs. In the future the scheduler will be a lot more flexible and will allow the user to upload schedules for arbitrary roles. For adding the Lab TA schedules, you will need to upload csv files with the permanent schedule in this format:

| Mon 7-9 | Mon 8-10 | Mon 8-10 | 226/217 Subs |
| ------- | -------- | -------- | ------------ |
| netid1  | netid3   | netid5   | netid6       |
| netid2  | netid4   |          | netid7       |
|         | netid1   |          | netid8       |

I used the following code to convert the permanent shift file with names to NetIDs:


    import pandas as pd
    cos2xx = pd.read_csv('cos2xx.csv')
    cos126 = pd.read_csv('cos126.csv')
    # these files had three rows: first name, last name, princeton email
    cos2xx_netid = pd.read_csv('cos2xx_netid.csv')
    cos126_netid = pd.read_csv('cos126_netid.csv')

    # make sure that the names are identical in both files
    email_dict = {f"{row['first_name']} {row['last_name']}": row['email'].split("@")[0] for i, row in cos2xx_netid.iterrows()}
    cos2xx_new = cos2xx.copy()
    # Replace names with email prefixes
    for column in cos2xx.columns:
        cos2xx_new[column] = cos2xx[column].apply(lambda x: email_dict[x] if x in email_dict else x)

    cos2xx.to_csv('cos2xx_new.csv')

# Credits
1. Code for some configuration and logging is adapted from: https://gitlab.com/patkennedy79/flask_user_management_example and https://github.com/miguelgrinberg/flasky