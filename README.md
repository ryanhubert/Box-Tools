# Box-Tools

Box.com offers tools that enable you to interact with your Box.com account from within Python. This is called the Box SDK.

## Setting Up Your Box.com Developer Account

In order to use the Box SDK, you will need to activate a developer account and create a "custom app" that will allow you to interact with your Box account through Python. Do the following:

1. Go to [http://developers.box.com](http://developers.box.com).
2. Log in using your credentials.
3. Create a new app (it doesn't matter what you call it).
4. Select a custom app, then under "Authentication Method," select **Standard OAuth 2.0**.

Once you have set up your custom app, there are two pieces of information you will need before you can use the `BoxTools` module: your `Client ID` and `Client Secret`. Both are found in the **Configuration** menu of your custom app.

## Installation

At your command line, execute `pip install boxsdk` to install the `boxsdk` Python module.

Then, install the `BoxTools` module from this Github repo.

## Other Information

For the full instructions, see [Box's Tutorial](http://opensource.box.com/box-python-sdk/tutorials/intro.html).
