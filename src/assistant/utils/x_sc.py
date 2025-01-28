import tweepy
from dotenv import load_dotenv
import os

# Load environment variables
load_dotenv()

# Define a configuration class to store API keys and tokens
class TwitterAPIConfig:
    """
    A configuration class to store and validate Twitter API keys and tokens.

    Attributes:
        access_token (str): Access token for Twitter API.
        access_token_secret (str): Access token secret for Twitter API.
        consumer_key (str): Consumer key for Twitter API.
        consumer_secret (str): Consumer secret for Twitter API.
        bearer_token (str): Bearer token for Twitter API.
    """

    def __init__(self):
        self.access_token = os.getenv("ACCESS_TOKEN")
        self.access_token_secret = os.getenv("ACCESS_TOKEN_SECRET")
        self.consumer_key = os.getenv("CONSUMER_KEY")
        self.consumer_secret = os.getenv("CONSUMER_SECRET")
        self.bearer_token = os.getenv("BEARER_TOKEN")

        # Validate credentials
        self._validate_credentials()

    def _validate_credentials(self):
        """
        Validates that all required API credentials are present.

        Raises:
            ValueError: If any of the API credentials are missing.
        """
        if not all([
            self.access_token,
            self.access_token_secret,
            self.consumer_key,
            self.consumer_secret,
            self.bearer_token
        ]):
            raise ValueError("One or more API credentials are missing from environment variables.")

# Define a Twitter API client class
class TwitterAPIClient:
    """
    A client class to interact with the Twitter API using Tweepy.

    Attributes:
        client (tweepy.Client): A Tweepy client instance for API v2.
    """

    def __init__(self, config):
        """
        Initializes the TwitterAPIClient with the given configuration.

        Args:
            config (TwitterAPIConfig): The configuration object containing API credentials.
        """
        self.client = tweepy.Client(
            access_token=config.access_token,
            access_token_secret=config.access_token_secret,
            consumer_key=config.consumer_key,
            consumer_secret=config.consumer_secret,
            bearer_token=config.bearer_token,
            wait_on_rate_limit=True
        )

    def get_client(self):
        """
        Returns the Tweepy client instance for API v2.

        Returns:
            tweepy.Client: The Tweepy client instance.
        """
        return self.client
    
    def v1_api(self, config):
        """
        Returns a Tweepy API instance for API v1.1.

        Args:
            config (TwitterAPIConfig): The configuration object containing API credentials.

        Returns:
            tweepy.API: The Tweepy API instance for API v1.1.
        """
        auth = tweepy.OAuthHandler(config.consumer_key, config.consumer_secret)
        auth.set_access_token(config.access_token, config.access_token_secret)
        return tweepy.API(auth)

# Function to initialize the Twitter API client
def initialize_twitter_client():
    """
    Initializes and returns the Twitter API client.

    Returns:
        tuple: A tuple containing the Tweepy client for API v2 and API v1.1.
        None: If there is an error in initializing the client.
    """
    try:
        config = TwitterAPIConfig()  # Load configuration
        client = TwitterAPIClient(config)  # Create client
        return client.get_client(), client.v1_api(config)  # Return the Tweepy client
    except ValueError as e:
        print(f"Error initializing Twitter client: {e}")
        return None
