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

# Credits
1. Code for some configuration and logging is adapted from: https://gitlab.com/patkennedy79/flask_user_management_example and https://github.com/miguelgrinberg/flasky